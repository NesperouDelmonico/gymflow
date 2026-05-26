# src/infrastructure/database/repositories/membership_repository_impl.py
from typing import Optional
from uuid import UUID

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

"Implementación de repositorios – capa de infraestructura."
"Implementa los contratos definidos en domain/repositories usando SQLAlchemy."
"Cada método se encarga de mapear entre modelos de base de datos y entidades del dominio"
from src.domain.entities.membership import Membership, MembershipStatus
from src.domain.entities.plan import MembershipPlan, PlanType
from src.domain.entities.user import User

"Repositorios para gestionar membresías, planes y usuarios. Son interfaces que definen el contrato de acceso a datos."
from src.domain.repositories.membership_repository import (
    IMembershipRepository, IPlanRepository, IUserRepository,
)
from src.infrastructure.database.models import (
    MembershipModel, MembershipPlanModel, UserModel,
)


class MembershipRepositoryImpl(IMembershipRepository):
    def __init__(self, session: AsyncSession):
        self._session = session

    async def create(self, membership: Membership) -> Membership:
        model = MembershipModel(
            id=membership.id,
            user_id=membership.user_id,
            plan_id=membership.plan_id,
            status=membership.status.value,
            start_date=membership.start_date,
            end_date=membership.end_date,
            auto_renew=membership.auto_renew,
            notes=membership.notes,
            created_by=membership.created_by,
        )
        self._session.add(model)
        await self._session.commit()
        await self._session.refresh(model)
        return membership

    async def get_by_id(self, membership_id: UUID) -> Optional[Membership]:
        result = await self._session.get(MembershipModel, membership_id)
        return _model_to_entity(result) if result else None

    async def get_by_user(self, user_id: UUID) -> list[Membership]:
        stmt = select(MembershipModel).where(MembershipModel.user_id == user_id)
        result = await self._session.execute(stmt)
        return [_model_to_entity(m) for m in result.scalars().all()]

    async def list_all(self, skip: int = 0, limit: int = 100) -> list[dict]:
        stmt = (
            select(MembershipModel)
            .options(
                selectinload(MembershipModel.user),
                selectinload(MembershipModel.plan),
            )
            .offset(skip)
            .limit(limit)
            .order_by(MembershipModel.created_at.desc())
        )
        result = await self._session.execute(stmt)
        rows = result.scalars().all()
        return [_model_to_dict(m) for m in rows]

    async def update(self, membership: Membership) -> Membership:
        model = await self._session.get(MembershipModel, membership.id)
        if not model:
            raise ValueError("Membresía no encontrada.")
        model.plan_id   = membership.plan_id
        model.status    = membership.status.value
        model.end_date  = membership.end_date
        model.auto_renew = membership.auto_renew
        model.notes     = membership.notes
        await self._session.commit()
        await self._session.refresh(model)
        return membership

    async def delete(self, membership_id: UUID) -> bool:
        model = await self._session.get(MembershipModel, membership_id)
        if not model:
            return False
        await self._session.delete(model)
        await self._session.commit()
        return True


class PlanRepositoryImpl(IPlanRepository):
    def __init__(self, session: AsyncSession):
        self._session = session

    async def get_all(self) -> list[MembershipPlan]:
        stmt = select(MembershipPlanModel).where(MembershipPlanModel.is_active.is_(True))
        result = await self._session.execute(stmt)
        return [_plan_model_to_entity(p) for p in result.scalars().all()]

    async def get_by_id(self, plan_id: UUID) -> Optional[MembershipPlan]:
        result = await self._session.get(MembershipPlanModel, plan_id)
        return _plan_model_to_entity(result) if result else None


class UserRepositoryImpl(IUserRepository):
    def __init__(self, session: AsyncSession):
        self._session = session

    async def get_by_id(self, user_id: UUID) -> Optional[User]:
        stmt = (
            select(UserModel)
            .options(selectinload(UserModel.role))
            .where(UserModel.id == user_id)
        )
        result = await self._session.execute(stmt)
        model = result.scalar_one_or_none()
        return _user_model_to_entity(model) if model else None

    async def get_by_email(self, email: str) -> Optional[User]:
        stmt = (
            select(UserModel)
            .options(selectinload(UserModel.role))
            .where(UserModel.email == email)
        )
        result = await self._session.execute(stmt)
        model = result.scalar_one_or_none()
        return _user_model_to_entity(model) if model else None

    async def get_model_by_email(self, email: str) -> Optional[UserModel]:
        stmt = select(UserModel).where(UserModel.email == email)
        result = await self._session.execute(stmt)
        return result.scalar_one_or_none()

    async def create(self, user: User, password_hash: str) -> User:
        from src.infrastructure.database.models import RoleModel
        role_stmt = select(RoleModel).where(RoleModel.name == (user.role_name or "user"))
        role_result = await self._session.execute(role_stmt)
        role = role_result.scalar_one_or_none()
        if not role:
            raise ValueError("Rol no encontrado.")

        model = UserModel(
            id=user.id,
            role_id=role.id,
            full_name=user.full_name,
            email=user.email,
            phone=user.phone,
            password_hash=password_hash,
        )
        self._session.add(model)
        await self._session.commit()
        await self._session.refresh(model)
        user.role_id = role.id
        return user

    async def list_all(self, skip: int = 0, limit: int = 100) -> list[User]:
        stmt = (
            select(UserModel)
            .options(selectinload(UserModel.role))
            .offset(skip)
            .limit(limit)
        )
        result = await self._session.execute(stmt)
        return [_user_model_to_entity(u) for u in result.scalars().all()]


# ── Mappers ───────────────────────────────────────────────────
def _model_to_entity(m: MembershipModel) -> Membership:
    return Membership(
        id=m.id,
        user_id=m.user_id,
        plan_id=m.plan_id,
        status=MembershipStatus(m.status),
        start_date=m.start_date,
        end_date=m.end_date,
        auto_renew=m.auto_renew,
        notes=m.notes,
        created_by=m.created_by,
    )


def _model_to_dict(m: MembershipModel) -> dict:
    return {
        "id": str(m.id),
        "status": m.status,
        "start_date": str(m.start_date),
        "end_date": str(m.end_date),
        "auto_renew": m.auto_renew,
        "notes": m.notes,
        "user_id": str(m.user_id),
        "user_name": m.user.full_name if m.user else None,
        "user_email": m.user.email if m.user else None,
        "plan_id": str(m.plan_id),
        "plan_name": m.plan.name if m.plan else None,
        "plan_display_name": m.plan.display_name if m.plan else None,
        "price_monthly": float(m.plan.price_monthly) if m.plan else None,
    }


def _plan_model_to_entity(p: MembershipPlanModel) -> MembershipPlan:
    return MembershipPlan(
        id=p.id,
        name=PlanType(p.name),
        display_name=p.display_name,
        description=p.description or "",
        price_monthly=float(p.price_monthly),
        features=p.features or [],
        is_active=p.is_active,
    )


def _user_model_to_entity(u: UserModel) -> User:
    return User(
        id=u.id,
        role_id=u.role_id,
        full_name=u.full_name,
        email=u.email,
        phone=u.phone,
        is_active=u.is_active,
        role_name=u.role.name if u.role else None,
    )
