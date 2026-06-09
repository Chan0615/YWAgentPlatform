from datetime import datetime

from sqlalchemy import Column, Integer, String, DateTime, Text

from app.core.database import Base


class AuditLog(Base):
    __tablename__ = "audit_logs"

    id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(Integer, nullable=True, index=True, comment="Operator user ID")
    username = Column(String(64), nullable=True, comment="Operator username")
    action = Column(String(64), nullable=False, index=True, comment="Action performed, e.g. login, create, update, delete")
    resource_type = Column(String(64), nullable=True, comment="Resource type, e.g. user, role, permission")
    resource_id = Column(String(64), nullable=True, comment="Resource ID")
    detail = Column(Text, nullable=True, comment="Action detail/description in JSON")
    ip_address = Column(String(64), nullable=True, comment="Client IP address")
    user_agent = Column(String(512), nullable=True, comment="Client User-Agent")
    status = Column(String(16), nullable=False, default="success", comment="Result: success or fail")
    created_at = Column(DateTime, nullable=False, default=datetime.utcnow, index=True, comment="Log timestamp")
