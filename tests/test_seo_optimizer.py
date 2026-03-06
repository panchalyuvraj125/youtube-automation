"""
Tests for modules/seo_optimizer.py
"""

import json
import os
import sys
import unittest
from unittest.mock import MagicMock, patch

sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

from modules.seo_optimizer import optimize_seo


MOCK_SEO = {
    "titles": [
        "10 Best AI Tools in 2024",
        "Top AI Tools You Need Right Now",
        "AI Tools That Will Change Your Life",
        "The Ultimate AI Tools Guide",
        "Must-Have AI Tools for Beginners",
        "AI Tools Ranked from Best to Worst",
        "Free AI Tools That Are Actually Good",
        "AI Tools Every Creator Should Know",
        "Best AI Tools for Productivity",
        "Hidden AI Tools Nobody Talks About",
    ],
    "description": (
        "Discover the best AI tools available in 2024.\n\n"
        "Timestamps:\n0:00 - Intro\n1:00 - Tool 1\n\n"
        "Links:\nhttps://example.com"
    ),
    "tags": [
        "ai tools", "artificial intelligence", "productivity", "tech", "2024",
        "best ai", "free ai", "chatgpt", "automation", "machine learning",
        "deep learning", "openai", "google ai", "microsoft ai", "ai apps",
        "ai software", "ai for beginners", "ai tutorial", "ai tips", "ai news",
        "top ai", "ai review", "ai comparison", "ai workflow", "ai writing",
        "ai image", "ai video", "ai audio", "ai coding", "ai marketing",
    ],
    "hashtags": [
        "#AITools", "#ArtificialIntelligence", "#Tech2024", "#Productivity", "#GoogleAI"
    ],
}


class TestSEOOptimizer(unittest.TestCase):
    """Unit tests for the optimize_seo function."""

    @patch("modules.seo_optimizer.get_gemini_key", return_value="fake-key")
    @patch("modules.seo_optimizer.genai")
    def test_optimize_seo_returns_required_keys(self, mock_genai, _mock_key):
        """optimize_seo should return a dict with titles, description, tags, hashtags."""
        mock_client = MagicMock()
        mock_genai.Client.return_value = mock_client
        mock_client.models.generate_content.return_value = MagicMock(text=json.dumps(MOCK_SEO))

        result = optimize_seo(topic="AI Tools", niche="tech")

        for key in ("titles", "description", "tags", "hashtags"):
            self.assertIn(key, result, f"Missing key: {key}")

    @patch("modules.seo_optimizer.get_gemini_key", return_value="fake-key")
    @patch("modules.seo_optimizer.genai")
    def test_titles_is_list_of_10(self, mock_genai, _mock_key):
        """titles should be a list of exactly 10 items."""
        mock_client = MagicMock()
        mock_genai.Client.return_value = mock_client
        mock_client.models.generate_content.return_value = MagicMock(text=json.dumps(MOCK_SEO))

        result = optimize_seo(topic="AI Tools", niche="tech")
        self.assertIsInstance(result["titles"], list)
        self.assertEqual(len(result["titles"]), 10)

    @patch("modules.seo_optimizer.get_gemini_key", return_value="fake-key")
    @patch("modules.seo_optimizer.genai")
    def test_tags_has_at_least_30(self, mock_genai, _mock_key):
        """tags should contain at least 30 items."""
        mock_client = MagicMock()
        mock_genai.Client.return_value = mock_client
        mock_client.models.generate_content.return_value = MagicMock(text=json.dumps(MOCK_SEO))

        result = optimize_seo(topic="AI Tools", niche="tech")
        self.assertIsInstance(result["tags"], list)
        self.assertGreaterEqual(len(result["tags"]), 30)

    @patch("modules.seo_optimizer.get_gemini_key", return_value="fake-key")
    @patch("modules.seo_optimizer.genai")
    def test_hashtags_count_range(self, mock_genai, _mock_key):
        """hashtags should be a list of 5 to 10 items."""
        mock_client = MagicMock()
        mock_genai.Client.return_value = mock_client
        mock_client.models.generate_content.return_value = MagicMock(text=json.dumps(MOCK_SEO))

        result = optimize_seo(topic="AI Tools", niche="tech")
        self.assertIsInstance(result["hashtags"], list)
        self.assertGreaterEqual(len(result["hashtags"]), 5)
        self.assertLessEqual(len(result["hashtags"]), 10)

    @patch("modules.seo_optimizer.get_gemini_key", return_value="fake-key")
    @patch("modules.seo_optimizer.genai")
    def test_description_is_string(self, mock_genai, _mock_key):
        """description should be a non-empty string."""
        mock_client = MagicMock()
        mock_genai.Client.return_value = mock_client
        mock_client.models.generate_content.return_value = MagicMock(text=json.dumps(MOCK_SEO))

        result = optimize_seo(topic="AI Tools", niche="tech")
        self.assertIsInstance(result["description"], str)
        self.assertTrue(len(result["description"]) > 0)

    @patch("modules.seo_optimizer.get_gemini_key", return_value="fake-key")
    @patch("modules.seo_optimizer.genai")
    def test_optimize_seo_saves_file(self, mock_genai, _mock_key):
        """optimize_seo should save a JSON file and include its path."""
        mock_client = MagicMock()
        mock_genai.Client.return_value = mock_client
        mock_client.models.generate_content.return_value = MagicMock(text=json.dumps(MOCK_SEO))

        result = optimize_seo(topic="AI Tools", niche="tech")
        self.assertIn("_output_file", result)
        self.assertTrue(os.path.exists(result["_output_file"]))

    @patch("modules.seo_optimizer.get_gemini_key", return_value="fake-key")
    @patch("modules.seo_optimizer.genai")
    def test_optimize_seo_raises_on_api_error(self, mock_genai, _mock_key):
        """optimize_seo should raise RuntimeError on Gemini API failure."""
        mock_client = MagicMock()
        mock_genai.Client.return_value = mock_client
        mock_client.models.generate_content.side_effect = Exception("fail")

        with self.assertRaises(RuntimeError):
            optimize_seo(topic="AI Tools", niche="tech")


if __name__ == "__main__":
    unittest.main()
