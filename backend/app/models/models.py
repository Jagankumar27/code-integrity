import json
from datetime import datetime
from sqlalchemy import Column, Integer, String, Float, Text, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from ..database.db import Base

class User(Base):
    __tablename__ = "users"
    id = Column(Integer, primary_key=True)
    username = Column(String(50), unique=True, nullable=False)
    name = Column(String(100), nullable=False)
    password_hash = Column(String(200), nullable=False)
    role = Column(String(10), nullable=False)  # teacher | student
    submissions = relationship("Submission", back_populates="user")

class Submission(Base):
    __tablename__ = "submissions"
    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    student_name = Column(String(100), nullable=False)
    filename = Column(String(150), nullable=False)
    stored_path = Column(String(300), nullable=False)
    language = Column(String(20), nullable=False)
    code = Column(Text, nullable=False)
    uploaded_at = Column(DateTime, default=datetime.utcnow)
    user = relationship("User", back_populates="submissions")

class Analysis(Base):
    __tablename__ = "analyses"
    id = Column(Integer, primary_key=True)
    created_by = Column(Integer, ForeignKey("users.id"))
    created_at = Column(DateTime, default=datetime.utcnow)
    n_submissions = Column(Integer, default=0)
    n_pairs = Column(Integer, default=0)
    comparisons = relationship("Comparison", back_populates="analysis", cascade="all, delete-orphan")

class Comparison(Base):
    __tablename__ = "comparisons"
    id = Column(Integer, primary_key=True)
    analysis_id = Column(Integer, ForeignKey("analyses.id"))
    sub_a_id = Column(Integer, ForeignKey("submissions.id"))
    sub_b_id = Column(Integer, ForeignKey("submissions.id"))
    text_sim = Column(Float); token_sim = Column(Float); structural_sim = Column(Float)
    semantic_sim = Column(Float); overall = Column(Float)
    risk = Column(String(20)); method = Column(String(60))
    details = Column(Text, default="{}")  # JSON: explanations, blocks, renames
    analysis = relationship("Analysis", back_populates="comparisons")
    sub_a = relationship("Submission", foreign_keys=[sub_a_id])
    sub_b = relationship("Submission", foreign_keys=[sub_b_id])
    def d(self):
        return json.loads(self.details or "{}")
