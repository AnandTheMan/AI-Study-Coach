from fastapi import APIRouter, HTTPException, Depends, Header
from sqlalchemy.orm import Session
from typing import Optional
from database import get_db, User, Paper, Evaluation
from schemas_new import UserCreate, UserLogin, UserResponse, Token, DashboardStats
from auth import get_password_hash, verify_password, create_access_token, decode_access_token
import json

router = APIRouter()


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


@router.post("/signup", response_model=Token)
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


@router.post("/login", response_model=Token)
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


@router.get("/me", response_model=UserResponse)
async def get_me(current_user: User = Depends(get_current_user)):
    """Get current user profile"""
    return UserResponse.model_validate(current_user)


@router.get("/dashboard", response_model=DashboardStats)
async def get_dashboard(current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    """Get user dashboard with progress tracking"""
    from main import calculate_grade
    
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
