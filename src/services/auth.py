from datetime import datetime, timezone

from fastapi import HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from src.async_tasks.send_grid_service import send_grid_service
from src.db.auth import (
    create_otp_code_db,
    create_user_db,
    decrease_attempt_amount,
    get_last_otp_code_for_user_db,
    has_user_account_db,
    update_user_db,
    verify_email_db,
)
from src.schemas.auth import (
    CreateUserRequest,
    CreateUserResponse,
    JWTTokenResponse,
    VerifyEmailRequest,
)
from src.utils.jwt import generate_jwt_tokens
from src.utils.logger import app_logger
from src.utils.password import hash_password


async def create_user(body: CreateUserRequest, db: AsyncSession):
    user_account = await has_user_account_db(db, email=body.email)
    if not user_account or not user_account.email_verified:
        if body.password != body.password2:
            app_logger.warning(
                "Password mismatch during registration",
                extra={"tags": {"email": body.email}}
            )
            raise HTTPException(status_code=400, detail="Incorrect password")
        hashed_password = hash_password(body.password)
        if not user_account:
            user_created = await create_user_db(body.email, hashed_password, db)
        else:
            user_created = await update_user_db(body.email, hashed_password, db)
        if not user_created:
            app_logger.error("Db connection failed", extra={"tags": {"email": body.email}})
            raise HTTPException(status_code=500, detail="Db connection failed")
        otp_code = await create_otp_code_db(body.email, db)
        if not otp_code:
            app_logger.warning("Incorrect OTP", extra={"tags": {"email": body.email}})
            raise HTTPException(status_code=400, detail="Incorrect OTP")
        await send_grid_service.send_otp_code(
            email=body.email,
            code=otp_code,
            otp_type=send_grid_service.OTPType.registration,
        )
        app_logger.info("User created", extra={"tags": {"email": body.email}})
        return CreateUserResponse(email=body.email)
    app_logger.info("User already exists", extra={"tags": {"email": body.email}})
    raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="User already exists")


async def verify_email_service(body: VerifyEmailRequest, db: AsyncSession):
    registration_otp = await get_last_otp_code_for_user_db(body.email, db)
    if not registration_otp:
        app_logger.warning(
            "Verification failed: OTP not found",
            extra={"tags": {"email": body.email}}
        )
        raise HTTPException(status_code=400, detail="Code does not exist")
    if registration_otp.is_used:
        app_logger.warning(
            "Verification failed: Code already used",
            extra={"tags": {"email": body.email}}
        )
        raise HTTPException(status_code=400, detail="Code already used")
    if registration_otp.expires_at < datetime.now(timezone.utc):
        app_logger.warning(
            "Verification failed: Code expired",
            extra={"tags": {"email": body.email}}
        )
        raise HTTPException(status_code=400, detail="Code expired")
    if registration_otp.attempts_left == 0:
        app_logger.warning(
            "Verification failed: No attempts left",
            extra={"tags": {"email": body.email}}
        )
        raise HTTPException(
            status_code=400,
            detail="No attempts left. Please request a new code."
        )
    if registration_otp.otp_code != body.otp_code:
        new_attempts = registration_otp.attempts_left - 1
        await decrease_attempt_amount(registration_otp.id, new_attempts, db)
        if new_attempts <= 0:
            app_logger.info(
                f"Wrong OTP code. Attempts left: {new_attempts}",
                extra={"tags": {"email": body.email, "attempts_left": new_attempts}}
            )
            raise HTTPException(
                status_code=400,
                detail="Wrong code. No attempts left. Please request a new code."
            )
        raise HTTPException(
            status_code=400,
            detail=f"Code is wrong. You have {new_attempts} attempts left."
        )
    user_id = await verify_email_db(registration_otp.id, body.email, db)
    jwt_tokens = generate_jwt_tokens(user_id)
    app_logger.info(
        "Email verified successfully",
        extra={"tags": {"email": body.email}}
    )
    return JWTTokenResponse(
        access_token=jwt_tokens["access_token"],
        refresh_token=jwt_tokens["refresh_token"],
    )