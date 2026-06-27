import time
import uuid
from fastapi import APIRouter
from pydantic import BaseModel

from app.rag.retriever import retrieve_docs
from app.rag.generator import generate_answer

router = APIRouter()


class QueryRequest(BaseModel):
    question: str


@router.post("/query")
def query(req: QueryRequest):

    request_id = str(uuid.uuid4())
    start_time = time.time()

    question = req.question.strip()

    # STEP 1: retrieve
    docs = retrieve_docs(question)

    # STEP 2: generate
    answer, topic = generate_answer(question, docs)

    latency_ms = round((time.time() - start_time) * 1000, 2)

    return {
        "request_id": request_id,
        "question": question,
        "topic": topic,
        "retrieved_docs": docs,
        "answer": answer,
        "latency_ms": latency_ms
    }
