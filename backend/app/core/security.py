from datetime import datetime, timedelta, timezone
from typing import Any, Union, Optional
from jose import jwt, JWTError
from passlib.context import CryptContext
from fastapi import Depends, HTTPException, status, Request
from fastapi.security import OAuth2PasswordBearer
from fastapi.security.utils import get_authorization_scheme_param

from .config import settings

# Security configurations
SECRET_KEY = settings.SECRET_KEY
ALGORITHM = settings.ALGORITHM
ACCESS_TOKEN_EXPIRE_MINUTES = settings.ACCESS_TOKEN_EXPIRE_MINUTES

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token", auto_error=False)


class OAuth2PasswordBearerWithCookie(OAuth2PasswordBearer):
    """
    OAuth2 scheme that supports both Authorization header and HTTPOnly cookies.
    Tries cookies first (more secure), then falls back to Authorization header.
    """
    
    async def __call__(self, request: Request) -> Optional[str]:
        import logging
        logger = logging.getLogger(__name__)
        
        # Try to get token from cookie first (HTTPOnly - more secure)
        token = request.cookies.get("access_token")
        
        if token:
            logger.info(f"✅ Token found in cookie: {token[:20]}...")
            return token
        
        # Fall back to Authorization header for backward compatibility
        authorization = request.headers.get("Authorization")
        scheme, param = get_authorization_scheme_param(authorization)
        
        if authorization and scheme.lower() == "bearer":
            logger.info(f"✅ Token found in Authorization header: {param[:20]}...")
            return param
        
        logger.warning(f"⚠️ No token found - Cookies: {list(request.cookies.keys())}, Auth header: {authorization}")
        
        # If auto_error is True, raise exception
        if self.auto_error:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Not authenticated",
                headers={"WWW-Authenticate": "Bearer"},
            )
        
        return None


# Use the cookie-aware scheme
oauth2_scheme_cookie = OAuth2PasswordBearerWithCookie(tokenUrl="token", auto_error=False)

# Password hashing context
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def verify_password(plain_password: str, hashed_password: str) -> bool:
    """
    Verify a password against a hash.
    
    Args:
        plain_password: Plain text password
        hashed_password: Hashed password
        
    Returns:
        bool: True if password matches, False otherwise
    """
    return pwd_context.verify(plain_password, hashed_password)

def get_password_hash(password: str) -> str:
    """
    Generate a password hash.
    
    Args:
        password: Plain text password
        
    Returns:
        str: Hashed password
    """
    return pwd_context.hash(password)

def create_access_token(
    subject: Union[str, Any], 
    expires_delta: timedelta = None,
    scopes: list[str] = None
) -> str:
    """
    Create a JWT access token with optional scopes.
    
    Args:
        subject: Subject to be stored in the token (usually user ID)
        expires_delta: Token expiration time delta
        scopes: List of scopes to include in the token
        
    Returns:
        str: Encoded JWT token
    """
    if expires_delta:
        expire = datetime.now(timezone.utc) + expires_delta
    else:
        expire = datetime.now(timezone.utc) + timedelta(
            minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES
        )
    
    to_encode = {
        "exp": expire,
        "sub": str(subject),
        "scopes": scopes or [],
        "type": "access",
    }
    
    encoded_jwt = jwt.encode(
        to_encode, 
        settings.SECRET_KEY, 
        algorithm=settings.ALGORITHM
    )
    return encoded_jwt

def decode_token(token: str) -> dict:
    """
    Decode a JWT token.
    
    Args:
        token: JWT token to decode
        
    Returns:
        dict: Decoded token payload
        
    Raises:
        JWTError: If token is invalid or expired
    """
    try:
        payload = jwt.decode(
            token,
            settings.SECRET_KEY,
            algorithms=[settings.ALGORITHM]
        )
        return payload
    except JWTError as e:
        raise e

def create_refresh_token(
    subject: Union[str, Any], 
    expires_delta: Optional[timedelta] = None
) -> str:
    """
    Create a long-lived refresh JWT used to obtain new access tokens.
    """
    # Default to 7 days if not specified
    expire = datetime.now(timezone.utc) + (expires_delta or timedelta(days=7))
    to_encode = {
        "exp": expire,
        "sub": str(subject),
        "type": "refresh",
    }
    encoded_jwt = jwt.encode(
        to_encode,
        settings.SECRET_KEY,
        algorithm=settings.ALGORITHM,
    )
    return encoded_jwt
