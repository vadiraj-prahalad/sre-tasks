import time

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel

from app.db.tools.evaluate_rag import evaluate
from app.db.tools.generate_chunk_embeddings import generate_chunk_embeddings
from app.db.tools.sync_standardized_articles import sync_standardized_articles
from app.services.draft_knowledge_service import (
    create_article_from_draft,
    delete_draft_answer,
    list_draft_answers,
    update_draft_status,
)
from app.services.knowledge_loader import load_knowledge_to_db
from scripts.refresh_knowledge import main as refresh_jsonl
from app.services.admin_knowledge_service import delete_admin_article_by_id


router = APIRouter(prefix="/admin/drafts", tags=["admin-drafts"])


class ApproveDraftRequest(BaseModel):
    question: str
    answer: str
    category: str


def validate_approved_content(
    question: str,
    answer: str,
    category: str,
) -> tuple[str, str, str]:
    clean_question = question.strip()
    clean_answer = answer.strip()
    clean_category = category.strip()

    if not clean_question:
        raise HTTPException(
            status_code=400,
            detail="Approved question cannot be empty.",
        )

    if not clean_answer:
        raise HTTPException(
            status_code=400,
            detail="Approved answer cannot be empty.",
        )

    if not clean_category:
        raise HTTPException(
            status_code=400,
            detail="Category cannot be empty.",
        )

    bad_markers = [
        "Provider:",
        "URL:",
        "Trust:",
        "ಸಂಗ್ರಹಿಸಿದ ಮೂಲಗಳು",
        "AI ಕನ್ನಡ ಕರಡು ಸಿದ್ಧಪಡಿಸಲು ಸಾಧ್ಯವಾಗಲಿಲ್ಲ",
        "ಈ ಕರಡು ಇನ್ನೂ ಪರಿಶೀಲಿತ ಉತ್ತರವಲ್ಲ",
        "ಮಾನವ ಪರಿಶೀಲನೆಯ ನಂತರ ಮಾತ್ರ ಪ್ರಕಟಿಸಬೇಕು",
    ]

    if any(marker in clean_answer for marker in bad_markers):
        raise HTTPException(
            status_code=400,
            detail=(
                "Approved answer still contains draft evidence. "
                "Please write a clean Kannada answer before approving."
            ),
        )
    return clean_question, clean_answer, clean_category


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
    question, answer, category = validate_approved_content(
        question=payload.question,
        answer=payload.answer,
        category=payload.category,
    )

    publishing_result = update_draft_status(
        draft_id=draft_id,
        status="publishing",
    )

    if publishing_result["status"] != "updated":
        raise HTTPException(
            status_code=404,
            detail="Draft not found.",
        )

    article_id = None

    try:
        article_result = create_article_from_draft(
            draft_id=draft_id,
            approved_question=question,
            approved_answer=answer,
            category=category,
        )

        if (
            article_result["status"]
            == "editorial_validation_failed"
        ):
            update_draft_status(
                draft_id=draft_id,
                status="draft",
            )

            raise HTTPException(
                status_code=422,
                detail={
                    "message": (
                        "The edited article failed "
                        "editorial validation."
                    ),
                    "validation": (
                        article_result[
                            "validation"
                        ]
                    ),
                },
            )

        if article_result["status"] != "article_created":
            update_draft_status(
                draft_id=draft_id,
                status="publish_failed",
            )

            raise HTTPException(
                status_code=409,
                detail=(
                    "Draft could not enter the publishing pipeline. "
                    f"Current status: "
                    f"{article_result.get('draft_status')}"
                ),
            )

        article = article_result.get("article") or {}
        article_id = article.get("id")

        if not article_id:
            raise RuntimeError(
                "Article was created without a stable article ID."
            )

        publish_result = publish_knowledge_after_approval()

        approval_result = update_draft_status(
            draft_id=draft_id,
            status="approved",
        )

        if approval_result["status"] != "updated":
            raise RuntimeError(
                "Knowledge was published, but the draft status "
                "could not be changed to approved."
            )

        return {
            "status": "approved",
            "draft_id": draft_id,
            "question": question,
            "category": category,
            "article": article,
            "publish": publish_result,
        }

    except HTTPException:
        raise

    except Exception as error:
        if article_id:
            delete_admin_article_by_id(article_id)

        update_draft_status(
            draft_id=draft_id,
            status="publish_failed",
        )

        raise HTTPException(
            status_code=500,
            detail=(
                "Publishing failed and the provisional article "
                f"was rolled back: {error}"
            ),
        ) from error