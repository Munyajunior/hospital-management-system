import os
import requests

async def send_reset_email(email: str, reset_link: str) -> bool:
    """Send a password reset email using Mailgun."""
    try:
        response = requests.post(
            f"https://api.mailgun.net/v3/{os.getenv('MAILGUN_DOMAIN')}/messages",
            auth=("api", os.getenv("MAILGUN_API_KEY")),
            data={
                "from": f"Password Reset Hospital Management System <postmaster@{os.getenv('MAILGUN_DOMAIN')}>",
                "to": [email],
                "subject": "Password Reset Request",
                "text": f"Click the link to reset your password: {reset_link}",
                "html": f"<p>Click the link to reset your password: <a href='{reset_link}'>{reset_link}</a></p>"
            }
        )
        return response.status_code == 200
    except Exception as e:
        print(f"Failed to send email: {e}")
        return False



async def send_password_email(email: str, password: str) -> bool:
    """Send the generated password to the patient's email using Mailgun."""
    try:
        response = requests.post(
            f"https://api.mailgun.net/v3/{os.getenv('MAILGUN_DOMAIN')}/messages",
            auth=("api", os.getenv("MAILGUN_API_KEY")),
            data={
                "from": f"Hospital Management System <noreply@{os.getenv('MAILGUN_DOMAIN')}>",
                "to": [email],
                "subject": "Your Hospital Management System Password",
                "text": f"Your password for the Hospital Management System is: {password}",
                "html": f"""
                    <p>Dear Patient,</p>
                    <p>Your password for the Hospital Management System is: <strong>{password}</strong></p>
                    <p>Please keep this password secure and do not share it with anyone.</p>
                    <p>Best regards,<br>Hospital Management Team</p>
                """
            }
        )
        return response.status_code == 200
    except Exception as e:
        print(f"Failed to send password email: {e}")
        return False