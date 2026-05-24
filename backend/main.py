from dotenv import load_dotenv
load_dotenv()

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from src.infrastructure.api.routes.auth import router as auth_router
from src.infrastructure.api.routes.memberships import router as memberships_router
from src.infrastructure.api.routes.plans import router as plans_router
from src.infrastructure.api.routes.users import router as users_router

app = FastAPI(
    title="GymFlow API",
    description="Sistema de gestión de membresías de gimnasio.",
    version="1.0.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(auth_router)
app.include_router(memberships_router)
app.include_router(plans_router)
app.include_router(users_router)

@app.get("/health")
async def health():
    return {"status": "ok", "service": "GymFlow API"}