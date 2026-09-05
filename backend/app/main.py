"""
FastAPI application entrypoint.

Run locally with:
    uvicorn app.main:app --reload

Router registration happens entirely inside app/api/v1/__init__.py —
this file should rarely need edits once set up, minimizing merge
conflicts as different developers add new route modules.
"""
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.core.config import settings
from app.api.v1 import api_router

app = FastAPI(title=settings.APP_NAME)

# CORS: permissive defaults for hackathon speed. Tighten allow_origins
# before any real deployment.
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(api_router, prefix="/api/v1")


@app.get("/health")
def health_check():
    return {"status": "ok", "app": settings.APP_NAME}
