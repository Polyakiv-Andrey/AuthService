from sqlalchemy import Boolean, DateTime, Integer, String

from src.models.user import OtpCode, OTPType, Role, User


def test_role():
    assert Role.ADMIN.value == "admin"
    assert Role.CUSTOMER.value == "customer"
    assert len(Role) == 2


def test_otp_type():
    assert OTPType.register.value == "register"
    assert len(OTPType) == 1


def test_user_model():
    columns = User.__table__.columns
    assert len(columns) == 8

    email = columns["email"]
    assert isinstance(email.type, String)
    assert email.type.length == 255
    assert email.unique is True
    assert email.nullable is False
    assert email.index is True

    pwd = columns["password_hash"]
    assert isinstance(pwd.type, String)
    assert pwd.type.length == 500
    assert pwd.nullable is False

    ev = columns["email_verified"]
    assert isinstance(ev.type, Boolean)
    assert ev.default.arg is False

    act = columns["active"]
    assert isinstance(act.type, Boolean)
    assert act.default.arg is True

    role_col = columns["role"]
    assert role_col.type.enum_class is Role
    assert role_col.default.arg == Role.CUSTOMER


def test_otp_code_model():
    columns = OtpCode.__table__.columns

    assert len(columns) == 9

    otp = columns["otp_code"]
    assert isinstance(otp.type, String)
    assert otp.type.length == 6
    assert otp.nullable is False

    email = columns["email"]
    assert email.type.length == 255
    assert email.index is True
    assert email.nullable is False

    is_used = columns["is_used"]
    assert isinstance(is_used.type, Boolean)
    assert is_used.default.arg is False

    expires = columns["expires_at"]
    assert isinstance(expires.type, DateTime)
    assert expires.type.timezone is True
    assert callable(expires.default.arg)

    attempts = columns["attempts_left"]
    assert isinstance(attempts.type, Integer)
    assert attempts.default.arg == 3

    otp_type = columns["otp_type"]
    assert otp_type.type.enum_class is OTPType
    assert otp_type.default.arg == OTPType.register
    assert otp_type.nullable is False


def test_otp_code_repr():
    otp = OtpCode(email="dev@polyakov.com", otp_code="654321", otp_type=OTPType.register)
    res = repr(otp)
    assert res == "OtpCode(email='dev@polyakov.com', code=65****, type=OTPType.register)"


def test_user_repr():
    user = User(email="test@example.com", role=Role.ADMIN, active=True)
    res = repr(user)
    assert res == "User(email=test@example.com, roles=Role.ADMIN)"
