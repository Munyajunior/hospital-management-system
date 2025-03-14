from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
import os
from fastapi_mail import FastMail, MessageSchema, ConnectionConfig
from google.oauth2 import service_account
from google.auth.transport.requests import Request
from google_auth_oauthlib.flow import InstalledAppFlow
from typing import List
from datetime import timedelta
from schemas.auth import UserCreate, UserResponse, Token, LoginRequest, AllUserResponse, ChangePasswordRequest, ResetPasswordRequest
from models.user import User
from models.patient import Patient
from utils.security import hash_password, verify_password, create_access_token, create_reset_token, verify_reset_token
from core.database import get_db
from core.dependencies import RoleChecker, get_current_user

router = APIRouter(prefix="/auth", tags=["Authentication"])


# Allow only admins to create users
admin_only = RoleChecker(["admin"])
@router.post("/register", response_model=UserResponse)
def register_user(user: UserCreate, db: Session = Depends(get_db),
                  _:User = Depends(admin_only)): # Only admins can register users
    # Check if user already exists
    existing_user = db.query(User).filter(User.email == user.email).first()
    if existing_user:
        raise HTTPException(status_code=400, detail="Email already registered")

    # Create new user
    new_user = User(
        full_name=user.full_name,
        email=user.email,
        hashed_password=hash_password(user.password),
        role=user.role
    )
    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    return new_user

@router.post("/login", response_model=Token)
def login_user(login_cred: LoginRequest, db: Session = Depends(get_db)):
    """
    Logs in a user and returns a JWT token.
    """
    user = db.query(User).filter(User.email == login_cred.email).first()
    if not user or not verify_password(login_cred.password, user.hashed_password):
        raise HTTPException(status_code=401, detail="Invalid credentials")
    access_token = create_access_token({"sub": user.id, "role":user.role}, expires_delta=timedelta(minutes=30))
    return {"access_token": access_token, "token_type": "bearer", "role": user.role, "sub":user.id}

@router.post("/login/patient", response_model=Token)
def login_user(login_cred: LoginRequest, db: Session = Depends(get_db)):
    """
    Logs in a user and returns a JWT token.
    """
    user = db.query(Patient).filter(Patient.email == login_cred.email).first()
    if not user or not verify_password(login_cred.password, user.hashed_password):
        raise HTTPException(status_code=401, detail="Invalid credentials")
    access_token = create_access_token({"sub": user.id, "role":user.role}, expires_delta=timedelta(minutes=30))
    return {"access_token": access_token, "token_type": "bearer", "role": user.role, "sub":user.id}


@router.get("/users", response_model=List[AllUserResponse])
def all_users(db: Session = Depends(get_db), _: User = Depends(admin_only)):
    all_users = db.query(User).all()
    if not all_users:
        return []
    return all_users


@router.delete("/user/{user_id}", status_code=status.HTTP_204_NO_CONTENT)
def all_users(user_id: int, db: Session = Depends(get_db), _: User = Depends(admin_only)):
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    db.delete(user)
    db.commit()
    
    
    
@router.post("/change-password", status_code=status.HTTP_200_OK)
def change_password(request: ChangePasswordRequest, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    user = db.query(User).filter(User.id == current_user.id).first()
    
    # Verify current password
    if not verify_password(request.current_password, user.hashed_password):
        raise HTTPException(status_code=401, detail="Current password is incorrect")
    # Hash new password
    hashed_new_password = hash_password(request.new_password)
    user.hashed_password = hashed_new_password
    db.commit()

    return user



# # Load your OAuth 2.0 credentials
# #credentials = service_account.Credentials.from_service_account_file( f'{os.getcwd()}\client_secret.json',
#     scopes=['https://www.googleapis.com/auth/gmail.send']
# #)

# # Refresh the credentials if necessary
# credentials.refresh(Request())

# # Configure email sender
# conf = ConnectionConfig(
#     MAIL_USERNAME=os.getenv("MAIL_USERNAME"),
#     MAIL_PASSWORD=credentials.token,
#     MAIL_FROM=("MAIL_FROM"),
#     MAIL_PORT=("MAIL_PORT"),
#     MAIL_SERVER=("MAIL_SERVER"),
#     MAIL_STARTTLS=False,
#     MAIL_SSL_TLS=True,
#     USE_CREDENTIALS=True,
#     VALIDATE_CERTS=True
# )



@router.post("/forgot-password")
async def forgot_password(email: str, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.email == email).first()
    if not user:
        raise HTTPException(status_code=404, detail="Email not registered")

    reset_token = create_reset_token(user.id)

    # Send email with reset link
    url = os.getenv("RESET_LINK")
    reset_link = f"{url}{reset_token}"
    message = MessageSchema(
        subject="Password Reset Request",
        recipients=[email],
        body=f"Click the link to reset your password: {reset_link}",
        subtype="html"
    )

    fm = FastMail(conf)
    await fm.send_message(message)

    return {"message": "Reset link sent to your email"}



@router.put("/reset-password")
def reset_password(request: ResetPasswordRequest, db: Session = Depends(get_db)):
    user_id = verify_reset_token(request.token)
    if not user_id:
        raise HTTPException(status_code=400, detail="Invalid or expired token")

    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    hashed_password = hash_password(request.new_password)
    user.hashed_password = hashed_password
    
    db.commit()
    db

    return {"message": "Password reset successfully"}