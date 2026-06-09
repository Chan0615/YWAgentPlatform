from sqlalchemy import Column, Integer, String, DateTime, SmallInteger

from app.core.database import Base
from app.utils.datetime import now_cn


class Application(Base):
    __tablename__ = "applications"

    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String(64), nullable=False, comment="Application display name")
    code = Column(String(64), unique=True, nullable=False, index=True, comment="Application unique code")
    description = Column(String(256), nullable=True, comment="Application description")
    url = Column(String(512), nullable=False, comment="Application URL")
    icon = Column(String(64), nullable=True, comment="Icon name or URL")
    sort_order = Column(Integer, nullable=False, default=0, comment="Display sort order")
    status = Column(SmallInteger, nullable=False, default=1, comment="1=active, 0=disabled")
    created_at = Column(DateTime, nullable=False, default=now_cn, comment="Created timestamp")
    updated_at = Column(
        DateTime, nullable=False, default=now_cn, onupdate=now_cn, comment="Updated timestamp"
    )
