"""
研究报告爬虫
从艾瑞咨询、易观分析等研究机构抓取消费金融行业报告数据
"""
import re
from typing import List, Dict, Any, Optional
from datetime import datetime
from .base import BaseScraper, ScraperFactory


class ResearchScraper(BaseScraper):
    """研究报告爬虫"""

    # 平台关键词映射
    PLATFORM_KEYWORDS = {
        '蚂蚁': ['花呗', '借呗', '网商银行', '蚂蚁集团', '蚂蚁花呗', '蚂蚁借呗', '网商'],
        '腾讯': ['微粒贷', '微业贷', '微众银行', '腾讯'],
        '字节': ['抖音', '今日头条', '字节跳动', '字节'],
        '百度': ['度小满', '百度金融', '有口令'],
        '京东': ['京东金条', '京东白条', '京东数科', '京东科技'],
        '美团': ['美团借钱', '美团生活费', '美团']
    }

    # 产品类型映射
    PLATFORM_TYPE_MAP = {
        '联合贷': ['联合贷', '联合放贷', '合作放贷'],
        '助贷': ['助贷', '撮合', '技术输出', '导流']
    }

    # 贷款用途映射
    LOAN_TYPE_MAP = {
        '消费类': ['消费', '个人', '信用卡', '花呗', '白条', '微粒贷', '借钱'],
        '经营类': ['经营', '小微', '企业', '网商', '微业']
    }

    def __init__(self):
        """初始化研究报告爬虫"""
        super().__init__(
            name='ResearchScraper',
            base_url='https://www.iresearch.com.cn'
        )

    def search_reports(self, keyword: str = '消费金融') -> List[Dict[str, str]]:
        """
        搜索报告列表

        Args:
            keyword: 搜索关键词

        Returns:
            报告列表
        """
        # 这里需要根据实际网站的搜索接口实现
        # 示例：艾瑞咨询的报告搜索
        search_url = f'{self.base_url}/search'
        params = {'keyword': keyword, 'type': 'report'}

        response = self.request_with_retry(search_url, params=params)
        if not response:
            return []

        soup = self.parse_html(response.text)
        reports = []

        # 解析报告列表（需要根据实际HTML结构调整）
        report_items = soup.find_all('div', class_='report-item')
        for item in report_items:
            title_elem = item.find('a', class_='title')
            date_elem = item.find('span', class_='date')

            if title_elem:
                reports.append({
                    'title': self.extract_text(title_elem),
                    'url': title_elem.get('href', ''),
                    'date': self.extract_text(date_elem) if date_elem else None
                })

        self.logger.info(f'找到 {len(reports)} 份报告')
        return reports

    def parse_report_data(self, report_url: str) -> List[Dict[str, Any]]:
        """
        解析报告内容，提取贷款数据

        Args:
            report_url: 报告URL

        Returns:
            提取的数据列表
        """
        response = self.request_with_retry(report_url)
        if not response:
            return []

        soup = self.parse_html(response.text)
        data = []

        # 查找包含数据的段落或表格
        # 这里需要根据实际报告内容结构进行调整

        # 示例：查找包含平台名称和数字的段落
        paragraphs = soup.find_all('p')
        for p in paragraphs:
            text = self.extract_text(p)
            if not text:
                continue

            # 尝试提取数据
            extracted = self._extract_platform_data(text, report_url)
            if extracted:
                data.extend(extracted)

        # 示例：查找表格中的数据
        tables = soup.find_all('table')
        for table in tables:
            extracted = self._extract_table_data(table, report_url)
            if extracted:
                data.extend(extracted)

        return data

    def _extract_platform_data(self, text: str, source_url: str) -> List[Dict[str, Any]]:
        """
        从文本中提取平台数据

        Args:
            text: 文本内容
            source_url: 来源URL

        Returns:
            提取的数据列表
        """
        data = []

        # 查找平台名称
        for group, keywords in self.PLATFORM_KEYWORDS.items():
            for keyword in keywords:
                if keyword in text:
                    # 提取贷款余额（亿元）
                    balance_match = re.search(r'(?:贷款余额|余额)[：:\s]*([0-9,]+\.?[0-9]*)\s*(?:亿|亿元)', text)
                    # 提取发放规模（亿元）
                    issued_match = re.search(r'(?:发放|交易|放款)[：:\s]*([0-9,]+\.?[0-9]*)\s*(?:亿|亿元)', text)
                    # 提取月份
                    month_match = re.search(r'(20\d{2})\s*年\s*(\d{1,2})\s*月', text)

                    if balance_match or issued_match:
                        platform_data = {
                            'name': keyword,
                            'company_group': group,
                            'report_month': self._parse_month(month_match) if month_match else None,
                            'loan_balance': self.clean_number(balance_match.group(1)) if balance_match else None,
                            'loan_issued': self.clean_number(issued_match.group(1)) if issued_match else None,
                            'platform_type': self._determine_platform_type(text),
                            'loan_type': self._determine_loan_type(text, group),
                            'data_source': '研究报告',
                            'source_url': source_url
                        }
                        data.append(platform_data)
                        break

        return data

    def _extract_table_data(self, table, source_url: str) -> List[Dict[str, Any]]:
        """
        从表格中提取数据

        Args:
            table: BeautifulSoup表格元素
            source_url: 来源URL

        Returns:
            提取的数据列表
        """
        data = []
        rows = table.find_all('tr')

        if not rows:
            return data

        # 获取表头
        headers = []
        header_row = rows[0]
        for th in header_row.find_all(['th', 'td']):
            headers.append(self.extract_text(th))

        # 解析数据行
        for row in rows[1:]:
            cells = row.find_all(['td', 'th'])
            if len(cells) < 2:
                continue

            row_data = {}
            for i, cell in enumerate(cells):
                if i < len(headers):
                    row_data[headers[i]] = self.extract_text(cell)

            # 尝试识别平台名称
            platform_name = self._identify_platform(row_data)
            if not platform_name:
                continue

            # 提取数值数据
            platform_data = {
                'name': platform_name,
                'company_group': self._identify_company_group(platform_name),
                'report_month': self._extract_month_from_row(row_data),
                'loan_balance': self._extract_balance_from_row(row_data),
                'loan_issued': self._extract_issued_from_row(row_data),
                'platform_type': '联合贷',  # 默认值，可以根据表格内容判断
                'loan_type': '消费类',  # 默认值
                'data_source': '研究报告',
                'source_url': source_url
            }

            if platform_data['loan_balance'] or platform_data['loan_issued']:
                data.append(platform_data)

        return data

    def _identify_platform(self, row_data: Dict[str, str]) -> Optional[str]:
        """从行数据中识别平台名称"""
        for value in row_data.values():
            for group, keywords in self.PLATFORM_KEYWORDS.items():
                for keyword in keywords:
                    if keyword in value:
                        return keyword
        return None

    def _identify_company_group(self, platform_name: str) -> Optional[str]:
        """根据平台名称识别所属集团"""
        for group, keywords in self.PLATFORM_KEYWORDS.items():
            if platform_name in keywords:
                return group
        return None

    def _determine_platform_type(self, text: str) -> str:
        """判断产品类型"""
        for ptype, keywords in self.PLATFORM_TYPE_MAP.items():
            for kw in keywords:
                if kw in text:
                    return ptype
        return '联合贷'  # 默认

    def _determine_loan_type(self, text: str, group: str) -> str:
        """判断贷款用途"""
        for ltype, keywords in self.LOAN_TYPE_MAP.items():
            for kw in keywords:
                if kw in text:
                    return ltype
        # 根据集团判断
        if group == '蚂蚁' and '网商' in text:
            return '经营类'
        return '消费类'  # 默认

    def _parse_month(self, month_match) -> Optional[datetime]:
        """解析月份"""
        try:
            year = int(month_match.group(1))
            month = int(month_match.group(2))
            return datetime(year, month, 1)
        except (ValueError, AttributeError):
            return None

    def _extract_month_from_row(self, row_data: Dict[str, str]) -> Optional[datetime]:
        """从行数据中提取月份"""
        for key, value in row_data.items():
            if '月' in key or '时间' in key or '日期' in key:
                month_match = re.search(r'(20\d{2})\s*[-/年]\s*(\d{1,2})', value)
                if month_match:
                    return self._parse_month(month_match)
        return None

    def _extract_balance_from_row(self, row_data: Dict[str, str]) -> Optional[float]:
        """从行数据中提取贷款余额"""
        for key, value in row_data.items():
            if '余额' in key or '规模' in key:
                return self.clean_number(value)
        return None

    def _extract_issued_from_row(self, row_data: Dict[str, str]) -> Optional[float]:
        """从行数据中提取发放规模"""
        for key, value in row_data.items():
            if '发放' in key or '交易' in key or '放款' in key:
                return self.clean_number(value)
        return None

    def scrape(self, search_keyword: str = '消费金融', max_reports: int = 10) -> List[Dict[str, Any]]:
        """
        执行爬取

        Args:
            search_keyword: 搜索关键词
            max_reports: 最大爬取报告数

        Returns:
            爬取的数据列表
        """
        self.logger.info(f'开始爬取研究报告，关键词: {search_keyword}')

        # 搜索报告
        reports = self.search_reports(search_keyword)
        reports = reports[:max_reports]

        all_data = []
        for report in reports:
            self.logger.info(f'解析报告: {report["title"]}')
            data = self.parse_report_data(report['url'])
            all_data.extend(data)

            # 添加延迟，避免请求过快
            import time
            time.sleep(2)

        self.logger.info(f'爬取完成，共获取 {len(all_data)} 条数据')
        return all_data

    def save_data(self, data: List[Dict[str, Any]], db_session) -> int:
        """
        保存数据到数据库

        Args:
            data: 数据列表
            db_session: 数据库会话

        Returns:
            保存的记录数
        """
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
ScraperFactory.register(ResearchScraper)
