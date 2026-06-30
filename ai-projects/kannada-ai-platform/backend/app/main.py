from fastapi import FastAPI
from app.api.ask import router as ask_router

app = FastAPI(title="Kannada AI Platform")

@app.get("/health")
def health():
    return {
        "status": "ok",
        "service": "kannada-ai-platform"
    }

app.include_router(ask_router)
