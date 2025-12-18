from fastapi import FastAPI, BackgroundTasks, Depends
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from sqlalchemy.orm import Session
import random
import asyncio
import json
import os
import datetime
from src.core.database import engine, Base, get_db
from src.models.chat import ChatMessage

try:
    from kafka import KafkaConsumer
except ImportError:
    KafkaConsumer = None

# Create Tables
Base.metadata.create_all(bind=engine)

app = FastAPI(title="Chat Service")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class Message(BaseModel):
    message: str

# Kafka Consumer Background Task (Simulated for Local)
async def consume_messages():
    pass 

@app.on_event("startup")
async def startup_event():
    pass

@app.get("/")
async def root():
    return {"service": "chat-service", "status": "running"}

@app.get("/health")
async def health():
    return {"status": "healthy"}

@app.post("/message")
async def chat_message(msg: Message, db: Session = Depends(get_db)):
    user_text = msg.message
    
    # Save User Message
    db_user_msg = ChatMessage(role="user", content=user_text)
    db.add(db_user_msg)
    
    # DeepSeek API Call
    response_text = ""
    try:
        headers = {
            "Content-Type": "application/json",
            "Authorization": "Bearer sk-062701f3c65d4ed2a941503f0b18c63e"
        }
        data = {
            "model": "deepseek-chat",
            "messages": [
                {"role": "system", "content": "You are a helpful cloud learning assistant. Answer questions about AWS, Azure, and Google Cloud clearly and concisely."},
                {"role": "user", "content": user_text}
            ],
            "stream": False
        }
        
        # Using requests (synchronous for simplicity in this task, async httpx preferred in prod)
        import requests
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

    # Save Assistant Message
    db_bot_msg = ChatMessage(role="assistant", content=response_text)
    db.add(db_bot_msg)
    db.commit()

    return {"message": response_text, "reply": response_text}

@app.get("/history")
async def get_history(db: Session = Depends(get_db)):
    messages = db.query(ChatMessage).order_by(ChatMessage.timestamp).all()
    return [{"role": m.role, "content": m.content, "timestamp": m.timestamp} for m in messages]
