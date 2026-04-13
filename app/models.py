from __future__ import annotations

from typing import Literal

from pydantic import BaseModel, Field, HttpUrl


class SummarizeNewsRequest(BaseModel):
    query: str = Field(..., min_length=1, description="Natural language news request")


class Article(BaseModel):
    title: str
    source: str
    url: HttpUrl
    published_at: str | None = None
    description: str | None = None
    content: str | None = None


class SummarizeNewsResponse(BaseModel):
    query: str
    topic: str | None = None
    summary: str
    highlights: list[str]
    articles: list[Article]
    mode: Literal["extractive", "groq", "error", "clarification", "no-results"]
    error: str | None = None
