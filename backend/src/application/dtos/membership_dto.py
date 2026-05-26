# src/application/dtos/membership_dto.py
from datetime import date
from typing import Optional
from uuid import UUID
from pydantic import BaseModel, EmailStr, field_validator

"DTOs para planes, usuarios, membresías y autenticación (registro/login)"""
# ── Planes ────────────────────────────────────────────────────
"DTO de respuesta para planes, incluye información detallada del plan."
class PlanResponseDTO(BaseModel):
    id: UUID
    name: str
    display_name: str
    description: str
    price_monthly: float
    features: list[str]
    is_active: bool

    class Config:
        from_attributes = True


# ── Usuarios ──────────────────────────────────────────────────
class UserCreateDTO(BaseModel):
    full_name: str
    email: EmailStr
    phone: Optional[str] = None
    password: str
    role_name: str = "user"

    @field_validator("role_name")
    @classmethod
    def validate_role(cls, v: str) -> str:
        if v not in ("admin", "user"):
            raise ValueError("Rol inválido. Use 'admin' o 'user'.")
        return v

"DTO de respuesta para usuarios, incluye información básica y rol."
class UserResponseDTO(BaseModel):
    id: UUID
    full_name: str
    email: str
    phone: Optional[str]
    is_active: bool
    role_name: Optional[str]

    class Config:
        from_attributes = True


# ── Membresías ────────────────────────────────────────────────
class MembershipCreateDTO(BaseModel):
    """Puerto de entrada para crear una membresía (patrón Command)."""
    user_id: UUID
    plan_id: UUID
    start_date: date = date.today()
    end_date: date
    auto_renew: bool = True
    notes: Optional[str] = None

    @field_validator("end_date")
    @classmethod
    def end_after_start(cls, v: date, info) -> date:
        start = info.data.get("start_date")
        if start and v <= start:
            raise ValueError("end_date debe ser posterior a start_date.")
        return v


class MembershipUpdateDTO(BaseModel):
    plan_id: Optional[UUID] = None
    status: Optional[str] = None
    end_date: Optional[date] = None
    auto_renew: Optional[bool] = None
    notes: Optional[str] = None

    @field_validator("status")
    @classmethod
    def validate_status(cls, v: Optional[str]) -> Optional[str]:
        valid = {"active", "paused", "cancelled", "expired"}
        if v and v not in valid:
            raise ValueError(f"Estado inválido. Opciones: {valid}")
        return v

"DTO de respuesta para membresías, incluye datos del usuario y plan asociado."
class MembershipResponseDTO(BaseModel):
    id: UUID
    status: str
    start_date: date
    end_date: date
    auto_renew: bool
    notes: Optional[str]
    user_id: UUID
    user_name: Optional[str] = None
    user_email: Optional[str] = None
    plan_id: UUID
    plan_name: Optional[str] = None
    plan_display_name: Optional[str] = None
    price_monthly: Optional[float] = None

    class Config:
        from_attributes = True


# ── Auth ──────────────────────────────────────────────────────
class LoginDTO(BaseModel):
    email: EmailStr
    password: str


class TokenDTO(BaseModel):
    access_token: str
    token_type: str = "bearer"
    user: UserResponseDTO
