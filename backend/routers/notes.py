"""
Notes API router.
POST /notes/upload     - Upload a PDF and trigger scoring
GET  /notes/           - List all notes (filter by subject/semester)
GET  /notes/{id}       - Get single note with full details
POST /notes/{id}/rate  - Submit a star rating
GET  /notes/subjects   - Get list of subjects with note counts
"""
import os
import asyncio
from datetime import datetime
from pathlib import Path
from typing import Optional

from fastapi import APIRouter, UploadFile, File, Form, HTTPException, Depends, BackgroundTasks
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func

from backend.database import get_db
from backend.models.note import Note
from backend.config import settings
from backend.services.pdf_extractor import extract_text_from_pdf
from backend.services.gemini_scorer import score_with_gemini
from backend.services.groq_scorer import score_with_groq
from backend.services.embedder import generate_embedding, save_embedding
from backend.services.recommender import (
    calculate_weighted_score,
    calculate_recommendation_score,
    rank_notes_for_subject,
)

router = APIRouter(prefix="/notes", tags=["notes"])


@router.post("/upload")
async def upload_note(
    background_tasks: BackgroundTasks,
    file: UploadFile = File(...),
    uploader_name: str = Form(...),
    subject: str = Form(...),
    semester: int = Form(...),
    branch: str = Form(default="BTech"),
    db: AsyncSession = Depends(get_db),
):
    """Upload a PDF note. Scoring happens in the background."""
    
    # Validate file type
    if not file.filename.lower().endswith(".pdf"):
        raise HTTPException(status_code=400, detail="Only PDF files are accepted")

    # Check file size
    content = await file.read()
    size_mb = len(content) / (1024 * 1024)
    if size_mb > settings.max_file_size_mb:
        raise HTTPException(
            status_code=400,
            detail=f"File too large. Max size: {settings.max_file_size_mb}MB"
        )

    # Save file to disk
    upload_dir = Path(settings.upload_dir)
    safe_filename = f"{datetime.utcnow().strftime('%Y%m%d_%H%M%S')}_{file.filename}"
    file_path = upload_dir / safe_filename
    
    with open(file_path, "wb") as f:
        f.write(content)

    # Create DB record with pending status
    note = Note(
        filename=file.filename,
        file_path=str(file_path),
        uploader_name=uploader_name,
        subject=subject,
        semester=semester,
        branch=branch,
        status="pending",
    )
    db.add(note)
    await db.commit()
    await db.refresh(note)

    # Trigger background scoring
    background_tasks.add_task(score_note_background, note.id, str(file_path), subject)

    return {
        "message": "Note uploaded successfully. Scoring in progress...",
        "note_id": note.id,
        "status": "pending",
    }


async def score_note_background(note_id: int, file_path: str, declared_subject: str):
    """Background task to score a note using all AI services."""
    from backend.database import AsyncSessionLocal
    
    async with AsyncSessionLocal() as db:
        # Fetch the note
        note = await db.get(Note, note_id)
        if not note:
            return

        try:
            note.status = "scoring"
            await db.commit()

            # Step 1: Extract text (local, fast)
            extraction = extract_text_from_pdf(file_path)
            note.extracted_text = extraction["text"]

            # Step 2: Score with Gemini (vision — handwriting, layout, diagrams)
            gemini_result = await score_with_gemini(file_path)
            note.handwriting_score = gemini_result["handwriting_score"]
            note.layout_score = gemini_result["layout_score"]
            note.diagram_score = gemini_result["diagram_score"]

            # Step 3: Score with Groq (content — depth, syllabus match, tags, summary)
            groq_result = await score_with_groq(
                extraction["text"],
                declared_subject
            )
            note.content_depth_score = groq_result["content_depth_score"]
            note.subject_match_score = groq_result["subject_match_score"]
            note.topic_tags = groq_result["topic_tags"]
            note.summary = groq_result["summary"]
            
            # Update detected subject if different from declared
            if groq_result["detected_subject"]:
                note.subject = groq_result["detected_subject"]

            # Step 4: Calculate weighted final score
            score_result = calculate_weighted_score(
                handwriting_score=note.handwriting_score,
                layout_score=note.layout_score,
                diagram_score=note.diagram_score,
                content_depth_score=note.content_depth_score,
                subject_match_score=note.subject_match_score,
            )
            note.final_score = score_result["final_score"]
            note.score_breakdown = {
                **score_result["breakdown"],
                "gemini_notes": {
                    "handwriting": gemini_result.get("handwriting_notes", ""),
                    "layout": gemini_result.get("layout_notes", ""),
                    "diagrams": gemini_result.get("diagram_notes", ""),
                },
                "groq_notes": {
                    "content": groq_result.get("content_notes", ""),
                    "subject": groq_result.get("subject_notes", ""),
                },
                "sources": {
                    "vision": gemini_result.get("source", ""),
                    "content": groq_result.get("source", ""),
                }
            }

            # Step 5: Calculate recommendation score (AI-only, no peer ratings yet)
            note.recommendation_score = calculate_recommendation_score(
                note.final_score, note.star_rating, note.rating_count
            )

            # Step 6: Generate embedding for semantic search
            if extraction["text"].strip():
                embedding_text = f"{note.subject} {note.summary} {' '.join(note.topic_tags)} {extraction['text'][:500]}"
                embedding = generate_embedding(embedding_text)
                if embedding is not None:
                    emb_path = save_embedding(note.id, embedding)
                    note.embedding_path = emb_path

            note.status = "scored"
            note.scored_at = datetime.utcnow()
            await db.commit()
            print(f"✅ Note {note_id} scored successfully. Final: {note.final_score}")

        except Exception as e:
            note.status = "failed"
            await db.commit()
            print(f"❌ Failed to score note {note_id}: {e}")
            raise


@router.get("/")
async def list_notes(
    subject: Optional[str] = None,
    semester: Optional[int] = None,
    branch: Optional[str] = None,
    limit: int = 20,
    offset: int = 0,
    db: AsyncSession = Depends(get_db),
):
    """List notes with optional filters. Returns ranked by recommendation_score."""
    stmt = select(Note).where(Note.status == "scored")
    
    if subject:
        stmt = stmt.where(Note.subject.ilike(f"%{subject}%"))
    if semester:
        stmt = stmt.where(Note.semester == semester)
    if branch:
        stmt = stmt.where(Note.branch.ilike(f"%{branch}%"))

    stmt = stmt.order_by(Note.recommendation_score.desc()).limit(limit).offset(offset)
    
    result = await db.execute(stmt)
    notes = result.scalars().all()
    
    notes_data = [n.to_dict() for n in notes]
    return {"notes": rank_notes_for_subject(notes_data), "total": len(notes_data)}


@router.get("/subjects")
async def get_subjects(db: AsyncSession = Depends(get_db)):
    """Get all subjects with note counts and top scores."""
    stmt = select(
        Note.subject,
        func.count(Note.id).label("count"),
        func.max(Note.recommendation_score).label("top_score"),
        func.avg(Note.recommendation_score).label("avg_score"),
    ).where(Note.status == "scored").group_by(Note.subject).order_by(func.count(Note.id).desc())

    result = await db.execute(stmt)
    rows = result.all()

    return {
        "subjects": [
            {
                "subject": row.subject,
                "note_count": row.count,
                "top_score": round(row.top_score or 0, 1),
                "avg_score": round(row.avg_score or 0, 1),
            }
            for row in rows
        ]
    }


@router.get("/{note_id}")
async def get_note(note_id: int, db: AsyncSession = Depends(get_db)):
    try:
        note = await db.get(Note, note_id)
        if not note:
            raise HTTPException(status_code=404, detail="Note not found")
        return note.to_dict()
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/{note_id}/rate")
async def rate_note(
    note_id: int,
    stars: float,
    db: AsyncSession = Depends(get_db),
):
    """Submit a 1-5 star rating for a note."""
    if not 1 <= stars <= 5:
        raise HTTPException(status_code=400, detail="Rating must be between 1 and 5")

    note = await db.get(Note, note_id)
    if not note:
        raise HTTPException(status_code=404, detail="Note not found")

    # Weighted average update
    total_stars = note.star_rating * note.rating_count + stars
    note.rating_count += 1
    note.star_rating = total_stars / note.rating_count

    # Recalculate recommendation score with new peer rating
    note.recommendation_score = calculate_recommendation_score(
        note.final_score, note.star_rating, note.rating_count
    )
    
    await db.commit()
    return {
        "message": "Rating submitted",
        "new_rating": round(note.star_rating, 1),
        "rating_count": note.rating_count,
        "recommendation_score": note.recommendation_score,
    }

@router.post("/rescore-all")
async def rescore_all(background_tasks: BackgroundTasks, db: AsyncSession = Depends(get_db)):
    """Re-trigger scoring for all notes that have default scores."""
    stmt = select(Note).where(Note.status == "scored")
    result = await db.execute(stmt)
    notes = result.scalars().all()
    count = 0
    for note in notes:
        if note.final_score <= 50.0:  # default score = was never properly scored
            note.status = "pending"
            background_tasks.add_task(score_note_background, note.id, note.file_path, note.subject)
            count += 1
    await db.commit()
    return {"message": f"Re-scoring {count} notes"}