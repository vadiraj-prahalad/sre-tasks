from app.llm.local_llm import get_llm_response
from app.models.knowledge_entity import (
    KnowledgeEntity,
)
from app.services.answer_composer import (
    compose_direct_answer,
)
from app.services.answer_quality_service import (
    clean_final_answer,
)
from app.services.answer_strategy import (
    should_use_direct_answer,
)
from app.services.retriever_service import (
    retrieve_chunks,
)
from app.services.retrieval_explanation_service import (
    explain_retrieval,
)


MIN_SIMILARITY_SCORE = 0.70


def build_sources_text(
    chunks: list[dict],
) -> str:
    source_titles: list[str] = []

    for chunk in chunks:
        title = str(
            chunk.get("title") or ""
        )

        if (
            title
            and title not in source_titles
        ):
            source_titles.append(
                title
            )

    return "\n".join(
        f"ಮೂಲ: {title}"
        for title in source_titles
    )


def build_prompt(
    context: str,
    question: str,
) -> str:
    return f"""
You are a trusted Kannada knowledge assistant.

Fact rules:
1. Use only the supplied context.
2. Do not invent facts.
3. Preserve names, titles, relationships, and meanings exactly.
4. Answer only in Kannada.

Kannada quality rules:
1. ಉತ್ತರವು ಸಹಜ, ಶುದ್ಧ ಮತ್ತು ಓದಲು ಸುಲಭವಾದ ಕನ್ನಡದಲ್ಲಿ ಇರಲಿ.
2. ಯಂತ್ರಾನುವಾದ ಶೈಲಿಯನ್ನು ತಪ್ಪಿಸಿ.
3. ಗೌರವಪೂರ್ಣ ರೂಪಗಳನ್ನು ಸರಿಯಾಗಿ ಬಳಸಿ.
4. ಅಗತ್ಯವಿಲ್ಲದ “ಅಭಿಪ್ರಾಯ”, “ಅರ್ಥ”, “ಎಂಬುದು” ಪದಗಳಿಂದ ಉತ್ತರ ಪ್ರಾರಂಭಿಸಬೇಡಿ.
5. ಉತ್ತರ 3 ರಿಂದ 5 ವಾಕ್ಯಗಳಲ್ಲಿ ಇರಲಿ.

ಮೂಲ ಮಾಹಿತಿ:
{context}

ಪ್ರಶ್ನೆ:
{question}

ಉತ್ತರ:
"""


def calculate_confidence(
    best_score: float,
    is_direct_answer: bool,
    chunk_count: int,
) -> dict:
    score_points = min(
        best_score,
        1.0,
    ) * 70

    direct_points = (
        20
        if is_direct_answer
        else 10
    )

    source_points = (
        10
        if chunk_count == 1
        else 5
    )

    confidence = round(
        score_points
        + direct_points
        + source_points
    )

    if confidence >= 90:
        label = "High"
        kannada_label = (
            "ಹೆಚ್ಚು ವಿಶ್ವಾಸಾರ್ಹ"
        )
    elif confidence >= 75:
        label = "Medium"
        kannada_label = (
            "ಮಧ್ಯಮ ವಿಶ್ವಾಸಾರ್ಹ"
        )
    else:
        label = "Low"
        kannada_label = (
            "ಕಡಿಮೆ ವಿಶ್ವಾಸಾರ್ಹ"
        )

    return {
        "score": confidence,
        "label": label,
        "kannada_label": kannada_label,
        "reasons": [
            (
                "Top retrieval score: "
                f"{best_score:.4f}"
            ),
            (
                "Direct answer used"
                if is_direct_answer
                else "LLM generation used"
            ),
            (
                "Context chunks used: "
                f"{chunk_count}"
            ),
        ],
    }


def answer_from_rag_with_trace(
    question: str,
    entity: KnowledgeEntity | None = None,
) -> dict:
    trace: list[dict] = []

    chunks = retrieve_chunks(
        question=question,
        entity=entity,
    )

    trace.append(
        {
            "step": "Retriever",
            "status": "completed",
            "details": (
                f"Retrieved {len(chunks)} "
                "chunk(s)."
            ),
        }
    )

    if entity is not None:
        trace.append(
            {
                "step": "Canonical Entity",
                "status": "available",
                "details": (
                    "Resolved topic: "
                    f"{entity.resolved_topic} | "
                    "preferred name: "
                    f"{entity.preferred_name} | "
                    "method: "
                    f"{entity.resolution_method} | "
                    "confidence: "
                    f"{entity.confidence:.2f}"
                ),
            }
        )

    if not chunks:
        return {
            "answer": None,
            "trace": trace,
            "confidence": None,
        }

    top_chunk = chunks[0]

    retrieval_explanation = explain_retrieval(
        selected_chunk=top_chunk,
        result_count=len(chunks),
    )

    best_score = (
        retrieval_explanation.bounded_score
    )

    trace.append(
        {
            "step": "Retrieval Explanation",
            "status": "completed",
            "details": {
                "selected_title": (
                    retrieval_explanation.selected_title
                ),
                "reasons": list(
                    retrieval_explanation.reasons
                ),
                "metrics": {
                    "semantic_score": (
                        retrieval_explanation.semantic_score
                    ),
                    "content_bonus": (
                        retrieval_explanation.content_bonus
                    ),
                    "title_bonus": (
                        retrieval_explanation.title_bonus
                    ),
                    "entity_title_bonus": (
                        retrieval_explanation.entity_title_bonus
                    ),
                    "raw_score": (
                        retrieval_explanation.raw_score
                    ),
                    "bounded_score": (
                        retrieval_explanation.bounded_score
                    ),
                },
                "source_name": (
                    retrieval_explanation.source_name
                ),
                "provenance": (
                    retrieval_explanation.provenance
                ),
            },
        }
    )
    trace.append(
        {
            "step": "Top Source",
            "status": "completed",
            "details": (
                f"Title: {retrieval_explanation.selected_title} | "
                "semantic="
                f"{retrieval_explanation.semantic_score:.4f} | "
                "content_bonus="
                f"{retrieval_explanation.content_bonus:.4f} | "
                "title_bonus="
                f"{retrieval_explanation.title_bonus:.4f} | "
                "entity_title_bonus="
                f"{retrieval_explanation.entity_title_bonus:.4f} | "
                "raw_score="
                f"{retrieval_explanation.raw_score:.4f} | "
                "bounded_score="
                f"{retrieval_explanation.bounded_score:.4f} | "
                f"source={retrieval_explanation.source_name} | "
                f"provenance={retrieval_explanation.provenance}"
            ),
        }
    )

    if (
        best_score
        < MIN_SIMILARITY_SCORE
    ):
        trace.append(
            {
                "step": "Score Check",
                "status": "failed",
                "details": (
                    f"Best score {best_score:.4f} "
                    "below threshold."
                ),
            }
        )

        return {
            "answer": None,
            "trace": trace,
            "confidence": None,
        }

    sources_text = build_sources_text(
        chunks
    )

    is_direct = (
        should_use_direct_answer(
            question
        )
    )

    confidence = calculate_confidence(
        best_score=best_score,
        is_direct_answer=is_direct,
        chunk_count=len(chunks),
    )

    trace.append(
        {
            "step": "Confidence Engine",
            "status": (
                confidence["label"].lower()
            ),
            "details": (
                f"{confidence['score']}% - "
                f"{confidence['kannada_label']}"
            ),
        }
    )

    if is_direct:
        trace.append(
            {
                "step": "Answer Strategy",
                "status": "direct",
                "details": (
                    "Direct answer selected. "
                    "LLM skipped."
                ),
            }
        )

        direct_answer = (
            compose_direct_answer(
                question,
                top_chunk["chunk_text"],
            )
        )

        direct_answer = (
            clean_final_answer(
                direct_answer
            )
        )

        return {
            "answer": (
                f"{direct_answer}\n\n"
                f"{sources_text}"
            ),
            "trace": trace,
            "confidence": confidence,
        }

    trace.append(
        {
            "step": "Answer Strategy",
            "status": "llm",
            "details": (
                "LLM generation selected."
            ),
        }
    )

    context = "\n\n".join(
        str(
            chunk.get(
                "chunk_text",
                "",
            )
        )
        for chunk in chunks
    )

    prompt = build_prompt(
        context=context,
        question=question,
    )

    trace.append(
        {
            "step": "Prompt Builder",
            "status": "completed",
            "details": (
                f"Prompt length: "
                f"{len(prompt)} characters."
            ),
        }
    )

    answer = get_llm_response(
        prompt
    )

    answer = clean_final_answer(
        answer
    )

    trace.append(
        {
            "step": "LLM",
            "status": "completed",
            "details": (
                "Ollama response received."
            ),
        }
    )

    return {
        "answer": (
            f"{answer}\n\n"
            f"{sources_text}"
        ),
        "trace": trace,
        "confidence": confidence,
    }


def answer_from_rag(
    question: str,
    entity: KnowledgeEntity | None = None,
) -> str | None:
    result = answer_from_rag_with_trace(
        question=question,
        entity=entity,
    )

    return result["answer"]