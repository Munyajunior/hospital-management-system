from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
import os
from typing import List
from datetime import timedelta
from schemas.auth import (UserCreate, UserResponse, Token, LoginRequest, AllUserResponse, 
                          ChangePasswordRequest, ResetPasswordRequest, ForgotPasswordRequest, IsActive)
from models.user import User
from models.patient import Patient
from utils.security import hash_password, verify_password, create_access_token, create_reset_token, verify_reset_token
from utils.email_util import send_reset_email
from core.database import get_db
from core.dependencies import RoleChecker, get_current_active_user

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
    if user.is_active == False:
        raise HTTPException(status_code=403, detail="You have been Deactivated")
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
    print("Login Credentials: " + login_cred.email + " " + login_cred.password)
    if not user or not verify_password(login_cred.password, user.hashed_password):
        raise HTTPException(status_code=401, detail="Invalid credentials")
    access_token = create_access_token({"sub": user.id, "role":user.role}, expires_delta=timedelta(minutes=30))
    return {"access_token": access_token, "token_type": "bearer", "role": user.role, "sub":user.id}

    
    
@router.post("/change-password", status_code=status.HTTP_200_OK)
def change_password(request: ChangePasswordRequest, db: Session = Depends(get_db), current_user: User = Depends(get_current_active_user)):
    user = db.query(User).filter(User.id == current_user.id).first()
    
    # Verify current password
    if not verify_password(request.current_password, user.hashed_password):
        raise HTTPException(status_code=404, detail="Current password is incorrect")
    # Hash new password
    hashed_new_password = hash_password(request.new_password)
    user.hashed_password = hashed_new_password
    db.commit()
    db.refresh(user)

    return user


@router.post("/forgot-password")
async def forgot_password(request: ForgotPasswordRequest, db: Session = Depends(get_db)):
    """Handle password reset requests."""
    # Check if the email is registered
    user = db.query(User).filter(User.email == request.email).first()
    if not user:
        raise HTTPException(status_code=404, detail="Email not registered")

    # Generate a reset token with an expiration time (e.g., 1 hour)
    reset_token = create_reset_token(user.id, expires_delta=timedelta(hours=1))
    # Create the reset link
    reset_link = f"{os.getenv('RESET_LINK')}?token={reset_token}"
    # Send the reset email using Mailgun
    email_sent = await send_reset_email(request.email, reset_link)
    if not email_sent:
        raise HTTPException(status_code=500, detail="Failed to send reset email")
 
    return {"message": "Reset link sent to your email"}



@router.put("/reset-password")
def reset_password(request: ResetPasswordRequest, db: Session = Depends(get_db)):
    """Handle password reset requests."""
    # Verify the reset token
    user_id = verify_reset_token(request.token)
    if not user_id:
        raise HTTPException(status_code=400, detail="Invalid or expired token")

    # Find the user
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    # Hash the new password and update the user
    user.hashed_password = hash_password(request.new_password)
    db.commit()

    return {"message": "Password reset successfully"}


