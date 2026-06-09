from datetime import datetime

from sqlalchemy import Column, Integer, String, DateTime, SmallInteger
from sqlalchemy.orm import relationship

from app.core.database import Base


class Permission(Base):
    __tablename__ = "permissions"

    id = Column(Integer, primary_key=True, autoincrement=True)
    parent_id = Column(Integer, nullable=True, default=None, index=True, comment="Parent permission ID, NULL for root")
    name = Column(String(64), nullable=False, comment="Permission display name")
    code = Column(String(128), unique=True, nullable=False, index=True, comment="Permission code, e.g. app:cmdb, menu:user, btn:user:create")
    type = Column(String(16), nullable=False, comment="Permission type: app, menu, button")
    path = Column(String(256), nullable=True, comment="Route path for menu type")
    icon = Column(String(64), nullable=True, comment="Icon name for menu/app")
    sort_order = Column(Integer, nullable=False, default=0, comment="Sort order for display")
    status = Column(SmallInteger, nullable=False, default=1, comment="1=active, 0=disabled")
    created_at = Column(DateTime, nullable=False, default=datetime.utcnow, comment="Created timestamp")

    # Relationships
    roles = relationship("Role", secondary="role_permissions", back_populates="permissions", lazy="selectin")
