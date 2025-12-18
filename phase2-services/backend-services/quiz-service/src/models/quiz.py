from sqlalchemy import Column, Integer, String, JSON
from src.core.database import Base

class Question(Base):
    __tablename__ = "questions"

    id = Column(Integer, primary_key=True, index=True)
    text = Column(String, index=True)
    options = Column(JSON)  # Store options as a JSON list ["A", "B", "C", "D"]
    answer = Column(String)

class QuizResult(Base):
    __tablename__ = "quiz_results"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, index=True) # Mock user ID
    score = Column(Integer)
    total_questions = Column(Integer)
