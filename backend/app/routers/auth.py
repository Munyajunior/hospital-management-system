from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
import os
from datetime import timedelta
from schemas.auth import (
    UserCreate, UserResponse, Token, LoginRequest,
    ChangePasswordRequest, ResetPasswordRequest, ForgotPasswordRequest
)
from models.user import User
from models.patient import Patient
from models.doctor import Doctor
from utils.security import (
    hash_password, verify_password,
    create_access_token, create_reset_token, verify_reset_token
)
from utils.email_util import send_reset_email
from core.database import get_async_db
from core.dependencies import RoleChecker, get_current_active_user
from core.cache import cache

router = APIRouter(prefix="/auth", tags=["Authentication"])

# Allow only admins to create users
admin_only = RoleChecker(["admin"])

@router.post("/register", response_model=UserResponse)
async def register_user(
    user: UserCreate,
    db: AsyncSession = Depends(get_async_db),
    _: User = Depends(admin_only)
):
    # Check if user already exists
    result = await db.execute(select(User).where(User.email == user.email))
    existing_user = result.scalars().first()
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
    await db.commit()
    await db.refresh(new_user)
    
    if user.role == "doctor":
        result = await db.execute(select(Doctor).where(Doctor.email == user.email))
        existing_doctor = result.scalars().first()
        if existing_doctor:
            raise HTTPException(status_code=400, detail="A doctor with this email already exists")
        
        new_doctor = Doctor(
            id=new_user.id,
            full_name=user.full_name,
            email=user.email
        )
        db.add(new_doctor)
        await db.commit()
    
    return new_user

@router.post("/login", response_model=Token)
@cache(expire=300)  # Cache for 5 minutes
async def login_user(
    login_cred: LoginRequest,
    db: AsyncSession = Depends(get_async_db)
):
    result = await db.execute(select(User).where(User.email == login_cred.email))
    user = result.scalars().first()
    
    if not user or not verify_password(login_cred.password, user.hashed_password):
        raise HTTPException(status_code=401, detail="Invalid credentials")
    if not user.is_active:
        raise HTTPException(status_code=403, detail="You have been Deactivated")
    
    access_token = create_access_token(
        {"sub": user.id, "role": user.role},
        expires_delta=timedelta(minutes=60)
    )
    return {
        "access_token": access_token,
        "token_type": "bearer",
        "role": user.role,
        "sub": user.id
    }

@router.post("/login/patient", response_model=Token)
@cache(expire=300)
async def login_patient(
    login_cred: LoginRequest,
    db: AsyncSession = Depends(get_async_db)
):
    result = await db.execute(
        select(Patient)
        .where(Patient.email == login_cred.email)
    )
    user = result.scalars().first()
    
    if not user or not verify_password(login_cred.password, user.hashed_password):
        raise HTTPException(status_code=401, detail="Invalid credentials")
    
    access_token = create_access_token(
        {"sub": user.id, "role": user.role},
        expires_delta=timedelta(minutes=30)
    )
    return {
        "access_token": access_token,
        "token_type": "bearer",
        "role": user.role,
        "sub": user.id
    }

@router.post("/change-password", status_code=status.HTTP_200_OK)
async def change_password(
    request: ChangePasswordRequest,
    db: AsyncSession = Depends(get_async_db),
    current_user: User = Depends(get_current_active_user)
):
    result = await db.execute(select(User).where(User.id == current_user.id))
    user = result.scalars().first()
    
    if not verify_password(request.current_password, user.hashed_password):
        raise HTTPException(status_code=404, detail="Current password is incorrect")
    
    user.hashed_password = hash_password(request.new_password)
    await db.commit()
    await db.refresh(user)
    return user

@router.post("/forgot-password")
async def forgot_password(
    request: ForgotPasswordRequest,
    db: AsyncSession = Depends(get_async_db)
):
    result = await db.execute(select(User).where(User.email == request.email))
    user = result.scalars().first()
    if not user:
        raise HTTPException(status_code=404, detail="Email not registered")

    reset_token = create_reset_token(user.id, expires_delta=timedelta(hours=1))
    reset_link = f"{os.getenv('RESET_LINK')}?token={reset_token}"
    email_sent = await send_reset_email(request.email, reset_link)
    if not email_sent:
        raise HTTPException(status_code=500, detail="Failed to send reset email")
 
    return {"message": "Reset link sent to your email"}

@router.put("/reset-password")
async def reset_password(
    request: ResetPasswordRequest,
    db: AsyncSession = Depends(get_async_db)
):
    user_id = verify_reset_token(request.token)
    if not user_id:
        raise HTTPException(status_code=400, detail="Invalid or expired token")

    result = await db.execute(select(User).where(User.id == user_id))
    user = result.scalars().first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    user.hashed_password = hash_password(request.new_password)
    await db.commit()
    return {"message": "Password reset successfully"}