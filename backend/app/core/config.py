from pydantic import Field
from pydantic_settings import BaseSettings
from typing import Any, Dict, List, Optional
import logging
from urllib.parse import quote_plus
from dotenv import load_dotenv

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Load environment variables from .env file
load_dotenv()

class Settings(BaseSettings):
    # API Settings
    API_V1_STR: str = "/api/v1"
    
    # Security
    SECRET_KEY: str = Field(..., env='SECRET_KEY')
    ALGORITHM: str = Field("HS256", env='ALGORITHM')
    ACCESS_TOKEN_EXPIRE_MINUTES: int = Field(30, env='ACCESS_TOKEN_EXPIRE_MINUTES')
    
    # Database
    MYSQL_SERVER: str = Field(..., env='MYSQL_SERVER')
    MYSQL_USER: str = Field(..., env='MYSQL_USER')
    MYSQL_PASSWORD: str = Field(..., env='MYSQL_PASSWORD')
    MYSQL_DB: str = Field(..., env='MYSQL_DB')
    
    # Frontend
    FRONTEND_URL: str = Field("http://localhost:3000", env='FRONTEND_URL')
    
    # Base domain for restaurant URLs (e.g., "shopacoffee.com" or "localhost:3000")
    BASE_DOMAIN: str = Field(default="shopacoffee.local:3000")
    
    # Protocol for restaurant URLs (http or https)
    BASE_PROTOCOL: str = Field(default="http")
    
    # Debug
    DEBUG: bool = Field(False, env='DEBUG')

    BASE_DOMAIN: str = Field(default="shopacoffee.local:3000")
    BASE_PROTOCOL: str = Field(default="http")    
    # Build database URL with proper escaping for special characters in password
    @property
    def DATABASE_URL(self) -> str:
        # URL encode the password to handle special characters
        encoded_password = quote_plus(self.MYSQL_PASSWORD)
        url = f"mysql+pymysql://{self.MYSQL_USER}:{encoded_password}@{self.MYSQL_SERVER}/{self.MYSQL_DB}?charset=utf8mb4"
        
        # Log the URL with password hidden for security
        safe_url = f"mysql+pymysql://{self.MYSQL_USER}:*****@{self.MYSQL_SERVER}/{self.MYSQL_DB}"
        logger.info(f"Using database URL: {safe_url}")
        
        return url
    
    # CORS origins
    BACKEND_CORS_ORIGINS: List[str] = ["*"]
    
    class Config:
        env_file = ".env"
        env_file_encoding = 'utf-8'
        case_sensitive = True
        extra = 'ignore'  # This allows extra fields in .env without validation errors

# Create settings instance
settings = Settings()

# Log important settings (without sensitive data)
logger.info(f"App environment: {'DEVELOPMENT' if settings.DEBUG else 'PRODUCTION'}")
logger.info(f"Frontend URL: {settings.FRONTEND_URL}")
logger.info(f"Token expires in: {settings.ACCESS_TOKEN_EXPIRE_MINUTES} minutes")
logger.info(f"Base Domain: {settings.BASE_DOMAIN}")
logger.info(f"Base Protocol: {settings.BASE_PROTOCOL}")
