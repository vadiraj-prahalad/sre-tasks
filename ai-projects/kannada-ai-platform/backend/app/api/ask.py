from fastapi import APIRouter

from app.llm.router import route_llm, route_llm_with_trace


router = APIRouter()


@router.post("/ask")
def ask_question(payload: dict):
    question = payload.get("question", "")
    debug = payload.get("debug", False)

    if debug:
        result = route_llm_with_trace(question)

        return {
            "question": question,
            "answer": result["answer"],
            "confidence": result.get("confidence"),
            "trace": [
                {
                    "step": "POST /ask",
                    "status": "received",
                    "details": f"Question received: {question}",
                },
                *result["trace"],
                {
                    "step": "Response",
                    "status": "completed",
                    "details": "Answer returned to frontend.",
                },
            ],
        }

    response = route_llm(question)

    return {
        "question": question,
        "answer": response,
    }