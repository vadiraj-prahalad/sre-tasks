import os

from app.llm.local_llm import get_llm_response


def generate_editorial_text(prompt: str) -> str:
    provider = os.getenv("EDITOR_PROVIDER", "ollama").lower()

    if provider == "ollama":
        return get_llm_response(prompt)

    if provider == "openai":
        return generate_with_openai(prompt)

    return get_llm_response(prompt)


def generate_with_openai(prompt: str) -> str:
    raise NotImplementedError(
        "OpenAI provider is not wired yet. Set EDITOR_PROVIDER=ollama for now."
    )
