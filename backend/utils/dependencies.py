from fastapi import Depends, HTTPException, Security
from fastapi.security import OAuth2PasswordBearer
from jose import JWTError
import jwt
import os
from utils.token import verify_access_token
from schemas.auth import TokenData
from models.user import UserRole
from dotenv import load_dotenv


load_dotenv()


oauth2_scheme = OAuth2PasswordBearer(tokenUrl="login")

SECRET_KEY: str = os.getenv("SECRET_KEY")

def get_current_user(token: str = Security(oauth2_scheme)) -> TokenData:
    """
    Validates the JWT token and extracts user information.
    """
    credentials_exception = HTTPException(
        status_code=401, detail="Invalid authentication credentials"
    )

    payload = verify_access_token(token)
    if payload is None:
        raise credentials_exception

    return payload

def role_required(required_roles: list[UserRole]):
    """
    Dependency to enforce role-based access control.
    """
    def role_checker(current_user: TokenData = Depends(get_current_user)):
        if current_user.role not in required_roles:
            raise HTTPException(status_code=403, detail="Access forbidden: Insufficient permissions")
        return current_user

    return role_checker
