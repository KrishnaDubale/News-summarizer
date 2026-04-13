from __future__ import annotations

import json
from urllib.error import HTTPError, URLError
from urllib.request import Request, urlopen

from app.config import settings
from app.models import Article


class GroqAPIError(Exception):
    """Raised when the Groq API cannot complete a summary request."""


def summarize_with_groq(topic: str | None, articles: list[Article]) -> tuple[str, list[str]]:
    if not settings.groq_api_key:
        raise GroqAPIError("Missing GROQ_API_KEY environment variable.")

    payload = {
        "model": settings.groq_model,
        "messages": [
            {
                "role": "system",
                "content": (
                    "You summarize current news. Return strict JSON with keys "
                    '"summary" and "highlights". "highlights" must be an array of 2 to 4 short strings.'
                ),
            },
            {"role": "user", "content": _build_prompt(topic, articles)},
        ],
        "temperature": 0.2,
        "response_format": {"type": "json_object"},
    }

    request = Request(
        settings.groq_api_base_url,
        data=json.dumps(payload).encode("utf-8"),
        headers={
            "Authorization": f"Bearer {settings.groq_api_key}",
            "Content-Type": "application/json",
            "User-Agent": "ai-news-summarizer/1.0",
        },
        method="POST",
    )

    try:
        with urlopen(request, timeout=settings.request_timeout_seconds) as response:
            raw_payload = json.loads(response.read().decode("utf-8"))
    except HTTPError as exc:
        try:
            body = exc.read().decode("utf-8")
        except Exception:
            body = ""
        raise GroqAPIError(f"Groq API returned HTTP {exc.code}. {body}".strip()) from exc
    except URLError as exc:
        raise GroqAPIError(f"Could not reach Groq API: {exc.reason}") from exc
    except TimeoutError as exc:
        raise GroqAPIError("Timed out while contacting the Groq API.") from exc
    except json.JSONDecodeError as exc:
        raise GroqAPIError("Groq API returned invalid JSON.") from exc

    return _parse_groq_response(raw_payload)


def _build_prompt(topic: str | None, articles: list[Article]) -> str:
    topic_label = topic or "the requested topic"
    article_lines: list[str] = []
    for article in articles[:5]:
        article_lines.append(
            "\n".join(
                [
                    f"Title: {article.title}",
                    f"Source: {article.source}",
                    f"Published: {article.published_at or 'Unknown'}",
                    f"Description: {article.description or ''}",
                    f"Content: {article.content or ''}",
                ]
            )
        )

    return (
        f"Summarize the latest news about {topic_label} using the articles below.\n"
        "Write a concise user-facing summary in 2 to 4 sentences.\n"
        "Then provide 2 to 4 short highlights.\n\n"
        "Articles:\n\n"
        + "\n\n---\n\n".join(article_lines)
    )


def _parse_groq_response(payload: dict) -> tuple[str, list[str]]:
    choices = payload.get("choices") or []
    if not choices:
        raise GroqAPIError("Groq API returned no choices.")

    message = choices[0].get("message") or {}
    content = message.get("content")
    if not content:
        raise GroqAPIError("Groq API returned an empty message.")

    try:
        data = json.loads(content)
    except json.JSONDecodeError as exc:
        raise GroqAPIError("Groq response content was not valid JSON.") from exc

    summary = str(data.get("summary", "")).strip()
    raw_highlights = data.get("highlights", [])
    highlights = [str(item).strip() for item in raw_highlights if str(item).strip()]
    if not summary:
        raise GroqAPIError("Groq response did not include a summary.")
    if not highlights:
        raise GroqAPIError("Groq response did not include highlights.")
    return summary, highlights[:4]
