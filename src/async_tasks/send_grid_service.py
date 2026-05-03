import asyncio
from enum import Enum
from pathlib import Path

from jinja2 import Environment, FileSystemLoader
from pydantic import EmailStr
from sendgrid import Mail, SendGridAPIClient

from src.config.settings import settings


class SendGridService:
    def __init__(self):
        self.api_key = settings.send_grid.SEND_GRID_API_KEY
        self.from_email = settings.send_grid.SEND_GRID_FROM_EMAIL
        self.client = SendGridAPIClient(self.api_key)
        template_path = Path(__file__).parent.parent.parent / "templates" / "email"
        self.template_env = Environment(loader=FileSystemLoader(template_path))

    class OTPType(str, Enum):
        registration = "registration"

    def _render_template(self, template_name: str, **context):
        template = self.template_env.get_template(template_name)
        return template.render(**context)

    async def send_otp_code(self, email: EmailStr, code: str, otp_type: OTPType):
        match otp_type:
            case otp_type.registration:
                company_name = settings.company.company_name
                template_name = "otp_registration.html"
                subject = f"Registration OTP Code from {company_name}"
                template_args = {
                    "company_name": company_name,
                    "code": code,
                }
            case _:
                raise ValueError("Unknown OTP type")
        html_content = self._render_template(
            template_name,
            **template_args
        )
        message = Mail(
            from_email=self.from_email,
            to_emails=email,
            subject=subject,
            html_content=html_content
        )
        loop = asyncio.get_event_loop()
        try:
            await loop.run_in_executor(None, self.client.send, message)
        except Exception as e:
            print(f"Error sending email to {email}: {e}")





send_grid_service = SendGridService()