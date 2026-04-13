import unittest
from unittest.mock import patch

from app.models import Article
from app.service import summarize_news


class ServiceTests(unittest.TestCase):
    @patch("app.service.fetch_articles", return_value=[])
    def test_service_returns_no_results(self, mock_fetch) -> None:
        response = summarize_news("give me IPL news")
        self.assertEqual(response.mode, "no-results")
        self.assertIsNone(response.error)
        mock_fetch.assert_called_once()

    def test_service_returns_clarification_for_vague_query(self) -> None:
        response = summarize_news("news")
        self.assertEqual(response.mode, "clarification")
        self.assertEqual(response.articles, [])

    @patch("app.service.summarize_with_groq", return_value=("Groq summary", ["Point 1", "Point 2"]))
    @patch("app.service.fetch_articles")
    @patch("app.service.settings")
    def test_service_uses_groq_when_available(self, mock_settings, mock_fetch, mock_groq) -> None:
        mock_settings.enable_llm_summary = True
        mock_settings.groq_api_key = "test-key"
        mock_settings.article_limit = 8
        mock_fetch.return_value = [
            Article(
                title="IPL playoffs race heats up",
                source="Source A",
                url="https://example.com/story",
                published_at="2026-04-11T10:00:00Z",
                description="Teams push for a top-four place",
                content="Detailed coverage.",
            )
        ]

        response = summarize_news("give me IPL news")
        self.assertEqual(response.mode, "groq")
        self.assertEqual(response.summary, "Groq summary")
        self.assertEqual(response.highlights, ["Point 1", "Point 2"])
        mock_groq.assert_called_once()


if __name__ == "__main__":
    unittest.main()
