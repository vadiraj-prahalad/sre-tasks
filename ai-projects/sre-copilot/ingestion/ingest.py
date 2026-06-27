# ingestion/ingest.py

import os
import numpy as np
import faiss
from sentence_transformers import SentenceTransformer
import pickle

# -------------------------
# PATHS
# -------------------------
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA_DIR = os.path.join(BASE_DIR, "data")

os.makedirs(DATA_DIR, exist_ok=True)

# -------------------------
# SAMPLE RUNBOOK DATA
# -------------------------
documents = [
    "CrashLoopBackOff occurs when a container repeatedly crashes on startup.",
    "ImagePullBackOff occurs when Kubernetes cannot pull container image due to auth or wrong image name.",
    "SEV1 incident requires immediate bridge call and stakeholder notification.",
    "Pod stuck in Pending usually means insufficient resources or node scheduling issues.",
    "High CPU usage in pods can be caused by traffic spikes or inefficient code."
]

# -------------------------
# EMBEDDING MODEL
# -------------------------
print("🔧 Loading embedding model...")
model = SentenceTransformer("all-MiniLM-L6-v2")

print("🔧 Encoding documents...")
embeddings = model.encode(documents)
embeddings = np.array(embeddings).astype("float32")

# -------------------------
# FAISS INDEX
# -------------------------
print("🔧 Building FAISS index...")
index = faiss.IndexFlatL2(embeddings.shape[1])
index.add(embeddings)

# Save index
index_path = os.path.join(DATA_DIR, "sre.index")
faiss.write_index(index, index_path)

# Save docs
docs_path = os.path.join(DATA_DIR, "docs.pkl")
with open(docs_path, "wb") as f:
    pickle.dump(documents, f)

print(f"✅ Ingestion complete. FAISS index: {index_path}, docs: {docs_path}")

