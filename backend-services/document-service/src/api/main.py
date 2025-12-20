from fastapi import FastAPI, UploadFile, File, HTTPException, Depends
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
import uuid
import os
import json
import requests
import threading

# PDF Library
try:
    import pypdf
    PDF_AVAILABLE = True
except ImportError:
    pypdf = None
    PDF_AVAILABLE = False

# AWS S3 Setup
try:
    import boto3
    from botocore.exceptions import ClientError
    s3_client = boto3.client('s3')
    S3_AVAILABLE = True
except ImportError:
    s3_client = None
    S3_AVAILABLE = False

# Kafka Setup
try:
    from kafka import KafkaProducer
except ImportError:
    KafkaProducer = None

# Environment Configuration
KAFKA_BOOTSTRAP_SERVERS = os.getenv("KAFKA_BOOTSTRAP_SERVERS", "localhost:9092")
S3_BUCKET = os.getenv("S3_BUCKET", "document-reader-storage-dev")
USE_S3 = os.getenv("USE_S3", "true").lower() == "true"

producer = None

# Kafka Producer Setup
if KafkaProducer:
    try:
        producer = KafkaProducer(
            bootstrap_servers=KAFKA_BOOTSTRAP_SERVERS,
            value_serializer=lambda v: json.dumps(v).encode('utf-8')
        )
        print(f"Kafka producer connected to {KAFKA_BOOTSTRAP_SERVERS}")
    except Exception as e:
        print(f"Warning: Kafka producer connection failed: {e}")

# Database Setup
from src.core.database import engine, Base, get_db
from src.models.document import DocumentMetadata

# Create Tables
Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="Document Service",
    description="Document Reader Service for Cloud Learning Platform",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Local fallback storage
UPLOAD_DIR = "mock_uploads"
os.makedirs(UPLOAD_DIR, exist_ok=True)

# DeepSeek Configuration
DEEPSEEK_API_KEY = os.getenv("DEEPSEEK_API_KEY", "sk-062701f3c65d4ed2a941503f0b18c63e")
DEEPSEEK_API_URL = "https://api.deepseek.com/chat/completions"

def upload_to_s3(file_path: str, s3_key: str) -> bool:
    """Upload file to S3 bucket."""
    if not S3_AVAILABLE or not USE_S3:
        return False
    try:
        s3_client.upload_file(file_path, S3_BUCKET, s3_key)
        print(f"Uploaded to S3: s3://{S3_BUCKET}/{s3_key}")
        return True
    except ClientError as e:
        print(f"S3 upload failed: {e}")
        return False

def download_from_s3(s3_key: str, local_path: str) -> bool:
    """Download file from S3 bucket."""
    if not S3_AVAILABLE:
        return False
    try:
        s3_client.download_file(S3_BUCKET, s3_key, local_path)
        return True
    except ClientError as e:
        print(f"S3 download failed: {e}")
        return False

def delete_from_s3(s3_key: str) -> bool:
    """Delete file from S3 bucket."""
    if not S3_AVAILABLE:
        return False
    try:
        s3_client.delete_object(Bucket=S3_BUCKET, Key=s3_key)
        return True
    except ClientError as e:
        print(f"S3 delete failed: {e}")
        return False

def save_notes_to_s3(file_id: str, notes: str) -> bool:
    """Save generated notes to S3."""
    if not S3_AVAILABLE or not USE_S3:
        return False
    try:
        s3_key = f"notes/{file_id}_notes.txt"
        s3_client.put_object(
            Bucket=S3_BUCKET,
            Key=s3_key,
            Body=notes.encode('utf-8'),
            ContentType='text/plain'
        )
        return True
    except ClientError as e:
        print(f"S3 notes save failed: {e}")
        return False

def extract_text_from_pdf(filepath):
    if not PDF_AVAILABLE:
        return "PDF library not available"
    try:
        reader = pypdf.PdfReader(filepath)
        text = ""
        for page in reader.pages:
            text += page.extract_text() + "\n"
        return text
    except Exception as e:
        print(f"Error extracting text: {e}")
        return None

def generate_summary(text):
    if not text:
        return "Could not extract text for summarization."
    
    truncated_text = text[:4000]
    
    try:
        response = requests.post(
            DEEPSEEK_API_URL,
            headers={
                "Content-Type": "application/json",
                "Authorization": f"Bearer {DEEPSEEK_API_KEY}"
            },
            json={
                "model": "deepseek-chat",
                "messages": [
                    {"role": "system", "content": "You are a helpful assistant that summarizes educational documents."},
                    {"role": "user", "content": f"Please provide a concise summary of the following text:\n\n{truncated_text}"}
                ],
                "stream": False
            },
            timeout=10
        )
        if response.status_code == 200:
            return response.json()['choices'][0]['message']['content']
        else:
            return f"Summarization failed: {response.status_code}"
    except Exception as e:
        return f"Summarization error: {str(e)}"

@app.get("/")
async def root(db: Session = Depends(get_db)):
    """List all documents."""
    docs = db.query(DocumentMetadata).all()
    if not docs:
        return []
    
    return [
        {
            "id": d.id,
            "file_id": d.file_id,
            "filename": d.filename,
            "status": d.status,
            "summary": d.summary,
            "storage": "s3" if d.s3_key else "local",
            "upload_date": str(d.upload_date)
        } for d in docs
    ]

@app.get("/health")
async def health():
    return {
        "status": "healthy",
        "kafka_connected": producer is not None,
        "s3_available": S3_AVAILABLE and USE_S3,
        "pdf_support": PDF_AVAILABLE
    }

@app.post("/upload")
async def upload_document(file: UploadFile = File(...), db: Session = Depends(get_db)):
    """Upload and process a document. Stores in S3 and produces Kafka events."""
    try:
        file_id = str(uuid.uuid4())
        file_ext = os.path.splitext(file.filename)[1].lower()
        filename = f"{file_id}{file_ext}"
        local_path = os.path.join(UPLOAD_DIR, filename)
        
        # Save locally first
        with open(local_path, "wb") as f:
            content = await file.read()
            f.write(content)

        # Upload to S3
        storage_type = "local"
        s3_key = f"documents/{filename}"
        
        if upload_to_s3(local_path, s3_key):
            storage_type = "s3"

        # Produce upload event
        if producer:
            event = {
                "event": "document.uploaded",
                "file_id": file_id,
                "filename": file.filename,
                "s3_key": s3_key if storage_type == "s3" else None,
                "storage": storage_type
            }
            producer.send("document.uploaded", event)
            print(f"Produced event: {event}")

        # Process Summary if PDF
        summary = "No summary available (not a PDF)"
        extracted_text = None
        if file_ext == '.pdf':
            extracted_text = extract_text_from_pdf(local_path)
            summary = generate_summary(extracted_text)
            # Save notes to S3
            save_notes_to_s3(file_id, summary)

        # Save Metadata to DB
        db_doc = DocumentMetadata(
            filename=file.filename,
            file_id=file_id,
            s3_key=s3_key if storage_type == "s3" else filename,
            status="Processed",
            summary=summary
        )
        db.add(db_doc)
        db.commit()
        db.refresh(db_doc)

        # Clean up local file if uploaded to S3
        if storage_type == "s3" and os.path.exists(local_path):
            os.remove(local_path)

        # Produce processed event
        if producer:
            event = {
                "event": "document.processed",
                "file_id": file_id,
                "document_id": db_doc.id,
                "filename": file.filename,
                "text_preview": extracted_text[:500] if extracted_text else "",
                "storage": storage_type,
                "status": "success"
            }
            producer.send("document.processed", event)
            
            # Produce notes.generated event
            notes_event = {
                "event": "notes.generated",
                "file_id": file_id,
                "document_id": db_doc.id,
                "summary": summary[:500]
            }
            producer.send("notes.generated", notes_event)
            print(f"Produced events: document.processed, notes.generated")

        return {
            "status": "success",
            "file_id": file_id,
            "document_id": db_doc.id,
            "filename": file.filename,
            "summary": summary,
            "storage": storage_type,
            "message": "File uploaded and processed"
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/document/{document_id}")
async def get_document(document_id: int, db: Session = Depends(get_db)):
    """Get document details by ID."""
    doc = db.query(DocumentMetadata).filter(DocumentMetadata.id == document_id).first()
    if not doc:
        raise HTTPException(status_code=404, detail="Document not found")
    return {
        "id": doc.id,
        "file_id": doc.file_id,
        "filename": doc.filename,
        "status": doc.status,
        "summary": doc.summary,
        "s3_key": doc.s3_key,
        "upload_date": str(doc.upload_date)
    }

@app.get("/document/{document_id}/notes")
async def get_document_notes(document_id: int, db: Session = Depends(get_db)):
    """Get generated notes for a document."""
    doc = db.query(DocumentMetadata).filter(DocumentMetadata.id == document_id).first()
    if not doc:
        raise HTTPException(status_code=404, detail="Document not found")
    return {
        "document_id": doc.id,
        "filename": doc.filename,
        "notes": doc.summary
    }

@app.post("/document/{document_id}/regenerate-notes")
async def regenerate_notes(document_id: int, db: Session = Depends(get_db)):
    """Regenerate notes for a document."""
    doc = db.query(DocumentMetadata).filter(DocumentMetadata.id == document_id).first()
    if not doc:
        raise HTTPException(status_code=404, detail="Document not found")
    
    # Try to get file from S3 or local
    local_path = os.path.join(UPLOAD_DIR, os.path.basename(doc.s3_key))
    
    if not os.path.exists(local_path):
        # Try downloading from S3
        if not download_from_s3(doc.s3_key, local_path):
            raise HTTPException(status_code=404, detail="Document file not found in S3 or local storage")
    
    # Re-extract and summarize
    if doc.s3_key.endswith('.pdf') or local_path.endswith('.pdf'):
        extracted_text = extract_text_from_pdf(local_path)
        new_summary = generate_summary(extracted_text)
        doc.summary = new_summary
        db.commit()
        
        # Save new notes to S3
        save_notes_to_s3(doc.file_id, new_summary)
        
        # Produce notes.generated event
        if producer:
            event = {
                "event": "notes.generated",
                "file_id": doc.file_id,
                "document_id": doc.id,
                "summary": new_summary[:500]
            }
            producer.send("notes.generated", event)
        
        return {"document_id": doc.id, "notes": new_summary, "message": "Notes regenerated successfully"}
    
    return {"document_id": doc.id, "notes": doc.summary, "message": "Document is not a PDF, cannot regenerate notes"}

@app.delete("/document/{document_id}")
async def delete_document(document_id: int, db: Session = Depends(get_db)):
    """Delete a document by ID from S3 and database."""
    doc = db.query(DocumentMetadata).filter(DocumentMetadata.id == document_id).first()
    if not doc:
        raise HTTPException(status_code=404, detail="Document not found")
    
    # Delete from S3
    if doc.s3_key:
        delete_from_s3(doc.s3_key)
        delete_from_s3(f"notes/{doc.file_id}_notes.txt")
    
    # Delete local file
    local_path = os.path.join(UPLOAD_DIR, os.path.basename(doc.s3_key or ""))
    if os.path.exists(local_path):
        os.remove(local_path)
    
    # Delete from DB
    db.delete(doc)
    db.commit()
    
    return {"message": "Document deleted successfully", "document_id": document_id}
