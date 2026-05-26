# src/application/use_cases/membership_use_cases.py
"""
Casos de uso – capa de aplicación.
Cada clase tiene una sola responsabilidad (SRP).
Dependen de abstracciones, no de implementaciones concretas (DIP).
"""
from datetime import date
from uuid import UUID, uuid4

"Casos de uso para gestionar membresías: creación, consulta, actualización y eliminación."
from src.domain.entities.membership import Membership, MembershipStatus
from src.domain.entities.plan import MembershipPlan, PlanType
from src.domain.entities.user import User

"Puertos de entrada para casos de uso relacionados con membresías."
from src.domain.repositories.membership_repository import (
    IMembershipRepository,
    IPlanRepository,
    IUserRepository,
)
"DTOs para planes, usuarios, membresías y autenticación (registro/login)"
from src.application.dtos.membership_dto import (
    MembershipCreateDTO,
    MembershipUpdateDTO,
    MembershipResponseDTO,
)

"Casos de uso para gestionar membresías: creación, consulta, actualización y eliminación."
class CreateMembershipUseCase:
    """Crea y asigna una membresía a un usuario."""

    def __init__(
        self,
        membership_repo: IMembershipRepository,
        plan_repo: IPlanRepository,
        user_repo: IUserRepository,
    ):
        self._memberships = membership_repo
        self._plans = plan_repo
        self._users = user_repo

    async def execute(
        self, dto: MembershipCreateDTO, admin_id: UUID
    ) -> MembershipResponseDTO:
        # Validar que el usuario exista
        user = await self._users.get_by_id(dto.user_id)
        if not user:
            raise ValueError(f"Usuario {dto.user_id} no encontrado.")

        # Validar que el plan exista y esté activo
        plan = await self._plans.get_by_id(dto.plan_id)
        if not plan or not plan.is_active:
            raise ValueError(f"Plan {dto.plan_id} no disponible.")

        membership = Membership(
            id=uuid4(),
            user_id=dto.user_id,
            plan_id=dto.plan_id,
            status=MembershipStatus.ACTIVE,
            start_date=dto.start_date,
            end_date=dto.end_date,
            auto_renew=dto.auto_renew,
            notes=dto.notes,
            created_by=admin_id,
        )

        saved = await self._memberships.create(membership)
        return _to_response(saved, user, plan)


class GetMembershipUseCase:
    def __init__(self, membership_repo: IMembershipRepository):
        self._repo = membership_repo

    async def execute(self, membership_id: UUID) -> dict:
        result = await self._repo.list_all()
        for m in result:
            if m["id"] == str(membership_id):
                return m
        raise ValueError(f"Membresía {membership_id} no encontrada.")


class ListMembershipsUseCase:
    def __init__(self, membership_repo: IMembershipRepository):
        self._repo = membership_repo

    async def execute(self, skip: int = 0, limit: int = 100) -> list[dict]:
        return await self._repo.list_all(skip=skip, limit=limit)


class UpdateMembershipUseCase:
    def __init__(
        self,
        membership_repo: IMembershipRepository,
        plan_repo: IPlanRepository,
    ):
        self._memberships = membership_repo
        self._plans = plan_repo

    async def execute(
        self, membership_id: UUID, dto: MembershipUpdateDTO
    ) -> Membership:
        membership = await self._memberships.get_by_id(membership_id)
        if not membership:
            raise ValueError(f"Membresía {membership_id} no encontrada.")

        if dto.plan_id:
            plan = await self._plans.get_by_id(dto.plan_id)
            if not plan or not plan.is_active:
                raise ValueError("Plan no disponible.")
            membership.plan_id = dto.plan_id

        if dto.status:
            membership.status = MembershipStatus(dto.status)

        if dto.end_date:
            membership.end_date = dto.end_date

        if dto.auto_renew is not None:
            membership.auto_renew = dto.auto_renew

        if dto.notes is not None:
            membership.notes = dto.notes

        return await self._memberships.update(membership)


class DeleteMembershipUseCase:
    def __init__(self, membership_repo: IMembershipRepository):
        self._repo = membership_repo

    async def execute(self, membership_id: UUID) -> bool:
        exists = await self._repo.get_by_id(membership_id)
        if not exists:
            raise ValueError(f"Membresía {membership_id} no encontrada.")
        return await self._repo.delete(membership_id)


# ── Helper privado ────────────────────────────────────────────
def _to_response(membership, user, plan) -> MembershipResponseDTO:
    return MembershipResponseDTO(
        id=membership.id,
        status=membership.status,
        start_date=membership.start_date,
        end_date=membership.end_date,
        auto_renew=membership.auto_renew,
        notes=membership.notes,
        user_id=user.id,
        user_name=user.full_name,
        user_email=user.email,
        plan_id=plan.id,
        plan_name=plan.name,
        plan_display_name=plan.display_name,
        price_monthly=plan.price_monthly,
    )
