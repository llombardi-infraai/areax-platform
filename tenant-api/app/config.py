from pydantic_settings import BaseSettings
from typing import List


class Settings(BaseSettings):
    # Database
    DATABASE_URL_TEMPLATE: str = "postgresql+asyncpg://user:pass@{host}/{db}"
    
    # Redis
    REDIS_URL: str = "redis://localhost:6379"
    
    # AI Service
    MOONSHOT_API_KEY: str = ""
    MOONSHOT_BASE_URL: str = "https://api.moonshot.cn/v1"
    MOONSHOT_MODEL: str = "moonshot-v1-128k"
    
    # Control Plane
    CONTROL_PLANE_URL: str = "http://localhost:8080"
    
    # JWT
    JWT_PUBLIC_KEY: str = ""
    JWT_ALGORITHM: str = "RS256"
    
    # File Storage
    FILE_STORAGE_BUCKET: str = "areax-files"
    FILE_STORAGE_ENDPOINT: str = "https://nyc3.digitaloceanspaces.com"
    FILE_STORAGE_ACCESS_KEY: str = ""
    FILE_STORAGE_SECRET_KEY: str = ""
    
    # Server
    PORT: int = 8081
    HOST: str = "0.0.0.0"
    
    # CORS
    CORS_ORIGINS: List[str] = ["*"]
    
    # Logging
    LOG_LEVEL: str = "INFO"
    
    # Security
    ENCRYPTION_KEY: str = ""
    
    class Config:
        env_file = ".env"
        case_sensitive = True


settings = Settings()
