from __future__ import annotations

import os
from dataclasses import dataclass

from dotenv import load_dotenv


load_dotenv()


@dataclass(frozen=True)
class Settings:
    news_api_key: str = os.getenv("NEWS_API_KEY", "").strip()
    news_api_base_url: str = os.getenv(
        "NEWS_API_BASE_URL", "https://newsapi.org/v2/everything"
    ).strip()
    request_timeout_seconds: float = float(os.getenv("REQUEST_TIMEOUT_SECONDS", "10"))
    article_limit: int = int(os.getenv("ARTICLE_LIMIT", "8"))
    groq_api_key: str = os.getenv("GROQ_API_KEY", "").strip()
    groq_api_base_url: str = os.getenv(
        "GROQ_API_BASE_URL", "https://api.groq.com/openai/v1/chat/completions"
    ).strip()
    groq_model: str = os.getenv("GROQ_MODEL", "llama-3.3-70b-versatile").strip()
    enable_llm_summary: bool = os.getenv("ENABLE_LLM_SUMMARY", "true").lower() == "true"


settings = Settings()
