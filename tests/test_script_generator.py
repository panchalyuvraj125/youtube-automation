"""
Tests for modules/script_generator.py
"""

import json
import os
import sys
import unittest
from unittest.mock import MagicMock, patch

# Ensure project root is on the path
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

from modules.script_generator import generate_script


MOCK_SCRIPT = {
    "hook": "Did you know AI can write your scripts?",
    "intro": "Welcome to this video about AI tools.",
    "body": [
        {"header": "Section 1", "content": "Content of section one."},
        {"header": "Section 2", "content": "Content of section two."},
    ],
    "call_to_action": "Like, subscribe, and hit the bell icon!",
    "outro": "Thanks for watching. See you next time!",
}


class TestScriptGenerator(unittest.TestCase):
    """Unit tests for the generate_script function."""

    @patch("modules.script_generator.get_gemini_key", return_value="fake-key")
    @patch("modules.script_generator.genai")
    def test_generate_script_returns_required_keys(self, mock_genai, _mock_key):
        """generate_script should return a dict with all required keys."""
        mock_model = MagicMock()
        mock_genai.GenerativeModel.return_value = mock_model
        mock_model.generate_content.return_value = MagicMock(
            text=json.dumps(MOCK_SCRIPT)
        )

        result = generate_script(topic="AI Tools", niche="tech")

        self.assertIsInstance(result, dict)
        for key in ("hook", "intro", "body", "call_to_action", "outro"):
            self.assertIn(key, result, f"Missing key: {key}")

    @patch("modules.script_generator.get_gemini_key", return_value="fake-key")
    @patch("modules.script_generator.genai")
    def test_generate_script_body_is_list(self, mock_genai, _mock_key):
        """generate_script body should be a list of sections."""
        mock_model = MagicMock()
        mock_genai.GenerativeModel.return_value = mock_model
        mock_model.generate_content.return_value = MagicMock(
            text=json.dumps(MOCK_SCRIPT)
        )

        result = generate_script(topic="AI Tools", niche="tech")
        self.assertIsInstance(result["body"], list)
        self.assertTrue(len(result["body"]) > 0)

    @patch("modules.script_generator.get_gemini_key", return_value="fake-key")
    @patch("modules.script_generator.genai")
    def test_generate_script_saves_file(self, mock_genai, _mock_key):
        """generate_script should save a JSON file and return its path."""
        mock_model = MagicMock()
        mock_genai.GenerativeModel.return_value = mock_model
        mock_model.generate_content.return_value = MagicMock(
            text=json.dumps(MOCK_SCRIPT)
        )

        result = generate_script(topic="Test Topic", niche="tech")
        self.assertIn("_output_file", result)
        self.assertTrue(os.path.exists(result["_output_file"]))

    @patch("modules.script_generator.get_gemini_key", return_value="fake-key")
    @patch("modules.script_generator.genai")
    def test_generate_script_raises_on_api_error(self, mock_genai, _mock_key):
        """generate_script should raise RuntimeError on Gemini API failure."""
        mock_model = MagicMock()
        mock_genai.GenerativeModel.return_value = mock_model
        mock_model.generate_content.side_effect = Exception("API error")

        with self.assertRaises(RuntimeError):
            generate_script(topic="AI Tools", niche="tech")

    @patch("modules.script_generator.get_gemini_key", return_value="fake-key")
    @patch("modules.script_generator.genai")
    def test_generate_script_handles_markdown_fences(self, mock_genai, _mock_key):
        """generate_script should handle JSON wrapped in markdown code fences."""
        mock_model = MagicMock()
        mock_genai.GenerativeModel.return_value = mock_model
        fenced = f"```json\n{json.dumps(MOCK_SCRIPT)}\n```"
        mock_model.generate_content.return_value = MagicMock(text=fenced)

        result = generate_script(topic="AI Tools", niche="tech")
        self.assertIn("hook", result)


if __name__ == "__main__":
    unittest.main()
