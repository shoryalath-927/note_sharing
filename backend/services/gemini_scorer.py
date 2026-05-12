"""
Gemini Vision API scorer.
Sends PDF pages as images to Gemini and gets handwriting/layout/diagram scores.
Uses google-generativeai or direct REST API.
"""
import httpx
import base64
import json
import fitz  # PyMuPDF - to render pages as images
from pathlib import Path
from backend.config import settings

GEMINI_API_URL = "https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-flash:generateContent"

SCORING_PROMPT = """
You are an expert academic note evaluator. Analyze these handwritten notes and score them strictly on:

1. HANDWRITING (0-10): Clarity, neatness, readability, consistent size/spacing
2. PAGE_LAYOUT (0-10): Organization, use of headings, spacing, margins, logical flow  
3. DIAGRAMS (0-10): Quality of labeled drawings, figures, graphs. Score 5 if no diagrams present.

Look at all provided pages and give AVERAGE scores across pages.

Respond ONLY in this exact JSON format (no markdown, no explanation):
{
  "handwriting_score": 7.5,
  "layout_score": 8.0,
  "diagram_score": 6.0,
  "handwriting_notes": "One line observation",
  "layout_notes": "One line observation",
  "diagram_notes": "One line observation"
}
"""


def pdf_to_base64_images(pdf_path: str, max_pages: int = 4) -> list[dict]:
    """Convert first N pages of PDF to base64 JPEG images for Gemini."""
    doc = fitz.open(pdf_path)
    images = []
    
    pages_to_scan = min(max_pages, len(doc))
    for page_num in range(pages_to_scan):
        page = doc[page_num]
        # Render at 150 DPI (good quality, reasonable size)
        mat = fitz.Matrix(150 / 72, 150 / 72)
        pix = page.get_pixmap(matrix=mat)
        img_bytes = pix.tobytes("jpeg")
        b64 = base64.b64encode(img_bytes).decode("utf-8")
        images.append({
            "inlineData": {
                "mimeType": "image/jpeg",
                "data": b64
            }
        })
    
    doc.close()
    return images


async def score_with_gemini(pdf_path: str) -> dict:
    """
    Score handwriting, layout, and diagrams using Gemini Vision.
    Falls back to default scores if API fails.
    """
    if not settings.gemini_api_key:
        return _default_scores("No Gemini API key configured")

    try:
        images = pdf_to_base64_images(pdf_path, max_pages=4)
        if not images:
            return _default_scores("Could not render PDF pages")

        # Build Gemini request
        parts = [{"text": SCORING_PROMPT}] + images

        payload = {
            "contents": [{"parts": parts}],
            "generationConfig": {
                "temperature": 0.1,
                "maxOutputTokens": 300,
            }
        }

        async with httpx.AsyncClient(timeout=60.0) as client:
            response = await client.post(
                f"{GEMINI_API_URL}?key={settings.gemini_api_key}",
                json=payload,
                headers={"Content-Type": "application/json"}
            )
            response.raise_for_status()
            data = response.json()

        # Parse response
        text = data["candidates"][0]["content"]["parts"][0]["text"]
        # Strip markdown fences if present
        text = text.strip().strip("```json").strip("```").strip()
        scores = json.loads(text)

        return {
            "handwriting_score": float(scores.get("handwriting_score", 5.0)),
            "layout_score": float(scores.get("layout_score", 5.0)),
            "diagram_score": float(scores.get("diagram_score", 5.0)),
            "handwriting_notes": scores.get("handwriting_notes", ""),
            "layout_notes": scores.get("layout_notes", ""),
            "diagram_notes": scores.get("diagram_notes", ""),
            "source": "gemini",
        }

    except httpx.HTTPStatusError as e:
        if e.response.status_code == 429:
            return _default_scores("Gemini rate limit hit — using defaults")
        return _default_scores(f"Gemini HTTP error: {e.response.status_code}")
    except json.JSONDecodeError:
        return _default_scores("Could not parse Gemini response")
    except Exception as e:
        return _default_scores(f"Gemini error: {str(e)}")


def _default_scores(reason: str = "") -> dict:
    return {
        "handwriting_score": 5.0,
        "layout_score": 5.0,
        "diagram_score": 5.0,
        "handwriting_notes": "Default score",
        "layout_notes": "Default score",
        "diagram_notes": "Default score",
        "source": "default",
        "reason": reason,
    }
