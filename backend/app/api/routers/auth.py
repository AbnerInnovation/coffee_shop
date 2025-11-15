from datetime import timedelta
from typing import Optional

from fastapi import APIRouter, Depends, status, Request, Response
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session

from ...db.base import get_db
from ...models.user import User as UserModel, UserRole
from ...models.restaurant import Restaurant
from ...schemas.token import Token, TokenRefreshRequest
from ...schemas.user import UserCreate, User as UserSchema, ChangePasswordRequest
from ...core.security import create_access_token, create_refresh_token, decode_token, verify_password, get_password_hash
from ...core.config import settings
from ...services import user as user_service
from ...services.user import get_current_active_user
from ...core.exceptions import ValidationError, UnauthorizedError, ConflictError
from ...core.error_handlers import handle_duplicate_error
from ...middleware.restaurant import get_restaurant_from_request

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
        handle_duplicate_error(e, "User")

@router.post("/token", response_model=Token)
async def login_for_access_token(
    request: Request,
    response: Response,
    form_data: OAuth2PasswordRequestForm = Depends(),
    db: Session = Depends(get_db)
) -> dict[str, str]:
    """
    OAuth2 compatible token login, get an access token for future requests.
    Validates that the user belongs to the restaurant subdomain.
    Sets HTTPOnly cookies for enhanced security.
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
    
    # Validate subdomain access (except for SYSADMIN)
    if user.role != UserRole.SYSADMIN:
        restaurant = await get_restaurant_from_request(request)
        
        # If there's a subdomain, validate user belongs to that restaurant
        if restaurant:
            if user.restaurant_id != restaurant.id:
                raise UnauthorizedError(
                    "You don't have access to this restaurant. "
                    "Please login using your restaurant's subdomain."
                )
        # If no subdomain but user has restaurant_id, they should use their subdomain
        elif user.restaurant_id:
            raise ValidationError(
                "Please access the system using your restaurant's subdomain."
            )
    
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
    
    # Determine if we're in production (HTTPS)
    is_production = request.url.scheme == "https"
    
    # Safari/iOS requires samesite="none" for cross-port cookies (localhost:3000 → localhost:8001)
    # But samesite="none" requires secure=True, which requires HTTPS
    # Solution: Use "lax" in development (same domain), "none" in production (cross-domain)
    samesite_value = "none" if is_production else "lax"
    
    # Set HTTPOnly cookies for enhanced security
    # Access token cookie
    response.set_cookie(
        key="access_token",
        value=access_token,
        httponly=True,  # JavaScript cannot access
        secure=is_production,  # Only send over HTTPS in production
        samesite=samesite_value,  # "none" for production (cross-domain), "lax" for dev
        max_age=settings.ACCESS_TOKEN_EXPIRE_MINUTES * 60,  # seconds
        path="/",
    )
    
    # Refresh token cookie
    response.set_cookie(
        key="refresh_token",
        value=refresh_token,
        httponly=True,
        secure=is_production,
        samesite=samesite_value,
        max_age=60 * 60 * 24 * 7,  # 7 days
        path="/",
    )
    
    # Still return tokens in response for backward compatibility
    # Frontend can use either cookies or tokens
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


@router.post("/logout", status_code=status.HTTP_200_OK)
async def logout(response: Response):
    """
    Logout user by clearing HTTPOnly cookies.
    """
    # Clear access token cookie
    response.delete_cookie(
        key="access_token",
        path="/",
    )
    
    # Clear refresh token cookie
    response.delete_cookie(
        key="refresh_token",
        path="/",
    )
    
    return {
        "message": "Successfully logged out",
        "success": True
    }


@router.post("/change-password", status_code=status.HTTP_200_OK)
async def change_password(
    password_data: ChangePasswordRequest,
    db: Session = Depends(get_db),
    current_user: UserModel = Depends(user_service.get_current_active_user)
):
    """
    Change the password for the currently authenticated user.
    Requires the current password for verification.
    """
    # Verify current password
    if not verify_password(password_data.current_password, current_user.hashed_password):
        raise ValidationError("La contraseña actual es incorrecta", field="current_password")
    
    # Check that new password is different from current
    if verify_password(password_data.new_password, current_user.hashed_password):
        raise ValidationError("La nueva contraseña debe ser diferente a la actual", field="new_password")
    
    # Update password - fetch user from db to ensure it's attached to the session
    try:
        user = db.query(UserModel).filter(UserModel.id == current_user.id).first()
        if not user:
            raise ValidationError("Usuario no encontrado")
        
        user.hashed_password = get_password_hash(password_data.new_password)
        db.commit()
        db.refresh(user)
        
        return {
            "message": "Contraseña actualizada exitosamente",
            "success": True
        }
    except ValidationError:
        raise
    except Exception as e:
        db.rollback()
        raise ValidationError(f"Error al actualizar la contraseña: {str(e)}")


@router.get("/me", response_model=UserSchema)
async def get_current_user_info(
    current_user: UserModel = Depends(get_current_active_user)
) -> UserModel:
    """
    Get current authenticated user information.
    
    Returns the user profile including:
    - email
    - full_name
    - role
    - restaurant_id (if applicable)
    - is_active status
    """
    return current_user
