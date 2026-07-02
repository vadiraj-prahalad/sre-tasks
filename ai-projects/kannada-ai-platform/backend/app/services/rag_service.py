from app.llm.local_llm import get_llm_response
from app.services.answer_strategy import should_use_direct_answer
from app.services.retriever_service import retrieve_chunks


MIN_SIMILARITY_SCORE = 0.70


def build_sources_text(chunks: list[dict]) -> str:
    source_titles = []

    for chunk in chunks:
        title = chunk["title"]
        if title not in source_titles:
            source_titles.append(title)

    return "\n".join([f"ಮೂಲ: {title}" for title in source_titles])


def build_prompt(context: str, question: str) -> str:
    return f"""
ನೀವು ವಿಶ್ವಾಸಾರ್ಹ ಕನ್ನಡ ಜ್ಞಾನ ಸಹಾಯಕರು.

ಕಟ್ಟುನಿಟ್ಟಿನ ನಿಯಮಗಳು:
1. ಕೆಳಗಿನ ಮೂಲ ಮಾಹಿತಿಯನ್ನು ಮಾತ್ರ ಬಳಸಿ ಉತ್ತರಿಸಿ.
2. ಮೂಲ ಮಾಹಿತಿಯಲ್ಲಿ ಇಲ್ಲದ ವಿಷಯವನ್ನು ಸೇರಿಸಬೇಡಿ.
3. ಮೂಲದಲ್ಲಿರುವ ತತ್ತ್ವ, ಹೆಸರು, ಸಂಬಂಧ, ಅರ್ಥಗಳನ್ನು ಬದಲಾಯಿಸಬೇಡಿ.
4. "ಭೇದವಿದೆ" ಎಂದಿದ್ದರೆ ಅದನ್ನು "ಭೇದವಿಲ್ಲ" ಎಂದು ಬದಲಾಯಿಸಬೇಡಿ.
5. ಉತ್ತರ ಚಿಕ್ಕದಾಗಿ, ಸ್ಪಷ್ಟವಾಗಿ ಮತ್ತು ಸರಳ ಕನ್ನಡದಲ್ಲಿ ಇರಲಿ.
6. ಖಚಿತ ಮಾಹಿತಿ ಇಲ್ಲದಿದ್ದರೆ: "ಮೂಲ ಮಾಹಿತಿಯಲ್ಲಿ ಇದಕ್ಕೆ ಸ್ಪಷ್ಟ ಉತ್ತರ ಇಲ್ಲ." ಎಂದು ಹೇಳಿ.

ಮೂಲ ಮಾಹಿತಿ:
{context}

ಪ್ರಶ್ನೆ:
{question}

ಉತ್ತರ:
"""


def answer_from_rag(question: str) -> str | None:
    chunks = retrieve_chunks(question)

    if not chunks:
        return None

    best_score = chunks[0]["score"]

    if best_score < MIN_SIMILARITY_SCORE:
        return None

    sources_text = build_sources_text(chunks)

    if should_use_direct_answer(question):
        direct_answer = chunks[0]["chunk_text"]
        return f"{direct_answer}\n\n{sources_text}"

    context = "\n\n".join([chunk["chunk_text"] for chunk in chunks])
    prompt = build_prompt(context, question)

    answer = get_llm_response(prompt)

    return f"{answer}\n\n{sources_text}"