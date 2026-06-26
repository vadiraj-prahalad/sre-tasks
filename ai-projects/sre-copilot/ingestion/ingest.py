import os
import chromadb
from chromadb.utils import embedding_functions

# -----------------------------
# Paths
# -----------------------------
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DOCS_PATH = os.path.join(BASE_DIR, "docs")
VECTOR_PATH = os.path.join(BASE_DIR, "vectorstore")

# -----------------------------
# ChromaDB setup
# -----------------------------
client = chromadb.PersistentClient(path=VECTOR_PATH)

collection = client.get_or_create_collection(
    name="sre_knowledge"
)

# Clear old data (safe reset)
try:
    collection.delete(where={})
except:
    pass


# -----------------------------
# Load documents
# -----------------------------
def load_documents():
    docs = []

    for file in os.listdir(DOCS_PATH):
        if file.endswith(".md"):
            with open(os.path.join(DOCS_PATH, file), "r") as f:
                docs.append({
                    "filename": file,
                    "content": f.read()
                })

    return docs


# -----------------------------
# Chunking logic (VERY IMPORTANT IN INTERVIEWS)
# -----------------------------
def chunk_text(text, chunk_size=300, overlap=50):
    chunks = []
    start = 0

    while start < len(text):
        end = start + chunk_size
        chunks.append(text[start:end])
        start = end - overlap

    return chunks


# -----------------------------
# Build vector DB
# -----------------------------
docs = load_documents()

for doc in docs:
    chunks = chunk_text(doc["content"])

    for i, chunk in enumerate(chunks):
        collection.add(
            documents=[chunk],
            ids=[f"{doc['filename']}_{i}"],
            metadatas=[{
                "source": doc["filename"],
                "chunk": i
            }]
        )

        print(f"Stored: {doc['filename']} {i}")
