from fastapi_mail import FastMail, MessageSchema, ConnectionConfig
from google.oauth2 import service_account
from google.auth.transport.requests import Request
import os

async def send_reset_email(email: str, reset_link: str):
    """Utility function to send a password reset email."""
    try:
        # Load OAuth 2.0 credentials
        credentials = service_account.Credentials.from_service_account_file(
            os.getenv("GOOGLE_CREDENTIALS_PATH"),
            scopes=['https://www.googleapis.com/auth/gmail.send']
        )
        credentials.refresh(Request())

        # Configure email sender
        conf = ConnectionConfig(
            MAIL_USERNAME=os.getenv("MAIL_USERNAME"),
            MAIL_PASSWORD=credentials.token,
            MAIL_FROM=os.getenv("MAIL_FROM"),
            MAIL_PORT=int(os.getenv("MAIL_PORT", 587)),  # Default to port 587
            MAIL_SERVER=os.getenv("MAIL_SERVER"),
            MAIL_STARTTLS=False,
            MAIL_SSL_TLS=True,
            USE_CREDENTIALS=True,
            VALIDATE_CERTS=True
        )

        # Create email message
        message = MessageSchema(
            subject="Password Reset Request",
            recipients=[email],
            body=f"Click the link to reset your password: {reset_link}",
            subtype="html"
        )

        # Send email
        fm = FastMail(conf)
        await fm.send_message(message)
        return True
    except Exception as e:
        print(f"Failed to send email: {e}")
        return False