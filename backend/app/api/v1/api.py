"""API router."""
from fastapi import APIRouter

from app.api.v1.endpoints import login, users, birth_charts, health

api_router = APIRouter()
api_router.include_router(login.router, tags=["login"])
api_router.include_router(users.router, prefix="/users", tags=["users"])
api_router.include_router(birth_charts.router, prefix="/birth-charts", tags=["birth-charts"])
api_router.include_router(health.router, prefix="/health", tags=["health"])
