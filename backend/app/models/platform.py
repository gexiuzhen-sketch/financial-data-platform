"""
平台数据模型
用于存储互联网助贷平台的贷款规模数据
"""
from sqlalchemy import Column, Integer, String, Float, Date, Text, DateTime
from sqlalchemy.ext.declarative import declarative_base
from datetime import datetime

Base = declarative_base()


class Platform(Base):
    """平台数据模型"""
    __tablename__ = 'platforms'

    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String(100), nullable=False, comment='平台名称')
    company_group = Column(String(50), comment='所属集团（蚂蚁/腾讯/字节/京东/美团/百度）')
    platform_type = Column(String(20), comment='产品类别（助贷/联合贷）')
    loan_type = Column(String(20), comment='贷款用途（消费类/经营类）')

    # 数据字段
    report_month = Column(Date, comment='报告月份')
    loan_balance = Column(Float, comment='贷款余额（亿元）')
    loan_issued = Column(Float, comment='发放规模（亿元）')
    yoy_growth = Column(Float, comment='同比增长率（%）')
    mom_growth = Column(Float, comment='环比增长率（%）')

    # 元数据
    data_source = Column(String(200), comment='数据来源')
    source_url = Column(String(500), comment='原始URL')
    created_at = Column(DateTime, default=datetime.now, comment='数据创建时间')
    updated_at = Column(DateTime, default=datetime.now, onupdate=datetime.now, comment='数据更新时间')

    def to_dict(self):
        """转换为字典格式"""
        return {
            'id': self.id,
            'name': self.name,
            'company_group': self.company_group,
            'platform_type': self.platform_type,
            'loan_type': self.loan_type,
            'report_month': self.report_month.strftime('%Y-%m') if self.report_month else None,
            'loan_balance': self.loan_balance,
            'loan_issued': self.loan_issued,
            'yoy_growth': self.yoy_growth,
            'mom_growth': self.mom_growth,
            'data_source': self.data_source,
            'source_url': self.source_url,
            'created_at': self.created_at.strftime('%Y-%m-%d %H:%M:%S') if self.created_at else None,
            'updated_at': self.updated_at.strftime('%Y-%m-%d %H:%M:%S') if self.updated_at else None
        }

    def __repr__(self):
        return f'<Platform {self.name} {self.report_month}>'
