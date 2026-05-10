from unittest.mock import AsyncMock

import pytest
from fastapi import status
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine

from src.models import OtpCode, User


@pytest.mark.asyncio
async def test_signup_success(async_client, monkeypatch):
    mock_send = AsyncMock()
    monkeypatch.setattr("src.services.auth.send_grid_service.send_otp_code", mock_send)
    payload = {
        "email": "test@example.com",
        "password": "StrongPassword1!",
        "password2": "StrongPassword1!",
    }
    response = await async_client.post("/api/v1/auth/sign_up", json=payload)
    assert response.status_code == status.HTTP_201_CREATED
    assert response.json()["email"] == "test@example.com"
    mock_send.assert_called_once()


@pytest.mark.asyncio
async def test_signup_validation_failed(async_client):
    payload = {
        "email": "test@example.com",
        "password": "StrongPassword1",
        "password2": "StrongPassword1",
    }
    response = await async_client.post("/api/v1/auth/sign_up", json=payload)
    assert response.status_code == status.HTTP_422_UNPROCESSABLE_CONTENT


@pytest.mark.asyncio
async def test_signup_failure(async_client, setup_database):
    engine = create_async_engine(setup_database)
    async_session = async_sessionmaker(engine, expire_on_commit=False, class_=AsyncSession)
    test_email = "manual1@test.com"
    async with async_session() as session:
        new_user = User(email=test_email, password_hash="hashed_password", email_verified=True)
        session.add(new_user)
        session.add(new_user)
        await session.commit()
    payload = {"email": test_email, "password": "StrongPassword1!", "password2": "StrongPassword1!"}
    response = await async_client.post("/api/v1/auth/sign_up", json=payload)
    assert response.status_code == status.HTTP_400_BAD_REQUEST


@pytest.mark.asyncio
async def test_verify_email_success(async_client, setup_database):
    engine = create_async_engine(setup_database)
    async_session = async_sessionmaker(engine, expire_on_commit=False, class_=AsyncSession)

    test_email = "manual2@test.com"
    test_code = "888777"

    async with async_session() as session:
        new_user = User(email=test_email, password_hash="hashed_password")
        session.add(new_user)
        new_otp = OtpCode(email=test_email, otp_code=test_code, is_used=False, attempts_left=3)
        session.add(new_otp)
        await session.commit()
    verify_payload = {"email": test_email, "otp_code": test_code}
    response = await async_client.post("/api/v1/auth/verify_email", json=verify_payload)
    assert response.status_code == status.HTTP_201_CREATED
    data = response.json()
    assert "access_token" in data
    assert "refresh_token" in data


@pytest.mark.asyncio
async def test_verify_email_failure(async_client):
    verify_payload = {"email": "manual3@test.com", "otp_code": "123456"}
    response = await async_client.post("/api/v1/auth/verify_email", json=verify_payload)
    assert response.status_code == status.HTTP_400_BAD_REQUEST


@pytest.mark.asyncio
async def test_verify_email_validation_failed(async_client):
    verify_payload = {"email": "manual3@test.com", "otp_code": "1234567"}
    response = await async_client.post("/api/v1/auth/verify_email", json=verify_payload)
    assert response.status_code == status.HTTP_422_UNPROCESSABLE_CONTENT
