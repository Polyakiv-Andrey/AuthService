import re

from pydantic import BaseModel, EmailStr, field_validator, model_validator


class CreateUserRequest(BaseModel):
    email: EmailStr
    password: str
    password2: str

    @model_validator(mode="after")
    def check_passwords_match(self) -> "CreateUserRequest":
        if self.password != self.password2:
            raise ValueError("Passwords must match")
        return self

    @field_validator("password")
    @classmethod
    def check_password_requirements(cls, password: str) -> str:
        if len(password) < 11:
            raise ValueError("Password must be at least 11 characters long")
        if not any(char.isdigit() for char in password):
            raise ValueError("Password must contain at least one digit")
        if not any(char.isupper() for char in password):
            raise ValueError("Password must contain at least one uppercase letter")
        if not re.search(r"[!@#$%^&*(),.?\":{}|<>]", password):
            raise ValueError("Password must contain at least one special character")
        return password


class CreateUserResponse(BaseModel):
    email: EmailStr


class VerifyEmailRequest(BaseModel):
    email: EmailStr
    otp_code: str

    @field_validator("otp_code")
    @classmethod
    def validate_otp_code(cls, otp_code: str) -> str:
        if len(otp_code) != 6:
            raise ValueError("OTP code must be exactly 6 characters long")
        if not otp_code.isdigit():
            raise ValueError("OTP code must contain only digits")
        return otp_code


class JWTTokenResponse(BaseModel):
    access_token: str
    refresh_token: str
