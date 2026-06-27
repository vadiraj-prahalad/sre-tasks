import os
import pickle
import faiss
import numpy as np
from sentence_transformers import SentenceTransformer

# -----------------------------
# PATHS
# -----------------------------
BASE_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
DATA_PATH = os.path.join(BASE_DIR, "data")

INDEX_PATH = os.path.join(DATA_PATH, "sre.index")
DOCS_PATH = os.path.join(DATA_PATH, "docs.pkl")

# -----------------------------
# LOAD MODEL (ONCE)
# -----------------------------
model = SentenceTransformer("all-MiniLM-L6-v2")

# -----------------------------
# LOAD FAISS + DOCS (ONCE)
# -----------------------------
index = faiss.read_index(INDEX_PATH)

with open(DOCS_PATH, "rb") as f:
    documents = pickle.load(f)


# -----------------------------
# RETRIEVAL FUNCTION
# -----------------------------
def retrieve_docs(question: str, top_k: int = 3):
    """
    Semantic FAISS retrieval
    """

    # 1. Embed query
    query_embedding = model.encode([question])
    query_embedding = np.array(query_embedding).astype("float32")

    # 2. Search FAISS
    distances, indices = index.search(query_embedding, top_k)

    # 3. Fetch docs
    results = []
    for i in indices[0]:
        if i < len(documents):
            results.append(documents[i])

    return results
