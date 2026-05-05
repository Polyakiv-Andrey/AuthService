import pytest
from pydantic import ValidationError

from src.schemas.auth import (
    CreateUserRequest,
    CreateUserResponse,
    JWTTokenResponse,
    VerifyEmailRequest,
)


def test_create_user_request():
    data = {
        "email": "test@example.com",
        "password": "At!strongpassword123",
        "password2": "At!strongpassword123",
    }
    user_request = CreateUserRequest(**data)

    assert user_request.email == data["email"]
    assert user_request.password == data["password"]
    assert user_request.password2 == data["password2"]


def test_create_user_request_password_validation():
    data_missmatch = {
        "email": "test@example.com",
        "password": "At!srongpassword123",
        "password2": "At!strongpassword321",
    }
    with pytest.raises(ValidationError, match="Passwords must match"):
        CreateUserRequest(**data_missmatch)

    data_short = {
        "email": "test@example.com",
        "password": "strong",
        "password2": "strong",
    }
    with pytest.raises(ValidationError, match="Password must be at least 11 characters long"):
        CreateUserRequest(**data_short)

    data_no_digits = {
        "email": "test@example.com",
        "password": "strongstrong",
        "password2": "strongstrong",
    }
    with pytest.raises(ValidationError, match="Password must contain at least one digit"):
        CreateUserRequest(**data_no_digits)

    data_no_uppercase_letters = {
        "email": "test@example.com",
        "password": "strongstrong1",
        "password2": "strongstrong1",
    }

    with pytest.raises(
        ValidationError, match="Password must contain at least one uppercase letter"
    ):
        CreateUserRequest(**data_no_uppercase_letters)

    data_no_signs = {
        "email": "test@example.com",
        "password": "Strongstrong1",
        "password2": "Strongstrong1",
    }
    with pytest.raises(
        ValidationError, match="Password must contain at least one special character"
    ):
        CreateUserRequest(**data_no_signs)


def test_create_user_response():
    data = {"email": "test@example.com"}
    user_response = CreateUserResponse(**data)

    assert user_response.email == data["email"]


def test_verify_email_request():
    data = {"email": "test@example.com", "otp_code": "123456"}
    verify_user_request = VerifyEmailRequest(**data)

    assert verify_user_request.email == data["email"]
    assert verify_user_request.otp_code == data["otp_code"]


def test_verify_email_request_otp_code_validation():
    data_with_wrong_length = {"email": "test@example.com", "otp_code": "1234567"}
    with pytest.raises(ValidationError, match="OTP code must be exactly 6 characters long"):
        VerifyEmailRequest(**data_with_wrong_length)

    data_with_letters = {"email": "test@example.com", "otp_code": "02D456"}
    with pytest.raises(ValidationError, match="OTP code must contain only digits"):
        VerifyEmailRequest(**data_with_letters)


def test_jwt_token_response():
    data = {
        "access_token": "test_access_token",
        "refresh_token": "test_refresh_token",
    }
    jwt_token = JWTTokenResponse(**data)

    assert jwt_token.access_token == data["access_token"]
    assert jwt_token.refresh_token == data["refresh_token"]
