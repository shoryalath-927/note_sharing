from sqlalchemy import String, Float, Integer, DateTime, Text, JSON
from sqlalchemy.orm import Mapped, mapped_column
from datetime import datetime
from backend.database import Base


class Note(Base):
    __tablename__ = "notes"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    
    # File info
    filename: Mapped[str] = mapped_column(String(255))
    file_path: Mapped[str] = mapped_column(String(500))
    uploader_name: Mapped[str] = mapped_column(String(100))
    
    # Academic info
    subject: Mapped[str] = mapped_column(String(100))          # "Mathematics", "Computer Science", etc.
    branch: Mapped[str] = mapped_column(String(100), default="BTech")
    semester: Mapped[int] = mapped_column(Integer, default=1)
    topic_tags: Mapped[list] = mapped_column(JSON, default=list)  # ["DSA", "Sorting", "Trees"]
    
    # AI Scores (0-10 each)
    handwriting_score: Mapped[float] = mapped_column(Float, default=0.0)  # Gemini
    layout_score: Mapped[float] = mapped_column(Float, default=0.0)       # Gemini
    diagram_score: Mapped[float] = mapped_column(Float, default=0.0)      # Gemini
    content_depth_score: Mapped[float] = mapped_column(Float, default=0.0) # Groq
    subject_match_score: Mapped[float] = mapped_column(Float, default=0.0) # Groq

    # Weighted final score (0-100)
    # Formula: Handwriting 35% + Content 45% + Layout 20%
    final_score: Mapped[float] = mapped_column(Float, default=0.0)

    # Student star rating (1-5, from peers)
    star_rating: Mapped[float] = mapped_column(Float, default=0.0)
    rating_count: Mapped[int] = mapped_column(Integer, default=0)

    # Recommendation score combines AI score + peer rating
    recommendation_score: Mapped[float] = mapped_column(Float, default=0.0)

    # Extracted text (for search & Groq scoring)
    extracted_text: Mapped[str] = mapped_column(Text, default="")
    
    # AI-generated summary
    summary: Mapped[str] = mapped_column(Text, default="")
    
    # Scoring details (for display)
    score_breakdown: Mapped[dict] = mapped_column(JSON, default=dict)
    
    # Embedding stored separately as .npy file (path here)
    embedding_path: Mapped[str] = mapped_column(String(500), default="")

    # Status
    status: Mapped[str] = mapped_column(String(50), default="pending")
    # pending | scoring | scored | failed

    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    scored_at: Mapped[datetime] = mapped_column(DateTime, nullable=True)

    def to_dict(self):
        return {
            "id": self.id,
            "filename": self.filename,
            "uploader_name": self.uploader_name,
            "subject": self.subject,
            "branch": self.branch,
            "semester": self.semester,
            "topic_tags": self.topic_tags or [],
            "handwriting_score": round(self.handwriting_score, 1),
            "layout_score": round(self.layout_score, 1),
            "diagram_score": round(self.diagram_score, 1),
            "content_depth_score": round(self.content_depth_score, 1),
            "subject_match_score": round(self.subject_match_score, 1),
            "final_score": round(self.final_score, 1),
            "star_rating": round(self.star_rating, 1),
            "rating_count": self.rating_count,
            "recommendation_score": round(self.recommendation_score, 1),
            "summary": self.summary,
            "score_breakdown": self.score_breakdown or {},
            "status": self.status,
            "created_at": self.created_at.isoformat() if self.created_at else None,
        }
