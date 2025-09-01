from datetime import datetime, timedelta
from typing import Optional, List, Dict, Any
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from jose import JWTError, jwt
from sqlalchemy.orm import Session
import logging

from app.core.config import settings
from app.core.security import oauth2_scheme, SECRET_KEY, ALGORITHM, get_password_hash, verify_password
from app.models.user import User as UserModel
from app.schemas.user import UserCreate, UserUpdate, UserRole
from app.db.base import SessionLocal

logger = logging.getLogger(__name__)

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")

def get_db() -> Session:
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

async def get_current_user(
    token: str = Depends(oauth2_scheme),
    db: Session = Depends(get_db)
) -> UserModel:
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        logger.debug(f"Decoding token: {token}")
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        logger.debug(f"Decoded payload: {payload}")
        
        # Check if the token has an email or user_id in the subject
        subject = payload.get("sub")
        if not subject:
            logger.error("No subject in token payload")
            raise credentials_exception
            
        # First try to get user by ID (if subject is numeric)
        user = None
        if subject.isdigit():
            user = get_user(db, user_id=int(subject))
            
        # If user not found by ID, try by email
        if not user:
            user = get_user_by_email(db, email=subject)
            
        if user is None:
            logger.error(f"User not found with subject: {subject}")
            raise credentials_exception
            
        logger.debug(f"Found user: {user.email} with role: {user.role}")
        return user
        
    except JWTError as e:
        logger.error(f"JWT Error: {str(e)}")
        raise credentials_exception

def get_current_active_user(
    current_user: UserModel = Depends(get_current_user)
) -> UserModel:
    if not current_user.is_active:
        raise HTTPException(status_code=400, detail="Inactive user")
    return current_user

def get_user(db: Session, user_id: int) -> Optional[UserModel]:
    """
    Get a user by ID.
    
    Args:
        db: Database session
        user_id: ID of the user to retrieve
        
    Returns:
        User object if found, None otherwise
    """
    return db.query(UserModel).filter(UserModel.id == user_id).first()

def get_user_by_email(db: Session, email: str) -> Optional[UserModel]:
    """
    Get a user by email.
    
    Args:
        db: Database session
        email: Email of the user to retrieve
        
    Returns:
        User object if found, None otherwise
    """
    return db.query(UserModel).filter(UserModel.email == email).first()

def get_users(db: Session, skip: int = 0, limit: int = 100) -> List[UserModel]:
    """
    Get a list of users with pagination.
    
    Args:
        db: Database session
        skip: Number of records to skip
        limit: Maximum number of records to return
        
    Returns:
        List of User objects
    """
    return db.query(UserModel).offset(skip).limit(limit).all()

def create_user(db: Session, user: UserCreate) -> UserModel:
    """
    Create a new user.
    
    Args:
        db: Database session
        user: User creation data
        role: User role (default: CUSTOMER)
        
    Returns:
        Created User object
        
    Raises:
        ValueError: If user with email already exists
    """
    # Check if user with this email already exists
    db_user = get_user_by_email(db, email=user.email)
    if db_user:
        raise ValueError("Email already registered")
        
    hashed_password = get_password_hash(user.password)
    db_user = UserModel(
        email=user.email,
        hashed_password=hashed_password,
        full_name=user.full_name,
        role=user.role,
        is_active=user.is_active if hasattr(user, 'is_active') else True
    )
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user

def update_user(
    db: Session, 
    db_user: UserModel, 
    user: UserUpdate
) -> UserModel:
    """
    Update a user.
    
    Args:
        db: Database session
        db_user: User object to update
        user: User update data
        
    Returns:
        Updated User object
    """
    user_data = user.dict(exclude_unset=True)
    
    if "password" in user_data:
        user_data["hashed_password"] = get_password_hash(user_data.pop("password"))
    
    for field, value in user_data.items():
        setattr(db_user, field, value)
    
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user

def delete_user(db: Session, db_user: UserModel) -> None:
    """
    Delete a user.
    
    Args:
        db: Database session
        db_user: User object to delete
    """
    db.delete(db_user)
    db.commit()

def authenticate_user(db: Session, email: str, password: str) -> Optional[UserModel]:
    """
    Authenticate a user by email and password.
    
    Args:
        db: Database session
        email: User's email
        password: Plain text password
        
    Returns:
        User object if authentication successful, None otherwise
    """
    user = get_user_by_email(db, email=email)
    if not user:
        return None
    if not verify_password(password, user.hashed_password):
        return None
    return user
