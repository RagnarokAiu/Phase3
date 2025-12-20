from fastapi import FastAPI, BackgroundTasks, Depends, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from sqlalchemy.orm import Session
import os
import json
import datetime
import threading

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
S3_BUCKET = os.getenv("S3_BUCKET", "chat-service-storage-dev")
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
from src.models.chat import ChatMessage

# Create Tables
Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="Chat Service",
    description="Chat Completion Service for Cloud Learning Platform",
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

class Message(BaseModel):
    message: str
    conversation_id: str = None

# In-memory conversation tracker
conversations = {}
document_knowledge = {}  # Stores document content from Kafka events

def save_conversation_to_s3(conversation_id: str, messages: list) -> bool:
    """Archive conversation to S3."""
    if not S3_AVAILABLE or not USE_S3:
        return False
    try:
        s3_key = f"conversations/{conversation_id}.json"
        s3_client.put_object(
            Bucket=S3_BUCKET,
            Key=s3_key,
            Body=json.dumps(messages),
            ContentType='application/json'
        )
        print(f"Archived conversation to S3: s3://{S3_BUCKET}/{s3_key}")
        return True
    except ClientError as e:
        print(f"S3 archive failed: {e}")
        return False

# Kafka Consumer Background Thread
def kafka_consumer_thread():
    """Background thread to consume document.processed events for knowledge base."""
    if not KafkaConsumer:
        return
    try:
        consumer = KafkaConsumer(
            'document.processed',
            bootstrap_servers=KAFKA_BOOTSTRAP_SERVERS,
            value_deserializer=lambda v: json.loads(v.decode('utf-8')),
            group_id='chat-service-group',
            auto_offset_reset='earliest'
        )
        print("Kafka consumer started for document.processed")
        for message in consumer:
            try:
                data = message.value
                print(f"Received document for knowledge base: {data.get('file_id')}")
                # Store document content in knowledge base
                file_id = data.get('file_id')
                if file_id:
                    document_knowledge[file_id] = {
                        "text_preview": data.get('text_preview', ''),
                        "filename": data.get('filename', '')
                    }
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
    return {"service": "chat-service", "status": "running"}

@app.get("/health")
async def health():
    return {
        "status": "healthy",
        "kafka_connected": producer is not None,
        "s3_available": S3_AVAILABLE and USE_S3,
        "documents_in_knowledge_base": len(document_knowledge)
    }

@app.post("/message")
async def chat_message(msg: Message, db: Session = Depends(get_db)):
    """Send a message and get AI response. Uses document knowledge base."""
    user_text = msg.message
    conversation_id = msg.conversation_id or str(datetime.datetime.now().timestamp())
    
    # Save User Message to DB
    db_user_msg = ChatMessage(role="user", content=user_text)
    db.add(db_user_msg)
    
    # Build context from document knowledge
    context = ""
    if document_knowledge:
        context = "Based on uploaded documents: " + " | ".join(
            [f"{d['filename']}: {d['text_preview'][:200]}" for d in list(document_knowledge.values())[:3]]
        )
    
    # DeepSeek API Call
    response_text = ""
    try:
        import requests
        headers = {
            "Content-Type": "application/json",
            "Authorization": "Bearer sk-062701f3c65d4ed2a941503f0b18c63e"
        }
        
        system_prompt = "You are a helpful cloud learning assistant. Answer questions about AWS, Azure, and Google Cloud clearly and concisely."
        if context:
            system_prompt += f"\n\n{context}"
        
        data = {
            "model": "deepseek-chat",
            "messages": [
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_text}
            ],
            "stream": False
        }
        
        api_response = requests.post("https://api.deepseek.com/chat/completions", headers=headers, json=data, timeout=10)
        
        if api_response.status_code == 200:
            result = api_response.json()
            response_text = result['choices'][0]['message']['content']
        else:
            print(f"DeepSeek Error: {api_response.text}")
            response_text = "I'm having trouble connecting to my brain (DeepSeek API). " + \
                            "But here's a fallback fact: AWS S3 is object storage built to store and retrieve any amount of data from anywhere."
            
    except Exception as e:
        print(f"API Call Failed: {e}")
        response_text = "I am currently offline. Please check your internet connection."

    # Save Assistant Message to DB
    db_bot_msg = ChatMessage(role="assistant", content=response_text)
    db.add(db_bot_msg)
    db.commit()
    
    # Track conversation
    if conversation_id not in conversations:
        conversations[conversation_id] = []
    conversations[conversation_id].append({"role": "user", "content": user_text, "timestamp": str(datetime.datetime.now())})
    conversations[conversation_id].append({"role": "assistant", "content": response_text, "timestamp": str(datetime.datetime.now())})
    
    # Archive to S3 periodically
    if len(conversations[conversation_id]) % 10 == 0:
        save_conversation_to_s3(conversation_id, conversations[conversation_id])
    
    # Produce Kafka event
    if producer:
        event = {
            "event": "chat.message",
            "conversation_id": conversation_id,
            "user_message": user_text[:200],
            "assistant_response": response_text[:200],
            "timestamp": str(datetime.datetime.now())
        }
        producer.send("chat.message", event)
        print(f"Produced event: {event}")

    return {
        "conversation_id": conversation_id,
        "message": user_text,
        "reply": response_text
    }

@app.get("/conversations")
async def list_conversations():
    """List all conversations."""
    return [{"conversation_id": cid, "message_count": len(msgs)} for cid, msgs in conversations.items()]

@app.get("/conversations/{conversation_id}")
async def get_conversation(conversation_id: str):
    """Get conversation history by ID."""
    if conversation_id not in conversations:
        raise HTTPException(status_code=404, detail="Conversation not found")
    return {"conversation_id": conversation_id, "messages": conversations[conversation_id]}

@app.delete("/conversations/{conversation_id}")
async def delete_conversation(conversation_id: str):
    """Delete conversation by ID."""
    if conversation_id not in conversations:
        raise HTTPException(status_code=404, detail="Conversation not found")
    
    # Archive before deleting
    save_conversation_to_s3(conversation_id, conversations[conversation_id])
    
    del conversations[conversation_id]
    return {"message": "Conversation deleted and archived to S3", "conversation_id": conversation_id}

@app.get("/history")
async def get_history(db: Session = Depends(get_db)):
    """Get all message history from database."""
    messages = db.query(ChatMessage).order_by(ChatMessage.timestamp).all()
    return [{"role": m.role, "content": m.content, "timestamp": str(m.timestamp)} for m in messages]

@app.get("/knowledge")
async def get_knowledge_base():
    """Get documents in the knowledge base from Kafka events."""
    return document_knowledge
