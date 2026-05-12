"""
Recommendation engine.
Combines AI scores + peer ratings into a final recommendation score.
Also calculates the weighted score from individual AI components.
"""
from datetime import datetime


# Scoring weights for the AI components
WEIGHTS = {
    "handwriting": 0.35,   # 35% — readability is critical
    "content": 0.45,       # 45% — content is most important
    "layout": 0.20,        # 20% — presentation matters
}

# Recommendation score: AI score 70% + peer rating 30%
RECOMMENDATION_WEIGHTS = {
    "ai_score": 0.70,
    "peer_rating": 0.30,
}


def calculate_weighted_score(
    handwriting_score: float,   # 0-10
    layout_score: float,        # 0-10
    diagram_score: float,       # 0-10
    content_depth_score: float, # 0-10
    subject_match_score: float, # 0-10
) -> dict:
    """
    Calculate the final weighted AI score (0-100).
    
    Handwriting component = avg(handwriting, layout) * 35%
    Content component = avg(content_depth, subject_match) * 45%  
    Layout component = avg(layout, diagram) * 20%
    """
    handwriting_component = handwriting_score  # pure handwriting
    content_component = (content_depth_score + subject_match_score) / 2
    layout_component = (layout_score + diagram_score) / 2

    # Each component is 0-10, multiply by 10 to get 0-100 range
    final_score = (
        handwriting_component * WEIGHTS["handwriting"] +
        content_component * WEIGHTS["content"] +
        layout_component * WEIGHTS["layout"]
    ) * 10  # Scale to 0-100

    return {
        "final_score": round(min(final_score, 100.0), 1),
        "breakdown": {
            "handwriting_component": round(handwriting_component * 10, 1),
            "content_component": round(content_component * 10, 1),
            "layout_component": round(layout_component * 10, 1),
            "handwriting_weight": f"{int(WEIGHTS['handwriting'] * 100)}%",
            "content_weight": f"{int(WEIGHTS['content'] * 100)}%",
            "layout_weight": f"{int(WEIGHTS['layout'] * 100)}%",
        }
    }


def calculate_recommendation_score(
    final_ai_score: float,    # 0-100
    star_rating: float,       # 0-5
    rating_count: int,        # Number of ratings
) -> float:
    """
    Combine AI score with peer ratings.
    
    If no ratings yet: pure AI score.
    If few ratings (< 5): mostly AI, small peer influence.
    If many ratings (>= 5): 70% AI + 30% peer.
    
    Peer rating is normalized from 0-5 to 0-100.
    """
    peer_score_normalized = (star_rating / 5.0) * 100

    if rating_count == 0:
        # No ratings: pure AI
        return round(final_ai_score, 1)
    elif rating_count < 5:
        # Few ratings: blend gradually
        peer_weight = (rating_count / 5.0) * RECOMMENDATION_WEIGHTS["peer_rating"]
        ai_weight = 1.0 - peer_weight
        score = ai_weight * final_ai_score + peer_weight * peer_score_normalized
    else:
        # Enough ratings: full blend
        score = (
            RECOMMENDATION_WEIGHTS["ai_score"] * final_ai_score +
            RECOMMENDATION_WEIGHTS["peer_rating"] * peer_score_normalized
        )

    return round(min(score, 100.0), 1)


def get_quality_badge(score: float) -> str:
    """Return a badge label based on score."""
    if score >= 85:
        return "Top Pick"
    elif score >= 70:
        return "Highly Rated"
    elif score >= 55:
        return "Good"
    elif score >= 40:
        return "Average"
    else:
        return "Needs Review"


def rank_notes_for_subject(notes: list[dict]) -> list[dict]:
    """
    Rank notes for a subject by recommendation_score.
    Adds rank, badge, and percentile fields.
    Returns sorted list.
    """
    sorted_notes = sorted(
        notes,
        key=lambda n: n.get("recommendation_score", 0),
        reverse=True
    )

    total = len(sorted_notes)
    for i, note in enumerate(sorted_notes):
        note["rank"] = i + 1
        note["badge"] = get_quality_badge(note.get("recommendation_score", 0))
        note["percentile"] = round(((total - i) / total) * 100) if total > 0 else 0

    return sorted_notes
