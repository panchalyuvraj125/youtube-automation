"""
Script Generator Module.

Uses OpenAI API (GPT model) to generate full YouTube video scripts.
"""

import json
import logging
import os
from datetime import datetime
from typing import List

import openai

from config import get_openai_key

logger = logging.getLogger(__name__)

OUTPUT_DIR = os.path.join(os.path.dirname(os.path.dirname(__file__)), "output", "scripts")


def generate_script(
    topic: str,
    niche: str,
    tone: str = "engaging",
    duration_minutes: int = 10,
) -> dict:
    """
    Generate a full YouTube video script using OpenAI GPT.

    Parameters:
        topic (str): The video topic.
        niche (str): The YouTube channel niche (e.g., "tech", "cooking").
        tone (str): The tone/style of the script (default: "engaging").
        duration_minutes (int): Approximate video duration in minutes (default: 10).

    Returns:
        dict: A dictionary containing:
            - hook (str): Opening hook to grab attention.
            - intro (str): Introduction section.
            - body (list): List of dicts with 'header' and 'content' keys.
            - call_to_action (str): CTA section.
            - outro (str): Closing section.

    Raises:
        RuntimeError: If the OpenAI API call fails.
    """
    logger.info("Generating script for topic='%s', niche='%s'", topic, niche)

    prompt = f"""Create a complete YouTube video script for a {duration_minutes}-minute video.

Topic: {topic}
Niche: {niche}
Tone: {tone}

Return a JSON object with these exact keys:
- "hook": A compelling 2-3 sentence opening that grabs attention immediately.
- "intro": A 1-2 paragraph introduction that sets up the video.
- "body": A list of 4-6 sections, each with "header" (section title) and "content" (detailed script text).
- "call_to_action": Encourage viewers to like, subscribe, and comment.
- "outro": Friendly closing remarks and tease of upcoming content.

Return only valid JSON with no extra text."""

    try:
        client = openai.OpenAI(api_key=get_openai_key())
        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {"role": "system", "content": "You are an expert YouTube scriptwriter."},
                {"role": "user", "content": prompt},
            ],
            temperature=0.7,
        )
        raw = response.choices[0].message.content.strip()
        # Strip markdown code fences if present
        if raw.startswith("```"):
            raw = raw.split("```")[1]
            if raw.startswith("json"):
                raw = raw[4:]
        script_data = json.loads(raw)
    except openai.OpenAIError as exc:
        logger.error("OpenAI API error: %s", exc)
        raise RuntimeError(f"OpenAI API error: {exc}") from exc
    except json.JSONDecodeError as exc:
        logger.error("Failed to parse OpenAI response as JSON: %s", exc)
        raise RuntimeError(f"Failed to parse script JSON: {exc}") from exc

    # Validate required keys
    required_keys = ["hook", "intro", "body", "call_to_action", "outro"]
    for key in required_keys:
        if key not in script_data:
            raise RuntimeError(f"Script response missing required key: '{key}'")

    # Save to file
    os.makedirs(OUTPUT_DIR, exist_ok=True)
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    safe_topic = "".join(c if c.isalnum() or c in "-_" else "_" for c in topic)[:50]
    filename = f"script_{safe_topic}_{timestamp}.json"
    filepath = os.path.join(OUTPUT_DIR, filename)
    with open(filepath, "w", encoding="utf-8") as fh:
        json.dump(script_data, fh, indent=2, ensure_ascii=False)

    logger.info("Script saved to %s", filepath)
    script_data["_output_file"] = filepath
    return script_data
