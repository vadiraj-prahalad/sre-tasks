import time

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel

from app.db.tools.evaluate_rag import evaluate
from app.db.tools.generate_chunk_embeddings import generate_chunk_embeddings
from app.db.tools.sync_standardized_articles import sync_standardized_articles
from app.services.draft_knowledge_service import (
    approve_draft_answer,
    delete_draft_answer,
    list_draft_answers,
)
from app.services.knowledge_loader import load_knowledge_to_db
from scripts.refresh_knowledge import main as refresh_jsonl


router = APIRouter(prefix="/admin/drafts", tags=["admin-drafts"])


class ApproveDraftRequest(BaseModel):
    question: str
    answer: str
    category: str


def validate_approved_answer(answer: str) -> None:
    bad_markers = [
        "Provider:",
        "URL:",
        "Trust:",
        "ಸಂಗ್ರಹಿಸಿದ ಮೂಲಗಳು",
        "AI ಕನ್ನಡ ಕರಡು ಸಿದ್ಧಪಡಿಸಲು ಸಾಧ್ಯವಾಗಲಿಲ್ಲ",
        "ಈ ಕರಡು ಇನ್ನೂ ಪರಿಶೀಲಿತ ಉತ್ತರವಲ್ಲ",
        "ಮಾನವ ಪರಿಶೀಲನೆಯ ನಂತರ ಮಾತ್ರ ಪ್ರಕಟಿಸಬೇಕು",
    ]

    if any(marker in answer for marker in bad_markers):
        raise HTTPException(
            status_code=400,
            detail=(
                "Approved answer still contains draft evidence. "
                "Please write a clean Kannada answer before approving."
            ),
        )


def publish_knowledge_after_approval() -> dict:
    start_time = time.time()

    refresh_jsonl()
    load_result = load_knowledge_to_db()
    sync_result = sync_standardized_articles()
    generate_chunk_embeddings()
    evaluation_result = evaluate()

    return {
        "status": "published",
        "records_loaded": load_result["records_loaded"],
        "articles_synced": sync_result["articles_synced"],
        "evaluation": {
            "passed": evaluation_result["passed"],
            "failed": evaluation_result["failed"],
            "success": evaluation_result["success"],
        },
        "duration_seconds": round(time.time() - start_time, 2),
    }


@router.get("")
def get_drafts():
    return {
        "drafts": list_draft_answers()
    }


@router.delete("/{draft_id}")
def delete_draft(draft_id: int):
    result = delete_draft_answer(draft_id)

    if result["status"] != "deleted":
        raise HTTPException(status_code=404, detail="Draft not found")

    return result


@router.post("/{draft_id}/approve")
def approve_draft(draft_id: int, payload: ApproveDraftRequest):
    validate_approved_answer(payload.answer)

    result = approve_draft_answer(
        draft_id=draft_id,
        approved_question=payload.question,
        approved_answer=payload.answer,
        category=payload.category,
    )

    if result["status"] != "approved":
        raise HTTPException(status_code=404, detail="Draft not found or already approved")

    publish_result = publish_knowledge_after_approval()

    return {
        **result,
        "publish": publish_result,
    }