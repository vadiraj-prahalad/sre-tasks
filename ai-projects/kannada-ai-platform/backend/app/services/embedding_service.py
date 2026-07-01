import requests


OLLAMA_EMBED_URL = "http://localhost:11434/api/embed"
EMBEDDING_MODEL = "nomic-embed-text"


def get_embedding(text: str) -> list[float]:
    response = requests.post(
        OLLAMA_EMBED_URL,
        json={
            "model": EMBEDDING_MODEL,
            "input": text,
        },
        timeout=30,
    )

    response.raise_for_status()

    data = response.json()
    embeddings = data.get("embeddings", [])

    if not embeddings:
        raise ValueError("No embedding returned from Ollama")

    return embeddings[0]
