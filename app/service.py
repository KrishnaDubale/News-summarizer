from __future__ import annotations

from app.config import settings
from app.groq_client import GroqAPIError, summarize_with_groq
from app.models import SummarizeNewsResponse
from app.newsapi import NewsAPIError, fetch_articles
from app.query_parser import parse_user_query
from app.summarizer import build_extractive_summary, rank_and_deduplicate_articles


def summarize_news(query: str) -> SummarizeNewsResponse:
    parsed = parse_user_query(query)
    if parsed.needs_clarification:
        return SummarizeNewsResponse(
            query=query,
            topic=parsed.topic,
            summary=parsed.clarification_message or "Please provide a more specific topic.",
            highlights=[],
            articles=[],
            mode="clarification",
            error=None,
        )

    try:
        fetched_articles = fetch_articles(parsed.search_terms)
    except NewsAPIError as exc:
        return SummarizeNewsResponse(
            query=query,
            topic=parsed.topic,
            summary="I couldn't fetch the latest articles right now.",
            highlights=[],
            articles=[],
            mode="error",
            error=str(exc),
        )

    ranked_articles = rank_and_deduplicate_articles(fetched_articles)
    if not ranked_articles:
        return SummarizeNewsResponse(
            query=query,
            topic=parsed.topic,
            summary=f"I could not find recent articles for {parsed.topic or 'that query'}.",
            highlights=[],
            articles=[],
            mode="no-results",
            error=None,
        )

    mode = "extractive"
    summary, highlights = build_extractive_summary(parsed.topic, ranked_articles)
    if settings.enable_llm_summary and settings.groq_api_key:
        try:
            summary, highlights = summarize_with_groq(parsed.topic, ranked_articles)
            mode = "groq"
        except GroqAPIError:
            mode = "extractive"
    return SummarizeNewsResponse(
        query=query,
        topic=parsed.topic,
        summary=summary,
        highlights=highlights,
        articles=ranked_articles[: settings.article_limit],
        mode=mode,
        error=None,
    )
