from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List
from models.user import User
from models.patient import Patient
from schemas.auth import UserResponse, IsActive, UserUpdate, AllUserResponse
from core.database import get_db
from core.dependencies import RoleChecker, get_current_active_user
from utils.security import hash_password


router = APIRouter(prefix="/user", tags=["Users"])

admin_only = RoleChecker(["admin"])

@router.get("/", response_model=List[AllUserResponse])
def all_users(db: Session = Depends(get_db), _: User = Depends(admin_only)):
    """Get all users"""
    all_users = db.query(User).all()
    if not all_users:
        return []
    return all_users

@router.get("/user/{user_id}", response_model=UserResponse)
def get_user_by_id(user_id: int, db: Session = Depends(get_db), current_user: User = Depends(get_current_active_user)):
    """
    Fetch a user by their ID.
    Only the user themselves or an admin can access this endpoint.
    """
    # Check if the current user is the same as the requested user or an admin
    if current_user.id != user_id and current_user.role != "admin":
        raise HTTPException(status_code=403, detail="You are not authorized to access this user's information")

    # Fetch the user from the database
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    return user


@router.get("/patient/{patient_id}", response_model=UserResponse)
def get_user_by_id(patient_id: int, db: Session = Depends(get_db), current_user: User = Depends(get_current_active_user)):
    """
    Fetch a user by their ID.
    Only the user themselves or an admin can access this endpoint.
    """
    # Check if the current user is the same as the requested user or an admin
    if current_user.id != patient_id and current_user.role != "admin":
        raise HTTPException(status_code=403, detail="You are not authorized to access this user's information")

    # Fetch the user from the database
    user = db.query(Patient).filter(Patient.id == patient_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    return user



@router.delete("/{user_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_user(user_id: int, db: Session = Depends(get_db), _: User = Depends(admin_only)):
    """"Delete a user"""
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail=f"User {user_id} not found")
    db.delete(user)
    db.commit()
    return user
    
@router.put("/{user_id}/is_active", response_model=UserResponse)
def activate_deactivate_user(user_id: int, active:IsActive, db: Session = Depends(get_db), _: User = Depends(admin_only)):
    """Activate or Deactivate a user"""
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    user.is_active = active.is_active
    
    db.commit()
    db.refresh(user)
    
    return user


@router.put("/{user_id}/update", response_model=UserResponse)
def update_user_login(user_id: int,update: UserUpdate,db: Session = Depends(get_db), _: User = Depends(admin_only)):
    """Update a user."""
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    # Check if the new email is already in use
    existing_user = db.query(User).filter(User.email == update.email).first()
    if existing_user and existing_user.id != user_id:
        raise HTTPException(status_code=400, detail="Email already in use")
    
    password_hash = hash_password(update.password)
    user.email = update.email
    user.hashed_password = password_hash
    
    db.commit()
    db.refresh(user)

    return user
