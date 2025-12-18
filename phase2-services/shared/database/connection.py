from typing import Generator
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, Session

from ..config.settings import settings
from ..utils.logger import get_logger

logger = get_logger(__name__)


class DatabaseManager:
    """Database connection manager."""
    
    def __init__(self):
        self.engines = {}
        self.session_makers = {}
        self._initialize_engines()
    
    def _initialize_engines(self):
        """Initialize database engines for all services."""
        services = ["document", "chat", "quiz", "stt", "user"]
        
        for service in services:
            try:
                database_url = settings.get_database_url(service)
                
                engine = create_engine(
                    database_url,
                    pool_size=20,
                    max_overflow=30,
                    pool_pre_ping=True,
                    pool_recycle=3600,
                    echo=settings.ENVIRONMENT == "development"
                )
                
                SessionLocal = sessionmaker(
                    autocommit=False,
                    autoflush=False,
                    bind=engine
                )
                
                self.engines[service] = engine
                self.session_makers[service] = SessionLocal
                
                logger.info(f"Database engine initialized for {service} service")
                
            except Exception as e:
                logger.error(f"Failed to initialize database for {service}: {e}")
                raise
    
    def get_session(self, service: str = "document") -> Session:
        """Get a database session for a specific service."""
        if service not in self.session_makers:
            raise ValueError(f"Unknown service: {service}")
        
        return self.session_makers[service]()
    
    def get_db(self, service: str = "document") -> Generator[Session, None, None]:
        """Dependency for FastAPI to get database session."""
        db = self.get_session(service)
        try:
            yield db
        finally:
            db.close()
    
    def create_all_tables(self, service: str = "document"):
        """Create all tables for a service."""
        from .models import Base
        Base.metadata.create_all(bind=self.engines[service])
        logger.info(f"Created tables for {service} service")
    
    def drop_all_tables(self, service: str = "document"):
        """Drop all tables for a service (use with caution!)."""
        from .models import Base
        Base.metadata.drop_all(bind=self.engines[service])
        logger.warning(f"Dropped all tables for {service} service")


# Database base for models
Base = declarative_base()

# Global database manager instance
db_manager = DatabaseManager()

# Convenience function for FastAPI dependency injection
def get_db_session(service: str = "document"):
    """FastAPI dependency to get database session."""
    return db_manager.get_db(service)