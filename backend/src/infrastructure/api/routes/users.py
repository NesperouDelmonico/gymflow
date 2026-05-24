# src/infrastructure/api/routes/users.py
from fastapi import APIRouter, Depends
from src.application.dtos.membership_dto import UserResponseDTO
from src.infrastructure.api.dependencies import get_user_repo, require_admin

router = APIRouter(prefix="/users", tags=["Usuarios"])


@router.get("/", response_model=list[UserResponseDTO])
async def list_users(_=Depends(require_admin), repo=Depends(get_user_repo)):
    users = await repo.list_all()
    return [
        UserResponseDTO(
            id=u.id,
            full_name=u.full_name,
            email=u.email,
            phone=u.phone,
            is_active=u.is_active,
            role_name=u.role_name,
        )
        for u in users
    ]
