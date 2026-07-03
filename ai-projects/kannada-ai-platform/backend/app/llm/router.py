from app.services.alias_service import resolve_alias
from app.services.knowledge_service import find_known_answer, find_known_answer_by_key
from app.services.query_normalizer import normalize_question
from app.services.rag_service import answer_from_rag, answer_from_rag_with_trace


FALLBACK_ANSWER = "ಈ ವಿಷಯದ ವಿಶ್ವಾಸಾರ್ಹ ಮಾಹಿತಿಯನ್ನು ಇನ್ನೂ ಸೇರಿಸಲಾಗಿಲ್ಲ. ದಯವಿಟ್ಟು ನಂತರ ಮತ್ತೆ ಪ್ರಯತ್ನಿಸಿ."


def route_llm(prompt: str) -> str:
    result = route_llm_with_trace(prompt)
    return result["answer"]


def route_llm_with_trace(prompt: str) -> dict:
    trace = []

    trace.append({
        "step": "Router",
        "status": "started",
        "details": "Routing question.",
    })

    alias_key = resolve_alias(prompt)

    if alias_key:
        alias_answer = find_known_answer_by_key(alias_key)

        if alias_answer:
            trace.append({
                "step": "Alias Resolver",
                "status": "matched",
                "details": f"Alias matched: {alias_key}",
            })
            return {
                "answer": alias_answer,
                "trace": trace,
            }

    normalized_question = normalize_question(prompt)

    trace.append({
        "step": "Query Normalizer",
        "status": "completed",
        "details": f"Normalized question: {normalized_question}",
    })

    known_answer = find_known_answer(normalized_question)

    if known_answer:
        trace.append({
            "step": "Known Answer",
            "status": "matched",
            "details": "Answer found in trusted known-answer store.",
        })
        return {
            "answer": known_answer,
            "trace": trace,
        }

    rag_result = answer_from_rag_with_trace(prompt)
    trace.extend(rag_result["trace"])

    if rag_result["answer"]:
        trace.append({
            "step": "Final Route",
            "status": "rag",
            "details": "Answer returned from RAG pipeline.",
        })
        return {
            "answer": rag_result["answer"],
            "trace": trace,
        }

    trace.append({
        "step": "Fallback",
        "status": "used",
        "details": "No trusted source found.",
    })

    return {
        "answer": FALLBACK_ANSWER,
        "trace": trace,
    }