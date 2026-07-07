from fastapi import APIRouter

from app.services.feedback_service import save_feedback


router = APIRouter()


@router.post("/feedback")
def submit_feedback(payload: dict):
    question = payload.get("question", "")
    answer = payload.get("answer", "")
    rating = payload.get("rating", "")
    confidence_score = payload.get("confidence_score")
    source = payload.get("source")

    if rating not in ["positive", "negative"]:
        return {
            "status": "error",
            "message": "Invalid rating",
        }

    result = save_feedback(
        question=question,
        answer=answer,
        rating=rating,
        confidence_score=confidence_score,
        source=source,
    )

    return result
