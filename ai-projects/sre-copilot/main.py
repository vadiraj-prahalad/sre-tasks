from fastapi import FastAPI
from prometheus_client import Counter, Histogram, generate_latest
from starlette.responses import Response
import time

app = FastAPI()

start_time = time.time()

# ----------------------------
# METRICS (SRE CORE)
# ----------------------------
QUERY_COUNT = Counter(
    "sre_queries_total",
    "Total number of SRE queries processed"
)

QUERY_LATENCY = Histogram(
    "sre_query_latency_seconds",
    "Latency of SRE query processing"
)

# ----------------------------
# HEALTH ENDPOINT
# ----------------------------
@app.get("/health")
def health():
    return {
        "status": "healthy",
        "uptime_seconds": round(time.time() - start_time, 2)
    }

# ----------------------------
# METRICS ENDPOINT
# ----------------------------
@app.get("/metrics")
def metrics():
    return Response(generate_latest(), media_type="text/plain")

# ----------------------------
# QUERY SIMULATION ENDPOINT
# (we'll connect real RAG later if needed)
# ----------------------------
@app.post("/query")
def query(payload: dict):
    start = time.time()

    QUERY_COUNT.inc()

    question = payload.get("question", "")

    # simulate processing
    time.sleep(0.2)

    QUERY_LATENCY.observe(time.time() - start)

    return {
        "question": question,
        "answer": "This is a placeholder response from SRE Copilot"
    }

# ----------------------------
# ROOT
# ----------------------------
@app.get("/")
def root():
    return {"message": "SRE Copilot running"}
