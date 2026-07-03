from fastapi import APIRouter

from app.llm.router import route_llm


router = APIRouter()


@router.post("/ask")
def ask_question(payload: dict):
    question = payload.get("question", "")
    debug = payload.get("debug", False)

    response = route_llm(question)

    result = {
        "question": question,
        "answer": response,
    }

    if debug:
        result["trace"] = [
            {
                "step": "POST /ask",
                "status": "received",
                "details": f"Question received: {question}",
            },
            {
                "step": "Router",
                "status": "completed",
                "details": "Question routed through LLM router.",
            },
            {
                "step": "RAG / LLM",
                "status": "completed",
                "details": "Answer generated from configured route.",
            },
            {
                "step": "Response",
                "status": "completed",
                "details": "Answer returned to frontend.",
            },
        ]

    return result