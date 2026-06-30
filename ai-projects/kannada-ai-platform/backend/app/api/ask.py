from fastapi import APIRouter
from app.llm.router import route_llm
router = APIRouter()

@router.post("/ask")
def ask_question(payload: dict):
    question = payload.get("question", "")

    response = route_llm(question)

    return {
        "question": question,
        "answer": response
    }
