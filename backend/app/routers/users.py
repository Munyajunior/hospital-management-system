from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from typing import List
from models.user import User
from schemas.auth import (
    UserResponse, IsActive, 
    UserUpdate, AllUserResponse
)
from core.database import get_async_db
from core.dependencies import RoleChecker, get_current_active_user
from utils.security import hash_password
from core.cache import cache

router = APIRouter(prefix="/user", tags=["Users"])

admin_only = RoleChecker(["admin"])

@router.get("/", response_model=List[AllUserResponse])
@cache(expire=120)  # Cache for 2 minutes
async def all_users(
    db: AsyncSession = Depends(get_async_db), 
    _: User = Depends(admin_only)
):
    """List all users with caching."""
    result = await db.execute(select(User))
    all_users = result.scalars().all()
    return all_users if all_users else []

@router.get("/user/{user_id}", response_model=UserResponse)
@cache(expire=120)  # Cache for 2 minutes
async def get_user_by_id(
    user_id: int, 
    db: AsyncSession = Depends(get_async_db), 
    current_user: User = Depends(get_current_active_user)
):
    """Get user by ID with caching and access control."""
    if current_user.id != user_id and current_user.role != "admin":
        raise HTTPException(
            status_code=403, 
            detail="You are not authorized to access this user's information"
        )

    result = await db.execute(
        select(User)
        .where(User.id == user_id)
    )
    user = result.scalars().first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return user

@router.delete("/{user_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_user(
    user_id: int, 
    db: AsyncSession = Depends(get_async_db), 
    _: User = Depends(admin_only)
):
    """Delete user with async operations."""
    async with db.begin():
        result = await db.execute(
            select(User)
            .where(User.id == user_id)
        )
        user = result.scalars().first()
        if not user:
            raise HTTPException(
                status_code=404, 
                detail=f"User {user_id} not found"
            )
        await db.delete(user)
        await db.commit()

@router.put("/{user_id}/is_active", response_model=UserResponse)
async def activate_deactivate_user(
    user_id: int, 
    active: IsActive, 
    db: AsyncSession = Depends(get_async_db), 
    _: User = Depends(admin_only)
):
    """Activate/deactivate user with async operations."""
    async with db.begin():
        result = await db.execute(
            select(User)
            .where(User.id == user_id)
        )
        user = result.scalars().first()
        if not user:
            raise HTTPException(status_code=404, detail="User not found")
        user.is_active = active.is_active
        
        await db.commit()
        await db.refresh(user)
        return user

@router.put("/{user_id}/update", response_model=UserResponse)
async def update_user_login(
    user_id: int,
    update: UserUpdate,
    db: AsyncSession = Depends(get_async_db), 
    _: User = Depends(admin_only)
):
    """Update user with async operations."""
    async with db.begin():
        result = await db.execute(
            select(User)
            .where(User.id == user_id)
        )
        user = result.scalars().first()
        if not user:
            raise HTTPException(status_code=404, detail="User not found")

        result = await db.execute(
            select(User)
            .where(User.email == update.email)
        )
        existing_user = result.scalars().first()
        if existing_user and existing_user.id != user_id:
            raise HTTPException(
                status_code=400, 
                detail="Email already in use"
            )
        
        password_hash = hash_password(update.password)
        user.email = update.email
        user.hashed_password = password_hash
        
        await db.commit()
        await db.refresh(user)
        return user