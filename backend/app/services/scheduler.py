"""
定时任务调度器
使用APScheduler实现数据抓取的定时执行
"""
from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.triggers.cron import CronTrigger
import logging
from datetime import datetime
import sys
import os

# 添加父目录到路径
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app import db
from app.models.source import DataSource


class ScraperScheduler:
    """爬虫定时调度器"""

    def __init__(self, app=None):
        """
        初始化调度器

        Args:
            app: Flask应用实例
        """
        self.scheduler = None
        self.app = app
        self.logger = logging.getLogger('scheduler')

    def init_app(self, app):
        """
        初始化应用

        Args:
            app: Flask应用实例
        """
        self.app = app

        # 创建调度器
        self.scheduler = BackgroundScheduler(
            timezone=app.config.get('SCHEDULER_TIMEZONE', 'Asia/Shanghai')
        )

        # 添加定时任务
        self._add_jobs()

        # 添加日志
        self.logger.setLevel(logging.INFO)

    def _add_jobs(self):
        """添加所有定时任务"""

        # 1. 研究报告爬虫 - 每周一10点执行
        self.scheduler.add_job(
            func=self._run_research_scraper,
            trigger=CronTrigger(day_of_week='mon', hour=10, minute=0),
            id='research_scraper',
            name='研究报告爬虫',
            replace_existing=True
        )

        # 2. 上市公司财报爬虫 - 每季度第一个月5号10点执行
        self.scheduler.add_job(
            func=self._run_corporate_scraper,
            trigger=CronTrigger(month='1,4,7,10', day=5, hour=10, minute=0),
            id='corporate_scraper',
            name='上市公司财报爬虫',
            replace_existing=True
        )

        # 3. 官方监管数据爬虫 - 每月15日10点执行
        self.scheduler.add_job(
            func=self._run_official_scraper,
            trigger=CronTrigger(day=15, hour=10, minute=0),
            id='official_scraper',
            name='官方监管数据爬虫',
            replace_existing=True
        )

        # 4. 财经媒体爬虫 - 每天9点执行
        self.scheduler.add_job(
            func=self._run_media_scraper,
            trigger=CronTrigger(hour=9, minute=0),
            id='media_scraper',
            name='财经媒体爬虫',
            replace_existing=True
        )

        self.logger.info('定时任务已添加')

    def _run_research_scraper(self):
        """运行研究报告爬虫"""
        with self.app.app_context():
            self.logger.info('[定时任务] 开始执行研究报告爬虫')
            try:
                scraper = ResearchScraper()
                result = scraper.run(db.session)

                # 更新数据源状态
                self._update_data_source_status('研究报告爬虫', result)

                self.logger.info(f'[定时任务] 研究报告爬虫完成: {result}')
            except Exception as e:
                self.logger.error(f'[定时任务] 研究报告爬虫失败: {str(e)}')

    def _run_corporate_scraper(self):
        """运行上市公司财报爬虫"""
        with self.app.app_context():
            self.logger.info('[定时任务] 开始执行上市公司财报爬虫')
            try:
                # 爬取蚂蚁集团财报
                scraper = CorporateScraper(company='蚂蚁集团')
                result = scraper.run(db.session, max_reports=3)

                # 更新数据源状态
                self._update_data_source_status('上市公司财报爬虫', result)

                self.logger.info(f'[定时任务] 上市公司财报爬虫完成: {result}')
            except Exception as e:
                self.logger.error(f'[定时任务] 上市公司财报爬虫失败: {str(e)}')

    def _run_official_scraper(self):
        """运行官方监管数据爬虫"""
        with self.app.app_context():
            self.logger.info('[定时任务] 开始执行官方监管数据爬虫')
            try:
                scraper = OfficialScraper(source='中国人民银行')
                result = scraper.run(db.session, max_files=5)

                # 更新数据源状态
                self._update_data_source_status('官方监管数据爬虫', result)

                self.logger.info(f'[定时任务] 官方监管数据爬虫完成: {result}')
            except Exception as e:
                self.logger.error(f'[定时任务] 官方监管数据爬虫失败: {str(e)}')

    def _run_media_scraper(self):
        """运行财经媒体爬虫"""
        with self.app.app_context():
            self.logger.info('[定时任务] 开始执行财经媒体爬虫')
            try:
                scraper = MediaScraper(source='新浪财经')
                result = scraper.run(db.session, keywords=['消费金融'], days=3, max_articles=10)

                # 更新数据源状态
                self._update_data_source_status('财经媒体爬虫', result)

                self.logger.info(f'[定时任务] 财经媒体爬虫完成: {result}')
            except Exception as e:
                self.logger.error(f'[定时任务] 财经媒体爬虫失败: {str(e)}')

    def _update_data_source_status(self, source_name: str, result: dict):
        """
        更新数据源状态

        Args:
            source_name: 数据源名称
            result: 爬取结果
        """
        try:
            data_source = db.session.query(DataSource).filter_by(name=source_name).first()

            if not data_source:
                # 创建新数据源记录
                data_source = DataSource(
                    name=source_name,
                    source_type='research' if '研究报告' in source_name else 'official',
                    update_frequency='weekly',
                    is_active=1,
                    priority=1
                )
                db.session.add(data_source)

            # 更新状态
            data_source.last_scrape_at = datetime.now()
            data_source.scrape_status = result['status']

            db.session.commit()

        except Exception as e:
            self.logger.error(f'更新数据源状态失败: {str(e)}')

    def start(self):
        """启动调度器"""
        if self.scheduler and not self.scheduler.running:
            self.scheduler.start()
            self.logger.info('定时任务调度器已启动')

            # 打印已添加的任务
            jobs = self.scheduler.get_jobs()
            self.logger.info(f'已添加 {len(jobs)} 个定时任务:')
            for job in jobs:
                self.logger.info(f'  - {job.name} (ID: {job.id}, 下次运行: {job.next_run_time})')

    def stop(self):
        """停止调度器"""
        if self.scheduler and self.scheduler.running:
            self.scheduler.shutdown()
            self.logger.info('定时任务调度器已停止')

    def run_job_now(self, job_id: str):
        """
        立即运行指定任务

        Args:
            job_id: 任务ID

        Returns:
            执行结果
        """
        if not self.scheduler:
            return {'error': '调度器未初始化'}

        job = self.scheduler.get_job(job_id)
        if not job:
            return {'error': f'任务不存在: {job_id}'}

        try:
            job.func()
            return {'success': True, 'message': f'任务 {job_id} 执行完成'}
        except Exception as e:
            return {'error': str(e)}

    def get_jobs(self):
        """
        获取所有任务

        Returns:
            任务列表
        """
        if not self.scheduler:
            return []

        jobs = []
        for job in self.scheduler.get_jobs():
            jobs.append({
                'id': job.id,
                'name': job.name,
                'next_run_time': job.next_run_time.strftime('%Y-%m-%d %H:%M:%S') if job.next_run_time else None
            })

        return jobs


# 创建全局调度器实例
scheduler = ScraperScheduler()
