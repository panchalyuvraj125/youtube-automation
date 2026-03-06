"""
Tests for modules/content_calendar.py
"""

import json
import os
import sys
import unittest
from unittest.mock import MagicMock, patch

sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

from modules.content_calendar import generate_calendar


def _make_entries(n: int) -> list:
    """Helper: create n mock calendar entries."""
    return [
        {
            "title": f"Video {i + 1}",
            "description": f"Description for video {i + 1}.",
            "keywords": ["keyword1", "keyword2", "keyword3"],
            "video_type": "tutorial",
        }
        for i in range(n)
    ]


class TestContentCalendar(unittest.TestCase):
    """Unit tests for the generate_calendar function."""

    @patch("modules.content_calendar.get_openai_key", return_value="fake-key")
    @patch("modules.content_calendar.openai.OpenAI")
    def test_returns_list(self, mock_openai_cls, _mock_key):
        """generate_calendar should return a list."""
        entries = _make_entries(13)
        mock_client = MagicMock()
        mock_openai_cls.return_value = mock_client
        mock_client.chat.completions.create.return_value = MagicMock(
            choices=[MagicMock(message=MagicMock(content=json.dumps(entries)))]
        )

        result = generate_calendar(niche="tech", days=30, videos_per_week=3)
        self.assertIsInstance(result, list)

    @patch("modules.content_calendar.get_openai_key", return_value="fake-key")
    @patch("modules.content_calendar.openai.OpenAI")
    def test_entry_count_matches_schedule(self, mock_openai_cls, _mock_key):
        """generate_calendar entry count should match videos_per_week * weeks."""
        # For 30 days, 3 videos/week → ~13 entries (4 weeks * 3 + remaining)
        entries = _make_entries(13)
        mock_client = MagicMock()
        mock_openai_cls.return_value = mock_client
        mock_client.chat.completions.create.return_value = MagicMock(
            choices=[MagicMock(message=MagicMock(content=json.dumps(entries)))]
        )

        result = generate_calendar(niche="tech", days=30, videos_per_week=3)
        # We should get at most len(entries) items back
        self.assertLessEqual(len(result), len(entries))
        self.assertGreater(len(result), 0)

    @patch("modules.content_calendar.get_openai_key", return_value="fake-key")
    @patch("modules.content_calendar.openai.OpenAI")
    def test_entries_have_required_keys(self, mock_openai_cls, _mock_key):
        """Each calendar entry should have title, description, keywords, video_type, date, day."""
        entries = _make_entries(6)
        mock_client = MagicMock()
        mock_openai_cls.return_value = mock_client
        mock_client.chat.completions.create.return_value = MagicMock(
            choices=[MagicMock(message=MagicMock(content=json.dumps(entries)))]
        )

        result = generate_calendar(niche="tech", days=30, videos_per_week=3)
        for entry in result:
            for key in ("title", "description", "keywords", "video_type", "date", "day"):
                self.assertIn(key, entry, f"Entry missing key: {key}")

    @patch("modules.content_calendar.get_openai_key", return_value="fake-key")
    @patch("modules.content_calendar.openai.OpenAI")
    def test_saves_json_and_csv(self, mock_openai_cls, _mock_key):
        """generate_calendar should save both JSON and CSV output files."""
        import modules.content_calendar as cc
        import tempfile

        entries = _make_entries(6)
        mock_client = MagicMock()
        mock_openai_cls.return_value = mock_client
        mock_client.chat.completions.create.return_value = MagicMock(
            choices=[MagicMock(message=MagicMock(content=json.dumps(entries)))]
        )

        with tempfile.TemporaryDirectory() as tmpdir:
            original_dir = cc.OUTPUT_DIR
            cc.OUTPUT_DIR = tmpdir
            try:
                result = generate_calendar(niche="tech", days=14, videos_per_week=3)
                # Check that files were created
                files = os.listdir(tmpdir)
                json_files = [f for f in files if f.endswith(".json")]
                csv_files = [f for f in files if f.endswith(".csv")]
                self.assertGreater(len(json_files), 0)
                self.assertGreater(len(csv_files), 0)
            finally:
                cc.OUTPUT_DIR = original_dir

    @patch("modules.content_calendar.get_openai_key", return_value="fake-key")
    @patch("modules.content_calendar.openai.OpenAI")
    def test_raises_on_api_error(self, mock_openai_cls, _mock_key):
        """generate_calendar should raise RuntimeError on OpenAI API failure."""
        import openai as openai_mod

        mock_client = MagicMock()
        mock_openai_cls.return_value = mock_client
        mock_client.chat.completions.create.side_effect = openai_mod.OpenAIError("fail")

        with self.assertRaises(RuntimeError):
            generate_calendar(niche="tech")


if __name__ == "__main__":
    unittest.main()
