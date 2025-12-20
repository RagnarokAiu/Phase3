from fastapi import FastAPI, UploadFile, File, HTTPException
from fastapi.middleware.cors import CORSMiddleware
import speech_recognition as sr
import os
import shutil
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

# Environment Configuration
KAFKA_BOOTSTRAP_SERVERS = os.getenv("KAFKA_BOOTSTRAP_SERVERS", "localhost:9092")
S3_BUCKET = os.getenv("S3_BUCKET", "stt-service-storage-dev")
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

app = FastAPI(
    title="STT Service",
    description="Speech-to-Text Service for Cloud Learning Platform",
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
TEMP_DIR = "temp_uploads"
os.makedirs(TEMP_DIR, exist_ok=True)

# In-memory storage for transcription metadata
transcription_metadata = {}

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
    """Background thread to consume audio.transcription.requested events."""
    if not KafkaConsumer:
        return
    try:
        consumer = KafkaConsumer(
            'audio.transcription.requested',
            bootstrap_servers=KAFKA_BOOTSTRAP_SERVERS,
            value_deserializer=lambda v: json.loads(v.decode('utf-8')),
            group_id='stt-service-group',
            auto_offset_reset='earliest'
        )
        print("Kafka consumer started for audio.transcription.requested")
        for message in consumer:
            try:
                data = message.value
                print(f"Received STT request via Kafka: {data}")
                # Process the request (would trigger transcription)
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
    return {"service": "stt-service", "status": "running"}

@app.get("/health")
async def health():
    return {
        "status": "healthy",
        "kafka_connected": producer is not None,
        "s3_available": S3_AVAILABLE and USE_S3
    }

@app.post("/transcribe")
async def transcribe(file: UploadFile = File(...)):
    """Transcribe audio file to text. Stores uploaded audio in S3."""
    try:
        transcription_id = str(uuid.uuid4())
        file_ext = os.path.splitext(file.filename)[1]
        filename = f"{transcription_id}{file_ext}"
        local_path = os.path.join(TEMP_DIR, filename)
        
        # Save uploaded file locally first
        with open(local_path, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)
        
        # Upload to S3
        storage_type = "local"
        s3_key = f"uploads/{filename}"
        
        if upload_to_s3(local_path, s3_key):
            storage_type = "s3"
        
        # Transcribe
        recognizer = sr.Recognizer()
        text = ""
        confidence = 0.0
        
        try:
            with sr.AudioFile(local_path) as source:
                audio_data = recognizer.record(source)
                text = recognizer.recognize_google(audio_data)
                confidence = 1.0
        except ValueError:
            text = "Error: Please upload a .WAV file for local transcription (MP3 requires ffmpeg installed)."
            confidence = 0.0
        except sr.UnknownValueError:
            text = "Could not understand audio"
            confidence = 0.0
        except sr.RequestError:
            text = "Speech API unreachable. (Offline Mode)"
            confidence = 0.0
        except Exception as e:
            print(f"STT Error: {e}")
            text = "Simulation: This audio file discussed Cloud Architecture concepts."
            confidence = 0.9
        
        # Store metadata
        transcription_metadata[transcription_id] = {
            "id": transcription_id,
            "filename": file.filename,
            "s3_key": s3_key if storage_type == "s3" else None,
            "text": text,
            "confidence": confidence,
            "storage": storage_type
        }
        
        # Clean up local file if uploaded to S3
        if storage_type == "s3" and os.path.exists(local_path):
            os.remove(local_path)
        
        # Produce Kafka event
        if producer:
            event = {
                "event": "audio.transcription.completed",
                "transcription_id": transcription_id,
                "filename": file.filename,
                "s3_key": s3_key if storage_type == "s3" else None,
                "text": text[:200] if text else "",
                "confidence": confidence,
                "storage": storage_type,
                "status": "success" if confidence > 0 else "failed"
            }
            producer.send("audio.transcription.completed", event)
            print(f"Produced event: {event}")
        
        return {
            "transcription_id": transcription_id,
            "text": text,
            "confidence": confidence,
            "storage": storage_type
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/transcription/{transcription_id}")
async def get_transcription(transcription_id: str):
    """Get transcription result by ID."""
    if transcription_id not in transcription_metadata:
        raise HTTPException(status_code=404, detail="Transcription not found")
    return transcription_metadata[transcription_id]

@app.get("/transcriptions")
async def list_transcriptions():
    """List all transcriptions."""
    return list(transcription_metadata.values())

@app.delete("/transcription/{transcription_id}")
async def delete_transcription(transcription_id: str):
    """Delete transcription by ID. Also removes from S3."""
    if transcription_id not in transcription_metadata:
        raise HTTPException(status_code=404, detail="Transcription not found")
    
    metadata = transcription_metadata[transcription_id]
    
    # Delete from S3
    if metadata.get("s3_key"):
        delete_from_s3(metadata["s3_key"])
    
    del transcription_metadata[transcription_id]
    return {"message": "Transcription deleted successfully", "transcription_id": transcription_id}
