import sys
import os
import asyncio


sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from app.utils.email_util import send_password_email

async def main():
    success = await send_password_email("example@gmail.com", "password")
    if success:
        print("Email sent successfully!")
    else:
        print("Failed to send email. Check logs for details.")

if __name__ == "__main__":
    asyncio.run(main())