"""
HuggingFace sentence-transformers embeddings.
Used for semantic search — find notes by meaning, not just keyword.
Embeddings are stored as .npy files locally.
"""
import numpy as np
import os
from pathlib import Path
from backend.config import settings

# We use sentence-transformers locally (free, runs on CPU)
# Model: all-MiniLM-L6-v2 — small, fast, good quality
_model = None


def get_model():
    """Lazy-load the embedding model (downloads ~90MB on first run)."""
    global _model
    if _model is None:
        try:
            from sentence_transformers import SentenceTransformer
            _model = SentenceTransformer("all-MiniLM-L6-v2")
            print("✅ Embedding model loaded: all-MiniLM-L6-v2")
        except ImportError:
            print("⚠️  sentence-transformers not installed. Run: pip install sentence-transformers")
            _model = None
    return _model


def generate_embedding(text: str) -> np.ndarray | None:
    """Generate a 384-dim embedding vector for the given text."""
    model = get_model()
    if model is None or not text.strip():
        return None
    
    # Use first 512 words for embedding (model limit)
    text_sample = " ".join(text.split()[:512])
    embedding = model.encode(text_sample, normalize_embeddings=True)
    return embedding


def save_embedding(note_id: int, embedding: np.ndarray) -> str:
    """Save embedding to disk, return path."""
    path = Path(settings.embeddings_dir) / f"note_{note_id}.npy"
    np.save(str(path), embedding)
    return str(path)


def load_embedding(embedding_path: str) -> np.ndarray | None:
    """Load embedding from disk."""
    try:
        return np.load(embedding_path)
    except Exception:
        return None


def cosine_similarity(a: np.ndarray, b: np.ndarray) -> float:
    """Compute cosine similarity between two vectors."""
    if a is None or b is None:
        return 0.0
    norm_a = np.linalg.norm(a)
    norm_b = np.linalg.norm(b)
    if norm_a == 0 or norm_b == 0:
        return 0.0
    return float(np.dot(a, b) / (norm_a * norm_b))


def search_similar_notes(
    query_text: str,
    note_embedding_paths: list[tuple[int, str]],
    top_k: int = 10
) -> list[tuple[int, float]]:
    """
    Find most similar notes to a query using cosine similarity.
    
    Args:
        query_text: Search query string
        note_embedding_paths: List of (note_id, embedding_path) tuples
        top_k: Number of results to return
    
    Returns:
        List of (note_id, similarity_score) sorted by similarity desc
    """
    query_embedding = generate_embedding(query_text)
    if query_embedding is None:
        return []

    results = []
    for note_id, path in note_embedding_paths:
        if not path or not os.path.exists(path):
            continue
        note_embedding = load_embedding(path)
        if note_embedding is None:
            continue
        sim = cosine_similarity(query_embedding, note_embedding)
        results.append((note_id, sim))

    # Sort by similarity descending
    results.sort(key=lambda x: x[1], reverse=True)
    return results[:top_k]
