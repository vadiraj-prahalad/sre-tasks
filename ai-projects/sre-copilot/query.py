import os
import chromadb
import requests

# ----------------------------
# Paths
# ----------------------------
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
VECTOR_PATH = os.path.join(BASE_DIR, "vectorstore")

# ----------------------------
# Connect to ChromaDB
# ----------------------------
client = chromadb.PersistentClient(path=VECTOR_PATH)
collection = client.get_collection(name="sre_knowledge")

# ----------------------------
# User query
# ----------------------------
query = input("\n🧑 Ask SRE question: ")

# ----------------------------
# Retrieve top-k relevant chunks
# ----------------------------
results = collection.query(
    query_texts=[query],
    n_results=3
)

docs = results.get("documents", [[]])[0]

# ----------------------------
# Safety check (IMPORTANT)
# ----------------------------
if not docs:
    print("\n❌ No relevant documents found in knowledge base.")
    exit()

# ----------------------------
# Build context
# ----------------------------
context = "\n\n".join(docs)

# ----------------------------
# STRICT SRE PROMPT (NO HALLUCINATION)
# ----------------------------
prompt = f"""
You are an expert Site Reliability Engineer assistant.

You MUST follow these rules strictly:

1. Use ONLY the provided context below.
2. Do NOT use external knowledge.
3. Do NOT invent Kubernetes commands or troubleshooting steps.
4. If the answer is not present in the context, respond:
   "I don't have enough information in the knowledge base."

FORMAT:
- Be concise
- Use bullet points
- Prefer step-by-step troubleshooting if available
- Keep answers production/SRE focused

------------------------
CONTEXT:
{context}
------------------------

QUESTION:
{query}

------------------------
ANSWER:
"""

# ----------------------------
# Call Ollama LLM
# ----------------------------
try:
    response = requests.post(
        "http://127.0.0.1:11434/api/generate",
        json={
            "model": "llama3.2",
            "prompt": prompt,
            "stream": False
        },
        timeout=60
    )

    response.raise_for_status()
    answer = response.json()["response"]

except Exception as e:
    print("\n❌ LLM request failed:", str(e))
    exit()

# ----------------------------
# Output
# ----------------------------
print("\n" + "=" * 70)
print("🧠 SRE COPILOT ANSWER")
print("=" * 70)
print(answer)
print("=" * 70)
