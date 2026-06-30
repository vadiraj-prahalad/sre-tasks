import requests
from app.core.config import OLLAMA_MODEL, OLLAMA_TIMEOUT_SECONDS, OLLAMA_URL


def get_llm_response(prompt: str) -> str:
    payload = {
        "model": OLLAMA_MODEL,
        "prompt": f"""
You are a Kannada language assistant.

Rules:
- Always respond in correct, simple Kannada
- Do not generate random or broken words
- Give clear and meaningful answers

User question:
{prompt}
""",
        "stream": False
    }

    try:
        response = requests.post(
            OLLAMA_URL,
            json=payload,
            timeout=OLLAMA_TIMEOUT_SECONDS
        )

        response.raise_for_status()

        data = response.json()
        return data.get("response", "").strip()

    except requests.exceptions.RequestException as error:
        return f"Local LLM error: {str(error)}"
