from app.llm.local_llm import get_llm_response
from app.services.alias_service import resolve_alias
from app.services.knowledge_service import find_known_answer, find_known_answer_by_key
from app.services.query_normalizer import normalize_question
from app.services.rag_service import answer_from_rag_with_trace
from app.services.draft_knowledge_service import save_draft_answer


FALLBACK_ANSWER = "ಈ ವಿಷಯದ ಉತ್ತರವನ್ನು ಸಿದ್ಧಪಡಿಸಲು ಸಾಧ್ಯವಾಗಲಿಲ್ಲ. ದಯವಿಟ್ಟು ನಂತರ ಮತ್ತೆ ಪ್ರಯತ್ನಿಸಿ."


def route_llm(prompt: str) -> str:
    result = route_llm_with_trace(prompt)
    return result["answer"]


def build_high_confidence_response(answer: str, trace: list[dict], reason: str) -> dict:
    return {
        "answer": answer,
        "trace": trace,
        "confidence": {
            "score": 95,
            "label": "High",
            "kannada_label": "ಹೆಚ್ಚು ವಿಶ್ವಾಸಾರ್ಹ",
            "reasons": [reason, "Known answer returned"],
        },
    }


def build_general_ai_prompt(question: str) -> str:
    return f"""
You are a Kannada knowledge assistant.

The trusted knowledge base did not contain an answer for this question.

Answer the question in Kannada using general knowledge.

Rules:
1. Be honest and concise.
2. Do not claim this is verified.
3. If unsure, say that the answer may need verification.
4. Use simple Kannada.
5. Keep the answer between 3 and 5 sentences.

Question:
{question}

Kannada answer:
"""


def route_llm_with_trace(prompt: str) -> dict:
    trace = [
        {
            "step": "Router",
            "status": "started",
            "details": "Routing question.",
        }
    ]

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
        return build_high_confidence_response(
            answer=known_answer,
            trace=trace,
            reason="Known answer store matched",
        )

    alias_key = resolve_alias(prompt)

    if alias_key:
        alias_answer = find_known_answer_by_key(alias_key)

        if alias_answer:
            trace.append({
                "step": "Alias Resolver",
                "status": "matched",
                "details": f"Alias matched before normalization: {alias_key}",
            })
            return build_high_confidence_response(
                answer=alias_answer,
                trace=trace,
                reason="Matched curated alias before normalization",
            )

    normalized_alias_key = resolve_alias(normalized_question)

    if normalized_alias_key:
        normalized_alias_answer = find_known_answer_by_key(normalized_alias_key)

        if normalized_alias_answer:
            trace.append({
                "step": "Alias Resolver",
                "status": "matched",
                "details": f"Alias matched after normalization: {normalized_alias_key}",
            })
            return build_high_confidence_response(
                answer=normalized_alias_answer,
                trace=trace,
                reason="Matched curated alias after normalization",
            )

    rag_result = answer_from_rag_with_trace(normalized_question)
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
            "confidence": rag_result.get("confidence"),
        }

    trace.append({
        "step": "Trusted Source Check",
        "status": "missed",
        "details": "No verified known answer or RAG source found.",
    })

    fallback_prompt = build_general_ai_prompt(normalized_question)

    trace.append({
        "step": "General AI Prompt",
        "status": "built",
        "details": f"Prompt length: {len(fallback_prompt)} characters.",
    })

    fallback_answer = get_llm_response(fallback_prompt)

    if not fallback_answer or "ಉತ್ತರವನ್ನು ಸಿದ್ಧಪಡಿಸಲು" in fallback_answer:
        trace.append({
            "step": "General AI",
            "status": "failed",
            "details": "Ollama fallback failed.",
        })

        return {
            "answer": FALLBACK_ANSWER,
            "trace": trace,
            "confidence": {
                "score": 0,
                "label": "Low",
                "kannada_label": "ಕಡಿಮೆ ವಿಶ್ವಾಸಾರ್ಹ",
                "reasons": ["Ollama fallback failed"],
            },
        }

    trace.append({
        "step": "General AI",
        "status": "completed",
        "details": "Ollama fallback answer generated.",
    })
    draft_result = save_draft_answer(normalized_question, fallback_answer)

    trace.append({
        "step": "Draft Knowledge",
        "status": draft_result["status"],
        "details": (
            f"Draft ID: {draft_result['draft_id']} | "
            f"Hit count: {draft_result['hit_count']}"
        ),
    })

    answer = (
        "ಪರಿಶೀಲಿತ ಮೂಲದಲ್ಲಿ ಈ ವಿಷಯ ಇನ್ನೂ ಲಭ್ಯವಿಲ್ಲ.\n\n"
        f"{fallback_answer}\n\n"
        "ಮೂಲ: General AI response - not yet verified"
    )

    return {
        "answer": answer,
        "trace": trace,
        "confidence": {
            "score": 55,
            "label": "Medium",
            "kannada_label": "ಮಧ್ಯಮ ವಿಶ್ವಾಸಾರ್ಹ",
            "reasons": [
                "No trusted source found",
                "General Ollama answer used",
                "Needs human review",
            ],
        },
    }