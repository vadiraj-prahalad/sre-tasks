from fastapi import FastAPI
from app.api.query import router

app = FastAPI(title="SRE Copilot")

app.include_router(router)
