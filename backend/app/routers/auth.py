from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from datetime import timedelta
from schemas.auth import UserCreate, UserResponse, Token, LoginRequest
from models.user import User
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