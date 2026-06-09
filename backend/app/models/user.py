from datetime import datetime

from sqlalchemy import (
    Column, Integer, String, DateTime, SmallInteger, Table, ForeignKey
)
from sqlalchemy.orm import relationship

from app.core.database import Base

# Association table for User <-> Role many-to-many
user_roles = Table(
    "user_roles",
    Base.metadata,
    Column("user_id", Integer, ForeignKey("users.id", ondelete="CASCADE"), primary_key=True),
    Column("role_id", Integer, ForeignKey("roles.id", ondelete="CASCADE"), primary_key=True),
)


class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, autoincrement=True)
    username = Column(String(64), unique=True, nullable=False, index=True, comment="Login username")
    password_hash = Column(String(256), nullable=False, comment="Bcrypt password hash")
    nickname = Column(String(64), nullable=True, comment="Display name")
    email = Column(String(128), nullable=True, index=True, comment="Email address")
    phone = Column(String(20), nullable=True, comment="Phone number")
    avatar = Column(String(512), nullable=True, comment="Avatar URL")
    status = Column(SmallInteger, nullable=False, default=1, comment="1=active, 0=disabled")
    created_at = Column(DateTime, nullable=False, default=datetime.utcnow, comment="Created timestamp")
    updated_at = Column(
        DateTime, nullable=False, default=datetime.utcnow, onupdate=datetime.utcnow, comment="Updated timestamp"
    )

    # Relationships
    roles = relationship("Role", secondary=user_roles, back_populates="users", lazy="selectin")
