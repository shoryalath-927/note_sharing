"""
Semantic search router.
GET /search?q=binary+trees&subject=Computer+Science
Uses HuggingFace embeddings to find notes by meaning.
"""
from typing import Optional
from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from backend.database import get_db
from backend.models.note import Note
from backend.services.embedder import search_similar_notes

router = APIRouter(prefix="/search", tags=["search"])


@router.get("/")
async def semantic_search(
    q: str = Query(..., min_length=2, description="Search query"),
    subject: Optional[str] = Query(None),
    semester: Optional[int] = Query(None),
    limit: int = Query(10, le=50),
    db: AsyncSession = Depends(get_db),
):
    """
    Search notes by meaning using sentence embeddings.
    Falls back to keyword search if embeddings unavailable.
    """
    # Get all scored notes with embeddings
    stmt = select(Note.id, Note.embedding_path).where(
        Note.status == "scored",
        Note.embedding_path != "",
    )
    if subject:
        stmt = stmt.where(Note.subject.ilike(f"%{subject}%"))
    if semester:
        stmt = stmt.where(Note.semester == semester)

    result = await db.execute(stmt)
    rows = result.all()

    if not rows:
        return {"results": [], "query": q, "method": "no_embeddings"}

    # Semantic search
    embedding_paths = [(row.id, row.embedding_path) for row in rows]
    similar = search_similar_notes(q, embedding_paths, top_k=limit)

    if not similar:
        # Fallback: keyword search in extracted text
        return await _keyword_search(q, subject, semester, limit, db)

    # Fetch full note data for results
    note_ids = [note_id for note_id, _ in similar]
    similarity_map = {note_id: sim for note_id, sim in similar}

    notes_stmt = select(Note).where(Note.id.in_(note_ids))
    notes_result = await db.execute(notes_stmt)
    notes = {n.id: n for n in notes_result.scalars().all()}

    results = []
    for note_id, sim_score in similar:
        if note_id in notes:
            note_data = notes[note_id].to_dict()
            note_data["similarity_score"] = round(sim_score * 100, 1)
            results.append(note_data)

    return {"results": results, "query": q, "method": "semantic"}


async def _keyword_search(
    query: str,
    subject: Optional[str],
    semester: Optional[int],
    limit: int,
    db: AsyncSession,
):
    """Fallback keyword search in extracted text and tags."""
    stmt = select(Note).where(
        Note.status == "scored",
        Note.extracted_text.ilike(f"%{query}%"),
    )
    if subject:
        stmt = stmt.where(Note.subject.ilike(f"%{subject}%"))
    if semester:
        stmt = stmt.where(Note.semester == semester)

    stmt = stmt.order_by(Note.recommendation_score.desc()).limit(limit)
    result = await db.execute(stmt)
    notes = result.scalars().all()

    return {
        "results": [n.to_dict() for n in notes],
        "query": query,
        "method": "keyword_fallback",
    }
