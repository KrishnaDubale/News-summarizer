from __future__ import annotations

import re
from dataclasses import dataclass


STOPWORDS = {
    "give",
    "me",
    "show",
    "latest",
    "news",
    "about",
    "tell",
    "what",
    "happening",
    "on",
    "please",
    "the",
}

TOPIC_ALIASES: dict[str, tuple[str, list[str]]] = {
    "ipl": (
        "IPL",
        [
            "IPL",
            '"Indian Premier League"',
            "cricket",
            "T20",
        ],
    ),
    "indian premier league": (
        "IPL",
        [
            "IPL",
            '"Indian Premier League"',
            "cricket",
            "T20",
        ],
    ),
    "cricket": ("Cricket", ["cricket"]),
    "ai": ("AI", ['"artificial intelligence"', "AI"]),
    "artificial intelligence": ("AI", ['"artificial intelligence"', "AI"]),
    "bitcoin": ("Bitcoin", ["bitcoin", "crypto"]),
    "stock market": ("Stock Market", ['"stock market"', "stocks"]),
}

VAGUE_QUERIES = {"news", "latest news", "headlines", "current affairs"}


@dataclass(frozen=True)
class ParsedQuery:
    raw_query: str
    normalized_query: str
    topic: str | None
    search_terms: list[str]
    needs_clarification: bool
    clarification_message: str | None = None


def _normalize(query: str) -> str:
    query = query.strip().lower()
    return re.sub(r"\s+", " ", query)


def parse_user_query(query: str) -> ParsedQuery:
    normalized = _normalize(query)
    if not normalized:
        return ParsedQuery(
            raw_query=query,
            normalized_query=normalized,
            topic=None,
            search_terms=[],
            needs_clarification=True,
            clarification_message="Please ask for a specific topic, like IPL, AI, or cricket news.",
        )

    if normalized in VAGUE_QUERIES:
        return ParsedQuery(
            raw_query=query,
            normalized_query=normalized,
            topic=None,
            search_terms=[],
            needs_clarification=True,
            clarification_message="Please be a bit more specific, for example: 'give me IPL news' or 'AI news'.",
        )

    for alias, (topic, search_terms) in TOPIC_ALIASES.items():
        if alias in normalized:
            return ParsedQuery(
                raw_query=query,
                normalized_query=normalized,
                topic=topic,
                search_terms=search_terms,
                needs_clarification=False,
            )

    tokens = [token for token in re.findall(r"[a-z0-9]+", normalized) if token not in STOPWORDS]
    if not tokens:
        return ParsedQuery(
            raw_query=query,
            normalized_query=normalized,
            topic=None,
            search_terms=[],
            needs_clarification=True,
            clarification_message="I need a clearer topic before I can fetch relevant news.",
        )

    topic = " ".join(token.upper() if len(token) <= 4 else token.title() for token in tokens[:3])
    return ParsedQuery(
        raw_query=query,
        normalized_query=normalized,
        topic=topic,
        search_terms=tokens[:5],
        needs_clarification=False,
    )
