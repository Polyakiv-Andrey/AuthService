from fastapi import APIRouter, Depends, status
from sqlalchemy.ext.asyncio import AsyncSession

from src.db.session import get_db
from src.schemas.auth import (
    CreateUserRequest,
    CreateUserResponse,
    JWTTokenResponse,
    VerifyEmailRequest,
)
from src.services.auth import create_user, verify_email_service

auth_router = APIRouter(prefix="/auth", tags=["Auth"])


@auth_router.post(
    "/sign_up",
    status_code=status.HTTP_201_CREATED,
    response_model=CreateUserResponse,
)
async def signup(body: CreateUserRequest, db: AsyncSession = Depends(get_db)):
    user = await create_user(body, db)
    return user


@auth_router.post(
    "/verify_email",
    status_code=status.HTTP_201_CREATED,
    response_model=JWTTokenResponse
)
async def verify_email(body: VerifyEmailRequest, db: AsyncSession = Depends(get_db)):
    user = await verify_email_service(body, db)
    return user
