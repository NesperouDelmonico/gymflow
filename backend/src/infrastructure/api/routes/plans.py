# src/infrastructure/api/routes/plans.py
from fastapi import APIRouter, Depends
from src.application.dtos.membership_dto import PlanResponseDTO
from src.infrastructure.api.dependencies import get_plan_repo

router = APIRouter(prefix="/plans", tags=["Planes"])


@router.get("/", response_model=list[PlanResponseDTO])
async def list_plans(repo=Depends(get_plan_repo)):
    plans = await repo.get_all()
    return [
        PlanResponseDTO(
            id=p.id,
            name=p.name,
            display_name=p.display_name,
            description=p.description,
            price_monthly=p.price_monthly,
            features=p.features,
            is_active=p.is_active,
        )
        for p in plans
    ]
