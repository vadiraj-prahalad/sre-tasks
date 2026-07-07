from fastapi import APIRouter

from app.services.admin_knowledge_service import (
    add_admin_article,
    delete_admin_article,
    get_admin_dashboard,
    list_admin_articles,
)

router = APIRouter(prefix="/admin")


@router.get("/knowledge")
def get_admin_knowledge():
    return {
        "articles": list_admin_articles(),
    }


@router.get("/knowledge/dashboard")
def get_knowledge_dashboard():
    return get_admin_dashboard()


@router.post("/knowledge")
def create_admin_knowledge(payload: dict):
    question = payload.get("question", "")
    answer = payload.get("answer", "")
    category = payload.get("category", "general")
    source = payload.get("source", "admin_cms")
    language = payload.get("language", "kn")

    if not question.strip() or not answer.strip():
        return {
            "status": "error",
            "message": "Question and answer are required.",
        }

    return add_admin_article(
        question=question,
        answer=answer,
        category=category,
        source=source,
        language=language,
    )


@router.delete("/knowledge/{index}")
def remove_admin_knowledge(index: int):
    return delete_admin_article(index)
