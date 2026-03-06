"""
Tests for modules/upload_scheduler.py
"""

import os
import sys
import tempfile
import unittest
from unittest.mock import MagicMock, patch, call

sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

from modules.upload_scheduler import upload_video


class TestUploadScheduler(unittest.TestCase):
    """Unit tests for the upload_video function."""

    def _make_video_file(self, tmpdir: str) -> str:
        """Create a dummy video file and return its path."""
        path = os.path.join(tmpdir, "test_video.mp4")
        with open(path, "wb") as fh:
            fh.write(b"\x00" * 1024)
        return path

    @patch("modules.upload_scheduler.authenticate_youtube")
    def test_upload_constructs_correct_body(self, mock_auth):
        """upload_video should call YouTube API with the correct request body."""
        mock_youtube = MagicMock()
        mock_auth.return_value = mock_youtube

        mock_insert = MagicMock()
        mock_youtube.videos.return_value.insert.return_value = mock_insert
        mock_insert.next_chunk.return_value = (None, {"id": "abc123", "status": {"privacyStatus": "private"}})

        with tempfile.TemporaryDirectory() as tmpdir:
            video_path = self._make_video_file(tmpdir)
            result = upload_video(
                video_path=video_path,
                title="My Test Video",
                description="A test description",
                tags=["tag1", "tag2"],
                category_id="22",
                privacy_status="private",
            )

        # Verify that videos().insert() was called
        mock_youtube.videos.return_value.insert.assert_called_once()
        call_kwargs = mock_youtube.videos.return_value.insert.call_args

        # Check body contains expected snippet and status fields
        body = call_kwargs.kwargs.get("body") or call_kwargs[1].get("body")
        self.assertEqual(body["snippet"]["title"], "My Test Video")
        self.assertEqual(body["snippet"]["description"], "A test description")
        self.assertIn("tag1", body["snippet"]["tags"])
        self.assertIn("tag2", body["snippet"]["tags"])
        self.assertEqual(body["snippet"]["categoryId"], "22")
        self.assertEqual(body["status"]["privacyStatus"], "private")

    @patch("modules.upload_scheduler.authenticate_youtube")
    def test_upload_returns_video_id_and_url(self, mock_auth):
        """upload_video should return a dict with video_id and url."""
        mock_youtube = MagicMock()
        mock_auth.return_value = mock_youtube

        mock_insert = MagicMock()
        mock_youtube.videos.return_value.insert.return_value = mock_insert
        mock_insert.next_chunk.return_value = (None, {"id": "xyz789", "status": {}})

        with tempfile.TemporaryDirectory() as tmpdir:
            video_path = self._make_video_file(tmpdir)
            result = upload_video(
                video_path=video_path,
                title="Title",
                description="Desc",
                tags=[],
            )

        self.assertEqual(result["video_id"], "xyz789")
        self.assertEqual(result["url"], "https://www.youtube.com/watch?v=xyz789")

    @patch("modules.upload_scheduler.authenticate_youtube")
    def test_upload_raises_if_video_not_found(self, _mock_auth):
        """upload_video should raise FileNotFoundError if video file doesn't exist."""
        with self.assertRaises(FileNotFoundError):
            upload_video(
                video_path="/nonexistent/video.mp4",
                title="Title",
                description="Desc",
                tags=[],
            )

    @patch("modules.upload_scheduler.authenticate_youtube")
    def test_upload_with_publish_at_sets_private(self, mock_auth):
        """upload_video with publish_at should set privacyStatus to private."""
        mock_youtube = MagicMock()
        mock_auth.return_value = mock_youtube

        mock_insert = MagicMock()
        mock_youtube.videos.return_value.insert.return_value = mock_insert
        mock_insert.next_chunk.return_value = (None, {"id": "sched1", "status": {}})

        with tempfile.TemporaryDirectory() as tmpdir:
            video_path = self._make_video_file(tmpdir)
            upload_video(
                video_path=video_path,
                title="Scheduled Video",
                description="Desc",
                tags=[],
                privacy_status="public",
                publish_at="2025-01-01T10:00:00Z",
            )

        call_kwargs = mock_youtube.videos.return_value.insert.call_args
        body = call_kwargs.kwargs.get("body") or call_kwargs[1].get("body")
        # When publish_at is set, privacyStatus must be "private"
        self.assertEqual(body["status"]["privacyStatus"], "private")
        self.assertEqual(body["status"]["publishAt"], "2025-01-01T10:00:00Z")

    @patch("modules.upload_scheduler.authenticate_youtube")
    def test_upload_raises_runtime_error_on_api_failure(self, mock_auth):
        """upload_video should raise RuntimeError if the API call fails."""
        mock_youtube = MagicMock()
        mock_auth.return_value = mock_youtube

        mock_insert = MagicMock()
        mock_youtube.videos.return_value.insert.return_value = mock_insert
        mock_insert.next_chunk.side_effect = Exception("Upload failure")

        with tempfile.TemporaryDirectory() as tmpdir:
            video_path = self._make_video_file(tmpdir)
            with self.assertRaises(RuntimeError):
                upload_video(
                    video_path=video_path,
                    title="Error Video",
                    description="Desc",
                    tags=[],
                )


if __name__ == "__main__":
    unittest.main()
