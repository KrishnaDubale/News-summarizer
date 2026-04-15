import ssl
import unittest
from unittest.mock import MagicMock, patch

from app.groq_client import summarize_with_groq
from app.models import Article
from app.newsapi import fetch_articles


class ClientSSLTests(unittest.TestCase):
    @patch("app.newsapi.urlopen")
    @patch("app.newsapi.settings")
    def test_newsapi_uses_ssl_context(self, mock_settings, mock_urlopen) -> None:
        mock_settings.news_api_key = "news-key"
        mock_settings.article_limit = 8
        mock_settings.news_api_base_url = "https://newsapi.org/v2/everything"
        mock_settings.request_timeout_seconds = 10

        response = MagicMock()
        response.read.return_value = b'{"status":"ok","articles":[]}'
        mock_urlopen.return_value.__enter__.return_value = response

        fetch_articles(["IPL"])

        context = mock_urlopen.call_args.kwargs["context"]
        self.assertIsInstance(context, ssl.SSLContext)

    @patch("app.groq_client.urlopen")
    @patch("app.groq_client.settings")
    def test_groq_uses_ssl_context(self, mock_settings, mock_urlopen) -> None:
        mock_settings.groq_api_key = "groq-key"
        mock_settings.groq_api_base_url = "https://api.groq.com/openai/v1/chat/completions"
        mock_settings.groq_model = "llama-3.3-70b-versatile"
        mock_settings.request_timeout_seconds = 10

        response = MagicMock()
        response.read.return_value = (
            b'{"choices":[{"message":{"content":"{\\"summary\\":\\"Short summary\\",\\"highlights\\":[\\"One\\",\\"Two\\"]}"}}]}'
        )
        mock_urlopen.return_value.__enter__.return_value = response

        summary, highlights = summarize_with_groq(
            "IPL",
            [
                Article(
                    title="IPL playoffs race heats up",
                    source="Source A",
                    url="https://example.com/story",
                    published_at="2026-04-15T10:00:00Z",
                    description="Teams push for a top-four place",
                    content="Detailed coverage.",
                )
            ],
        )

        context = mock_urlopen.call_args.kwargs["context"]
        self.assertIsInstance(context, ssl.SSLContext)
        self.assertEqual(summary, "Short summary")
        self.assertEqual(highlights, ["One", "Two"])


if __name__ == "__main__":
    unittest.main()
