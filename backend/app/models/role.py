from sqlalchemy import (
    Column, Integer, String, DateTime, SmallInteger, Table, ForeignKey
)
from sqlalchemy.orm import relationship

from app.core.database import Base
from app.utils.datetime import now_cn

# Association table for Role <-> Permission many-to-many
role_permissions = Table(
    "role_permissions",
    Base.metadata,
    Column("role_id", Integer, ForeignKey("roles.id", ondelete="CASCADE"), primary_key=True),
    Column("permission_id", Integer, ForeignKey("permissions.id", ondelete="CASCADE"), primary_key=True),
)


class Role(Base):
    __tablename__ = "roles"

    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String(64), unique=True, nullable=False, comment="Role display name")
    code = Column(String(64), unique=True, nullable=False, index=True, comment="Role code for programmatic use")
    description = Column(String(256), nullable=True, comment="Role description")
    status = Column(SmallInteger, nullable=False, default=1, comment="1=active, 0=disabled")
    created_at = Column(DateTime, nullable=False, default=now_cn, comment="Created timestamp")
    updated_at = Column(
        DateTime, nullable=False, default=now_cn, onupdate=now_cn, comment="Updated timestamp"
    )

    # Relationships
    users = relationship("User", secondary="user_roles", back_populates="roles", lazy="selectin")
    permissions = relationship(
        "Permission", secondary=role_permissions, back_populates="roles", lazy="selectin"
    )
