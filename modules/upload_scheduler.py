"""
Upload Scheduler Module.

Handles video uploads to YouTube via the YouTube Data API v3
with OAuth2 authentication.
"""

import logging
import os
from typing import List, Optional

from googleapiclient.discovery import build
from googleapiclient.http import MediaFileUpload
from google_auth_oauthlib.flow import InstalledAppFlow
from google.oauth2.credentials import Credentials
from google.auth.transport.requests import Request

from config import get_youtube_config

logger = logging.getLogger(__name__)

SCOPES = [
    "https://www.googleapis.com/auth/youtube.upload",
    "https://www.googleapis.com/auth/youtube",
]
TOKEN_FILE = "token.json"
CLIENT_SECRET_FILE = "client_secret.json"


def authenticate_youtube():
    """
    Perform OAuth2 authentication and return an authorized YouTube API service.

    Uses stored credentials in token.json if available and valid;
    otherwise initiates the OAuth2 browser flow.

    Returns:
        googleapiclient.discovery.Resource: Authorized YouTube API service object.

    Raises:
        FileNotFoundError: If client_secret.json is not found.
        RuntimeError: If authentication fails.
    """
    return build("youtube", "v3", credentials=_get_credentials())


def _get_credentials() -> Credentials:
    """
    Obtain valid OAuth2 credentials, refreshing or re-authorizing as needed.

    This is a lower-level helper used by both authenticate_youtube() and the
    analytics dashboard so that both can share the same credential object
    without accessing private library internals.

    Returns:
        google.oauth2.credentials.Credentials: Valid OAuth2 credentials.

    Raises:
        FileNotFoundError: If client_secret.json is not found.
    """
    creds: Optional[Credentials] = None

    if os.path.exists(TOKEN_FILE):
        try:
            creds = Credentials.from_authorized_user_file(TOKEN_FILE, SCOPES)
        except Exception as exc:  # noqa: BLE001
            logger.warning("Failed to load token file: %s", exc)

    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            try:
                creds.refresh(Request())
            except Exception as exc:  # noqa: BLE001
                logger.warning("Token refresh failed: %s", exc)
                creds = None

        if not creds:
            if not os.path.exists(CLIENT_SECRET_FILE):
                raise FileNotFoundError(
                    f"OAuth2 client secrets file not found: {CLIENT_SECRET_FILE}. "
                    "Download it from the Google Cloud Console."
                )
            flow = InstalledAppFlow.from_client_secrets_file(CLIENT_SECRET_FILE, SCOPES)
            creds = flow.run_local_server(port=0)
            logger.info("OAuth2 flow completed successfully")

        with open(TOKEN_FILE, "w", encoding="utf-8") as token_fh:
            token_fh.write(creds.to_json())
            logger.info("Credentials saved to %s", TOKEN_FILE)

    return creds


def upload_video(
    video_path: str,
    title: str,
    description: str,
    tags: List[str],
    category_id: str = "22",
    privacy_status: str = "private",
    publish_at: Optional[str] = None,
) -> dict:
    """
    Upload a video to YouTube with the specified metadata.

    Parameters:
        video_path (str): Local path to the video file.
        title (str): Video title.
        description (str): Video description.
        tags (list): List of tag strings.
        category_id (str): YouTube category ID (default: "22" = People & Blogs).
        privacy_status (str): One of "private", "public", "unlisted" (default: "private").
        publish_at (str): ISO 8601 datetime string for scheduled publishing (e.g.,
            "2024-01-15T10:00:00Z"). Only used when privacy_status is "private".

    Returns:
        dict: Upload response containing at minimum:
            - video_id (str): The uploaded video's YouTube ID.
            - url (str): Full YouTube watch URL.
            - status (dict): Raw status object from the API response.

    Raises:
        FileNotFoundError: If the video file does not exist.
        RuntimeError: If the upload fails.
    """
    if not os.path.exists(video_path):
        raise FileNotFoundError(f"Video file not found: {video_path}")

    logger.info("Authenticating with YouTube API")
    youtube = authenticate_youtube()

    body = {
        "snippet": {
            "title": title,
            "description": description,
            "tags": tags,
            "categoryId": category_id,
        },
        "status": {
            "privacyStatus": privacy_status,
        },
    }

    if publish_at:
        body["status"]["publishAt"] = publish_at
        body["status"]["privacyStatus"] = "private"
        logger.info("Video scheduled for publishing at %s", publish_at)

    logger.info("Starting video upload: '%s'", title)
    try:
        media = MediaFileUpload(video_path, chunksize=-1, resumable=True)
        request = youtube.videos().insert(
            part=",".join(body.keys()),
            body=body,
            media_body=media,
        )
        response = None
        while response is None:
            status, response = request.next_chunk()
            if status:
                logger.debug("Upload progress: %d%%", int(status.progress() * 100))
    except Exception as exc:  # noqa: BLE001
        logger.error("Upload failed: %s", exc)
        raise RuntimeError(f"Video upload failed: {exc}") from exc

    video_id = response.get("id", "")
    result = {
        "video_id": video_id,
        "url": f"https://www.youtube.com/watch?v={video_id}",
        "status": response.get("status", {}),
    }
    logger.info("Upload successful. Video ID: %s", video_id)
    return result
