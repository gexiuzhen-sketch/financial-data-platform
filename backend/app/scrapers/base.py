"""
基础爬虫类
提供所有爬虫的通用功能和反爬虫策略
"""
import requests
from fake_useragent import UserAgent
import time
import random
import logging
from typing import List, Dict, Optional, Any
from datetime import datetime
from bs4 import BeautifulSoup


class BaseScraper:
    """基础爬虫类"""

    def __init__(self, name: str, base_url: str):
        """
        初始化爬虫

        Args:
            name: 爬虫名称
            base_url: 基础URL
        """
        self.name = name
        self.base_url = base_url
        self.ua = UserAgent()
        self.session = requests.Session()
        self.logger = self._setup_logger()

    def _setup_logger(self) -> logging.Logger:
        """设置日志"""
        logger = logging.getLogger(f'scraper.{self.name}')
        logger.setLevel(logging.INFO)
        return logger

    def get_headers(self) -> Dict[str, str]:
        """
        生成随机请求头

        Returns:
            请求头字典
        """
        return {
            'User-Agent': self.ua.random,
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
            'Accept-Language': 'zh-CN,zh;q=0.9,en;q=0.8',
            'Accept-Encoding': 'gzip, deflate, br',
            'Connection': 'keep-alive',
            'Upgrade-Insecure-Requests': '1',
            'Referer': self.base_url
        }

    def request_with_retry(
        self,
        url: str,
        max_retries: int = 3,
        method: str = 'GET',
        **kwargs
    ) -> Optional[requests.Response]:
        """
        带重试机制的请求

        Args:
            url: 请求URL
            max_retries: 最大重试次数
            method: 请求方法（GET/POST）
            **kwargs: 其他请求参数

        Returns:
            Response对象或None
        """
        headers = self.get_headers()

        for attempt in range(max_retries):
            try:
                # 随机延迟，避免请求过快
                time.sleep(random.uniform(1, 3))

                self.logger.info(f'请求 {url} (尝试 {attempt + 1}/{max_retries})')

                response = self.session.request(
                    method=method,
                    url=url,
                    headers=headers,
                    timeout=30,
                    **kwargs
                )

                # 检查是否被重定向到验证页面
                if 'captcha' in response.url.lower() or response.status_code == 403:
                    raise Exception('遇到反爬验证')

                if response.status_code == 200:
                    self.logger.info(f'请求成功: {url}')
                    return response
                else:
                    self.logger.warning(f'请求失败，状态码: {response.status_code}')

            except Exception as e:
                self.logger.error(f'请求异常 (尝试 {attempt + 1}/{max_retries}): {str(e)}')
                if attempt == max_retries - 1:
                    self.logger.error(f'请求失败，已达最大重试次数: {url}')
                    return None
                time.sleep(random.uniform(5, 10))

        return None

    def parse_html(self, html: str) -> BeautifulSoup:
        """
        解析HTML

        Args:
            html: HTML字符串

        Returns:
            BeautifulSoup对象
        """
        return BeautifulSoup(html, 'lxml')

    def extract_text(self, element) -> str:
        """
        提取元素文本

        Args:
            element: BeautifulSoup元素

        Returns:
            提取的文本
        """
        if element is None:
            return ''
        return element.get_text(strip=True)

    def clean_number(self, text: str) -> Optional[float]:
        """
        清理并转换数字字符串

        Args:
            text: 数字字符串

        Returns:
            浮点数或None
        """
        if not text:
            return None
        # 移除逗号、空格等
        text = text.replace(',', '').replace(' ', '').strip()
        try:
            return float(text)
        except ValueError:
            self.logger.warning(f'无法转换数字: {text}')
            return None

    def save_data(self, data: List[Dict[str, Any]], db_session) -> int:
        """
        保存数据到数据库（子类需实现具体逻辑）

        Args:
            data: 数据列表
            db_session: 数据库会话

        Returns:
            保存的记录数
        """
        raise NotImplementedError('子类必须实现save_data方法')

    def scrape(self, **kwargs) -> List[Dict[str, Any]]:
        """
        执行爬取（子类需实现具体逻辑）

        Args:
            **kwargs: 爬取参数

        Returns:
            爬取的数据列表
        """
        raise NotImplementedError('子类必须实现scrape方法')

    def run(self, db_session, **kwargs) -> Dict[str, Any]:
        """
        运行爬虫

        Args:
            db_session: 数据库会话
            **kwargs: 爬取参数

        Returns:
            爬取结果统计
        """
        start_time = datetime.now()
        self.logger.info(f'开始爬取: {self.name}')

        try:
            # 执行爬取
            data = self.scrape(**kwargs)

            # 保存数据
            if data:
                saved_count = self.save_data(data, db_session)
                db_session.commit()
            else:
                saved_count = 0

            end_time = datetime.now()
            duration = (end_time - start_time).total_seconds()

            result = {
                'scraper': self.name,
                'status': 'success',
                'records_found': len(data),
                'records_saved': saved_count,
                'duration': duration,
                'started_at': start_time,
                'completed_at': end_time,
                'error': None
            }

            self.logger.info(f'爬取完成: 找到 {len(data)} 条记录，保存 {saved_count} 条，耗时 {duration:.2f} 秒')
            return result

        except Exception as e:
            end_time = datetime.now()
            duration = (end_time - start_time).total_seconds()

            result = {
                'scraper': self.name,
                'status': 'failed',
                'records_found': 0,
                'records_saved': 0,
                'duration': duration,
                'started_at': start_time,
                'completed_at': end_time,
                'error': str(e)
            }

            self.logger.error(f'爬取失败: {str(e)}')
            db_session.rollback()
            return result


class ScraperFactory:
    """爬虫工厂类"""

    _scrapers = {}

    @classmethod
    def register(cls, scraper_class: type):
        """注册爬虫"""
        cls._scrapers[scraper_class.__name__] = scraper_class

    @classmethod
    def create(cls, scraper_name: str, **kwargs) -> BaseScraper:
        """创建爬虫实例"""
        scraper_class = cls._scrapers.get(scraper_name)
        if not scraper_class:
            raise ValueError(f'未找到爬虫: {scraper_name}')
        return scraper_class(**kwargs)

    @classmethod
    def list_scrapers(cls) -> List[str]:
        """列出所有已注册的爬虫"""
        return list(cls._scrapers.keys())
