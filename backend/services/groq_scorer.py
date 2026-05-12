"""
Groq API scorer using Llama 3.3 70B.
Scores content depth, syllabus match, auto-tags subjects, generates summary.
300+ tokens/sec — very fast for text-based scoring.
"""
import httpx
import json
from backend.config import settings

GROQ_API_URL = "https://api.groq.com/openai/v1/chat/completions"

BTECH_SUBJECTS = [
    "Mathematics", "Computer Science", "Electronics", "Electrical Engineering",
    "Mechanical Engineering", "Civil Engineering", "Physics", "Chemistry",
    "Data Structures", "Algorithms", "Operating Systems", "Database Management",
    "Computer Networks", "Software Engineering", "Machine Learning",
    "Digital Electronics", "Signals and Systems", "Control Systems",
    "Thermodynamics", "Fluid Mechanics", "Engineering Drawing"
]

CONTENT_SCORING_PROMPT = """You are an academic note quality evaluator for BTech students.

Analyze the following extracted text from handwritten notes and respond ONLY in JSON format.

Notes text:
{text}

Declared subject by student: {declared_subject}

Evaluate and return this exact JSON (no markdown, no extra text):
{{
  "content_depth_score": 7.5,
  "subject_match_score": 8.0,
  "detected_subject": "Computer Science",
  "topic_tags": ["Data Structures", "Binary Trees", "Graph Algorithms"],
  "summary": "2-3 sentence summary of what these notes cover",
  "content_notes": "Brief observation about content quality",
  "subject_notes": "Brief observation about syllabus relevance"
}}

Scoring criteria:
- content_depth_score (0-10): Coverage depth, formulas present, examples, definitions, completeness
- subject_match_score (0-10): How well content matches declared subject and BTech syllabus
- detected_subject: Best matching subject from: {subjects}
- topic_tags: 3-5 specific topics covered (e.g. "Dijkstra's Algorithm", "Merge Sort")
- summary: 2-3 sentences describing the notes content
"""


async def score_with_groq(
    extracted_text: str,
    declared_subject: str,
) -> dict:
    """
    Score content depth and subject match using Groq's fast Llama model.
    """
    if not settings.groq_api_key:
        return _default_scores("No Groq API key configured")

    if not extracted_text or len(extracted_text.strip()) < 50:
        return _default_scores("Insufficient text extracted from PDF")

    # Limit text to avoid token limits (use first 3000 chars)
    text_sample = extracted_text[:3000]

    prompt = CONTENT_SCORING_PROMPT.format(
        text=text_sample,
        declared_subject=declared_subject,
        subjects=", ".join(BTECH_SUBJECTS)
    )

    try:
        async with httpx.AsyncClient(timeout=30.0) as client:
            response = await client.post(
                GROQ_API_URL,
                json={
                    "model": "llama-3.3-70b-versatile",
                    "messages": [
                        {
                            "role": "system",
                            "content": "You are a strict academic note evaluator. Always respond only in valid JSON."
                        },
                        {"role": "user", "content": prompt}
                    ],
                    "temperature": 0.1,
                    "max_tokens": 500,
                },
                headers={
                    "Authorization": f"Bearer {settings.groq_api_key}",
                    "Content-Type": "application/json"
                }
            )
            response.raise_for_status()
            data = response.json()

        raw = data["choices"][0]["message"]["content"]
        # Strip markdown fences
        raw = raw.strip().strip("```json").strip("```").strip()
        scores = json.loads(raw)

        return {
            "content_depth_score": float(scores.get("content_depth_score", 5.0)),
            "subject_match_score": float(scores.get("subject_match_score", 5.0)),
            "detected_subject": scores.get("detected_subject", declared_subject),
            "topic_tags": scores.get("topic_tags", [])[:5],
            "summary": scores.get("summary", ""),
            "content_notes": scores.get("content_notes", ""),
            "subject_notes": scores.get("subject_notes", ""),
            "source": "groq",
        }

    except httpx.HTTPStatusError as e:
        if e.response.status_code == 429:
            # Try OpenRouter as fallback
            return await _fallback_openrouter(prompt)
        return _default_scores(f"Groq HTTP error: {e.response.status_code}")
    except json.JSONDecodeError:
        return _default_scores("Could not parse Groq response as JSON")
    except Exception as e:
        return _default_scores(f"Groq error: {str(e)}")


async def _fallback_openrouter(prompt: str) -> dict:
    """Fallback to OpenRouter free models when Groq rate limits."""
    if not settings.openrouter_api_key:
        return _default_scores("Groq rate limited, no OpenRouter fallback key")

    try:
        async with httpx.AsyncClient(timeout=45.0) as client:
            response = await client.post(
                "https://openrouter.ai/api/v1/chat/completions",
                json={
                    "model": "deepseek/deepseek-r1:free",
                    "messages": [
                        {"role": "system", "content": "Respond only in valid JSON."},
                        {"role": "user", "content": prompt}
                    ],
                    "temperature": 0.1,
                    "max_tokens": 500,
                },
                headers={
                    "Authorization": f"Bearer {settings.openrouter_api_key}",
                    "Content-Type": "application/json",
                    "HTTP-Referer": "https://noteshare.app",
                }
            )
            response.raise_for_status()
            data = response.json()
            raw = data["choices"][0]["message"]["content"].strip()
            raw = raw.strip("```json").strip("```").strip()
            scores = json.loads(raw)

            return {
                "content_depth_score": float(scores.get("content_depth_score", 5.0)),
                "subject_match_score": float(scores.get("subject_match_score", 5.0)),
                "detected_subject": scores.get("detected_subject", ""),
                "topic_tags": scores.get("topic_tags", [])[:5],
                "summary": scores.get("summary", ""),
                "content_notes": scores.get("content_notes", ""),
                "subject_notes": scores.get("subject_notes", ""),
                "source": "openrouter_fallback",
            }
    except Exception as e:
        return _default_scores(f"OpenRouter fallback also failed: {str(e)}")


def _default_scores(reason: str = "") -> dict:
    return {
        "content_depth_score": 5.0,
        "subject_match_score": 5.0,
        "detected_subject": "",
        "topic_tags": [],
        "summary": "",
        "content_notes": "Default score",
        "subject_notes": "Default score",
        "source": "default",
        "reason": reason,
    }
