from fastapi import FastAPI, Depends
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
import random
from src.core.database import engine, Base, get_db
from src.models.quiz import Question

# Create Tables
Base.metadata.create_all(bind=engine)

app = FastAPI(title="Quiz Service")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Seed Data on Startup
def seed_data():
    db = next(get_db())
    if db.query(Question).count() == 0:
        questions = [
            {"text": "What does EC2 stand for?", "options": ["Elastic Compute Cloud", "Elastic Cloud Compute", "Electric Cloud Control", "Elastic Cache Cloud"], "answer": "Elastic Compute Cloud"},
            {"text": "Which service is used for object storage?", "options": ["RDS", "S3", "EBS", "Glacier"], "answer": "S3"},
            {"text": "What is the function of AWS Lambda?", "options": ["To host websites", "To run code without servers", "To store databases", "To manage networks"], "answer": "To run code without servers"},
            {"text": "Which of these is a NoSQL database?", "options": ["MySQL", "PostgreSQL", "DynamoDB", "Oracle"], "answer": "DynamoDB"},
            {"text": "What is IAM used for?", "options": ["Internet Access Management", "Identity and Access Management", "Internal Access Monitor", "Identity Authentication Method"], "answer": "Identity and Access Management"},
            {"text": "What does VPC stand for?", "options": ["Virtual Private Cloud", "Verified Private Connection", "Virtual Public Cloud", "Visual Private Center"], "answer": "Virtual Private Cloud"},
            {"text": "Which service provides Content Delivery Network (CDN)?", "options": ["Route 53", "CloudFront", "Direct Connect", "VPC"], "answer": "CloudFront"},
            {"text": "What is the primary use of Route 53?", "options": ["Load Balancing", "DNS Management", "Database Caching", "Auto Scaling"], "answer": "DNS Management"},
            {"text": "Which service is used for relational databases?", "options": ["DynamoDB", "RDS", "Redshift", "ElastiCache"], "answer": "RDS"},
            {"text": "What is CloudFormation used for?", "options": ["Infrastructure as Code", "Data Warehousing", "Machine Learning", "Monitoring"], "answer": "Infrastructure as Code"}
        ]
        for q in questions:
            db_q = Question(text=q["text"], options=q["options"], answer=q["answer"])
            db.add(db_q)
        db.commit()
        print("Database seeded with initial questions.")

seed_data()

@app.get("/")
async def root():
    return {"service": "quiz-service", "status": "running"}

@app.get("/health")
async def health():
    return {"status": "healthy"}

@app.get("/generate")
async def generate_quiz(topic: str = "Cloud Computing (AWS/Azure/GCP)", db: Session = Depends(get_db)):
    # Try Generating from DeepSeek first
    try:
        import requests
        import json
        
        headers = {
            "Content-Type": "application/json",
            "Authorization": "Bearer sk-062701f3c65d4ed2a941503f0b18c63e"
        }
        
        prompt = f"""
        Generate 2 multiple choice questions about {topic}.
        Format purely as a JSON object with this key: "questions": [{{"text": "...", "options": ["A", "B", "C", "D"], "answer": "A"}}]
        Do not include markdown formatting.
        """
        
        data = {
            "model": "deepseek-chat",
            "messages": [
                {"role": "system", "content": "You are a trivia generator api."},
                {"role": "user", "content": prompt}
            ],
            "stream": False
        }
        
        api_response = requests.post("https://api.deepseek.com/chat/completions", headers=headers, json=data, timeout=10)
        
        if api_response.status_code == 200:
            content = api_response.json()['choices'][0]['message']['content']
            # Clean potential markdown
            content = content.replace("```json", "").replace("```", "").strip()
            quiz_data = json.loads(content)
            
            # Save new questions to DB for future caching
            new_questions = []
            for q in quiz_data.get("questions", []):
                db_q = Question(text=q["text"], options=q["options"], answer=q["answer"])
                db.add(db_q)
                db.commit()
                db.refresh(db_q)
                new_questions.append(db_q)
                
            return {
                "quiz_id": f"quiz_ai_{random.randint(1000, 9999)}",
                "questions": [
                    { "id": q.id, "text": q.text, "options": q.options, "answer": q.answer } for q in new_questions
                ]
            }
            
    except Exception as e:
        print(f"AI Gen Failed: {e}. Falling back to DB.")

    # Fallback: Fetch from DB
    total_questions = db.query(Question).count()
    if total_questions < 5:
        questions = db.query(Question).all()
    else:
        all_ids = [q.id for q in db.query(Question.id).all()]
        random_ids = random.sample(all_ids, min(5, len(all_ids)))
        questions = db.query(Question).filter(Question.id.in_(random_ids)).all()

    return {
        "quiz_id": f"quiz_db_{random.randint(1000, 9999)}",
        "questions": [
            {
                "id": q.id,
                "text": q.text,
                "options": q.options,
                "answer": q.answer
            } for q in questions
        ]
    }
