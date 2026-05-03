from pydantic import BaseModel, EmailStr


class CreateUserRequest(BaseModel):
    email: EmailStr
    password: str
    password2: str

class CreateUserResponse(BaseModel):
    email: EmailStr


class VerifyEmailRequest(BaseModel):
    email: EmailStr
    otp_code: str


class JWTTokenResponse(BaseModel):
    access_token: str
    refresh_token: str