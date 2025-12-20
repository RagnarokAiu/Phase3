import os
from typing import Dict, Optional
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Application settings loaded from environment variables."""
    
    # Application
    PROJECT_NAME: str = "Cloud Learning Platform"
    API_V1_STR: str = "/api/v1"
    ENVIRONMENT: str = os.getenv("ENVIRONMENT", "development")
    
    # AWS Configuration
    AWS_ACCESS_KEY_ID: Optional[str] = os.getenv("AWS_ACCESS_KEY_ID")
    AWS_SECRET_ACCESS_KEY: Optional[str] = os.getenv("AWS_SECRET_ACCESS_KEY")
    AWS_SESSION_TOKEN: Optional[str] = os.getenv("AWS_SESSION_TOKEN")
    AWS_DEFAULT_REGION: str = os.getenv("AWS_DEFAULT_REGION", "us-east-1")
    
    # S3 Configuration (will be populated from Terraform outputs)
    S3_BUCKETS: Dict[str, str] = {
        "document": os.getenv("S3_DOCUMENT_BUCKET", ""),
        "tts": os.getenv("S3_TTS_BUCKET", ""),
        "stt": os.getenv("S3_STT_BUCKET", ""),
        "chat": os.getenv("S3_CHAT_BUCKET", ""),
        "quiz": os.getenv("S3_QUIZ_BUCKET", ""),
        "shared": os.getenv("S3_SHARED_BUCKET", ""),
    }
    
    # Kafka Configuration
    KAFKA_BOOTSTRAP_SERVERS: str = os.getenv(
        "KAFKA_BOOTSTRAP_SERVERS", 
        "localhost:9092"
    )
    KAFKA_CONSUMER_GROUP: str = os.getenv(
        "KAFKA_CONSUMER_GROUP", 
        "cloud-learning-platform"
    )
    
    # Database Configuration
    DB_HOST: str = os.getenv("DB_HOST", "localhost")
    DB_PORT: int = int(os.getenv("DB_PORT", "5432"))
    DB_NAME: str = os.getenv("DB_NAME", "postgres")
    DB_USER: str = os.getenv("DB_USER", "postgres")
    DB_PASSWORD: str = os.getenv("DB_PASSWORD", "")
    
    # OpenAI Configuration
    OPENAI_API_KEY: Optional[str] = os.getenv("OPENAI_API_KEY")
    OPENAI_BASE_URL: str = os.getenv(
        "OPENAI_BASE_URL", 
        "https://api.openai.com/v1"
    )
    OPENAI_MODEL: str = os.getenv("OPENAI_MODEL", "gpt-3.5-turbo")
    
    # Service Configuration
    SERVICE_PORTS: Dict[str, int] = {
        "document": 8000,
        "tts": 8001,
        "stt": 8002,
        "chat": 8003,
        "quiz": 8004,
        "user": 8005,
    }
    
    # Security
    JWT_SECRET_KEY: str = os.getenv(
        "JWT_SECRET_KEY", 
        "your-secret-key-change-in-production"
    )
    JWT_ALGORITHM: str = "HS256"
    JWT_ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    
    # Logging
    LOG_LEVEL: str = os.getenv("LOG_LEVEL", "INFO")
    
    model_config = SettingsConfigDict(
        case_sensitive=True,
        env_file=".env",
        extra="ignore"
    )
    
    def get_database_url(self, service: str = "default") -> str:
        """Get database URL for a specific service."""
        if service == "document":
            db_name = "document_db"
        elif service == "chat":
            db_name = "chat_db"
        elif service == "quiz":
            db_name = "quiz_db"
        elif service == "stt":
            db_name = "stt_db"
        elif service == "user":
            db_name = "user_db"
        else:
            db_name = self.DB_NAME
            
        return (
            f"postgresql://{self.DB_USER}:{self.DB_PASSWORD}"
            f"@{self.DB_HOST}:{self.DB_PORT}/{db_name}"
        )
    
    def get_bucket_name(self, service: str) -> str:
        """Get S3 bucket name for a specific service."""
        return self.S3_BUCKETS.get(service, "")


settings = Settings()