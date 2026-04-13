import unittest

from app.models import Article
from app.summarizer import build_extractive_summary, rank_and_deduplicate_articles


def make_article(title: str, source: str, description: str | None = None) -> Article:
    return Article(
        title=title,
        source=source,
        url="https://example.com/story",
        published_at="2026-04-11T10:00:00Z",
        description=description,
        content="Detailed coverage of the story with context.",
    )


class SummarizerTests(unittest.TestCase):
    def test_rank_and_deduplicate_articles_removes_duplicates(self) -> None:
        articles = [
            make_article("IPL 2026 season starts strong", "Source A", "Opening matches draw attention"),
            make_article("IPL 2026 season starts strong", "Source B", "Duplicate headline"),
            make_article("Mumbai wins thriller in IPL", "Source C", "Close finish in late chase"),
        ]

        ranked = rank_and_deduplicate_articles(articles)
        self.assertEqual(len(ranked), 2)

    def test_build_extractive_summary_returns_highlights(self) -> None:
        articles = [
            make_article("IPL playoffs race heats up", "Source A", "Teams push for a top-four place"),
            make_article("Star batter returns for key IPL clash", "Source B", "Return changes playoff equation"),
        ]

        summary, highlights = build_extractive_summary("IPL", articles)
        self.assertIn("IPL", summary)
        self.assertEqual(len(highlights), 2)
        self.assertTrue(highlights[0].startswith("Source A:"))


if __name__ == "__main__":
    unittest.main()
