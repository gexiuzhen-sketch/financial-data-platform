"""
财经媒体爬虫
从新浪财经、网易财经等财经媒体抓取行业新闻数据
"""
import re
from typing import List, Dict, Any, Optional
from datetime import datetime, timedelta
from .base import BaseScraper, ScraperFactory


class MediaScraper(BaseScraper):
    """财经媒体爬虫"""

    # 财经媒体配置
    MEDIA_SOURCES = {
        '新浪财经': {
            'base_url': 'https://finance.sina.com.cn',
            'search_path': '/search/',
            'search_param': 'q'
        },
        '网易财经': {
            'base_url': 'https://money.163.com',
            'search_path': '/search/',
            'search_param': 'q'
        },
        '搜狐财经': {
            'base_url': 'https://business.sohu.com',
            'search_path': '/search',
            'search_param': 'keyword'
        }
    }

    # 平台关键词映射
    PLATFORM_KEYWORDS = {
        '蚂蚁': ['花呗', '借呗', '网商银行', '蚂蚁集团', '蚂蚁花呗', '蚂蚁借呗'],
        '腾讯': ['微粒贷', '微业贷', '微众银行', '腾讯'],
        '字节': ['抖音', '今日头条', '字节跳动', '字节'],
        '百度': ['度小满', '百度金融'],
        '京东': ['京东金条', '京东白条', '京东数科', '京东科技'],
        '美团': ['美团借钱', '美团生活费', '美团']
    }

    def __init__(self, source: str = '新浪财经'):
        """
        初始化财经媒体爬虫

        Args:
            source: 媒体名称
        """
        if source not in self.MEDIA_SOURCES:
            raise ValueError(f'不支持的媒体: {source}')

        config = self.MEDIA_SOURCES[source]
        super().__init__(
            name=f'MediaScraper_{source}',
            base_url=config['base_url']
        )
        self.source = source
        self.search_path = config['search_path']
        self.search_param = config['search_param']

    def search_articles(self, keyword: str, days: int = 30) -> List[Dict[str, str]]:
        """
        搜索新闻文章

        Args:
            keyword: 搜索关键词
            days: 搜索最近多少天的文章

        Returns:
            文章列表
        """
        # 计算日期范围
        end_date = datetime.now()
        start_date = end_date - timedelta(days=days)

        search_url = f'{self.base_url}{self.search_path}'
        params = {self.search_param: keyword}

        response = self.request_with_retry(search_url, params=params)
        if not response:
            return []

        soup = self.parse_html(response.text)
        articles = []

        # 解析文章列表（需要根据实际HTML结构调整）
        article_items = soup.find_all('div', class_=re.compile(r'article|item|news'))
        for item in article_items:
            title_elem = item.find('a', class_=re.compile(r'title|link'))
            date_elem = item.find('span', class_=re.compile(r'date|time'))

            if not title_elem:
                continue

            title = self.extract_text(title_elem)
            url = title_elem.get('href', '')
            date_str = self.extract_text(date_elem) if date_elem else ''

            # 补全URL
            if url and not url.startswith('http'):
                url = f'{self.base_url}{url}'

            # 解析日期
            pub_date = self._parse_date(date_str)

            # 过滤日期范围
            if pub_date and pub_date >= start_date:
                articles.append({
                    'title': title,
                    'url': url,
                    'pub_date': pub_date
                })

        self.logger.info(f'找到 {len(articles)} 篇文章')
        return articles

    def parse_article(self, article_url: str, pub_date: datetime) -> List[Dict[str, Any]]:
        """
        解析文章内容

        Args:
            article_url: 文章URL
            pub_date: 发布日期

        Returns:
            提取的数据列表
        """
        self.logger.info(f'解析文章: {article_url}')

        response = self.request_with_retry(article_url)
        if not response:
            return []

        soup = self.parse_html(response.text)
        data = []

        # 查找文章正文
        article_body = soup.find('div', class_=re.compile(r'article|content|body'))
        if not article_body:
            return []

        # 提取所有文本段落
        paragraphs = article_body.find_all('p')
        full_text = ' '.join(self.extract_text(p) for p in paragraphs)

        # 提取数据
        for group, keywords in self.PLATFORM_KEYWORDS.items():
            for keyword in keywords:
                if keyword in full_text:
                    # 查找该平台相关的数据
                    extracted = self._extract_platform_data(full_text, group, keyword, article_url, pub_date)
                    if extracted:
                        data.append(extracted)

        return data

    def _extract_platform_data(
        self,
        text: str,
        group: str,
        keyword: str,
        source_url: str,
        pub_date: datetime
    ) -> Optional[Dict[str, Any]]:
        """从文本中提取平台数据"""

        # 提取贷款余额
        balance_patterns = [
            rf'{keyword}[：:\s]*(?:贷款余额|余额|存量)[：:\s]*([0-9,]+\.?[0-9]*)\s*(?:亿|亿元)',
            r'(?:贷款余额|余额|存量)[：:\s]*([0-9,]+\.?[0-9]*)\s*(?:亿|亿元).*?{keyword}',
        ]
        loan_balance = None
        for pattern in balance_patterns:
            match = re.search(pattern, text)
            if match:
                loan_balance = self.clean_number(match.group(1))
                break

        # 提取发放规模
        issued_patterns = [
            rf'{keyword}[：:\s]*(?:发放|交易|放款)[：:\s]*([0-9,]+\.?[0-9]*)\s*(?:亿|亿元)',
            r'(?:发放|交易|放款)[：:\s]*([0-9,]+\.?[0-9]*)\s*(?:亿|亿元).*?{keyword}',
        ]
        loan_issued = None
        for pattern in issued_patterns:
            match = re.search(pattern, text)
            if match:
                loan_issued = self.clean_number(match.group(1))
                break

        # 如果没有找到任何数据，返回None
        if not loan_balance and not loan_issued:
            return None

        # 判断产品类型和贷款用途
        platform_type = '联合贷' if '联合' in text else '助贷'
        loan_type = '经营类' if '小微' in text or '企业' in text else '消费类'

        return {
            'name': keyword,
            'company_group': group,
            'report_month': pub_date.replace(day=1),  # 使用月份作为报告月
            'loan_balance': loan_balance,
            'loan_issued': loan_issued,
            'platform_type': platform_type,
            'loan_type': loan_type,
            'data_source': self.source,
            'source_url': source_url
        }

    def _parse_date(self, date_str: str) -> Optional[datetime]:
        """解析日期字符串"""
        if not date_str:
            return None

        # 尝试多种日期格式
        patterns = [
            r'(\d{4})-(\d{1,2})-(\d{1,2})',
            r'(\d{4})/(\d{1,2})/(\d{1,2})',
            r'(\d{4})年(\d{1,2})月(\d{1,2})日',
            r'(\d{1,2})-(\d{1,2})',  # MM-DD，使用当年
            r'(\d{1,2})月(\d{1,2})日',  # MM月DD日，使用当年
        ]

        for pattern in patterns:
            match = re.search(pattern, date_str)
            if match:
                try:
                    groups = match.groups()
                    if len(groups) == 3:
                        return datetime(int(groups[0]), int(groups[1]), int(groups[2]))
                    elif len(groups) == 2:
                        return datetime(datetime.now().year, int(groups[0]), int(groups[1]))
                except ValueError:
                    continue

        return None

    def scrape(self, keywords: List[str] = None, days: int = 7, max_articles: int = 20) -> List[Dict[str, Any]]:
        """
        执行爬取

        Args:
            keywords: 搜索关键词列表
            days: 搜索最近多少天的文章
            max_articles: 每个关键词最大文章数

        Returns:
            爬取的数据列表
        """
        if keywords is None:
            keywords = ['消费金融', '互联网贷款', '助贷平台']

        self.logger.info(f'开始爬取{self.source}，关键词: {keywords}')

        all_data = []

        for keyword in keywords:
            self.logger.info(f'搜索关键词: {keyword}')

            articles = self.search_articles(keyword, days)[:max_articles]

            for article in articles:
                data = self.parse_article(article['url'], article['pub_date'])
                all_data.extend(data)

                # 添加延迟
                import time
                time.sleep(1)

        self.logger.info(f'爬取完成，共获取 {len(all_data)} 条数据')
        return all_data

    def save_data(self, data: List[Dict[str, Any]], db_session) -> int:
        """保存数据到数据库"""
        from ..models import Platform

        saved_count = 0
        for item in data:
            # 检查是否已存在
            existing = db_session.query(Platform).filter_by(
                name=item['name'],
                report_month=item['report_month'],
                platform_type=item.get('platform_type', '联合贷'),
                loan_type=item.get('loan_type', '消费类')
            ).first()

            if not existing:
                platform = Platform(**item)
                db_session.add(platform)
                saved_count += 1

        return saved_count


# 注册爬虫
ScraperFactory.register(MediaScraper)
