from datetime import timedelta
from typing import Optional

from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session

from ...db.base import get_db
from ...models.user import User as UserModel, UserRole
from ...schemas.token import Token
from ...schemas.user import UserCreate, User as UserSchema
from ...core.security import create_access_token, get_password_hash, verify_password
from ...core.config import settings
from ...services import user as user_service

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
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )

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
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Inactive user",
        )
    
    # Define scopes based on user role
    if user.role == UserRole.ADMIN:
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
    
    return {
        "access_token": access_token, 
        "token_type": "bearer",
        "scopes": scopes
    }

@router.post("/refresh-token", response_model=Token)
async def refresh_token(
    current_user: UserModel = Depends(user_service.get_current_active_user)
) -> dict[str, str]:
    """
    Refresh an access token.
    """
    access_token_expires = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        subject=current_user.id,
        expires_delta=access_token_expires
    )
    
    return {"access_token": access_token, "token_type": "bearer"}
