# src/infrastructure/api/routes/auth.py
from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm

"Rutas de autenticación: registro, login y perfil del usuario."""
from src.application.dtos.membership_dto import LoginDTO, TokenDTO, UserCreateDTO, UserResponseDTO
from src.infrastructure.api.dependencies import (
    get_user_repo, get_auth_service, get_current_user,
)

router = APIRouter(prefix="/auth", tags=["Autenticación"])


@router.post("/register", response_model=UserResponseDTO, status_code=201)
async def register(dto: UserCreateDTO, auth_svc=Depends(get_auth_service)):
    try:
        return await auth_svc.register(dto)
    except ValueError as e:
        raise HTTPException(400, detail=str(e))


@router.post("/login", response_model=TokenDTO)
async def login(form: OAuth2PasswordRequestForm = Depends(), auth_svc=Depends(get_auth_service)):
    try:
        return await auth_svc.login(form.username, form.password)
    except ValueError as e:
        raise HTTPException(status_code=401, detail=str(e))


@router.get("/me", response_model=UserResponseDTO)
async def me(current_user=Depends(get_current_user)):
    return UserResponseDTO(
        id=current_user.id,
        full_name=current_user.full_name,
        email=current_user.email,
        phone=current_user.phone,
        is_active=current_user.is_active,
        role_name=current_user.role_name,
    )
