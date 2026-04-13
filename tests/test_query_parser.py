import unittest

from app.query_parser import parse_user_query


class QueryParserTests(unittest.TestCase):
    def test_parse_known_topic_ipl(self) -> None:
        parsed = parse_user_query("give me IPL news")
        self.assertEqual(parsed.topic, "IPL")
        self.assertEqual(parsed.search_terms[0], "IPL")
        self.assertFalse(parsed.needs_clarification)

    def test_parse_vague_news_query(self) -> None:
        parsed = parse_user_query("news")
        self.assertTrue(parsed.needs_clarification)
        self.assertIn("specific", (parsed.clarification_message or "").lower())

    def test_parse_freeform_topic(self) -> None:
        parsed = parse_user_query("startup funding in india")
        self.assertFalse(parsed.needs_clarification)
        self.assertEqual(parsed.topic, "Startup Funding IN")


if __name__ == "__main__":
    unittest.main()
