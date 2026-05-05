from datetime import datetime, timedelta
from enum import Enum

from sqlalchemy import DateTime, String
from sqlalchemy.orm import Mapped, mapped_column

from src.models import Base


class Role(str, Enum):
    ADMIN = "admin"
    CUSTOMER = "customer"


class User(Base):
    email: Mapped[str] = mapped_column(String(255), unique=True, nullable=False, index=True)
    password_hash: Mapped[str] = mapped_column(String(500), nullable=False)
    email_verified: Mapped[bool] = mapped_column(default=False)
    active: Mapped[bool] = mapped_column(default=True)
    role: Mapped[Role] = mapped_column(default=Role.CUSTOMER)

    def __repr__(self):
        return f"User(email={self.email}, roles={self.role})"


class OTPType(str, Enum):
    register = "register"


class OtpCode(Base):
    otp_code: Mapped[str] = mapped_column(String(6), nullable=False)
    email: Mapped[str] = mapped_column(String(255), nullable=False, index=True)
    is_used: Mapped[bool] = mapped_column(default=False)
    expires_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=lambda: datetime.now() + timedelta(minutes=10)
    )
    attempts_left: Mapped[int] = mapped_column(default=3)
    otp_type: Mapped[OTPType] = mapped_column(default=OTPType.register, nullable=False)

    def __repr__(self):
        masked_code = f"{self.otp_code[:2]}****" if self.otp_code else "None"
        return f"OtpCode(email={self.email!r}, code={masked_code}, type={self.otp_type})"
