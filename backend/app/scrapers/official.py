"""
官方监管数据爬虫
从中国人民银行、银保监会等官方网站抓取监管数据
"""
import re
from typing import List, Dict, Any, Optional
from datetime import datetime
from .base import BaseScraper, ScraperFactory


class OfficialScraper(BaseScraper):
    """官方监管数据爬虫"""

    # 官方数据源配置
    OFFICIAL_SOURCES = {
        '中国人民银行': {
            'base_url': 'https://www.pbc.gov.cn',
            'data_path': '/diaochatongjisi',
            'file_pattern': r'https://www\.pbc\.gov\.cn/diaochatongjisi/attachDir/\d+/\d+/\d+\.xlsx'
        },
        '银保监会': {
            'base_url': 'https://www.cbirc.gov.cn',
            'data_path': '/cn/static/data',
            'file_pattern': r'https://www\.cbirc\.gov\.cn.*\.xlsx'
        }
    }

    def __init__(self, source: str = '中国人民银行'):
        """
        初始化官方数据爬虫

        Args:
            source: 数据源名称
        """
        if source not in self.OFFICIAL_SOURCES:
            raise ValueError(f'不支持的数据源: {source}')

        config = self.OFFICIAL_SOURCES[source]
        super().__init__(
            name=f'OfficialScraper_{source}',
            base_url=config['base_url']
        )
        self.source = source
        self.data_path = config['data_path']
        self.file_pattern = config['file_pattern']

    def get_data_files(self) -> List[Dict[str, str]]:
        """
        获取数据文件列表

        Returns:
            文件列表
        """
        url = f'{self.base_url}{self.data_path}'
        response = self.request_with_retry(url)
        if not response:
            return []

        soup = self.parse_html(response.text)
        files = []

        # 查找所有Excel文件链接
        for link in soup.find_all('a', href=True):
            href = link['href']

            # 检查是否匹配文件模式
            if re.search(self.file_pattern, href) or href.endswith('.xlsx') or href.endswith('.xls'):
                title = self.extract_text(link)

                # 补全URL
                if not href.startswith('http'):
                    href = f'{self.base_url}{href}'

                # 提取日期
                date_match = re.search(r'(\d{4})(\d{2})(\d{2})', href)
                if date_match:
                    file_date = datetime(int(date_match.group(1)), int(date_match.group(2)), int(date_match.group(3)))
                else:
                    file_date = None

                files.append({
                    'title': title,
                    'url': href,
                    'date': file_date
                })

        # 按日期排序，最新的在前
        files.sort(key=lambda x: x['date'] or datetime.min, reverse=True)
        return files

    def parse_excel_file(self, file_url: str, file_title: str) -> List[Dict[str, Any]]:
        """
        解析Excel文件

        Args:
            file_url: 文件URL
            file_title: 文件标题

        Returns:
            提取的数据列表
        """
        self.logger.info(f'解析Excel文件: {file_title}')

        try:
            import urllib.request
            import ssl
            import pandas as pd
            import io

            # 禁用SSL验证
            ssl._create_default_https_context = ssl._create_unverified_context

            # 下载文件
            response = urllib.request.urlopen(file_url, timeout=60)
            file_content = response.read()

            # 使用pandas读取Excel
            excel_file = io.BytesIO(file_content)
            xls = pd.ExcelFile(excel_file)

            all_data = []

            # 遍历所有工作表
            for sheet_name in xls.sheet_names:
                try:
                    df = pd.read_excel(xls, sheet_name=sheet_name)
                    extracted = self._extract_dataframe_data(df, file_url, sheet_name)
                    all_data.extend(extracted)
                except Exception as e:
                    self.logger.warning(f'读取工作表失败 {sheet_name}: {str(e)}')
                    continue

            return all_data

        except Exception as e:
            self.logger.error(f'Excel解析失败: {str(e)}')
            return []

    def _extract_dataframe_data(self, df, source_url: str, sheet_name: str) -> List[Dict[str, Any]]:
        """从DataFrame中提取数据"""
        data = []

        # 查找包含平台数据的行
        # 根据实际数据结构调整

        # 示例：查找包含平台名称的行
        platform_keywords = {
            '蚂蚁': ['花呗', '借呗', '网商', '蚂蚁'],
            '腾讯': ['微粒贷', '微众', '腾讯'],
            '京东': ['京东', '白条', '金条'],
            '美团': ['美团'],
            '百度': ['度小满'],
            '字节': ['抖音', '字节']
        }

        for index, row in df.iterrows():
            # 将整行转换为字符串
            row_text = ' '.join(str(v) for v in row.values)

            # 检查是否包含平台关键词
            for group, keywords in platform_keywords.items():
                for keyword in keywords:
                    if keyword in row_text:
                        # 尝试提取数据
                        extracted = self._extract_row_data(row, group, keyword, source_url, sheet_name)
                        if extracted:
                            data.append(extracted)
                        break

        return data

    def _extract_row_data(self, row, group: str, keyword: str, source_url: str, sheet_name: str) -> Optional[Dict[str, Any]]:
        """从行数据中提取信息"""
        # 这里需要根据实际数据格式调整
        # 示例：假设第一列是名称，后面是数值

        values = list(row.values)
        if len(values) < 2:
            return None

        # 查找月份（可能在某个单元格中）
        report_month = None
        for val in values:
            if isinstance(val, str):
                month_match = re.search(r'(\d{4})\s*[-年]\s*(\d{1,2})\s*月', val)
                if month_match:
                    try:
                        report_month = datetime(int(month_match.group(1)), int(month_match.group(2)), 1)
                    except ValueError:
                        pass

        # 查找数值（假设后面几列可能是贷款余额、发放规模等）
        loan_balance = None
        loan_issued = None

        for val in values[1:]:
            if isinstance(val, (int, float)):
                if loan_balance is None:
                    loan_balance = float(val)
                elif loan_issued is None:
                    loan_issued = float(val)
                    break
            elif isinstance(val, str):
                num = self.clean_number(val)
                if num is not None:
                    if loan_balance is None:
                        loan_balance = num
                    elif loan_issued is None:
                        loan_issued = num
                        break

        if loan_balance or loan_issued:
            return {
                'name': keyword,
                'company_group': group,
                'report_month': report_month,
                'loan_balance': loan_balance,
                'loan_issued': loan_issued,
                'platform_type': '联合贷',
                'loan_type': '消费类',
                'data_source': f'{self.source} ({sheet_name})',
                'source_url': source_url
            }

        return None

    def scrape(self, max_files: int = 10) -> List[Dict[str, Any]]:
        """
        执行爬取

        Args:
            max_files: 最大爬取文件数

        Returns:
            爬取的数据列表
        """
        self.logger.info(f'开始爬取{self.source}官方数据')

        files = self.get_data_files()[:max_files]
        all_data = []

        for file_info in files:
            self.logger.info(f'解析文件: {file_info["title"]}')
            data = self.parse_excel_file(file_info['url'], file_info['title'])
            all_data.extend(data)

            # 添加延迟
            import time
            time.sleep(2)

        self.logger.info(f'爬取完成，共获取 {len(all_data)} 条数据')
        return all_data

    def save_data(self, data: List[Dict[str, Any]], db_session) -> int:
        """保存数据到数据库"""
        from ..models import Platform, Bank

        saved_count = 0

        for item in data:
            # 根据数据类型决定保存到哪个表
            # 这里简单判断：如果是银行名则保存到银行表，否则保存到平台表

            # 检查是否是银行数据
            bank_keywords = ['银行', '招商银行', '兴业银行', '浦发银行', '民生银行', '平安银行']
            is_bank = any(kw in item['name'] for kw in bank_keywords)

            if is_bank:
                # 保存到银行表
                existing = db_session.query(Bank).filter_by(
                    name=item['name'],
                    report_month=item['report_month']
                ).first()

                if not existing:
                    # 转换数据格式
                    bank_data = {
                        'name': item['name'],
                        'bank_type': '股份制',  # 默认
                        'report_month': item['report_month'],
                        'total_internet_loan': item['loan_balance'],
                        'data_source': item['data_source'],
                        'source_url': item['source_url']
                    }
                    bank = Bank(**bank_data)
                    db_session.add(bank)
                    saved_count += 1
            else:
                # 保存到平台表
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
ScraperFactory.register(OfficialScraper)
