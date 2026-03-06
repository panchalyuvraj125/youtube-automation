"""
Central configuration module for YouTube Automation System.

Loads environment variables from .env file and provides
accessor functions for API keys and configuration values.
"""

import os
import logging
from dotenv import load_dotenv

load_dotenv()

logger = logging.getLogger(__name__)

# Logging configuration
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
)


def get_openai_key() -> str:
    """
    Retrieve the OpenAI API key from environment variables.

    Returns:
        str: The OpenAI API key.

    Raises:
        ValueError: If the OPENAI_API_KEY environment variable is not set.
    """
    key = os.getenv("OPENAI_API_KEY", "")
    if not key:
        raise ValueError(
            "OPENAI_API_KEY is not set. "
            "Please add it to your .env file or environment variables."
        )
    return key


def get_youtube_config() -> dict:
    """
    Retrieve all YouTube-related configuration values from environment variables.

    Returns:
        dict: A dictionary with keys:
            - client_id (str)
            - client_secret (str)
            - api_key (str)
    """
    return {
        "client_id": os.getenv("YOUTUBE_CLIENT_ID", ""),
        "client_secret": os.getenv("YOUTUBE_CLIENT_SECRET", ""),
        "api_key": os.getenv("YOUTUBE_API_KEY", ""),
    }
