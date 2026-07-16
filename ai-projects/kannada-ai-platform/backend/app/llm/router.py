from app.llm.local_llm import (
    get_llm_response,
)
from app.services.alias_service import (
    resolve_alias,
)
from app.services.domain_classifier import (
    classify_domain,
    requires_verified_source,
)
from app.services.draft_knowledge_service import (
    save_draft_answer,
)
from app.services.entity_resolution_service import (
    resolve_entity,
)
from app.services.knowledge_service import (
    find_known_answer,
    find_known_answer_by_key,
)
from app.services.query_normalizer import (
    normalize_question,
)
from app.services.rag_service import (
    answer_from_rag_with_trace,
)
from app.services.related_topics_service import (
    get_related_topics,
)


FALLBACK_ANSWER = (
    "ಈ ವಿಷಯದ ಉತ್ತರವನ್ನು ಸಿದ್ಧಪಡಿಸಲು ಸಾಧ್ಯವಾಗಲಿಲ್ಲ. "
    "ದಯವಿಟ್ಟು ನಂತರ ಮತ್ತೆ ಪ್ರಯತ್ನಿಸಿ."
)

VERIFIED_ONLY_FALLBACK_ANSWER = (
    "ಈ ವಿಷಯಕ್ಕೆ ಪರಿಶೀಲಿತ ಮಾಹಿತಿ ಇನ್ನೂ ಜ್ಞಾನ ಸಂಗ್ರಹದಲ್ಲಿ "
    "ಲಭ್ಯವಿಲ್ಲ.\n\n"
    "ಧಾರ್ಮಿಕ, ವೈದ್ಯಕೀಯ ಅಥವಾ ಕಾನೂನು ಸಂಬಂಧಿತ ವಿಷಯಗಳಲ್ಲಿ "
    "ತಪ್ಪು ಮಾಹಿತಿ ನೀಡದಂತೆ, ಪರಿಶೀಲಿತ ಮೂಲ ಸೇರಿಸಿದ ನಂತರ "
    "ಮಾತ್ರ ಉತ್ತರ ನೀಡಲಾಗುತ್ತದೆ.\n\n"
    "ಮೂಲ: Verified source required"
)


def route_llm(
    prompt: str,
) -> str:
    result = route_llm_with_trace(
        prompt
    )

    return result["answer"]


def build_high_confidence_response(
    answer: str,
    trace: list[dict],
    reason: str,
    related_topics: list[str],
) -> dict:
    return {
        "answer": answer,
        "trace": trace,
        "related_topics": related_topics,
        "confidence": {
            "score": 95,
            "label": "High",
            "kannada_label": (
                "ಹೆಚ್ಚು ವಿಶ್ವಾಸಾರ್ಹ"
            ),
            "reasons": [
                reason,
                "Known answer returned",
            ],
        },
    }


def build_general_ai_prompt(
    question: str,
) -> str:
    return f"""
You are a Kannada knowledge assistant.

The trusted knowledge base did not contain an answer for this question.

Answer the question in Kannada using general knowledge.

Rules:
1. Be honest and concise.
2. Do not claim this is verified.
3. If unsure, say that the answer may need verification.
4. Use simple, natural Kannada.
5. Keep the answer between 3 and 5 sentences.
6. If the question is only a short topic name, explain the topic clearly.
7. Do not say you cannot answer unless the topic is truly unclear.
8. Avoid machine-translation style Kannada.

Question:
{question}

Kannada answer:
"""


def build_verified_only_response(
    trace: list[dict],
    related_topics: list[str],
    domain: str,
) -> dict:
    trace.append(
        {
            "step": "Domain Safety",
            "status": "blocked",
            "details": (
                f"Domain '{domain}' requires "
                "verified source. "
                "LLM fallback skipped."
            ),
        }
    )

    return {
        "answer": (
            VERIFIED_ONLY_FALLBACK_ANSWER
        ),
        "trace": trace,
        "related_topics": related_topics,
        "confidence": {
            "score": 0,
            "label": "Low",
            "kannada_label": (
                "ಪರಿಶೀಲಿತ ಮೂಲ ಅಗತ್ಯ"
            ),
            "reasons": [
                "Sensitive domain detected",
                "Verified source required",
                "LLM fallback skipped",
            ],
        },
    }


def route_llm_with_trace(
    prompt: str,
) -> dict:
    related_topics = get_related_topics(
        prompt
    )

    domain = classify_domain(
        prompt
    )

    trace: list[dict] = [
        {
            "step": "Router",
            "status": "started",
            "details": (
                "Routing question."
            ),
        },
        {
            "step": "Domain Classifier",
            "status": domain,
            "details": (
                f"Detected domain: {domain}"
            ),
        },
    ]

    normalized_question = normalize_question(
        prompt
    )

    trace.append(
        {
            "step": "Query Normalizer",
            "status": "completed",
            "details": (
                "Normalized question: "
                f"{normalized_question}"
            ),
        }
    )

    known_answer = find_known_answer(
        normalized_question
    )

    if known_answer:
        trace.append(
            {
                "step": "Known Answer",
                "status": "matched",
                "details": (
                    "Answer found in trusted "
                    "known-answer store."
                ),
            }
        )

        return build_high_confidence_response(
            answer=known_answer,
            trace=trace,
            reason=(
                "Known answer store matched"
            ),
            related_topics=related_topics,
        )

    alias_key = resolve_alias(
        prompt
    )

    if alias_key:
        alias_answer = (
            find_known_answer_by_key(
                alias_key
            )
        )

        if alias_answer:
            trace.append(
                {
                    "step": "Alias Resolver",
                    "status": "matched",
                    "details": (
                        "Alias matched before "
                        "normalization: "
                        f"{alias_key}"
                    ),
                }
            )

            return build_high_confidence_response(
                answer=alias_answer,
                trace=trace,
                reason=(
                    "Matched curated alias "
                    "before normalization"
                ),
                related_topics=related_topics,
            )

    normalized_alias_key = resolve_alias(
        normalized_question
    )

    if normalized_alias_key:
        normalized_alias_answer = (
            find_known_answer_by_key(
                normalized_alias_key
            )
        )

        if normalized_alias_answer:
            trace.append(
                {
                    "step": "Alias Resolver",
                    "status": "matched",
                    "details": (
                        "Alias matched after "
                        "normalization: "
                        f"{normalized_alias_key}"
                    ),
                }
            )

            return build_high_confidence_response(
                answer=(
                    normalized_alias_answer
                ),
                trace=trace,
                reason=(
                    "Matched curated alias "
                    "after normalization"
                ),
                related_topics=related_topics,
            )

    entity = resolve_entity(
        topic=normalized_question,
        category=domain,
    )

    trace.append(
        {
            "step": "Entity Resolver",
            "status": (
                entity.resolution_method
            ),
            "details": (
                "Resolved topic: "
                f"{entity.resolved_topic} | "
                "preferred name: "
                f"{entity.preferred_name} | "
                "confidence: "
                f"{entity.confidence:.2f}"
            ),
        }
    )

    rag_result = answer_from_rag_with_trace(
        question=normalized_question,
        entity=entity,
    )

    trace.extend(
        rag_result["trace"]
    )

    if rag_result["answer"]:
        trace.append(
            {
                "step": "Final Route",
                "status": "rag",
                "details": (
                    "Answer returned from "
                    "RAG pipeline."
                ),
            }
        )

        return {
            "answer": (
                rag_result["answer"]
            ),
            "trace": trace,
            "confidence": (
                rag_result.get(
                    "confidence"
                )
            ),
            "related_topics": (
                related_topics
            ),
        }

    trace.append(
        {
            "step": "Trusted Source Check",
            "status": "missed",
            "details": (
                "No verified known answer "
                "or RAG source found."
            ),
        }
    )

    if requires_verified_source(
        prompt
    ):
        return build_verified_only_response(
            trace=trace,
            related_topics=related_topics,
            domain=domain,
        )

    fallback_prompt = (
        build_general_ai_prompt(
            normalized_question
        )
    )

    trace.append(
        {
            "step": "General AI Prompt",
            "status": "built",
            "details": (
                f"Prompt length: "
                f"{len(fallback_prompt)} "
                "characters."
            ),
        }
    )

    fallback_answer = get_llm_response(
        fallback_prompt
    )

    if (
        not fallback_answer
        or "ಉತ್ತರವನ್ನು ಸಿದ್ಧಪಡಿಸಲು"
        in fallback_answer
    ):
        trace.append(
            {
                "step": "General AI",
                "status": "failed",
                "details": (
                    "Ollama fallback failed."
                ),
            }
        )

        return {
            "answer": FALLBACK_ANSWER,
            "trace": trace,
            "related_topics": (
                related_topics
            ),
            "confidence": {
                "score": 0,
                "label": "Low",
                "kannada_label": (
                    "ಕಡಿಮೆ ವಿಶ್ವಾಸಾರ್ಹ"
                ),
                "reasons": [
                    "Ollama fallback failed",
                ],
            },
        }

    trace.append(
        {
            "step": "General AI",
            "status": "completed",
            "details": (
                "Ollama fallback answer "
                "generated."
            ),
        }
    )

    draft_result = save_draft_answer(
        normalized_question,
        fallback_answer,
    )

    trace.append(
        {
            "step": "Draft Knowledge",
            "status": (
                draft_result["status"]
            ),
            "details": (
                "Draft ID: "
                f"{draft_result['draft_id']} | "
                "Hit count: "
                f"{draft_result['hit_count']}"
            ),
        }
    )

    answer = (
        "ಪರಿಶೀಲಿತ ಮೂಲದಲ್ಲಿ ಈ ವಿಷಯ ಇನ್ನೂ "
        "ಲಭ್ಯವಿಲ್ಲ.\n\n"
        f"{fallback_answer}\n\n"
        "ಮೂಲ: General AI response - "
        "not yet verified"
    )

    return {
        "answer": answer,
        "trace": trace,
        "related_topics": (
            related_topics
        ),
        "confidence": {
            "score": 55,
            "label": "Medium",
            "kannada_label": (
                "ಮಧ್ಯಮ ವಿಶ್ವಾಸಾರ್ಹ"
            ),
            "reasons": [
                "No trusted source found",
                "General Ollama answer used",
                "Needs human review",
            ],
        },
    }