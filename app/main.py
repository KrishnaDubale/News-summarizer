from __future__ import annotations

from pathlib import Path

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles

from app.models import SummarizeNewsRequest, SummarizeNewsResponse
from app.service import summarize_news


BASE_DIR = Path(__file__).resolve().parent.parent
STATIC_DIR = BASE_DIR / "static"

app = FastAPI(title="AI News Summarizer", version="1.0.0")
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
app.mount("/static", StaticFiles(directory=str(STATIC_DIR)), name="static")


@app.get("/", include_in_schema=False)
def read_index() -> FileResponse:
    return FileResponse(STATIC_DIR / "index.html")


@app.post("/summarize-news", response_model=SummarizeNewsResponse)
def summarize_news_endpoint(payload: SummarizeNewsRequest) -> SummarizeNewsResponse:
    return summarize_news(payload.query)


@app.get("/health")
def health_check() -> dict[str, str]:
    return {"status": "ok"}
