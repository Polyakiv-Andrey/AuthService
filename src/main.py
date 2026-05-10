from fastapi import FastAPI

from src.config.settings import settings
from src.middlewares.logging import logging_middleware
from src.routes import auth_router

app = FastAPI(root_path=settings.API_V1_STR)

app.middleware("http")(logging_middleware)

app.include_router(auth_router)
