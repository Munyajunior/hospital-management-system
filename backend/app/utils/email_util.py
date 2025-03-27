import os
import requests
from dotenv import load_dotenv

load_dotenv()

async def send_reset_email(email: str, reset_link: str) -> bool:
    """Send a password reset email using Mailgun."""
    try:
        domain = os.getenv("MAILGUN_DOMAIN")
        api_key = os.getenv("MAILGUN_API_KEY")

        if not domain or not api_key:
            #print("Mailgun domain or API key is not set in environment variables.")
            return False

        response = requests.post(
            f"https://api.mailgun.net/v3/{domain}/messages",
            auth=("api", api_key),
            data={
                "from": f"Hospital Management System <noreply@{domain}>",
                "to": [email],
                "subject": "Password Reset Request",
                "text": f"""
                    You requested a password reset for your Hospital Management System account.
                    Please click the link below to reset your password:
                    {reset_link}

                    If you did not request this, please ignore this email.
                """,
                "html": f"""
                    <div style="font-family: Arial, sans-serif; color: #333;">
                        <h2 style="color: #007BFF;">Password Reset Request</h2>
                        <p>You requested a password reset for your <strong>Hospital Management System</strong> account.</p>
                        <p>Please click the button below to reset your password:</p>
                        <p>
                            <a href="{reset_link}" 
                               style="display: inline-block; padding: 10px 20px; background-color: #007BFF; color: white; text-decoration: none; border-radius: 5px;">
                                Reset Password
                            </a>
                        </p>
                        <p>If the button above does not work, copy and paste this link into your browser:</p>
                        <p><a href="{reset_link}" style="color: #007BFF;">{reset_link}</a></p>
                        <p>If you did not request this, please ignore this email.</p>
                        <hr>
                        <p style="font-size: 12px; color: #777;">
                            This email was sent by the Hospital Management System. Please do not reply to this email.
                        </p>
                    </div>
                """
            }
        )

        #print("Mailgun API Response:", response.status_code, response.text)  # Debugging

        return response.status_code == 200
    except Exception as e:
        #print(f"Failed to send email: {e}")
        return False


async def send_password_email(email: str, password: str) -> bool:
    """Send the generated password to the patient's email using Mailgun."""
    try:
        domain = os.getenv("MAILGUN_DOMAIN")
        api_key = os.getenv("MAILGUN_API_KEY")

        if not domain or not api_key:
            #print("Mailgun domain or API key is not set in environment variables.")
            return False

        response = requests.post(
            f"https://api.mailgun.net/v3/{domain}/messages",
            auth=("api", api_key),
            data={
                "from": f"Hospital Management System <noreply@{domain}>",
                "to": [email],
                "subject": "Your Hospital Management System Password",
                "text": f"""
                    Dear Patient,

                    Your password for the Hospital Management System is: {password}

                    Please keep this password secure and do not share it with anyone.

                    Best regards,
                    Hospital Management Team
                """,
                "html": f"""
                    <div style="font-family: Arial, sans-serif; color: #333;">
                        <h2 style="color: #007BFF;">Welcome to the Hospital Management System</h2>
                        <p>Dear Patient,</p>
                        <p>Your account has been successfully created. Below are your login credentials:</p>
                        <div style="background-color: #f9f9f9; padding: 15px; border-radius: 5px; border: 1px solid #ddd;">
                            <p style="margin: 0;"><strong>Password:</strong> {password}</p>
                        </div>
                        <p style="margin-top: 20px;">
                            Please keep this password secure and do not share it with anyone.
                        </p>
                        <p>If you have any questions or need assistance, feel free to contact our support team.</p>
                        <p>Best regards,</p>
                        <p><strong>Hospital Management Team</strong></p>
                        <hr>
                        <p style="font-size: 12px; color: #777;">
                            This email was sent by the Hospital Management System. Please do not reply to this email.
                        </p>
                    </div>
                """
            }
        )

        #print("Mailgun API Response:", response.status_code, response.text)  # Debugging

        return response.status_code == 200
    except Exception as e:
        #print(f"Failed to send password email: {e}")
        return False