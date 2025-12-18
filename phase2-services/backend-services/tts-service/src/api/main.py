from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
from pydantic import BaseModel
from gtts import gTTS
import os
import uuid

app = FastAPI(title="TTS Service")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

AUDIO_DIR = "generated_audio"
os.makedirs(AUDIO_DIR, exist_ok=True)

class TextRequest(BaseModel):
    text: str

@app.get("/")
async def root():
    return {"service": "tts-service", "status": "running"}

@app.get("/health")
async def health():
    return {"status": "healthy"}

@app.post("/synthesize")
async def synthesize(req: TextRequest):
    try:
        # Generate Audio using gTTS
        filename = f"{uuid.uuid4()}.mp3"
        filepath = os.path.join(AUDIO_DIR, filename)
        
        tts = gTTS(text=req.text, lang='en', slow=False)
        tts.save(filepath)
        
        # In a real setup, we'd upload to S3. Here, we serve it via static file or direct URL
        # For localhost dev, we return a path the frontend (via Nginx or direct) can hit.
        # Since we don't have a static file server set up in Nginx for this dir, 
        # we'll return a data uri or just the path for the user to find.
        # IMPROVEMENT: Add a GET endpoint to serve these files.
        
        return {
            "audio_url": f"http://localhost:8006/audio/{filename}",
            "message": "Audio generated successfully"
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/audio/{filename}")
async def get_audio(filename: str):
    filepath = os.path.join(AUDIO_DIR, filename)
    if os.path.exists(filepath):
        return FileResponse(filepath)
    return {"error": "File not found"}
