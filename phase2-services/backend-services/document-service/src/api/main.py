from fastapi import FastAPI, UploadFile, File, HTTPException, Depends
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
import uuid
import os
import json
from src.core.database import engine, Base, get_db
from src.models.document import DocumentMetadata

try:
    from kafka import KafkaProducer
except ImportError:
    KafkaProducer = None

# Create Tables
Base.metadata.create_all(bind=engine)

# Kafka Config
KAFKA_BOOTSTRAP_SERVERS = os.getenv("KAFKA_BOOTSTRAP_SERVERS", "localhost:9092")
producer = None

if KafkaProducer:
    try:
        producer = KafkaProducer(
            bootstrap_servers=KAFKA_BOOTSTRAP_SERVERS,
            value_serializer=lambda v: json.dumps(v).encode('utf-8')
        )
    except Exception as e:
        print(f"Warning: Kafka connection failed: {e}")


app = FastAPI(title="Document Service")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Mock storage directory
UPLOAD_DIR = "mock_uploads"
os.makedirs(UPLOAD_DIR, exist_ok=True)

@app.get("/")
async def root(db: Session = Depends(get_db)):
    # Return real documents from DB
    docs = db.query(DocumentMetadata).all()
    # If empty, return simple status to confirm service is up
    if not docs:
        return []
    
    return [
        {
            "id": d.id,
            "filename": d.filename,
            "status": d.status,
            "summary": d.summary,
            "upload_date": str(d.upload_date)
        } for d in docs
    ]

@app.get("/health")
async def health():
    return {"status": "healthy"}

import requests
import pypdf

# ... (Previous imports)

# DeepSeek Configuration
DEEPSEEK_API_KEY = "sk-062701f3c65d4ed2a941503f0b18c63e"
DEEPSEEK_API_URL = "https://api.deepseek.com/chat/completions"

def extract_text_from_pdf(filepath):
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
    
    # Truncate text to avoid token limits (optimistic ~4000 chars)
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

@app.post("/upload")
async def upload_document(file: UploadFile = File(...), db: Session = Depends(get_db)):
    try:
        file_id = str(uuid.uuid4())
        file_ext = os.path.splitext(file.filename)[1].lower()
        filename = f"{file_id}{file_ext}"
        
        # Save locally
        file_path = os.path.join(UPLOAD_DIR, filename)
        with open(file_path, "wb") as f:
            content = await file.read()
            f.write(content)

        # Process Summary if PDF
        summary = "No summary available (not a PDF)"
        if file_ext == '.pdf':
            extracted_text = extract_text_from_pdf(file_path)
            summary = generate_summary(extracted_text)

        # Save Metadata to DB
        db_doc = DocumentMetadata(
            filename=file.filename,
            file_id=file_id,
            s3_key=filename,
            status="Processed",
            summary=summary
        )
        db.add(db_doc)
        db.commit()

        # Produce Event
        if producer:
            event = {
                "event": "document.uploaded",
                "file_id": file_id,
                "filename": file.filename,
                "s3_key": filename 
            }
            producer.send("document.uploaded", event)
            print(f"Produced event: {event}")

        return {
            "status": "success",
            "file_id": file_id,
            "filename": file.filename,
            "summary": summary,
            "message": "File uploaded and processed"
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

