from fastapi import APIRouter
from app.api.api_v1.endpoints import energy_system, login

api_router = APIRouter()
api_router.include_router(login.router, tags=["login"])
api_router.include_router(energy_system.router, prefix="/system", tags=["system"])
