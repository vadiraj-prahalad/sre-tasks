import time
import uuid
from typing import List, Dict

# ----------------------------
# SIMPLE QUERY CLASSIFIER
# ----------------------------
def classify_query(question: str) -> str:
    q = question.lower()

    if any(x in q for x in ["crashloopbackoff", "kubernetes", "pod", "kubectl"]):
        return "kubernetes"

    if any(x in q for x in ["docker", "container", "image", "docker ps"]):
        return "docker"

    if any(x in q for x in ["incident", "sev", "oncall", "alert"]):
        return "incident"

    return "general"


# ----------------------------
# MOCK VECTOR SEARCH (replace with ChromaDB later)
# ----------------------------
def retrieve_docs(query: str, docs: List[Dict]) -> List[Dict]:
    """
    Simulated semantic retrieval.
    Replace this with chromadb collection.query(...)
    """
    results = []

    for d in docs:
        if query.lower() in d["text"].lower():
            results.append(d)

    # fallback: return top docs if nothing matched
    if not results:
        results = docs[:2]

    return results


# ----------------------------
# ANSWER GENERATION (RAG CORE)
# ----------------------------
def generate_answer(question: str, docs: List[Dict]) -> Dict:
    request_id = str(uuid.uuid4())
    start_time = time.time()

    topic = classify_query(question)
    retrieved = retrieve_docs(question, docs)

    # build context
    context_text = "\n\n".join([d["text"] for d in retrieved])

    # simple grounded response (you can replace with LLM later)
    answer = f"""
## Topic: {topic.upper()}

## Likely Cause
Based on runbook context:
{context_text}

## Debug Steps
1. kubectl describe pod <pod>
2. kubectl logs <pod>
3. Check image version
4. Verify probes

## SRE Note
Always correlate logs + events + metrics before taking action.
""".strip()

    latency = round(time.time() - start_time, 4)

    return {
        "request_id": request_id,
        "question": question,
        "topic": topic,
        "retrieved_docs": [d["text"] for d in retrieved],
        "answer": answer,
        "latency_seconds": latency
    }


# ----------------------------
# SAMPLE RUN (for CLI testing)
# ----------------------------
if __name__ == "__main__":

    DOCUMENTS = [
        {
            "text": "CrashLoopBackOff occurs when a container repeatedly crashes due to startup failure or misconfiguration."
        },
        {
            "text": "ImagePullBackOff happens when Kubernetes cannot pull container image due to auth or wrong image name."
        },
        {
            "text": "Incident response: SEV1 requires immediate escalation, bridge call, and stakeholder notification."
        }
    ]

    while True:
        question = input("\n🧑 Ask SRE question: ")

        result = generate_answer(question, DOCUMENTS)

        print("\n" + "=" * 60)
        print("🧠 SRE COPILOT ANSWER")
        print("=" * 60)
        print(result["answer"])

        print("\n--- METADATA ---")
        print(f"Request ID: {result['request_id']}")
        print(f"Topic: {result['topic']}")
        print(f"Latency: {result['latency_seconds']}s")
