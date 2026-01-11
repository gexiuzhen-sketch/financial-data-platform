"""
银行数据模型
用于存储银行与平台合作的互联网贷款业务数据
"""
from sqlalchemy import Column, Integer, String, Float, Date, DateTime
from datetime import datetime
from .platform import Base


class Bank(Base):
    """银行数据模型"""
    __tablename__ = 'banks'

    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String(100), nullable=False, comment='银行名称')
    bank_type = Column(String(50), comment='银行类型（股份制/国有/城商行等）')

    # 数据字段
    report_month = Column(Date, comment='报告月份')
    total_internet_loan = Column(Float, comment='互联网贷款总规模（亿元）')
    coop_platform_count = Column(Integer, comment='合作平台数量')
    top3_platform_share = Column(Float, comment='前3大平台占比（%）')

    # 元数据
    data_source = Column(String(200), comment='数据来源')
    source_url = Column(String(500), comment='原始URL')
    created_at = Column(DateTime, default=datetime.now, comment='创建时间')
    updated_at = Column(DateTime, default=datetime.now, onupdate=datetime.now, comment='更新时间')

    def to_dict(self):
        """转换为字典格式"""
        return {
            'id': self.id,
            'name': self.name,
            'bank_type': self.bank_type,
            'report_month': self.report_month.strftime('%Y-%m') if self.report_month else None,
            'total_internet_loan': self.total_internet_loan,
            'coop_platform_count': self.coop_platform_count,
            'top3_platform_share': self.top3_platform_share,
            'data_source': self.data_source,
            'source_url': self.source_url,
            'created_at': self.created_at.strftime('%Y-%m-%d %H:%M:%S') if self.created_at else None,
            'updated_at': self.updated_at.strftime('%Y-%m-%d %H:%M:%S') if self.updated_at else None
        }

    def __repr__(self):
        return f'<Bank {self.name} {self.report_month}>'
