from fastapi import FastAPI, HTTPException, Depends, UploadFile, File, Form, Header
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
import json
from datetime import datetime, timedelta
from typing import Optional

from database import get_db, Paper, Evaluation, User
from schemas_new import (
    UserCreate, UserLogin, UserResponse, Token, DashboardStats,
    PaperGenerationRequest, PaperGenerationResponse, Question,
    EvaluationRequest, EvaluationResponse, QuestionFeedback, Answer,
    DocumentPaperRequest, DocumentPaperResponse, MediaPaperRequest, MediaPaperResponse
)
from openai_service import generate_paper_with_ai, evaluate_paper_with_ai, generate_paper_from_document, generate_paper_from_media_transcript
from document_utils import extract_text_from_file, validate_document_length
from media_utils import transcribe_media_file, validate_transcript_length, get_media_info
from auth import get_password_hash, verify_password, create_access_token, decode_access_token

app = FastAPI(
    title="Oxford Curriculum Paper Generator & Evaluator API",
    description="Generate and evaluate examination papers following Oxford Curriculum standards",
    version="1.0.0"
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


def get_current_user(authorization: Optional[str] = Header(None), db: Session = Depends(get_db)):
    """Get current authenticated user from JWT token"""
    if not authorization or not authorization.startswith("Bearer "):
        raise HTTPException(status_code=401, detail="Not authenticated")
    
    token = authorization.split(" ")[1]
    payload = decode_access_token(token)
    
    if not payload:
        raise HTTPException(status_code=401, detail="Invalid or expired token")
    
    user_id = payload.get("sub")
    if not user_id:
        raise HTTPException(status_code=401, detail="Invalid token payload")
    
    user = db.query(User).filter(User.id == int(user_id)).first()
    if not user:
        raise HTTPException(status_code=401, detail="User not found")
    
    return user


@app.get("/")
def read_root():
    return {
        "message": "AI Study Coach API",
        "endpoints": {
            "auth": {
                "signup": "/api/auth/signup",
                "login": "/api/auth/login",
                "me": "/api/auth/me"
            },
            "papers": {
                "generate_paper": "/api/generate_paper",
                "generate_from_document": "/api/generate_paper_from_document",
                "generate_from_media": "/api/generate_paper_from_media",
                "get_paper": "/api/papers/{paper_id}",
                "evaluate": "/api/evaluate_paper"
            },
            "dashboard": "/api/dashboard"
        }
    }


@app.post("/api/auth/signup", response_model=Token)
async def signup(user: UserCreate, db: Session = Depends(get_db)):
    """Register a new user"""
    # Check if user already exists
    existing_user = db.query(User).filter(
        (User.email == user.email) | (User.username == user.username)
    ).first()
    
    if existing_user:
        raise HTTPException(status_code=400, detail="Email or username already registered")
    
    # Create new user
    hashed_password = get_password_hash(user.password)
    db_user = User(
        email=user.email,
        username=user.username,
        hashed_password=hashed_password,
        full_name=user.full_name
    )
    
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    
    # Create access token
    access_token = create_access_token(data={"sub": str(db_user.id)})
    
    return Token(
        access_token=access_token,
        token_type="bearer",
        user=UserResponse.model_validate(db_user)
    )


@app.post("/api/auth/login", response_model=Token)
async def login(user: UserLogin, db: Session = Depends(get_db)):
    """Login user and return JWT token"""
    # Find user
    db_user = db.query(User).filter(User.email == user.email).first()
    
    if not db_user or not verify_password(user.password, db_user.hashed_password):
        raise HTTPException(status_code=401, detail="Incorrect email or password")
    
    # Create access token
    access_token = create_access_token(data={"sub": str(db_user.id)})
    
    return Token(
        access_token=access_token,
        token_type="bearer",
        user=UserResponse.model_validate(db_user)
    )


@app.get("/api/auth/me", response_model=UserResponse)
async def get_me(current_user: User = Depends(get_current_user)):
    """Get current user profile"""
    return UserResponse.model_validate(current_user)


@app.get("/api/papers/{paper_id}")
async def get_paper(
    paper_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get a specific paper by ID"""
    paper = db.query(Paper).filter(
        Paper.id == paper_id,
        Paper.user_id == current_user.id
    ).first()
    
    if not paper:
        raise HTTPException(status_code=404, detail="Paper not found")
    
    # Parse questions from JSON
    questions = json.loads(paper.questions)
    
    # Format response
    from schemas_new import Question
    formatted_questions = [
        Question(
            question_number=q["question_number"],
            question_type=q["question_type"],
            question_text=q["question_text"],
            marks=q["marks"],
            options=q.get("options")
        )
        for q in questions
    ]
    
    return {
        "paper_id": paper.id,
        "grade": paper.grade,
        "subject": paper.subject,
        "chapter": paper.chapter,
        "topic": paper.topic,
        "document_name": paper.document_name,
        "paper_type": paper.paper_type,
        "questions": formatted_questions,
        "total_marks": paper.total_marks,
        "created_at": paper.created_at
    }


@app.get("/api/dashboard", response_model=DashboardStats)
async def get_dashboard(current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    """Get user dashboard with progress tracking"""
    # Get user's papers and evaluations
    papers = db.query(Paper).filter(Paper.user_id == current_user.id).all()
    evaluations = db.query(Evaluation).filter(Evaluation.user_id == current_user.id).all()
    
    # Calculate statistics
    total_papers = len(papers)
    total_evaluations = len(evaluations)
    average_score = sum(e.score / e.total_marks * 100 for e in evaluations) / len(evaluations) if evaluations else 0
    
    # Recent papers
    recent_papers = [
        {
            "id": p.id,
            "type": p.paper_type,
            "grade": p.grade,
            "subject": p.subject,
            "chapter": p.chapter,
            "document_name": p.document_name,
            "total_marks": p.total_marks,
            "created_at": p.created_at.isoformat()
        }
        for p in sorted(papers, key=lambda x: x.created_at, reverse=True)[:10]
    ]
    
    # Recent evaluations with paper details
    recent_evaluations = [
        {
            "id": e.id,
            "paper_id": e.paper_id,
            "score": e.score,
            "total_marks": e.total_marks,
            "percentage": round((e.score / e.total_marks) * 100, 2),
            "grade": calculate_grade((e.score / e.total_marks) * 100),
            "evaluated_at": e.evaluated_at.isoformat()
        }
        for e in sorted(evaluations, key=lambda x: x.evaluated_at, reverse=True)[:10]
    ]
    
    # Subject performance
    subject_scores = {}
    for e in evaluations:
        paper = db.query(Paper).filter(Paper.id == e.paper_id).first()
        if paper and paper.subject:
            if paper.subject not in subject_scores:
                subject_scores[paper.subject] = {"total": 0, "count": 0}
            subject_scores[paper.subject]["total"] += (e.score / e.total_marks) * 100
            subject_scores[paper.subject]["count"] += 1
    
    subject_performance = [
        {
            "subject": subject,
            "average_score": round(scores["total"] / scores["count"], 2)
        }
        for subject, scores in subject_scores.items()
    ]
    
    # Grade distribution
    grade_dist = {}
    for e in evaluations:
        grade = calculate_grade((e.score / e.total_marks) * 100)
        grade_dist[grade] = grade_dist.get(grade, 0) + 1
    
    return DashboardStats(
        total_papers=total_papers,
        total_evaluations=total_evaluations,
        average_score=round(average_score, 2),
        recent_papers=recent_papers,
        recent_evaluations=recent_evaluations,
        subject_performance=subject_performance,
        grade_distribution=grade_dist
    )


@app.post("/api/generate_paper", response_model=PaperGenerationResponse)
async def generate_paper(
    request: PaperGenerationRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Generate an examination paper following Oxford Curriculum pattern
    
    - **grade**: Grade level (e.g., '9', '10', 'A-Level')
    - **subject**: Subject name (e.g., 'Mathematics', 'Physics', 'Chemistry')
    - **chapter**: Chapter name
    - **topic**: Optional specific topic within the chapter
    """
    try:
        # Generate paper using OpenAI
        paper_data = generate_paper_with_ai(
            grade=request.grade,
            subject=request.subject,
            chapter=request.chapter,
            topic=request.topic
        )
        
        # Calculate total marks
        total_marks = sum(q.get("marks", 0) for q in paper_data["questions"])
        
        # Save to database
        db_paper = Paper(
            user_id=current_user.id,
            grade=request.grade,
            paper_type="curriculum",
            subject=request.subject,
            chapter=request.chapter,
            topic=request.topic,
            questions=json.dumps(paper_data["questions"]),
            total_marks=total_marks
        )
        db.add(db_paper)
        db.commit()
        db.refresh(db_paper)
        
        # Format response
        questions = [
            Question(
                question_number=q["question_number"],
                question_type=q["question_type"],
                question_text=q["question_text"],
                marks=q["marks"],
                options=q.get("options")
            )
            for q in paper_data["questions"]
        ]
        
        return PaperGenerationResponse(
            paper_id=db_paper.id,
            grade=db_paper.grade,
            subject=db_paper.subject,
            chapter=db_paper.chapter,
            topic=db_paper.topic,
            questions=questions,
            total_marks=total_marks,
            instructions=paper_data.get("instructions", "Answer all questions."),
            created_at=db_paper.created_at
        )
        
    except Exception as e:
        import traceback
        print(f"ERROR in generate_paper: {str(e)}")
        print(traceback.format_exc())
        raise HTTPException(status_code=500, detail=f"Error generating paper: {str(e)}")


@app.post("/api/generate_paper_from_document", response_model=DocumentPaperResponse)
async def generate_paper_from_document_endpoint(
    file: UploadFile = File(..., description="Document file (PDF, DOCX, or TXT)"),
    num_mcqs: int = Form(0, ge=0, description="Number of MCQ questions"),
    num_short_questions: int = Form(0, ge=0, description="Number of short answer questions"),
    marks_per_mcq: int = Form(2, ge=1, description="Marks per MCQ"),
    marks_per_short: int = Form(5, ge=1, description="Marks per short answer"),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Generate an examination paper based on uploaded document content
    
    - **file**: Upload a document (PDF, DOCX, or TXT)
    - **num_mcqs**: Number of Multiple Choice Questions (0 to skip)
    - **num_short_questions**: Number of Short Answer Questions (0 to skip)
    - **marks_per_mcq**: Marks for each MCQ (default: 2)
    - **marks_per_short**: Marks for each short answer (default: 5)
    
    You must specify at least one question type (MCQs or Short Questions)
    """
    try:
        # Validate at least one question type
        if num_mcqs == 0 and num_short_questions == 0:
            raise HTTPException(
                status_code=400, 
                detail="Please specify at least one question type (num_mcqs or num_short_questions)"
            )
        
        # Extract text from document
        document_text = await extract_text_from_file(file)
        
        # Validate document length
        validate_document_length(document_text)
        
        # Generate paper using OpenAI
        paper_data = generate_paper_from_document(
            document_text=document_text,
            num_mcqs=num_mcqs,
            num_short_questions=num_short_questions,
            marks_per_mcq=marks_per_mcq,
            marks_per_short=marks_per_short
        )
        
        # Calculate total marks
        total_marks = sum(q.get("marks", 0) for q in paper_data["questions"])
        
        # Save to database
        db_paper = Paper(
            user_id=current_user.id,
            document_name=file.filename,
            paper_type="document",
            questions=json.dumps(paper_data["questions"]),
            total_marks=total_marks
        )
        db.add(db_paper)
        db.commit()
        db.refresh(db_paper)
        
        # Format response
        questions = [
            Question(
                question_number=q["question_number"],
                question_type=q["question_type"],
                question_text=q["question_text"],
                marks=q["marks"],
                options=q.get("options")
            )
            for q in paper_data["questions"]
        ]
        
        return DocumentPaperResponse(
            paper_id=db_paper.id,
            document_name=file.filename,
            questions=questions,
            total_marks=total_marks,
            instructions=paper_data.get("instructions", "Answer all questions based on the document."),
            created_at=db_paper.created_at
        )
        
    except HTTPException:
        raise
    except Exception as e:
        import traceback
        print(f"ERROR in generate_paper_from_document: {str(e)}")
        print(traceback.format_exc())
        raise HTTPException(status_code=500, detail=f"Error generating paper from document: {str(e)}")


@app.post("/api/generate_paper_from_media", response_model=MediaPaperResponse)
async def generate_paper_from_media_endpoint(
    file: UploadFile = File(..., description="Media file (Audio: MP3, WAV, M4A | Video: MP4, AVI, MOV)"),
    num_mcqs: int = Form(0, ge=0, description="Number of MCQ questions"),
    num_short_questions: int = Form(0, ge=0, description="Number of short answer questions"),
    marks_per_mcq: int = Form(2, ge=1, description="Marks per MCQ"),
    marks_per_short: int = Form(5, ge=1, description="Marks per short answer"),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Generate an examination paper based on uploaded audio/video content
    
    - **file**: Upload a media file (Audio: MP3, WAV, M4A | Video: MP4, AVI, MOV)
    - **num_mcqs**: Number of Multiple Choice Questions (0 to skip)
    - **num_short_questions**: Number of Short Answer Questions (0 to skip)
    - **marks_per_mcq**: Marks for each MCQ (default: 2)
    - **marks_per_short**: Marks for each short answer (default: 5)
    
    You must specify at least one question type (MCQs or Short Questions)
    Maximum file size: 25MB
    """
    try:
        # Validate at least one question type
        if num_mcqs == 0 and num_short_questions == 0:
            raise HTTPException(
                status_code=400, 
                detail="Please specify at least one question type (num_mcqs or num_short_questions)"
            )
        
        # Get media info
        media_info = get_media_info(file.filename)
        
        # Transcribe audio/video to text using Whisper API
        transcript = await transcribe_media_file(file)
        
        # Validate transcript length
        validate_transcript_length(transcript)
        
        # Generate paper using OpenAI
        paper_data = generate_paper_from_media_transcript(
            transcript=transcript,
            num_mcqs=num_mcqs,
            num_short_questions=num_short_questions,
            marks_per_mcq=marks_per_mcq,
            marks_per_short=marks_per_short
        )
        
        # Calculate total marks
        total_marks = sum(q.get("marks", 0) for q in paper_data["questions"])
        
        # Save to database
        db_paper = Paper(
            user_id=current_user.id,
            document_name=file.filename,  # Store media filename
            paper_type="media",  # New paper type for audio/video
            questions=json.dumps(paper_data["questions"]),
            total_marks=total_marks
        )
        db.add(db_paper)
        db.commit()
        db.refresh(db_paper)
        
        # Format response
        questions = [
            Question(
                question_number=q["question_number"],
                question_type=q["question_type"],
                question_text=q["question_text"],
                marks=q["marks"],
                options=q.get("options")
            )
            for q in paper_data["questions"]
        ]
        
        # Create transcript preview (first 200 characters)
        transcript_preview = transcript[:200] + "..." if len(transcript) > 200 else transcript
        
        return MediaPaperResponse(
            paper_id=db_paper.id,
            media_name=file.filename,
            media_type=media_info["media_type"],
            transcript_preview=transcript_preview,
            questions=questions,
            total_marks=total_marks,
            instructions=paper_data.get("instructions", "Answer all questions based on the audio/video content."),
            created_at=db_paper.created_at
        )
        
    except HTTPException:
        raise
    except Exception as e:
        import traceback
        print(f"ERROR in generate_paper_from_media: {str(e)}")
        print(traceback.format_exc())
        raise HTTPException(status_code=500, detail=f"Error generating paper from media: {str(e)}")


@app.post("/api/evaluate_paper", response_model=EvaluationResponse)
async def evaluate_paper(
    request: EvaluationRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Evaluate a student's answers for a generated paper
    
    - **paper_id**: ID of the generated paper
    - **answers**: List of student answers with question numbers
    """
    try:
        # Fetch the paper from database
        paper = db.query(Paper).filter(Paper.id == request.paper_id).first()
        if not paper:
            raise HTTPException(status_code=404, detail="Paper not found")
        
        # Verify paper belongs to current user
        if paper.user_id != current_user.id:
            raise HTTPException(status_code=403, detail="Access denied: This paper belongs to another user")
        
        questions = json.loads(paper.questions)
        
        # Convert student answers to dict for easier lookup
        student_answers_dict = {
            ans.question_number: ans.answer 
            for ans in request.answers
        }
        
        print(f"Evaluating paper {request.paper_id} with {len(questions)} questions")
        print(f"Student provided answers for {len(student_answers_dict)} questions")
        print(f"Question types: {[q['question_type'] for q in questions]}")
        
        # Evaluate using OpenAI
        evaluation_data = evaluate_paper_with_ai(questions, student_answers_dict)
        
        print(f"Received feedback for {len(evaluation_data['question_feedback'])} questions")
        
        # Validate that all questions were evaluated
        evaluated_q_numbers = {fb["question_number"] for fb in evaluation_data["question_feedback"]}
        all_q_numbers = {q["question_number"] for q in questions}
        
        if evaluated_q_numbers != all_q_numbers:
            missing = all_q_numbers - evaluated_q_numbers
            print(f"WARNING: Not all questions were evaluated. Missing: {missing}")
            # Add zero marks for missing questions
            for q_num in missing:
                question = next(q for q in questions if q["question_number"] == q_num)
                evaluation_data["question_feedback"].append({
                    "question_number": q_num,
                    "marks_obtained": 0.0,
                    "marks_total": question["marks"],
                    "feedback": "No evaluation provided for this question.",
                    "correct_answer": question.get("correct_answer", "N/A")
                })
        
        # Calculate total score - ensure we sum all feedback items
        total_score = 0.0
        for fb in evaluation_data["question_feedback"]:
            marks = fb.get("marks_obtained", 0)
            if marks is None:
                marks = 0.0
            total_score += float(marks)
        
        print(f"Total score calculated: {total_score} out of {paper.total_marks}")
        
        # Calculate percentage and grade
        if paper.total_marks > 0:
            percentage = (total_score / paper.total_marks) * 100
        else:
            percentage = 0.0
            
        grade_letter = calculate_grade(percentage)
        
        # Save evaluation to database
        db_evaluation = Evaluation(
            user_id=current_user.id,
            paper_id=request.paper_id,
            student_answers=json.dumps(student_answers_dict),
            score=total_score,
            total_marks=paper.total_marks,
            feedback=json.dumps(evaluation_data["question_feedback"])
        )
        db.add(db_evaluation)
        db.commit()
        db.refresh(db_evaluation)
        
        # Format response
        feedback_list = [
            QuestionFeedback(
                question_number=fb["question_number"],
                student_answer=student_answers_dict.get(fb["question_number"], "Not answered"),
                marks_obtained=fb["marks_obtained"],
                marks_total=fb["marks_total"],
                feedback=fb["feedback"],
                correct_answer=fb.get("correct_answer")
            )
            for fb in evaluation_data["question_feedback"]
        ]
        
        return EvaluationResponse(
            evaluation_id=db_evaluation.id,
            paper_id=request.paper_id,
            total_score=float(total_score),
            total_marks=paper.total_marks,
            percentage=round(float(percentage), 2),
            grade_letter=grade_letter,
            feedback=feedback_list,
            overall_feedback=evaluation_data.get("overall_feedback", ""),
            evaluated_at=db_evaluation.evaluated_at
        )
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error evaluating paper: {str(e)}")


def calculate_grade(percentage: float) -> str:
    """Calculate letter grade based on Oxford grading system"""
    if percentage >= 90:
        return "A*"
    elif percentage >= 80:
        return "A"
    elif percentage >= 70:
        return "B"
    elif percentage >= 60:
        return "C"
    elif percentage >= 50:
        return "D"
    elif percentage >= 40:
        return "E"
    else:
        return "U"  # Ungraded


@app.get("/api/papers")
async def get_all_papers(current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    """Get all papers for current user"""
    papers = db.query(Paper).filter(Paper.user_id == current_user.id).order_by(Paper.created_at.desc()).all()
    return {
        "count": len(papers),
        "papers": [
            {
                "id": p.id,
                "grade": p.grade,
                "subject": p.subject,
                "chapter": p.chapter,
                "topic": p.topic,
                "total_marks": p.total_marks,
                "created_at": p.created_at
            }
            for p in papers
        ]
    }


@app.get("/api/evaluations")
async def get_all_evaluations(current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    """Get all evaluations for current user"""
    evaluations = db.query(Evaluation).filter(Evaluation.user_id == current_user.id).order_by(Evaluation.evaluated_at.desc()).all()
    return {
        "count": len(evaluations),
        "evaluations": [
            {
                "id": e.id,
                "paper_id": e.paper_id,
                "score": e.score,
                "total_marks": e.total_marks,
                "percentage": round((e.score / e.total_marks) * 100, 2),
                "evaluated_at": e.evaluated_at
            }
            for e in evaluations
        ]
    }


if __name__ == "__main__":
    import uvicorn
    import sys
    from pathlib import Path
    
    print("=" * 60)
    print("Starting AI Study Coach Backend API")
    print("=" * 60)
    
    # Check for .env file
    env_file = Path(__file__).parent / ".env"
    if not env_file.exists():
        print("\n❌ ERROR: .env file not found!")
        print(f"   Expected location: {env_file}")
        print("\nPlease create backend/.env with:")
        print("   OPENAI_API_KEY=your_api_key_here")
        print("   DATABASE_URL=sqlite:///./oxford_papers.db")
        print("   SECRET_KEY=your-secret-key")
        sys.exit(1)
    
    # Check OpenAI API Key
    import config
    if not config.OPENAI_API_KEY or config.OPENAI_API_KEY == "your_openai_api_key_here":
        print("\n❌ ERROR: OpenAI API Key not configured!")
        print("   Edit backend/.env and set OPENAI_API_KEY")
        print("   Get your key from: https://platform.openai.com/api-keys")
        sys.exit(1)
    
    print(f"\n✓ Environment configuration loaded")
    print(f"✓ OpenAI API Key: {config.OPENAI_API_KEY[:20]}...")
    print(f"✓ Database: {config.DATABASE_URL}")
    
    # Initialize database
    try:
        from database import init_db
        init_db()
        print(f"✓ Database initialized")
    except Exception as e:
        print(f"\n⚠️  Warning: Could not initialize database: {e}")
        print("   Database will be created on first request")
    
    print(f"\n🚀 Starting server on http://0.0.0.0:8000")
    print(f"📚 API Documentation: http://localhost:8000/docs")
    print("=" * 60)
    print()
    
    try:
        uvicorn.run(app, host="0.0.0.0", port=8000)
    except Exception as e:
        print(f"\n❌ ERROR: Failed to start server!")
        print(f"   {str(e)}")
        sys.exit(1)
