from fastapi import APIRouter

from src.config.settings import settings
from src.routes.auth import auth_router

router_v1 = APIRouter(prefix=settings.API_V1_STR)

router_v1.include_router(auth_router)