from fastapi import APIRouter

from app.llm.router import route_llm_with_trace
from app.services.conversation_memory_service import (
    enrich_question_with_memory,
    save_assistant_message,
)

router = APIRouter()


@router.post("/ask")
def ask_question(payload: dict):
    question = payload.get("question", "")
    debug = payload.get("debug", False)
    conversation_id = payload.get("conversation_id", "default")

    memory_result = enrich_question_with_memory(
        question=question,
        conversation_id=conversation_id,
    )

    enriched_question = memory_result["question"]
    result = route_llm_with_trace(enriched_question)

    save_assistant_message(
        conversation_id=conversation_id,
        answer=result["answer"],
    )

    base_response = {
        "question": question,
        "enriched_question": enriched_question,
        "conversation_id": conversation_id,
        "memory": {
            "used": memory_result["memory_used"],
            "entity": memory_result.get("entity"),
        },
        "answer": result["answer"],
        "confidence": result.get("confidence"),
        "related_topics": result.get("related_topics", []),
    }

    if debug:
        base_response["trace"] = [
            {
                "step": "POST /ask",
                "status": "received",
                "details": f"Question received: {question}",
            },
            {
                "step": "Conversation Memory",
                "status": "used" if memory_result["memory_used"] else "not_used",
                "details": f"Enriched question: {enriched_question}",
            },
            *result["trace"],
            {
                "step": "Response",
                "status": "completed",
                "details": "Answer returned to frontend.",
            },
        ]

    return base_response