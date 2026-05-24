# src/infrastructure/api/dependencies.py
"""
Inyección de dependencias – patrón Factory + DIP.
FastAPI resuelve estas funciones en cada request.
"""
from datetime import datetime, timedelta
from typing import Optional
from uuid import uuid4

from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from jose import JWTError, jwt
from passlib.context import CryptContext
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine, async_sessionmaker

from src.application.dtos.membership_dto import TokenDTO, UserCreateDTO, UserResponseDTO
from src.application.use_cases.membership_use_cases import (
    CreateMembershipUseCase,
    DeleteMembershipUseCase,
    ListMembershipsUseCase,
    UpdateMembershipUseCase,
)
from src.domain.entities.membership import User
from src.infrastructure.database.repositories.membership_repository_impl import (
    MembershipRepositoryImpl,
    PlanRepositoryImpl,
    UserRepositoryImpl,
)

import os

# ── Config ────────────────────────────────────────────────────
DATABASE_URL = "postgresql+psycopg://postgres.xdraasirlplnuualyuke:Naapacmapv1!@aws-1-us-west-2.pooler.supabase.com:6543/postgres?sslmode=require"
SECRET_KEY   = os.getenv("SECRET_KEY", "change-me-in-production")
ALGORITHM    = "HS256"
TOKEN_EXPIRE = 60 * 24  # minutos

engine = create_async_engine(DATABASE_URL, echo=False, connect_args={"sslmode": "require"} if "supabase" in DATABASE_URL else {})
AsyncSession_ = async_sessionmaker(engine, expire_on_commit=False)

pwd_ctx   = CryptContext(schemes=["bcrypt"], deprecated="auto")
oauth2    = OAuth2PasswordBearer(tokenUrl="/auth/login")


# ── DB Session ────────────────────────────────────────────────
async def get_db() -> AsyncSession:
    async with AsyncSession_() as session:
        yield session


# ── Repos & UCs ───────────────────────────────────────────────
def get_membership_repo(db: AsyncSession = Depends(get_db)):
    return MembershipRepositoryImpl(db)

def get_plan_repo(db: AsyncSession = Depends(get_db)):
    return PlanRepositoryImpl(db)

def get_user_repo(db: AsyncSession = Depends(get_db)):
    return UserRepositoryImpl(db)

def get_list_memberships_uc(repo=Depends(get_membership_repo)):
    return ListMembershipsUseCase(repo)

def get_create_membership_uc(
    m_repo=Depends(get_membership_repo),
    p_repo=Depends(get_plan_repo),
    u_repo=Depends(get_user_repo),
):
    return CreateMembershipUseCase(m_repo, p_repo, u_repo)

def get_update_membership_uc(
    m_repo=Depends(get_membership_repo),
    p_repo=Depends(get_plan_repo),
):
    return UpdateMembershipUseCase(m_repo, p_repo)

def get_delete_membership_uc(repo=Depends(get_membership_repo)):
    return DeleteMembershipUseCase(repo)


# ── Auth Service (Service Layer pattern) ─────────────────────
class AuthService:
    def __init__(self, user_repo: UserRepositoryImpl):
        self._users = user_repo

    async def register(self, dto: UserCreateDTO) -> UserResponseDTO:
        existing = await self._users.get_by_email(dto.email)
        if existing:
            raise ValueError("El email ya está registrado.")
        user = User(
            id=uuid4(),
            role_id=uuid4(),  # se reemplaza en repo
            full_name=dto.full_name,
            email=dto.email,
            phone=dto.phone,
            role_name=dto.role_name,
        )
        hashed = pwd_ctx.hash(dto.password)
        saved = await self._users.create(user, hashed)
        return UserResponseDTO(
            id=saved.id,
            full_name=saved.full_name,
            email=saved.email,
            phone=saved.phone,
            is_active=saved.is_active,
            role_name=saved.role_name,
        )

    async def login(self, email: str, password: str) -> TokenDTO:
        model = await self._users.get_model_by_email(email)
        if not model or not pwd_ctx.verify(password, model.password_hash):
            raise ValueError("Credenciales inválidas.")
        token = _create_token({"sub": str(model.id), "email": model.email})
        user_entity = await self._users.get_by_id(model.id)
        return TokenDTO(
            access_token=token,
            user=UserResponseDTO(
                id=user_entity.id,
                full_name=user_entity.full_name,
                email=user_entity.email,
                phone=user_entity.phone,
                is_active=user_entity.is_active,
                role_name=user_entity.role_name,
            ),
        )


def get_auth_service(user_repo=Depends(get_user_repo)):
    return AuthService(user_repo)


# ── JWT helpers ───────────────────────────────────────────────
def _create_token(data: dict) -> str:
    expire = datetime.utcnow() + timedelta(minutes=TOKEN_EXPIRE)
    return jwt.encode({**data, "exp": expire}, SECRET_KEY, algorithm=ALGORITHM)


async def get_current_user(
    token: str = Depends(oauth2),
    user_repo=Depends(get_user_repo),
) -> User:
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        user_id = payload.get("sub")
        if not user_id:
            raise JWTError()
    except JWTError:
        raise HTTPException(status_code=401, detail="Token inválido.")
    from uuid import UUID
    user = await user_repo.get_by_id(UUID(user_id))
    if not user:
        raise HTTPException(status_code=401, detail="Usuario no encontrado.")
    return user


async def require_admin(current_user: User = Depends(get_current_user)) -> User:
    if current_user.role_name != "admin":
        raise HTTPException(status_code=403, detail="Se requiere rol de administrador.")
    return current_user
