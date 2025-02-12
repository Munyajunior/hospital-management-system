from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from backend.database.session import get_db
from backend.models.user import User, UserRole
from backend.schemas.auth import UserCreate, UserResponse
from backend.app.core.security import hash_password

router = APIRouter(prefix="/auth", tags=["Authentication"])

@router.post("/register", response_model=UserResponse)
def register_user(user_data: UserCreate, db: Session = Depends(get_db)):
    # Check if username or email already exists
    existing_user = db.query(User).filter((User.username == user_data.username) | (User.email == user_data.email)).first()
    if existing_user:
        raise HTTPException(status_code=400, detail="Username or Email already exists")
    
    # Hash password before storing
    hashed_password = hash_password(user_data.password)

    # Create user
    new_user = User(
        username=user_data.username,
        full_name=user_data.full_name,
        email=user_data.email,
        hashed_password=hashed_password,
        role=user_data.role,  # Ensure role is a valid UserRole
    )

    db.add(new_user)
    db.commit()
    db.refresh(new_user)

    return new_user  # Returns user data except password
