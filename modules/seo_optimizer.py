"""
SEO Optimizer Module.

Uses Google Gemini API to generate optimized YouTube titles, descriptions,
tags, and hashtags.
"""

import json
import logging
import os
from datetime import datetime

import google.generativeai as genai

from config import get_gemini_key

logger = logging.getLogger(__name__)

OUTPUT_DIR = os.path.join(os.path.dirname(os.path.dirname(__file__)), "output", "seo")


def optimize_seo(
    topic: str,
    niche: str,
    target_audience: str = "general",
) -> dict:
    """
    Generate SEO-optimized metadata for a YouTube video.

    Parameters:
        topic (str): The video topic.
        niche (str): The YouTube channel niche.
        target_audience (str): Description of the target audience (default: "general").

    Returns:
        dict: A dictionary containing:
            - titles (list): 10 title options ranked by click-worthiness.
            - description (str): Optimized description with keywords, timestamp
              placeholders, and a links section.
            - tags (list): 30+ relevant tags.
            - hashtags (list): 5-10 hashtags.

    Raises:
        RuntimeError: If the Gemini API call fails.
    """
    logger.info("Optimizing SEO for topic='%s', niche='%s'", topic, niche)

    prompt = f"""Generate SEO-optimized YouTube metadata for the following video.

Topic: {topic}
Niche: {niche}
Target Audience: {target_audience}

Return a JSON object with these exact keys:
- "titles": A list of exactly 10 title options, ordered from most to least click-worthy.
- "description": A detailed, keyword-rich description (~300 words) that includes:
    * A compelling opening paragraph.
    * A "Timestamps:" section with placeholder entries like "0:00 - Intro".
    * A "Links:" section with placeholder links.
    * Relevant keywords naturally integrated.
- "tags": A list of at least 30 relevant tags (strings, no # prefix).
- "hashtags": A list of 5 to 10 hashtags (strings, with # prefix).

Return only valid JSON with no extra text."""

    try:
        genai.configure(api_key=get_gemini_key())
        model = genai.GenerativeModel("gemini-1.5-flash")
        response = model.generate_content(prompt)
        raw = response.text.strip()
        if raw.startswith("```"):
            raw = raw.split("```")[1]
            if raw.startswith("json"):
                raw = raw[4:]
        seo_data = json.loads(raw)
    except json.JSONDecodeError as exc:
        logger.error("Failed to parse Gemini response as JSON: %s", exc)
        raise RuntimeError(f"Failed to parse SEO JSON: {exc}") from exc
    except Exception as exc:
        logger.error("Gemini API error: %s", exc)
        raise RuntimeError(f"Gemini API error: {exc}") from exc

    # Validate required keys
    required_keys = ["titles", "description", "tags", "hashtags"]
    for key in required_keys:
        if key not in seo_data:
            raise RuntimeError(f"SEO response missing required key: '{key}'")

    # Save to file
    os.makedirs(OUTPUT_DIR, exist_ok=True)
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    safe_topic = "".join(c if c.isalnum() or c in "-_" else "_" for c in topic)[:50]
    filename = f"seo_{safe_topic}_{timestamp}.json"
    filepath = os.path.join(OUTPUT_DIR, filename)
    with open(filepath, "w", encoding="utf-8") as fh:
        json.dump(seo_data, fh, indent=2, ensure_ascii=False)

    logger.info("SEO data saved to %s", filepath)
    seo_data["_output_file"] = filepath
    return seo_data
