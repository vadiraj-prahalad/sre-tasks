from pathlib import Path
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from app.api import admin_drafts
from app.api.admin_knowledge import router as admin_knowledge_router
from app.api.admin_refresh import router as admin_refresh_router
from app.api.ask import router as ask_router
from app.api.feedback import router as feedback_router

BASE_DIR = Path(__file__).resolve().parent

app = FastAPI()

templates = Jinja2Templates(directory=str(BASE_DIR / "templates"))


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
app.include_router(admin_knowledge_router)
app.include_router(admin_refresh_router)
app.include_router(admin_drafts.router)


@app.get("/health")
def health():
    return {"status": "ok"}


@app.get("/admin", response_class=HTMLResponse)
def admin_page(request: Request):
    return templates.TemplateResponse(
        request=request,
        name="admin.html",
        context={},
    )