import requests

OLLAMA_URL = "http://localhost:11434/api/generate"
MODEL = "llama3.2"


def generate_answer(question: str, docs: list):
    """
    LLM-powered RAG generator using Ollama
    """

    if not docs:
        return (
            "No relevant runbooks found for this issue.",
            "unknown"
        )

    context = "\n\n".join(docs)

    prompt = f"""
You are a Senior Site Reliability Engineer (SRE).

Use ONLY the provided runbooks context to answer.

Context:
{context}

Question:
{question}

Return format:
1. Likely cause
2. Debug steps
3. Kubernetes/Linux commands (if relevant)
4. Short conclusion
"""

    response = requests.post(
        OLLAMA_URL,
        json={
            "model": MODEL,
            "prompt": prompt,
            "stream": False
        }
    )

    answer = response.json().get("response", "")

    # simple topic detection (keep same as before)
    q = question.lower()

    if "crashloopbackoff" in q:
        topic = "kubernetes"
    elif "imagepullbackoff" in q:
        topic = "kubernetes"
    elif "cpu" in q:
        topic = "performance"
    else:
        topic = "general"

    return answer, topic
