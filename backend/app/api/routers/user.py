from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from ...db.base import get_db
from ...models.user import User as UserModel
from ...schemas.user import User as UserSchema
from ...services.user import get_current_active_user

router = APIRouter(
    prefix="/users",
    tags=["users"]
)

@router.get("/me", response_model=UserSchema)
async def read_users_me(
    current_user: UserModel = Depends(get_current_active_user)
) -> UserModel:
    """
    Get current user information.
    
    Returns the currently authenticated user's data.
    """
    return current_user
