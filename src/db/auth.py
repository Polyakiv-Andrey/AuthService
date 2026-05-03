import secrets
from uuid import UUID

from pydantic import EmailStr
from sqlalchemy import select, update
from sqlalchemy.dialects.mysql import insert
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession

from src.models import OtpCode, User
from src.models.user import OTPType


async def has_user_account_db(db: AsyncSession, email: EmailStr) -> User | None:
    query = select(User).where(User.email == email)
    result = await db.execute(query)
    return result.scalar()

async def create_user_db(email: EmailStr, hashed_password: str, db: AsyncSession) -> bool:
    new_user = User(
        email=email,
        password_hash=hashed_password,
    )
    try:
        db.add(new_user)
        await db.commit()
        return True
    except IntegrityError:
        await db.rollback()
        return False

async def update_user_db(email: EmailStr, hashed_password: str, db: AsyncSession) -> bool:
    query = (
        update(User)
        .where(User.email == email)
        .values(password_hash=hashed_password)
    )
    try:
        await db.execute(query)
        await db.commit()
        return True
    except IntegrityError:
        await db.rollback()
        return False

async def create_otp_code_db(email: EmailStr, db: AsyncSession) -> str | None:

    otp_code = "".join([str(secrets.randbelow(10)) for _ in range(6)])
    stmt = insert(OtpCode).values(
        email=email,
        otp_code=otp_code,
        is_used=False
    )
    try:
        await db.execute(stmt)
        await db.commit()
        return otp_code
    except IntegrityError:
        await db.rollback()
        return None


async def get_last_otp_code_for_user_db(email: str, db: AsyncSession) -> OtpCode | None:
    stmt = (
        select(OtpCode)
        .where(
            OtpCode.email == email,
            OtpCode.otp_type == OTPType.register,
        )
        .order_by(OtpCode.created_at.desc())
        .limit(1)
    )

    result = await db.execute(stmt)
    return result.scalar_one_or_none()


async def decrease_attempt_amount(otp_id: UUID, attempts_left: int, db: AsyncSession) -> None:
    stmt = (
        update(OtpCode).where(OtpCode.id == otp_id).values(attempts_left=attempts_left)
    )
    try:
        await db.execute(stmt)
        await db.commit()
    except IntegrityError:
        await db.rollback()


async def verify_email_db(otp_id: UUID, email: EmailStr, db: AsyncSession) ->  UUID:
    user_stmt = (
        update(User).where(User.email == email).values(email_verified=True)
    )
    otp_stmt = (
        update(OtpCode).where(OtpCode.id == otp_id).values(is_used=True)
    )
    select_stmt = (
        select(User).where(User.email == email)
    )
    try:
        await db.execute(user_stmt)
        await db.execute(otp_stmt)
        await db.commit()
        result = await db.execute(select_stmt)
        return result.scalar().id
    except IntegrityError:
        await db.rollback()
        raise IntegrityError