# src/domain/repositories/membership_repository.py
"""
Puerto de salida (output port) – Arquitectura Hexagonal.
Define el contrato; la implementación vive en infrastructure.
"""
from abc import ABC, abstractmethod
from typing import Optional
from uuid import UUID

"Repositorios para gestionar membresías, planes y usuarios. Son interfaces que definen el contrato de acceso a datos."
from src.domain.entities.membership import Membership, MembershipStatus
from src.domain.entities.plan import MembershipPlan, PlanType
from src.domain.entities.user import User


class IMembershipRepository(ABC):
    @abstractmethod
    async def create(self, membership: Membership) -> Membership: ...

    @abstractmethod
    async def get_by_id(self, membership_id: UUID) -> Optional[Membership]: ...

    @abstractmethod
    async def get_by_user(self, user_id: UUID) -> list[Membership]: ...

    @abstractmethod
    async def list_all(self, skip: int = 0, limit: int = 100) -> list[dict]: ...

    @abstractmethod
    async def update(self, membership: Membership) -> Membership: ...

    @abstractmethod
    async def delete(self, membership_id: UUID) -> bool: ...


class IPlanRepository(ABC):
    @abstractmethod
    async def get_all(self) -> list[MembershipPlan]: ...

    @abstractmethod
    async def get_by_id(self, plan_id: UUID) -> Optional[MembershipPlan]: ...


class IUserRepository(ABC):
    @abstractmethod
    async def get_by_id(self, user_id: UUID) -> Optional[User]: ...

    @abstractmethod
    async def get_by_email(self, email: str) -> Optional[User]: ...

    @abstractmethod
    async def create(self, user: User, password_hash: str) -> User: ...

    @abstractmethod
    async def list_all(self, skip: int = 0, limit: int = 100) -> list[User]: ...
