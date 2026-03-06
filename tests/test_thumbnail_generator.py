"""
Tests for modules/thumbnail_generator.py
"""

import os
import sys
import tempfile
import unittest

sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

from modules.thumbnail_generator import create_thumbnail, THUMBNAIL_WIDTH, THUMBNAIL_HEIGHT


class TestThumbnailGenerator(unittest.TestCase):
    """Unit tests for the create_thumbnail function."""

    def test_creates_valid_png_file(self):
        """create_thumbnail should create a valid PNG file."""
        from PIL import Image

        with tempfile.TemporaryDirectory() as tmpdir:
            output_path = os.path.join(tmpdir, "test_thumbnail.png")
            result = create_thumbnail(title="Test Title", output_path=output_path)

            self.assertTrue(os.path.exists(result))
            img = Image.open(result)
            self.assertEqual(img.format, "PNG")

    def test_thumbnail_dimensions(self):
        """create_thumbnail should produce a 1280x720 image."""
        from PIL import Image

        with tempfile.TemporaryDirectory() as tmpdir:
            output_path = os.path.join(tmpdir, "test_thumb_dims.png")
            create_thumbnail(title="Dimensions Test", output_path=output_path)

            img = Image.open(output_path)
            self.assertEqual(img.size, (THUMBNAIL_WIDTH, THUMBNAIL_HEIGHT))
            self.assertEqual(img.size, (1280, 720))

    def test_custom_background_color(self):
        """create_thumbnail should use the provided background color."""
        from PIL import Image

        with tempfile.TemporaryDirectory() as tmpdir:
            output_path = os.path.join(tmpdir, "blue_thumbnail.png")
            create_thumbnail(title="Blue BG", bg_color="#0000FF", output_path=output_path)

            img = Image.open(output_path)
            # Sample a corner pixel — should be blue-ish
            r, g, b = img.getpixel((5, 5))
            self.assertGreater(b, g)
            self.assertGreater(b, r)

    def test_with_subtitle(self):
        """create_thumbnail should succeed when subtitle is provided."""
        from PIL import Image

        with tempfile.TemporaryDirectory() as tmpdir:
            output_path = os.path.join(tmpdir, "subtitle_thumb.png")
            result = create_thumbnail(
                title="Main Title",
                subtitle="This is a subtitle",
                output_path=output_path,
            )
            self.assertTrue(os.path.exists(result))
            img = Image.open(result)
            self.assertEqual(img.size, (1280, 720))

    def test_auto_output_path_created(self):
        """create_thumbnail should create file in output/thumbnails/ when no path given."""
        # We need to avoid polluting the real output dir in tests —
        # patch OUTPUT_DIR to a temp location.
        import modules.thumbnail_generator as tg

        with tempfile.TemporaryDirectory() as tmpdir:
            original_dir = tg.OUTPUT_DIR
            tg.OUTPUT_DIR = tmpdir
            try:
                result = create_thumbnail(title="Auto Path Test")
                self.assertTrue(os.path.exists(result))
                self.assertTrue(result.startswith(tmpdir))
            finally:
                tg.OUTPUT_DIR = original_dir

    def test_returns_string_path(self):
        """create_thumbnail should return a string file path."""
        with tempfile.TemporaryDirectory() as tmpdir:
            output_path = os.path.join(tmpdir, "return_type.png")
            result = create_thumbnail(title="Return Type", output_path=output_path)
            self.assertIsInstance(result, str)


if __name__ == "__main__":
    unittest.main()
