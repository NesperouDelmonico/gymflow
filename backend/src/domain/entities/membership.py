# src/domain/entities/membership.py
from dataclasses import dataclass
from datetime import date
from enum import Enum
from typing import Optional
from uuid import UUID


class MembershipStatus(str, Enum):
    ACTIVE = "active"
    PAUSED = "paused"
    CANCELLED = "cancelled"
    EXPIRED = "expired"


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
