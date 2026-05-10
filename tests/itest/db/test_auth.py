from src.db.auth import (
    create_otp_code_db,
    create_user_db,
    decrease_attempt_amount,
    get_last_otp_code_for_user_db,
    has_user_account_db,
    update_user_db,
    verify_email_db,
)
from src.models import OtpCode, User


async def test_has_user_account_db(db_session) -> None:
    test_email = "manual1@test.com"
    new_user = User(email=test_email, password_hash="hashed_password")
    db_session.add(new_user)
    result = await has_user_account_db(db_session, test_email)
    assert result.email == test_email


async def test_has_not_user_account_db(db_session) -> None:
    result = await has_user_account_db(db_session, "manual2@test.com")
    assert result is None


async def test_create_user_db(db_session) -> None:
    test_email = "manual3@test.com"
    result = await create_user_db(test_email, "password", db_session)
    assert result is True


async def test_update_user_db(db_session) -> None:
    test_email = "manual4@test.com"
    new_user = User(email=test_email, password_hash="hashed_password")
    db_session.add(new_user)
    result = await update_user_db(test_email, "password", db_session)
    assert result is True


async def test_update_user_db_without_user(db_session) -> None:
    test_email = "manual5@test.com"
    result = await update_user_db(test_email, "password", db_session)
    assert result is False


async def test_create_otp_code_db(db_session) -> None:
    test_email = "manual5@test.com"
    result = await create_otp_code_db(test_email, db_session)
    assert result is not None


async def test_get_last_otp_code_for_user_db_without_otp_code(db_session) -> None:
    test_email = "manual6@test.com"
    result = await get_last_otp_code_for_user_db(test_email, db_session)
    assert result is None


async def test_get_last_otp_code_for_user_db_with_otp_code(db_session) -> None:
    test_email = "manual6@test.com"
    test_code = "123456"
    new_otp = OtpCode(email=test_email, otp_code=test_code, is_used=False, attempts_left=3)
    db_session.add(new_otp)
    result = await get_last_otp_code_for_user_db(test_email, db_session)
    assert result.otp_code == test_code


async def test_decrease_attempt_amount(db_session) -> None:
    test_email = "manual6@test.com"
    test_code = "123456"
    new_otp = OtpCode(email=test_email, otp_code=test_code, is_used=False, attempts_left=3)
    db_session.add(new_otp)
    await db_session.flush()
    await decrease_attempt_amount(new_otp.id, 2, db_session)
    await db_session.refresh(new_otp)

    assert new_otp.attempts_left == 2


async def test_verify_email_db(db_session) -> None:
    test_email = "manual6@test.com"
    test_code = "123456"

    new_user = User(email=test_email, password_hash="hashed_password")
    db_session.add(new_user)
    new_otp = OtpCode(email=test_email, otp_code=test_code, is_used=False, attempts_left=3)
    db_session.add(new_otp)
    await db_session.flush()

    result = await verify_email_db(new_otp.id, test_email, db_session)

    await db_session.refresh(new_user)
    await db_session.refresh(new_otp)

    assert result == new_user.id
    assert new_user.email_verified
    assert new_otp.is_used
