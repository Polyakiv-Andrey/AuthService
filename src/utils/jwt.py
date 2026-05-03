from datetime import datetime, timedelta, timezone
from uuid import UUID

import jwt

from src.config.settings import settings


def generate_jwt_tokens(user_id: UUID) -> dict:
    now = datetime.now(timezone.utc)
    access_payload = {
        "sub": str(user_id),
        "exp": now + timedelta(minutes=settings.auth.ACCESS_TOKEN_EXPIRE_MINUTES),
        "iat": now,
        "type": "access"
    }
    refresh_payload = {
        "sub": str(user_id),
        "exp": now + timedelta(days=settings.auth.REFRESH_TOKEN_EXPIRE_DAYS),
        "iat": now,
        "type": "refresh"
    }
    access_token = jwt.encode(
        access_payload,
        settings.auth.JWT_SECRET_KEY,
        algorithm=settings.auth.JWT_ALGORITHM
    )
    refresh_token = jwt.encode(
        refresh_payload,
        settings.auth.JWT_SECRET_KEY,
        algorithm=settings.auth.JWT_ALGORITHM
    )
    return {
        "access_token": access_token,
        "refresh_token": refresh_token
    }