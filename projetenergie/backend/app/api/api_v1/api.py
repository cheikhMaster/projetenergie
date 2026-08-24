from fastapi import APIRouter
from app.api.api_v1.endpoints import energy, energy_system

api_router = APIRouter()
api_router.include_router(energy.router, prefix="/energy", tags=["energy"])
api_router.include_router(energy_system.router, prefix="/system", tags=["energy-system"])
