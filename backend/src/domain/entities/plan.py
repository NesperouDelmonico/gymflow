# src/domain/entities/plan.py
from dataclasses import dataclass
from enum import Enum
from uuid import UUID


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
