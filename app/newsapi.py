from __future__ import annotations

import json
import ssl
from typing import Any
from urllib.error import HTTPError, URLError
from urllib.parse import urlencode
from urllib.request import Request, urlopen

import certifi

from app.config import settings
from app.models import Article


class NewsAPIError(Exception):
    """Raised when NewsAPI cannot be reached or returns an invalid response."""


SSL_CONTEXT = ssl.create_default_context(cafile=certifi.where())


def _build_query(search_terms: list[str]) -> str:
    return " OR ".join(search_terms)


def fetch_articles(search_terms: list[str], limit: int | None = None) -> list[Article]:
    if not settings.news_api_key:
        raise NewsAPIError("Missing NEWS_API_KEY environment variable.")

    query = _build_query(search_terms)
    params = urlencode(
        {
            "q": query,
            "language": "en",
            "sortBy": "publishedAt",
            "pageSize": limit or settings.article_limit,
        }
    )
    request = Request(
        f"{settings.news_api_base_url}?{params}",
        headers={
            "X-Api-Key": settings.news_api_key,
            "User-Agent": "ai-news-summarizer/1.0",
        },
        method="GET",
    )

    try:
        with urlopen(
            request,
            timeout=settings.request_timeout_seconds,
            context=SSL_CONTEXT,
        ) as response:
            payload = json.loads(response.read().decode("utf-8"))
    except HTTPError as exc:
        try:
            body = exc.read().decode("utf-8")
        except Exception:
            body = ""
        raise NewsAPIError(f"NewsAPI returned HTTP {exc.code}. {body}".strip()) from exc
    except URLError as exc:
        raise NewsAPIError(f"Could not reach NewsAPI: {exc.reason}") from exc
    except TimeoutError as exc:
        raise NewsAPIError("Timed out while contacting NewsAPI.") from exc
    except json.JSONDecodeError as exc:
        raise NewsAPIError("NewsAPI returned an invalid JSON response.") from exc

    if payload.get("status") != "ok":
        message = payload.get("message", "Unknown NewsAPI error")
        raise NewsAPIError(message)

    return [_normalize_article(article) for article in payload.get("articles", [])]


def _normalize_article(article: dict[str, Any]) -> Article:
    source_data = article.get("source") or {}
    return Article(
        title=(article.get("title") or "Untitled").strip(),
        source=(source_data.get("name") or "Unknown source").strip(),
        url=article.get("url"),
        published_at=article.get("publishedAt"),
        description=_clean_text(article.get("description")),
        content=_clean_text(article.get("content")),
    )


def _clean_text(value: str | None) -> str | None:
    if not value:
        return None
    cleaned = value.replace("\n", " ").strip()
    if "[+" in cleaned:
        cleaned = cleaned.split("[+", maxsplit=1)[0].strip()
    return cleaned or None
