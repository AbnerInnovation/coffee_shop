from pydantic import BaseModel, Field

class Token(BaseModel):
    """
    Token schema for authentication.
    """
    access_token: str = Field(..., description="JWT access token")
    token_type: str = Field("bearer", description="Token type")

class TokenData(BaseModel):
    """
    Token data schema for JWT payload.
    """
    sub: str | None = Field(None, description="Subject (user ID)")
