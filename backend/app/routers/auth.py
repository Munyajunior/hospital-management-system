from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List
from datetime import timedelta
from schemas.auth import UserCreate, UserResponse, Token, LoginRequest, AllUserResponse
from models.user import User
from models.patient import Patient
from utils.security import hash_password, verify_password, create_access_token
from core.database import get_db
from core.dependencies import RoleChecker

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