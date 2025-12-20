from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse, StreamingResponse
from pydantic import BaseModel
import os
import uuid
import json
import threading
import io

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
    from kafka import KafkaProducer, KafkaConsumer
except ImportError:
    KafkaProducer = None
    KafkaConsumer = None

# TTS Library
from gtts import gTTS

# Environment Configuration
KAFKA_BOOTSTRAP_SERVERS = os.getenv("KAFKA_BOOTSTRAP_SERVERS", "localhost:9092")
S3_BUCKET = os.getenv("S3_BUCKET", "tts-service-storage-dev")
USE_S3 = os.getenv("USE_S3", "true").lower() == "true"

producer = None
consumer = None

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

app = FastAPI(
    title="TTS Service",
    description="Text-to-Speech Service for Cloud Learning Platform",
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

# Local fallback directory
LOCAL_AUDIO_DIR = "generated_audio"
os.makedirs(LOCAL_AUDIO_DIR, exist_ok=True)

# In-memory storage for audio metadata
audio_metadata = {}

class TextRequest(BaseModel):
    text: str
    language: str = "en"

class SynthesizeResponse(BaseModel):
    audio_id: str
    audio_url: str
    message: str
    storage: str

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

def get_from_s3(s3_key: str) -> bytes:
    """Download file from S3 bucket."""
    if not S3_AVAILABLE:
        return None
    try:
        response = s3_client.get_object(Bucket=S3_BUCKET, Key=s3_key)
        return response['Body'].read()
    except ClientError as e:
        print(f"S3 download failed: {e}")
        return None

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

# Kafka Consumer Background Thread
def kafka_consumer_thread():
    """Background thread to consume audio.generation.requested events."""
    if not KafkaConsumer:
        return
    try:
        consumer = KafkaConsumer(
            'audio.generation.requested',
            bootstrap_servers=KAFKA_BOOTSTRAP_SERVERS,
            value_deserializer=lambda v: json.loads(v.decode('utf-8')),
            group_id='tts-service-group',
            auto_offset_reset='earliest'
        )
        print("Kafka consumer started for audio.generation.requested")
        for message in consumer:
            try:
                data = message.value
                print(f"Received TTS request via Kafka: {data}")
                # Process the request (would trigger synthesis)
            except Exception as e:
                print(f"Error processing Kafka message: {e}")
    except Exception as e:
        print(f"Kafka consumer failed: {e}")

@app.on_event("startup")
async def startup_event():
    """Start Kafka consumer on app startup."""
    if KafkaConsumer:
        thread = threading.Thread(target=kafka_consumer_thread, daemon=True)
        thread.start()

@app.get("/")
async def root():
    return {"service": "tts-service", "status": "running"}

@app.get("/health")
async def health():
    return {
        "status": "healthy",
        "kafka_connected": producer is not None,
        "s3_available": S3_AVAILABLE and USE_S3
    }

@app.post("/synthesize", response_model=SynthesizeResponse)
async def synthesize(req: TextRequest):
    """Generate speech from text using gTTS. Stores in S3 or local storage."""
    try:
        audio_id = str(uuid.uuid4())
        filename = f"{audio_id}.mp3"
        local_path = os.path.join(LOCAL_AUDIO_DIR, filename)
        
        # Generate Audio using gTTS
        tts = gTTS(text=req.text, lang=req.language, slow=False)
        tts.save(local_path)
        
        # Upload to S3 if available
        storage_type = "local"
        s3_key = f"audio/{filename}"
        
        if upload_to_s3(local_path, s3_key):
            storage_type = "s3"
            # Clean up local file after S3 upload
            os.remove(local_path)
        
        # Store metadata
        audio_metadata[audio_id] = {
            "id": audio_id,
            "filename": filename,
            "s3_key": s3_key if storage_type == "s3" else None,
            "text": req.text[:100] + "..." if len(req.text) > 100 else req.text,
            "language": req.language,
            "storage": storage_type
        }
        
        # Produce Kafka event
        if producer:
            event = {
                "event": "audio.generation.completed",
                "audio_id": audio_id,
                "filename": filename,
                "s3_key": s3_key if storage_type == "s3" else None,
                "storage": storage_type,
                "status": "success"
            }
            producer.send("audio.generation.completed", event)
            print(f"Produced event: {event}")
        
        return SynthesizeResponse(
            audio_id=audio_id,
            audio_url=f"/audio/{audio_id}",
            message="Audio generated successfully",
            storage=storage_type
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/audio/{audio_id}")
async def get_audio(audio_id: str):
    """Retrieve generated audio file by ID from S3 or local storage."""
    if audio_id not in audio_metadata:
        raise HTTPException(status_code=404, detail="Audio not found")
    
    metadata = audio_metadata[audio_id]
    
    # Try S3 first
    if metadata.get("storage") == "s3" and metadata.get("s3_key"):
        audio_data = get_from_s3(metadata["s3_key"])
        if audio_data:
            return StreamingResponse(io.BytesIO(audio_data), media_type="audio/mpeg")
    
    # Fallback to local
    local_path = os.path.join(LOCAL_AUDIO_DIR, metadata["filename"])
    if os.path.exists(local_path):
        return FileResponse(local_path, media_type="audio/mpeg")
    
    raise HTTPException(status_code=404, detail="Audio file not found")

@app.get("/audio")
async def list_audio():
    """List all generated audio files."""
    return list(audio_metadata.values())

@app.delete("/audio/{audio_id}")
async def delete_audio(audio_id: str):
    """Delete generated audio file by ID from S3 and local."""
    if audio_id not in audio_metadata:
        raise HTTPException(status_code=404, detail="Audio not found")
    
    metadata = audio_metadata[audio_id]
    
    # Delete from S3
    if metadata.get("s3_key"):
        delete_from_s3(metadata["s3_key"])
    
    # Delete local file
    local_path = os.path.join(LOCAL_AUDIO_DIR, metadata["filename"])
    if os.path.exists(local_path):
        os.remove(local_path)
    
    del audio_metadata[audio_id]
    
    return {"message": "Audio deleted successfully", "audio_id": audio_id}
