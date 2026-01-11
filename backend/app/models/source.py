"""
数据源配置模型
用于管理各种数据源的配置和抓取状态
"""
from sqlalchemy import Column, Integer, String, DateTime, Text
from datetime import datetime
from .platform import Base


class DataSource(Base):
    """数据源配置模型"""
    __tablename__ = 'data_sources'

    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String(100), nullable=False, comment='数据源名称')
    url = Column(String(500), comment='基础URL')
    source_type = Column(String(50), comment='数据源类型（research/corporate/official/media）')
    update_frequency = Column(String(50), comment='更新频率（daily/weekly/monthly/quarterly）')
    is_active = Column(Integer, default=1, comment='是否启用（1=启用，0=禁用）')
    priority = Column(Integer, default=1, comment='优先级（1=最高，数字越大优先级越低）')
    last_scrape_at = Column(DateTime, comment='最后抓取时间')
    scrape_status = Column(String(50), comment='抓取状态（success/failed/pending）')
    config = Column(Text, comment='配置信息（JSON格式）')
    description = Column(Text, comment='描述')
    created_at = Column(DateTime, default=datetime.now, comment='创建时间')
    updated_at = Column(DateTime, default=datetime.now, onupdate=datetime.now, comment='更新时间')

    def to_dict(self):
        """转换为字典格式"""
        return {
            'id': self.id,
            'name': self.name,
            'url': self.url,
            'source_type': self.source_type,
            'update_frequency': self.update_frequency,
            'is_active': bool(self.is_active),
            'priority': self.priority,
            'last_scrape_at': self.last_scrape_at.strftime('%Y-%m-%d %H:%M:%S') if self.last_scrape_at else None,
            'scrape_status': self.scrape_status,
            'config': self.config,
            'description': self.description,
            'created_at': self.created_at.strftime('%Y-%m-%d %H:%M:%S') if self.created_at else None,
            'updated_at': self.updated_at.strftime('%Y-%m-%d %H:%M:%S') if self.updated_at else None
        }

    def __repr__(self):
        return f'<DataSource {self.name} type={self.source_type}>'
