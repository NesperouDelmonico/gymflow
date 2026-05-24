# src/domain/entities/membership.py
from dataclasses import dataclass, field
from datetime import date
from enum import Enum
from typing import Optional
from uuid import UUID


class MembershipStatus(str, Enum):
    ACTIVE = "active"
    PAUSED = "paused"
    CANCELLED = "cancelled"
    EXPIRED = "expired"


class PlanType(str, Enum):
    BASIC = "basic"
    PREMIUM = "premium"
    DELUXE = "deluxe"


@dataclass
class MembershipPlan:
    id: UUID
    name: PlanType
    display_name: str
    description: str
    price_monthly: float
    features: list[str]
    is_active: bool = True


@dataclass
class User:
    id: UUID
    role_id: UUID
    full_name: str
    email: str
    phone: Optional[str]
    is_active: bool = True
    role_name: Optional[str] = None


@dataclass
class Membership:
    id: UUID
    user_id: UUID
    plan_id: UUID
    status: MembershipStatus
    start_date: date
    end_date: date
    auto_renew: bool = True
    notes: Optional[str] = None
    created_by: Optional[UUID] = None

    # ── Reglas de negocio (lógica en el dominio) ──────────────
    def is_active(self) -> bool:
        return self.status == MembershipStatus.ACTIVE

    def is_expired(self) -> bool:
        return self.end_date < date.today()

    def cancel(self) -> None:
        if self.status == MembershipStatus.CANCELLED:
            raise ValueError("La membresía ya está cancelada.")
        self.status = MembershipStatus.CANCELLED

    def pause(self) -> None:
        if self.status != MembershipStatus.ACTIVE:
            raise ValueError("Solo se pueden pausar membresías activas.")
        self.status = MembershipStatus.PAUSED

    def resume(self) -> None:
        if self.status != MembershipStatus.PAUSED:
            raise ValueError("Solo se pueden reactivar membresías pausadas.")
        self.status = MembershipStatus.ACTIVE
