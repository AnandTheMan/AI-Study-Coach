from pydantic import BaseModel, Field, EmailStr
from typing import Optional, List, Dict, Any
from datetime import datetime


class UserCreate(BaseModel):
    email: EmailStr
    username: str = Field(..., min_length=3, max_length=50)
    password: str = Field(..., min_length=6)
    full_name: Optional[str] = None


class UserLogin(BaseModel):
    email: EmailStr
    password: str


class UserResponse(BaseModel):
    id: int
    email: str
    username: str
    full_name: Optional[str]
    created_at: datetime
    
    class Config:
        from_attributes = True


class Token(BaseModel):
    access_token: str
    token_type: str
    user: UserResponse


class PaperGenerationRequest(BaseModel):
    grade: str = Field(..., description="Grade level (e.g., '9', '10', 'A-Level')")
    subject: str = Field(..., description="Subject name (e.g., 'Mathematics', 'Physics')")
    chapter: str = Field(..., description="Chapter name")
    topic: Optional[str] = Field(None, description="Specific topic within the chapter")
    
    class Config:
        json_schema_extra = {
            "example": {
                "grade": "10",
                "subject": "Mathematics",
                "chapter": "Algebra",
                "topic": "Quadratic Equations"
            }
        }


class Question(BaseModel):
    question_number: int
    question_type: str  # MCQ, Short Answer, Long Answer
    question_text: str
    marks: int
    options: Optional[List[str]] = None  # For MCQs


class PaperGenerationResponse(BaseModel):
    paper_id: int
    grade: str
    subject: str
    chapter: str
    topic: Optional[str]
    questions: List[Question]
    total_marks: int
    instructions: str
    created_at: datetime


class Answer(BaseModel):
    question_number: int
    answer: str


class EvaluationRequest(BaseModel):
    paper_id: int = Field(..., description="ID of the generated paper")
    answers: List[Answer] = Field(..., description="Student's answers")
    
    class Config:
        json_schema_extra = {
            "example": {
                "paper_id": 1,
                "answers": [
                    {"question_number": 1, "answer": "A"},
                    {"question_number": 2, "answer": "The solution is x = 2"}
                ]
            }
        }


class QuestionFeedback(BaseModel):
    question_number: int
    student_answer: str
    marks_obtained: float
    marks_total: int
    feedback: str
    correct_answer: Optional[str] = None


class EvaluationResponse(BaseModel):
    evaluation_id: int
    paper_id: int
    total_score: float
    total_marks: int
    percentage: float
    grade_letter: str
    feedback: List[QuestionFeedback]
    overall_feedback: str
    evaluated_at: datetime


class DocumentPaperRequest(BaseModel):
    num_mcqs: int = Field(0, ge=0, description="Number of MCQ questions (0 if not needed)")
    num_short_questions: int = Field(0, ge=0, description="Number of short answer questions (0 if not needed)")
    marks_per_mcq: int = Field(2, ge=1, description="Marks per MCQ question")
    marks_per_short: int = Field(5, ge=1, description="Marks per short answer question")
    
    class Config:
        json_schema_extra = {
            "example": {
                "num_mcqs": 10,
                "num_short_questions": 5,
                "marks_per_mcq": 2,
                "marks_per_short": 5
            }
        }


class DocumentPaperResponse(BaseModel):
    paper_id: int
    document_name: str
    questions: List[Question]
    total_marks: int
    instructions: str
    created_at: datetime


class DashboardStats(BaseModel):
    total_papers: int
    total_evaluations: int
    average_score: float
    recent_papers: List[Dict[str, Any]]
    recent_evaluations: List[Dict[str, Any]]
    subject_performance: List[Dict[str, Any]]
    grade_distribution: Dict[str, int]


class MediaPaperRequest(BaseModel):
    num_mcqs: int = Field(0, ge=0, description="Number of MCQ questions (0 if not needed)")
    num_short_questions: int = Field(0, ge=0, description="Number of short answer questions (0 if not needed)")
    marks_per_mcq: int = Field(2, ge=1, description="Marks per MCQ question")
    marks_per_short: int = Field(5, ge=1, description="Marks per short answer question")
    
    class Config:
        json_schema_extra = {
            "example": {
                "num_mcqs": 10,
                "num_short_questions": 5,
                "marks_per_mcq": 2,
                "marks_per_short": 5
            }
        }


class MediaPaperResponse(BaseModel):
    paper_id: int
    media_name: str
    media_type: str  # 'audio' or 'video'
    transcript_preview: str
    questions: List[Question]
    total_marks: int
    instructions: str
    created_at: datetime
