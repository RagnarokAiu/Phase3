from fastapi import FastAPI, Depends, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
from pydantic import BaseModel
from typing import List, Optional
import random
import os
import json
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
S3_BUCKET = os.getenv("S3_BUCKET", "quiz-service-storage-dev")
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
from src.models.quiz import Question

# Create Tables
Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="Quiz Service",
    description="Quiz and Exercise Service for Cloud Learning Platform",
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

# In-memory quiz storage
quizzes = {}
quiz_results = {}
document_notes = {}  # Stores notes from Kafka events

class QuizSubmission(BaseModel):
    answers: dict  # {question_id: answer}

def save_quiz_to_s3(quiz_id: str, quiz_data: dict) -> bool:
    """Save quiz to S3."""
    if not S3_AVAILABLE or not USE_S3:
        return False
    try:
        s3_key = f"quizzes/{quiz_id}.json"
        s3_client.put_object(
            Bucket=S3_BUCKET,
            Key=s3_key,
            Body=json.dumps(quiz_data),
            ContentType='application/json'
        )
        print(f"Saved quiz to S3: s3://{S3_BUCKET}/{s3_key}")
        return True
    except ClientError as e:
        print(f"S3 save failed: {e}")
        return False

def save_results_to_s3(quiz_id: str, results: dict) -> bool:
    """Save quiz results to S3."""
    if not S3_AVAILABLE or not USE_S3:
        return False
    try:
        s3_key = f"results/{quiz_id}_results.json"
        s3_client.put_object(
            Bucket=S3_BUCKET,
            Key=s3_key,
            Body=json.dumps(results),
            ContentType='application/json'
        )
        return True
    except ClientError as e:
        print(f"S3 results save failed: {e}")
        return False

# Kafka Consumer Background Thread
def kafka_consumer_thread():
    """Background thread to consume notes.generated and quiz.requested events."""
    if not KafkaConsumer:
        return
    try:
        consumer = KafkaConsumer(
            'notes.generated', 'quiz.requested',
            bootstrap_servers=KAFKA_BOOTSTRAP_SERVERS,
            value_deserializer=lambda v: json.loads(v.decode('utf-8')),
            group_id='quiz-service-group',
            auto_offset_reset='earliest'
        )
        print("Kafka consumer started for notes.generated, quiz.requested")
        for message in consumer:
            try:
                data = message.value
                event_type = data.get('event')
                
                if event_type == 'notes.generated':
                    file_id = data.get('file_id')
                    summary = data.get('summary', '')
                    print(f"Received notes for document {file_id}")
                    document_notes[file_id] = summary
                    
                elif event_type == 'quiz.requested':
                    print(f"Received quiz request via Kafka: {data}")
                    # Could trigger automatic quiz generation here
                    
            except Exception as e:
                print(f"Error processing Kafka message: {e}")
    except Exception as e:
        print(f"Kafka consumer failed: {e}")

@app.on_event("startup")
async def startup_event():
    """Start Kafka consumer and seed data on app startup."""
    # Seed data
    try:
        seed_data()
    except Exception as e:
        print(f"Seed data error (non-fatal): {e}")
    
    # Start Kafka consumer
    if KafkaConsumer:
        thread = threading.Thread(target=kafka_consumer_thread, daemon=True)
        thread.start()

def seed_data():
    """Seed initial questions into database."""
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

@app.get("/")
async def root():
    return {"service": "quiz-service", "status": "running"}

@app.get("/health")
async def health():
    return {
        "status": "healthy",
        "kafka_connected": producer is not None,
        "s3_available": S3_AVAILABLE and USE_S3,
        "document_notes_count": len(document_notes)
    }

@app.get("/generate")
async def generate_quiz(topic: str = "Cloud Computing (AWS/Azure/GCP)", document_id: str = None, db: Session = Depends(get_db)):
    """Generate a quiz on a given topic. Uses document notes if available."""
    quiz_id = f"quiz_{random.randint(10000, 99999)}"
    
    # Get document notes for context if available
    context = ""
    if document_id and document_id in document_notes:
        context = document_notes[document_id]
    
    # Try Generating from DeepSeek first
    try:
        import requests
        
        headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {os.getenv('DEEPSEEK_API_KEY', 'sk-062701f3c65d4ed2a941503f0b18c63e')}"
        }
        
        prompt = f"""
        Generate 3 multiple choice questions about {topic}.
        {f"Based on this content: {context[:1000]}" if context else ""}
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
            content = content.replace("```json", "").replace("```", "").strip()
            quiz_data = json.loads(content)
            
            questions_list = []
            answers_dict = {}
            
            for idx, q in enumerate(quiz_data.get("questions", [])):
                db_q = Question(text=q["text"], options=q["options"], answer=q["answer"])
                db.add(db_q)
                db.commit()
                db.refresh(db_q)
                questions_list.append({
                    "id": db_q.id,
                    "text": q["text"],
                    "options": q["options"]
                })
                answers_dict[str(db_q.id)] = q["answer"]
            
            # Store quiz
            quiz_store = {
                "id": quiz_id,
                "topic": topic,
                "questions": questions_list,
                "answers": answers_dict
            }
            quizzes[quiz_id] = quiz_store
            
            # Save to S3
            save_quiz_to_s3(quiz_id, quiz_store)
            
            # Produce Kafka event
            if producer:
                event = {
                    "event": "quiz.generated",
                    "quiz_id": quiz_id,
                    "topic": topic,
                    "question_count": len(questions_list),
                    "status": "success"
                }
                producer.send("quiz.generated", event)
                print(f"Produced event: {event}")
            
            return {
                "quiz_id": quiz_id,
                "topic": topic,
                "questions": questions_list
            }
            
    except Exception as e:
        print(f"AI Gen Failed: {e}. Falling back to DB.")

    # Fallback: Fetch from DB
    total_questions = db.query(Question).count()
    if total_questions < 5:
        db_questions = db.query(Question).all()
    else:
        all_ids = [q.id for q in db.query(Question.id).all()]
        random_ids = random.sample(all_ids, min(5, len(all_ids)))
        db_questions = db.query(Question).filter(Question.id.in_(random_ids)).all()

    questions_list = [{"id": q.id, "text": q.text, "options": q.options} for q in db_questions]
    answers_dict = {str(q.id): q.answer for q in db_questions}
    
    quiz_store = {
        "id": quiz_id,
        "topic": topic,
        "questions": questions_list,
        "answers": answers_dict
    }
    quizzes[quiz_id] = quiz_store
    
    # Save to S3
    save_quiz_to_s3(quiz_id, quiz_store)
    
    # Produce Kafka event
    if producer:
        event = {
            "event": "quiz.generated",
            "quiz_id": quiz_id,
            "topic": topic,
            "question_count": len(questions_list),
            "status": "success",
            "source": "database"
        }
        producer.send("quiz.generated", event)
        print(f"Produced event: {event}")

    return {
        "quiz_id": quiz_id,
        "topic": topic,
        "questions": questions_list
    }

@app.get("/quiz/{quiz_id}")
async def get_quiz(quiz_id: str):
    """Get quiz questions by ID."""
    if quiz_id not in quizzes:
        raise HTTPException(status_code=404, detail="Quiz not found")
    quiz = quizzes[quiz_id]
    return {
        "quiz_id": quiz_id,
        "topic": quiz["topic"],
        "questions": quiz["questions"]
    }

@app.post("/quiz/{quiz_id}/submit")
async def submit_quiz(quiz_id: str, submission: QuizSubmission):
    """Submit quiz answers and get results. Saves results to S3."""
    if quiz_id not in quizzes:
        raise HTTPException(status_code=404, detail="Quiz not found")
    
    quiz = quizzes[quiz_id]
    correct_answers = quiz["answers"]
    
    score = 0
    total = len(correct_answers)
    results = []
    
    for q_id, user_answer in submission.answers.items():
        correct = correct_answers.get(q_id, "")
        is_correct = user_answer == correct
        if is_correct:
            score += 1
        results.append({
            "question_id": q_id,
            "user_answer": user_answer,
            "correct_answer": correct,
            "is_correct": is_correct
        })
    
    result = {
        "quiz_id": quiz_id,
        "score": score,
        "total": total,
        "percentage": round((score / total) * 100, 2) if total > 0 else 0,
        "results": results
    }
    
    quiz_results[quiz_id] = result
    
    # Save results to S3
    save_results_to_s3(quiz_id, result)
    
    return result

@app.get("/quiz/{quiz_id}/results")
async def get_quiz_results(quiz_id: str):
    """Get quiz results by ID."""
    if quiz_id not in quiz_results:
        raise HTTPException(status_code=404, detail="Quiz results not found. Please submit the quiz first.")
    return quiz_results[quiz_id]

@app.get("/history")
async def get_quiz_history():
    """Get all quiz history."""
    return [{"quiz_id": qid, "topic": q["topic"], "question_count": len(q["questions"])} for qid, q in quizzes.items()]

@app.delete("/quiz/{quiz_id}")
async def delete_quiz(quiz_id: str):
    """Delete quiz by ID."""
    if quiz_id not in quizzes:
        raise HTTPException(status_code=404, detail="Quiz not found")
    del quizzes[quiz_id]
    if quiz_id in quiz_results:
        del quiz_results[quiz_id]
    return {"message": "Quiz deleted successfully", "quiz_id": quiz_id}

@app.get("/documents")
async def get_available_documents():
    """Get documents available from Kafka notes.generated events."""
    return document_notes
