from fastapi import FastAPI
import chromadb
import requests
import os

app = FastAPI(title="SRE Copilot API")

# ----------------------------
# Paths
# ----------------------------
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
VECTOR_PATH = os.path.join(BASE_DIR, "vectorstore")

# ----------------------------
# Vector DB
# ----------------------------
client = chromadb.PersistentClient(path=VECTOR_PATH)
collection = client.get_or_create_collection(name="sre_knowledge")


# ----------------------------
# Core RAG function
# ----------------------------
def run_rag(query: str):
    results = collection.query(
        query_texts=[query],
        n_results=3,
        include=["documents", "metadatas"]
    )

    docs = results["documents"][0]
    metas = results["metadatas"][0]

    context_blocks = []
    sources = []

    for doc, meta in zip(docs, metas):
        context_blocks.append(f"""
Source: {meta['source']}
Chunk: {meta['chunk_id']}
{doc}
""")
        sources.append(meta["source"])

    context = "\n---\n".join(context_blocks)

    prompt = f"""
You are a Senior Site Reliability Engineer.

Use ONLY the context below.

Context:
{context}

Question:
{query}

Format:
1. Likely cause
2. Debug steps
3. Commands
4. Source
"""

    response = requests.post(
        "http://localhost:11434/api/generate",
        json={
            "model": "llama3.2",
            "prompt": prompt,
            "stream": False
        }
    )

    return {
        "answer": response.json().get("response", ""),
        "sources": list(set(sources))
    }


# ----------------------------
# API Endpoint
# ----------------------------
@app.post("/query")
def query_sre(payload: dict):
    question = payload.get("question", "")
    return run_rag(question)
