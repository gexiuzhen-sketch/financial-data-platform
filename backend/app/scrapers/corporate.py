"""
上市公司财报爬虫
从蚂蚁集团、京东科技等上市公司财报中抓取数据
"""
import re
from typing import List, Dict, Any, Optional
from datetime import datetime
from .base import BaseScraper, ScraperFactory


class CorporateScraper(BaseScraper):
    """上市公司财报爬虫"""

    # 上市公司财报URL配置
    REPORT_SOURCES = {
        '蚂蚁集团': {
            'base_url': 'https://www.antgroup.com',
            'report_path': '/investor-relations',
            'keywords': ['花呗', '借呗', '网商银行', '信贷', '贷款']
        },
        '京东科技': {
            'base_url': 'https://www.jdcloud.com',
            'report_path': '/ir',
            'keywords': ['京东金条', '京东白条', '信贷', '贷款']
        },
        '陆金所': {
            'base_url': 'https://www.lufaxholding.com',
            'report_path': '/investor-relations',
            'keywords': ['贷款', '信贷', '消费金融']
        }
    }

    def __init__(self, company: str = '蚂蚁集团'):
        """
        初始化财报爬虫

        Args:
            company: 公司名称
        """
        if company not in self.REPORT_SOURCES:
            raise ValueError(f'不支持的公司: {company}')

        config = self.REPORT_SOURCES[company]
        super().__init__(
            name=f'CorporateScraper_{company}',
            base_url=config['base_url']
        )
        self.company = company
        self.report_path = config['report_path']
        self.keywords = config['keywords']

    def get_reports_list(self) -> List[Dict[str, str]]:
        """
        获取财报列表

        Returns:
            财报列表
        """
        url = f'{self.base_url}{self.report_path}'
        response = self.request_with_retry(url)
        if not response:
            return []

        soup = self.parse_html(response.text)
        reports = []

        # 解析财报列表（需要根据实际HTML结构调整）
        report_items = soup.find_all('a', href=re.compile(r'(?i)(report|earning|annual)'))
        for item in report_items:
            title = self.extract_text(item)
            href = item.get('href', '')
            if any(kw in title for kw in ['年报', '年度', '年报报告', '20', 'Annual', 'Year']):
                # 补全URL
                if not href.startswith('http'):
                    href = f'{self.base_url}{href}'

                # 提取年份
                year_match = re.search(r'20\d{2}', title)
                year = int(year_match.group()) if year_match else None

                reports.append({
                    'title': title,
                    'url': href,
                    'year': year
                })

        # 按年份排序，最新的在前
        reports.sort(key=lambda x: x['year'] or 0, reverse=True)
        return reports

    def parse_report(self, report_url: str, year: int) -> List[Dict[str, Any]]:
        """
        解析财报内容

        Args:
            report_url: 财报URL
            year: 年份

        Returns:
            提取的数据列表
        """
        self.logger.info(f'解析财报: {report_url}')

        response = self.request_with_retry(report_url)
        if not response:
            return []

        # 如果是PDF文件，需要特殊处理
        if report_url.endswith('.pdf'):
            return self._parse_pdf_report(report_url, year)

        # HTML财报解析
        return self._parse_html_report(response.text, report_url, year)

    def _parse_html_report(self, html: str, source_url: str, year: int) -> List[Dict[str, Any]]:
        """解析HTML财报"""
        soup = self.parse_html(html)
        data = []

        # 查找包含关键词的段落
        paragraphs = soup.find_all('p')
        for p in paragraphs:
            text = self.extract_text(p)
            if not text:
                continue

            # 检查是否包含关键词
            if not any(kw in text for kw in self.keywords):
                continue

            # 提取数据
            extracted = self._extract_financial_data(text, source_url, year)
            if extracted:
                data.extend(extracted)

        # 查找表格数据
        tables = soup.find_all('table')
        for table in tables:
            extracted = self._extract_table_data(table, source_url, year)
            if extracted:
                data.extend(extracted)

        return data

    def _parse_pdf_report(self, pdf_url: str, year: int) -> List[Dict[str, Any]]:
        """解析PDF财报（需要安装pdfplumber）"""
        try:
            import pdfplumber
            import requests
            import io

            self.logger.info(f'解析PDF财报: {pdf_url}')

            # 下载PDF
            response = requests.get(pdf_url, timeout=60)
            pdf_file = io.BytesIO(response.content)

            data = []
            with pdfplumber.open(pdf_file) as pdf:
                for page in pdf.pages:
                    text = page.extract_text()
                    if text and any(kw in text for kw in self.keywords):
                        extracted = self._extract_financial_data(text, pdf_url, year)
                        data.extend(extracted)

            return data

        except ImportError:
            self.logger.warning('未安装pdfplumber，无法解析PDF财报')
            return []
        except Exception as e:
            self.logger.error(f'PDF解析失败: {str(e)}')
            return []

    def _extract_financial_data(self, text: str, source_url: str, year: int) -> List[Dict[str, Any]]:
        """从文本中提取财务数据"""
        data = []

        # 识别平台
        from .research import ResearchScraper as Research
        platform_keywords = Research.PLATFORM_KEYWORDS

        for group, keywords in platform_keywords.items():
            for keyword in keywords:
                if keyword in text:
                    # 提取贷款余额（单位通常为亿元）
                    balance_match = re.search(
                        rf'{keyword}[：:\s]*(?:贷款余额|余额|存量)[：:\s]*([0-9,]+\.?[0-9]*)\s*(?:亿|亿元)',
                        text
                    )
                    if not balance_match:
                        balance_match = re.search(
                            r'(?:贷款余额|余额|存量)[：:\s]*([0-9,]+\.?[0-9]*)\s*(?:亿|亿元).*?' + keyword,
                            text
                        )

                    # 提取发放规模
                    issued_match = re.search(
                        rf'{keyword}[：:\s]*(?:发放|交易|放款)[：:\s]*([0-9,]+\.?[0-9]*)\s*(?:亿|亿元)',
                        text
                    )

                    if balance_match or issued_match:
                        # 确定季度（财报通常是季度数据）
                        quarter_match = re.search(r'第([1-4])季度|Q([1-4])', text)
                        if quarter_match:
                            quarter = int(quarter_match.group(1) or quarter_match.group(2))
                            month = quarter * 3
                        else:
                            month = 12  # 默认年报

                        data.append({
                            'name': keyword,
                            'company_group': group,
                            'report_month': datetime(year, month, 1),
                            'loan_balance': self.clean_number(balance_match.group(1)) if balance_match else None,
                            'loan_issued': self.clean_number(issued_match.group(1)) if issued_match else None,
                            'platform_type': '联合贷' if '联合' in text else '助贷',
                            'loan_type': '经营类' if '小微' in text or '企业' in text else '消费类',
                            'data_source': f'{self.company}财报',
                            'source_url': source_url
                        })
                        break

        return data

    def _extract_table_data(self, table, source_url: str, year: int) -> List[Dict[str, Any]]:
        """从表格中提取数据"""
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

            # 识别平台并提取数据
            from .research import ResearchScraper as Research
            platform_keywords = Research.PLATFORM_KEYWORDS

            for group, keywords in platform_keywords.items():
                for keyword in keywords:
                    if any(keyword in str(v) for v in row_data.values()):
                        data.append({
                            'name': keyword,
                            'company_group': group,
                            'report_month': datetime(year, 12, 1),  # 默认年报
                            'loan_balance': self._extract_value(row_data, ['余额', '规模']),
                            'loan_issued': self._extract_value(row_data, ['发放', '交易']),
                            'platform_type': '联合贷',
                            'loan_type': '消费类',
                            'data_source': f'{self.company}财报',
                            'source_url': source_url
                        })
                        break

        return data

    def _extract_value(self, row_data: Dict[str, str], keywords: List[str]) -> Optional[float]:
        """从行数据中提取数值"""
        for key, value in row_data.items():
            if any(kw in key for kw in keywords):
                return self.clean_number(value)
        return None

    def scrape(self, max_reports: int = 5) -> List[Dict[str, Any]]:
        """
        执行爬取

        Args:
            max_reports: 最大爬取报告数

        Returns:
            爬取的数据列表
        """
        self.logger.info(f'开始爬取{self.company}财报')

        reports = self.get_reports_list()[:max_reports]
        all_data = []

        for report in reports:
            if not report['year']:
                continue

            self.logger.info(f'解析财报: {report["title"]}')
            data = self.parse_report(report['url'], report['year'])
            all_data.extend(data)

            # 添加延迟
            import time
            time.sleep(2)

        self.logger.info(f'爬取完成，共获取 {len(all_data)} 条数据')
        return all_data

    def save_data(self, data: List[Dict[str, Any]], db_session) -> int:
        """保存数据到数据库"""
        from ..models import Platform

        saved_count = 0
        for item in data:
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
ScraperFactory.register(CorporateScraper)
