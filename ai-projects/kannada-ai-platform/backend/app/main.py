from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.api.feedback import router as feedback_router

from app.api.ask import router as ask_router

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5173",
        "http://127.0.0.1:5173",
        "http://localhost:4173",
        "http://127.0.0.1:4173",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(ask_router)
app.include_router(feedback_router)

@app.get("/health")
def health():
    return {"status": "ok"}
