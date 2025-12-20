from sqlalchemy import Column, Integer, String, DateTime
from sqlalchemy.sql import func
from src.core.database import Base

class DocumentMetadata(Base):
    __tablename__ = "documents"

    id = Column(Integer, primary_key=True, index=True)
    filename = Column(String, index=True)
    file_id = Column(String, unique=True, index=True)
    s3_key = Column(String)
    status = Column(String, default="Uploaded")
    summary = Column(String, nullable=True)
    upload_date = Column(DateTime(timezone=True), server_default=func.now())
