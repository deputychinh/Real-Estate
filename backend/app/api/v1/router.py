from fastapi import APIRouter

from app.modules.auth.router import router as auth_router
from app.modules.currency.router import router as currency_router
from app.modules.favorites.router import router as favorites_router
from app.modules.health.router import router as health_router
from app.modules.inquiries.router import router as inquiries_router
from app.modules.locations.router import router as lookups_router
from app.modules.properties.router import agent_router
from app.modules.properties.router import router as properties_router
from app.modules.users.router import router as users_router

api_router = APIRouter()
for router in (
    health_router,
    auth_router,
    users_router,
    properties_router,
    agent_router,
    favorites_router,
    inquiries_router,
    lookups_router,
    currency_router,
):
    api_router.include_router(router)
