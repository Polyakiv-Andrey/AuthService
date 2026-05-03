from fastapi import FastAPI

from src.config.settings import settings
from src.routes import router_v1

app = FastAPI(root_path=settings.API_V1_STR)

app.include_router(router_v1)




