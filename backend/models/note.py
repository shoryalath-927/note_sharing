from sqlalchemy import String, Float, Integer, DateTime, Text, JSON
from sqlalchemy.orm import Mapped, mapped_column
from datetime import datetime
from backend.database import Base
import os, json


class Note(Base):
    __tablename__ = "notes"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    filename: Mapped[str] = mapped_column(String(255), default="")
    file_path: Mapped[str] = mapped_column(String(500), default="")
    uploader_name: Mapped[str] = mapped_column(String(100), default="")
    subject: Mapped[str] = mapped_column(String(100), default="")
    branch: Mapped[str] = mapped_column(String(100), default="BTech")
    semester: Mapped[int] = mapped_column(Integer, default=1)
    topic_tags: Mapped[list] = mapped_column(JSON, default=list)
    handwriting_score: Mapped[float] = mapped_column(Float, default=0.0)
    layout_score: Mapped[float] = mapped_column(Float, default=0.0)
    diagram_score: Mapped[float] = mapped_column(Float, default=0.0)
    content_depth_score: Mapped[float] = mapped_column(Float, default=0.0)
    subject_match_score: Mapped[float] = mapped_column(Float, default=0.0)
    final_score: Mapped[float] = mapped_column(Float, default=0.0)
    star_rating: Mapped[float] = mapped_column(Float, default=0.0)
    rating_count: Mapped[int] = mapped_column(Integer, default=0)
    recommendation_score: Mapped[float] = mapped_column(Float, default=0.0)
    extracted_text: Mapped[str] = mapped_column(Text, default="")
    summary: Mapped[str] = mapped_column(Text, default="")
    score_breakdown: Mapped[dict] = mapped_column(JSON, default=dict)
    embedding_path: Mapped[str] = mapped_column(String(500), default="")
    status: Mapped[str] = mapped_column(String(50), default="pending")
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    scored_at: Mapped[datetime] = mapped_column(DateTime, nullable=True)

    def to_dict(self):
        def safe_json(val, default):
            if val is None:
                return default
            if isinstance(val, (dict, list)):
                return val
            try:
                return json.loads(val)
            except Exception:
                return default

        return {
            "id": self.id,
            "filename": self.filename or "",
            "file_path": self.file_path or "",
            "saved_filename": os.path.basename(self.file_path) if self.file_path else "",
            "uploader_name": self.uploader_name or "",
            "subject": self.subject or "",
            "branch": self.branch or "",
            "semester": self.semester or 1,
            "topic_tags": safe_json(self.topic_tags, []),
            "handwriting_score": round(float(self.handwriting_score or 0), 1),
            "layout_score": round(float(self.layout_score or 0), 1),
            "diagram_score": round(float(self.diagram_score or 0), 1),
            "content_depth_score": round(float(self.content_depth_score or 0), 1),
            "subject_match_score": round(float(self.subject_match_score or 0), 1),
            "final_score": round(float(self.final_score or 0), 1),
            "star_rating": round(float(self.star_rating or 0), 1),
            "rating_count": self.rating_count or 0,
            "recommendation_score": round(float(self.recommendation_score or 0), 1),
            "summary": self.summary or "",
            "score_breakdown": safe_json(self.score_breakdown, {}),
            "status": self.status or "pending",
            "created_at": self.created_at.isoformat() if self.created_at else None,
        }