from fastapi import APIRouter, HTTPException
from pydantic import BaseModel

from app.services.draft_knowledge_service import (
    approve_draft_answer,
    delete_draft_answer,
    list_draft_answers,
)

router = APIRouter(prefix="/admin/drafts", tags=["admin-drafts"])


class ApproveDraftRequest(BaseModel):
    question: str
    answer: str
    category: str


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
    result = approve_draft_answer(
        draft_id=draft_id,
        approved_question=payload.question,
        approved_answer=payload.answer,
        category=payload.category,
    )

    if result["status"] != "approved":
        raise HTTPException(status_code=404, detail="Draft not found or already approved")

    return result
