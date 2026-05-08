from uuid import uuid4

import jwt

from src.config.settings import settings
from src.utils.jwt import generate_jwt_tokens


def test_generate_jwt_tokens_success():
    user_id = uuid4()
    tokens = generate_jwt_tokens(user_id)

    assert "access_token" in tokens
    assert "refresh_token" in tokens
    assert isinstance(tokens["access_token"], str)
    assert isinstance(tokens["refresh_token"], str)
    assert len(tokens) == 2


def test_jwt_payload_contents():
    user_id = uuid4()
    tokens = generate_jwt_tokens(user_id)

    access_payload = jwt.decode(
        tokens["access_token"],
        settings.auth.JWT_SECRET_KEY,
        algorithms=[settings.auth.JWT_ALGORITHM],
    )

    assert access_payload["sub"] == str(user_id)
    assert access_payload["type"] == "access"
    assert "exp" in access_payload
    assert "iat" in access_payload

    refresh_payload = jwt.decode(
        tokens["refresh_token"],
        settings.auth.JWT_SECRET_KEY,
        algorithms=[settings.auth.JWT_ALGORITHM],
    )

    assert refresh_payload["sub"] == str(user_id)
    assert refresh_payload["type"] == "refresh"
