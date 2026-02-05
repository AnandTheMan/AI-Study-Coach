from sqlalchemy import create_engine, Column, Integer, String, Text, DateTime, Float, ForeignKey
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, relationship
from datetime import datetime
import config

DATABASE_URL = config.DATABASE_URL

# Create engine with appropriate settings for SQLite or PostgreSQL
if DATABASE_URL.startswith("sqlite"):
    engine = create_engine(DATABASE_URL, connect_args={"check_same_thread": False})
else:
    # PostgreSQL or other databases
    engine = create_engine(DATABASE_URL)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()


class User(Base):
    __tablename__ = "users"
    
    id = Column(Integer, primary_key=True, index=True)
    email = Column(String(255), unique=True, index=True, nullable=False)
    username = Column(String(100), unique=True, index=True, nullable=False)
    hashed_password = Column(String(255), nullable=False)
    full_name = Column(String(200))
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # Relationships
    papers = relationship("Paper", back_populates="user")
    evaluations = relationship("Evaluation", back_populates="user")


class Paper(Base):
    __tablename__ = "papers"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    grade = Column(String(50), nullable=True)
    subject = Column(String(100), nullable=True)
    chapter = Column(String(200), nullable=True)
    topic = Column(String(200), nullable=True)
    document_name = Column(String(500), nullable=True)
    paper_type = Column(String(50), default="curriculum")
    questions = Column(Text, nullable=False)
    total_marks = Column(Integer, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # Relationships
    user = relationship("User", back_populates="papers")
    evaluations = relationship("Evaluation", back_populates="paper")


class Evaluation(Base):
    __tablename__ = "evaluations"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    paper_id = Column(Integer, ForeignKey("papers.id"), nullable=False)
    student_answers = Column(Text, nullable=False)
    score = Column(Float, nullable=False)
    total_marks = Column(Integer, nullable=False)
    feedback = Column(Text, nullable=False)
    evaluated_at = Column(DateTime, default=datetime.utcnow)
    
    # Relationships
    user = relationship("User", back_populates="evaluations")
    paper = relationship("Paper", back_populates="evaluations")


# Create tables
Base.metadata.create_all(bind=engine)


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
