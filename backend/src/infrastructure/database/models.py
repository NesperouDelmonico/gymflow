# src/infrastructure/database/models.py
from datetime import date
from uuid import uuid4

from sqlalchemy import (
    Boolean, Column, Date, ForeignKey,
    Numeric, String, Text, TIMESTAMP, func,
)
from sqlalchemy.dialects.postgresql import UUID, JSONB
from sqlalchemy.orm import DeclarativeBase, relationship


class Base(DeclarativeBase):
    pass


class RoleModel(Base):
    __tablename__ = "roles"

    id         = Column(UUID(as_uuid=True), primary_key=True, default=uuid4)
    name       = Column(String(50), nullable=False, unique=True)
    description = Column(Text)
    created_at = Column(TIMESTAMP(timezone=True), server_default=func.now())

    users = relationship("UserModel", back_populates="role")


class UserModel(Base):
    __tablename__ = "users"

    id            = Column(UUID(as_uuid=True), primary_key=True, default=uuid4)
    role_id       = Column(UUID(as_uuid=True), ForeignKey("roles.id"), nullable=False)
    full_name     = Column(String(150), nullable=False)
    email         = Column(String(255), nullable=False, unique=True)
    phone         = Column(String(20))
    password_hash = Column(Text, nullable=False)
    is_active     = Column(Boolean, nullable=False, default=True)
    created_at    = Column(TIMESTAMP(timezone=True), server_default=func.now())
    updated_at    = Column(TIMESTAMP(timezone=True), server_default=func.now(), onupdate=func.now())

    role        = relationship("RoleModel", back_populates="users")
    memberships = relationship("MembershipModel", back_populates="user", foreign_keys="MembershipModel.user_id")


class MembershipPlanModel(Base):
    __tablename__ = "membership_plans"

    id            = Column(UUID(as_uuid=True), primary_key=True, default=uuid4)
    name          = Column(String(50), nullable=False, unique=True)
    display_name  = Column(String(100), nullable=False)
    description   = Column(Text)
    price_monthly = Column(Numeric(10, 2), nullable=False)
    features      = Column(JSONB, nullable=False, default=list)
    is_active     = Column(Boolean, nullable=False, default=True)
    created_at    = Column(TIMESTAMP(timezone=True), server_default=func.now())
    updated_at    = Column(TIMESTAMP(timezone=True), server_default=func.now(), onupdate=func.now())

    memberships = relationship("MembershipModel", back_populates="plan")


class MembershipModel(Base):
    __tablename__ = "memberships"

    id         = Column(UUID(as_uuid=True), primary_key=True, default=uuid4)
    user_id    = Column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    plan_id    = Column(UUID(as_uuid=True), ForeignKey("membership_plans.id"), nullable=False)
    status     = Column(String(20), nullable=False, default="active")
    start_date = Column(Date, nullable=False, default=date.today)
    end_date   = Column(Date, nullable=False)
    auto_renew = Column(Boolean, nullable=False, default=True)
    notes      = Column(Text)
    created_by = Column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="SET NULL"))
    created_at = Column(TIMESTAMP(timezone=True), server_default=func.now())
    updated_at = Column(TIMESTAMP(timezone=True), server_default=func.now(), onupdate=func.now())

    user    = relationship("UserModel", back_populates="memberships", foreign_keys=[user_id])
    plan    = relationship("MembershipPlanModel", back_populates="memberships")
    creator = relationship("UserModel", foreign_keys=[created_by])
