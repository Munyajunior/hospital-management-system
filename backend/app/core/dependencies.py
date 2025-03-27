from fastapi import Depends, HTTPException, status, Header
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from jose import JWTError, jwt
from typing import Union
from core.database import get_async_db
from models.user import User
from models.patient import Patient
from core.security import SECRET_KEY, ALGORITHM
from fastapi.security import OAuth2PasswordBearer

# OAuth2 scheme for token authentication
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="auth/login")

async def get_current_user(
    token: str = Depends(oauth2_scheme),
    db: AsyncSession = Depends(get_async_db)
) -> Union[User, Patient]:
    """
    Async function to extract the current user from the JWT token.
    Handles both regular users and patients.
    """
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        user_id: str = payload.get("sub")
        role: str = payload.get("role")
        
        if not user_id or not role:
            raise credentials_exception
            
        if role == "patient":
            result = await db.execute(
                select(Patient).where(Patient.id == user_id)
            )
            user = result.scalars().first()
        else:
            result = await db.execute(
                select(User).where(User.id == user_id)
            )
            user = result.scalars().first()
        
        if user is None:
            raise credentials_exception
            
        return user
        
    except JWTError as e:
        raise credentials_exception

async def get_current_active_user(
    current_user: Union[User, Patient] = Depends(get_current_user)
) -> Union[User, Patient]:
    """
    Async function to ensure the user is active.
    Patients are always considered active.
    """
    if isinstance(current_user, Patient):
        return current_user
    
    if not current_user.is_active:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Inactive user"
        )
    return current_user

class RoleChecker:
    """
    Async-compatible role-based access control.
    """
    def __init__(self, allowed_roles: list):
        self.allowed_roles = allowed_roles

    async def __call__(
        self, 
        user: Union[User, Patient] = Depends(get_current_active_user)
    ) -> Union[User, Patient]:
        if user.role not in self.allowed_roles:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Operation not permitted"
            )
        return user