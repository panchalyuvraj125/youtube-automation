"""
Content Calendar Module.

Uses Google Gemini API to generate a 30-day YouTube content calendar.
"""

import csv
import json
import logging
import os
from datetime import datetime, timedelta
from typing import List

import google.generativeai as genai

from config import get_gemini_key

logger = logging.getLogger(__name__)

OUTPUT_DIR = os.path.join(os.path.dirname(os.path.dirname(__file__)), "output", "calendars")


def generate_calendar(
    niche: str,
    days: int = 30,
    videos_per_week: int = 3,
) -> list:
    """
    Generate a YouTube content calendar using Google Gemini.

    Parameters:
        niche (str): The YouTube channel niche (e.g., "personal finance").
        days (int): Number of days to plan (default: 30).
        videos_per_week (int): Number of videos to schedule per week (default: 3).

    Returns:
        list: A list of dicts, one per scheduled video, each containing:
            - date (str): ISO date string (YYYY-MM-DD).
            - day (str): Day of the week (e.g., "Monday").
            - title (str): Suggested video title.
            - description (str): Brief description of the video.
            - keywords (list): Suggested keywords/tags.
            - video_type (str): Type of video (tutorial, listicle, how-to, etc.).

    Raises:
        RuntimeError: If the Gemini API call fails.
    """
    logger.info(
        "Generating %d-day content calendar for niche='%s', %d videos/week",
        days,
        niche,
        videos_per_week,
    )

    total_videos = (days // 7) * videos_per_week + min(videos_per_week, days % 7)

    prompt = f"""Create a YouTube content calendar for a {niche} channel.

Parameters:
- Duration: {days} days starting from today
- Videos per week: {videos_per_week}
- Total videos: approximately {total_videos}

Generate exactly {total_videos} video entries. Include a variety of formats:
tutorials, listicles, how-to guides, trending topic videos, Q&A, case studies.

Return a JSON array where each element has these exact keys:
- "title": Engaging video title.
- "description": 2-3 sentence description of what the video covers.
- "keywords": List of 5-8 relevant keyword strings.
- "video_type": One of: tutorial, listicle, how-to, trending, qa, case_study, review.

Return only a valid JSON array with no extra text."""

    try:
        genai.configure(api_key=get_gemini_key())
        model = genai.GenerativeModel("gemini-1.5-flash")
        response = model.generate_content(prompt)
        raw = response.text.strip()
        if raw.startswith("```"):
            raw = raw.split("```")[1]
            if raw.startswith("json"):
                raw = raw[4:]
        entries = json.loads(raw)
    except json.JSONDecodeError as exc:
        logger.error("Failed to parse Gemini response as JSON: %s", exc)
        raise RuntimeError(f"Failed to parse calendar JSON: {exc}") from exc
    except Exception as exc:
        logger.error("Gemini API error: %s", exc)
        raise RuntimeError(f"Gemini API error: {exc}") from exc

    # Assign dates — spread videos_per_week across each week
    calendar = []
    # Determine posting days within each week (0=Mon, 6=Sun)
    week_slots = _get_week_slots(videos_per_week)
    start_date = datetime.now().replace(hour=0, minute=0, second=0, microsecond=0)

    entry_idx = 0
    day_offset = 0
    while entry_idx < len(entries) and day_offset < days:
        current_date = start_date + timedelta(days=day_offset)
        weekday = current_date.weekday()  # 0=Mon
        if weekday in week_slots:
            entry = entries[entry_idx]
            entry["date"] = current_date.strftime("%Y-%m-%d")
            entry["day"] = current_date.strftime("%A")
            calendar.append(entry)
            entry_idx += 1
        day_offset += 1

    # Save outputs
    os.makedirs(OUTPUT_DIR, exist_ok=True)
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    safe_niche = "".join(c if c.isalnum() or c in "-_" else "_" for c in niche)[:30]

    json_path = os.path.join(OUTPUT_DIR, f"calendar_{safe_niche}_{timestamp}.json")
    with open(json_path, "w", encoding="utf-8") as fh:
        json.dump(calendar, fh, indent=2, ensure_ascii=False)
    logger.info("Calendar JSON saved to %s", json_path)

    csv_path = os.path.join(OUTPUT_DIR, f"calendar_{safe_niche}_{timestamp}.csv")
    _save_csv(calendar, csv_path)
    logger.info("Calendar CSV saved to %s", csv_path)

    # Attach output paths as metadata on first entry sentinel
    for entry in calendar:
        entry.setdefault("_json_file", json_path)
        entry.setdefault("_csv_file", csv_path)
        break

    return calendar


def _get_week_slots(videos_per_week: int) -> list:
    """Return weekday indices (0=Mon) for posting based on videos_per_week."""
    schedules = {
        1: [1],           # Tuesday
        2: [1, 4],        # Tue, Fri
        3: [1, 3, 5],     # Tue, Thu, Sat
        4: [0, 2, 4, 6],  # Mon, Wed, Fri, Sun
        5: [0, 1, 2, 4, 5],
        6: [0, 1, 2, 3, 4, 5],
        7: list(range(7)),
    }
    vpw = max(1, min(videos_per_week, 7))
    return schedules.get(vpw, schedules[3])


def _save_csv(calendar: list, csv_path: str) -> None:
    """Save calendar list to a CSV file."""
    fieldnames = ["date", "day", "title", "description", "keywords", "video_type"]
    with open(csv_path, "w", newline="", encoding="utf-8") as fh:
        writer = csv.DictWriter(fh, fieldnames=fieldnames, extrasaction="ignore")
        writer.writeheader()
        for entry in calendar:
            row = dict(entry)
            if isinstance(row.get("keywords"), list):
                row["keywords"] = ", ".join(row["keywords"])
            writer.writerow(row)
