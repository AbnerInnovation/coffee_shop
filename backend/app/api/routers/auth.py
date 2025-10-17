from datetime import timedelta
from typing import Optional

from fastapi import APIRouter, Depends, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session

from ...db.base import get_db
from ...models.user import User as UserModel, UserRole
from ...schemas.token import Token, TokenRefreshRequest
from ...schemas.user import UserCreate, User as UserSchema
from ...core.security import create_access_token, create_refresh_token, decode_token
from ...core.config import settings
from ...services import user as user_service
from ...core.exceptions import ValidationError, UnauthorizedError, ConflictError

router = APIRouter(
    prefix="/auth",
    tags=["auth"]
)

@router.post("/register", response_model=UserSchema, status_code=status.HTTP_201_CREATED)
async def register_user(
    user_create: UserCreate,
    db: Session = Depends(get_db)
) -> UserModel:
    """
    Register a new user.
    
    - **email**: must be a valid email address and unique
    - **password**: at least 8 characters
    - **full_name**: user's full name
    """
    try:
        # Use the user service to create the user
        db_user = user_service.create_user(
            db=db,
            user=user_create,
        )
        return db_user
    except ValueError as e:
        # Check if it's a duplicate email error
        if "already registered" in str(e).lower() or "already exists" in str(e).lower():
            raise ConflictError(str(e), resource="User")
        raise ValidationError(str(e))

@router.post("/token", response_model=Token)
async def login_for_access_token(
    form_data: OAuth2PasswordRequestForm = Depends(),
    db: Session = Depends(get_db)
) -> dict[str, str]:
    """
    OAuth2 compatible token login, get an access token for future requests.
    """
    user = user_service.authenticate_user(
        db, 
        email=form_data.username, 
        password=form_data.password
    )
    
    if not user:
        raise UnauthorizedError("Incorrect email or password")
    
    if not user.is_active:
        raise ValidationError("Account is inactive. Please contact support.")
    
    # Define scopes based on user role
    if user.role == UserRole.SYSADMIN:
        scopes = ["read:items", "write:items", "read:orders", "write:orders", "admin", "sysadmin", "manage:restaurants"]
    elif user.role == UserRole.ADMIN:
        scopes = ["read:items", "write:items", "read:orders", "write:orders", "admin"]
    elif user.role == UserRole.STAFF:
        scopes = ["read:items", "write:items", "read:orders", "write:orders"]
    else:  # CUSTOMER
        scopes = ["read:items", "read:orders"]
    
    access_token_expires = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        subject=user.id,
        expires_delta=access_token_expires,
        scopes=scopes
    )
    refresh_token = create_refresh_token(subject=user.id)
    
    return {
        "access_token": access_token,
        "token_type": "bearer",
        "scopes": scopes,
        "refresh_token": refresh_token,
    }

@router.post("/refresh-token", response_model=Token)
async def refresh_token(body: TokenRefreshRequest, db: Session = Depends(get_db)) -> dict[str, str]:
    """
    Exchange a refresh token for a new access token.
    """
    try:
        payload = decode_token(body.refresh_token)
        token_type = payload.get("type")
        sub = payload.get("sub")
        if token_type != "refresh" or not sub:
            raise UnauthorizedError("Invalid refresh token")
        # Find the user
        user = user_service.get_user(db, int(sub)) if str(sub).isdigit() else user_service.get_user_by_email(db, str(sub))
        if not user or not user.is_active:
            raise UnauthorizedError("Invalid user or inactive account")
        # Issue new tokens
        access_token_expires = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
        access_token = create_access_token(subject=user.id, expires_delta=access_token_expires)
        # Optionally rotate refresh token
        new_refresh_token = create_refresh_token(subject=user.id)
        return {"access_token": access_token, "token_type": "bearer", "refresh_token": new_refresh_token}
    except (UnauthorizedError, ValidationError):
        raise
    except Exception:
        raise UnauthorizedError("Could not refresh token")
