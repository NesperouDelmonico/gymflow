# src/infrastructure/api/routes/memberships.py
from typing import Annotated
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, status

from src.application.dtos.membership_dto import (
    MembershipCreateDTO,
    MembershipUpdateDTO,
    MembershipResponseDTO,
)
from src.application.use_cases.membership_use_cases import (
    CreateMembershipUseCase,
    DeleteMembershipUseCase,
    ListMembershipsUseCase,
    UpdateMembershipUseCase,
)
from src.infrastructure.api.dependencies import (
    get_create_membership_uc,
    get_delete_membership_uc,
    get_list_memberships_uc,
    get_update_membership_uc,
    require_admin,
    get_current_user,
)

router = APIRouter(prefix="/memberships", tags=["Membresías"])


@router.get("/", response_model=list[dict])
async def list_memberships(
    skip: int = 0,
    limit: int = 100,
    _=Depends(require_admin),
    uc: ListMembershipsUseCase = Depends(get_list_memberships_uc),
):
    """Lista todas las membresías (solo admin)."""
    return await uc.execute(skip=skip, limit=limit)


@router.post("/", response_model=MembershipResponseDTO, status_code=status.HTTP_201_CREATED)
async def create_membership(
    dto: MembershipCreateDTO,
    admin=Depends(require_admin),
    uc: CreateMembershipUseCase = Depends(get_create_membership_uc),
):
    """Crea y asigna una membresía a un usuario (solo admin)."""
    try:
        return await uc.execute(dto, admin_id=admin.id)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.put("/{membership_id}", response_model=dict)
async def update_membership(
    membership_id: UUID,
    dto: MembershipUpdateDTO,
    _=Depends(require_admin),
    uc: UpdateMembershipUseCase = Depends(get_update_membership_uc),
):
    """Actualiza plan, estado o fechas de una membresía (solo admin)."""
    try:
        result = await uc.execute(membership_id, dto)
        return {"id": str(result.id), "status": result.status, "message": "Actualizado correctamente."}
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))


@router.delete("/{membership_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_membership(
    membership_id: UUID,
    _=Depends(require_admin),
    uc: DeleteMembershipUseCase = Depends(get_delete_membership_uc),
):
    """Elimina una membresía (solo admin)."""
    try:
        await uc.execute(membership_id)
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))


@router.get("/my", response_model=list[dict])
async def my_memberships(
    current_user=Depends(get_current_user),
    uc: ListMembershipsUseCase = Depends(get_list_memberships_uc),
):
    """Membresías del usuario autenticado."""
    all_m = await uc.execute()
    return [m for m in all_m if m["user_id"] == str(current_user.id)]
