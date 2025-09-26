from pydantic import BaseModel, Field

class Token(BaseModel):
    """
    Token schema for authentication.
    """
    access_token: str = Field(..., description="JWT access token")
    token_type: str = Field("bearer", description="Token type")
    refresh_token: str | None = Field(None, description="JWT refresh token")

class TokenData(BaseModel):
    """
    Token data schema for JWT payload.
    """
    sub: str | None = Field(None, description="Subject (user ID)")

class TokenRefreshRequest(BaseModel):
    """
    Request body for refreshing an access token.
    """
    refresh_token: str = Field(..., description="Refresh token to exchange for a new access token")
