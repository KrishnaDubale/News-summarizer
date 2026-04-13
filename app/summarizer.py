from __future__ import annotations

import re
from collections import Counter

from app.models import Article


def rank_and_deduplicate_articles(articles: list[Article]) -> list[Article]:
    seen_signatures: set[str] = set()
    ranked: list[tuple[int, Article]] = []

    for article in articles:
        signature = _signature(article.title)
        if signature in seen_signatures:
            continue
        seen_signatures.add(signature)
        score = _score_article(article)
        ranked.append((score, article))

    ranked.sort(key=lambda item: item[0], reverse=True)
    return [article for _, article in ranked]


def build_extractive_summary(topic: str | None, articles: list[Article]) -> tuple[str, list[str]]:
    if not articles:
        fallback_topic = topic or "this topic"
        return (
            f"I could not find fresh articles about {fallback_topic}. Try another search phrase.",
            [],
        )

    top_articles = articles[:5]
    key_phrases = _extract_key_phrases(top_articles)
    topic_label = topic or "your topic"
    source_count = len({article.source for article in top_articles})

    summary = (
        f"Here is a quick summary of the latest {topic_label} coverage based on "
        f"{len(top_articles)} recent articles from {source_count} sources. "
        f"The main themes are {', '.join(key_phrases[:3]) if key_phrases else 'recent developments and updates'}."
    )
    highlights = [_make_highlight(article) for article in top_articles[:3]]
    return summary, highlights


def _score_article(article: Article) -> int:
    score = 0
    score += 3 if article.description else 0
    score += 2 if article.content else 0
    score += 1 if article.published_at else 0
    score += min(len(article.title.split()), 12)
    return score


def _signature(text: str) -> str:
    tokens = [token for token in re.findall(r"[a-z0-9]+", text.lower()) if len(token) > 2]
    return " ".join(tokens[:8])


def _extract_key_phrases(articles: list[Article]) -> list[str]:
    counter: Counter[str] = Counter()
    for article in articles:
        combined = " ".join(filter(None, [article.title, article.description, article.content]))
        words = [
            word
            for word in re.findall(r"[a-zA-Z]{4,}", combined.lower())
            if word
            not in {
                "that",
                "with",
                "from",
                "have",
                "will",
                "this",
                "about",
                "after",
                "their",
                "news",
                "latest",
                "says",
            }
        ]
        counter.update(words)
    return [word.title() for word, _ in counter.most_common(5)]


def _make_highlight(article: Article) -> str:
    detail = article.description or article.content or "Fresh coverage is available."
    detail = detail.rstrip(".")
    return f"{article.source}: {article.title}. {detail}."
