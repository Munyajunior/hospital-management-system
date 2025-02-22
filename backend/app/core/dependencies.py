# app/core/dependencies.py
from fastapi import Depends, HTTPException, status, Header
from sqlalchemy.orm import Session
from jose import JWTError, jwt
from core.database import get_db
from models.user import User
from core.security import SECRET_KEY, ALGORITHM

async def get_current_user(authorization: str = Header(...), db: Session = Depends(get_db)) -> User:
    """
    Extracts the current user from the JWT token.
    """
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    
    try:
        token = authorization.split(" ")[1]  
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        
        id: str = payload.get("sub")
        role: str = payload.get("role")
        
        if not id or not role:
            raise credentials_exception
    except (JWTError, IndexError) as e:
        print(f"Error decoding token: {str(e)}")
        raise credentials_exception
    
    user = db.query(User).filter(User.id == id).first()
    if user is None:
        raise credentials_exception
        
    return user


def get_current_active_user(current_user: User = Depends(get_current_user)):
    """
    Ensures the user is active.
    """
    if not current_user.is_active:
        raise HTTPException(status_code=400, detail="Inactive user")
    return current_user

class RoleChecker:
    """
    Role-based access control.
    """
    def __init__(self, allowed_roles: list):
        self.allowed_roles = allowed_roles

    def __call__(self, user: User = Depends(get_current_active_user)):
        if user.role not in self.allowed_roles:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Operation not permitted"
            )
        return user