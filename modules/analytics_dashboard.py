"""
Analytics Dashboard Module.

Fetches YouTube channel analytics and generates formatted Markdown reports.
"""

import logging
import os
from datetime import datetime, timedelta

from googleapiclient.discovery import build

from modules.upload_scheduler import authenticate_youtube, _get_credentials

logger = logging.getLogger(__name__)

OUTPUT_DIR = os.path.join(os.path.dirname(os.path.dirname(__file__)), "output")


def get_channel_analytics(days: int = 30) -> dict:
    """
    Fetch YouTube channel analytics for the specified number of past days.

    Parameters:
        days (int): Number of past days to fetch data for (default: 30).

    Returns:
        dict: Analytics data containing:
            - period (dict): start_date and end_date strings.
            - summary (dict): total views, watch_time_minutes, subscribers_gained,
              subscribers_lost, average_view_duration_seconds, estimated_ctr.
            - top_videos (list): Up to 10 dicts with video_id, title, views,
              watch_time_minutes.

    Raises:
        RuntimeError: If the API call fails.
    """
    logger.info("Fetching channel analytics for the past %d days", days)

    end_date = datetime.utcnow().date()
    start_date = end_date - timedelta(days=days)

    creds = _get_credentials()
    youtube = build("youtube", "v3", credentials=creds)
    yt_analytics = build("youtubeAnalytics", "v2", credentials=creds)

    try:
        # Summary metrics
        summary_response = (
            yt_analytics.reports()
            .query(
                ids="channel==MINE",
                startDate=start_date.isoformat(),
                endDate=end_date.isoformat(),
                metrics="views,estimatedMinutesWatched,subscribersGained,subscribersLost,"
                        "averageViewDuration,annotationClickThroughRate",
                dimensions="",
            )
            .execute()
        )

        rows = summary_response.get("rows", [[0, 0, 0, 0, 0, 0]])
        row = rows[0] if rows else [0, 0, 0, 0, 0, 0]
        summary = {
            "views": int(row[0]),
            "watch_time_minutes": float(row[1]),
            "subscribers_gained": int(row[2]),
            "subscribers_lost": int(row[3]),
            "average_view_duration_seconds": float(row[4]),
            "estimated_ctr": float(row[5]) if len(row) > 5 else None,
        }

        # Top videos
        top_response = (
            yt_analytics.reports()
            .query(
                ids="channel==MINE",
                startDate=start_date.isoformat(),
                endDate=end_date.isoformat(),
                metrics="views,estimatedMinutesWatched",
                dimensions="video",
                sort="-views",
                maxResults=10,
            )
            .execute()
        )

        top_videos = []
        for video_row in top_response.get("rows", []):
            top_videos.append(
                {
                    "video_id": video_row[0],
                    "title": "",  # Titles require a separate Videos.list call
                    "views": int(video_row[1]),
                    "watch_time_minutes": float(video_row[2]),
                }
            )

        # Enrich top videos with titles
        if top_videos:
            video_ids = ",".join(v["video_id"] for v in top_videos)
            titles_response = (
                youtube.videos()
                .list(part="snippet", id=video_ids)
                .execute()
            )
            title_map = {
                item["id"]: item["snippet"]["title"]
                for item in titles_response.get("items", [])
            }
            for v in top_videos:
                v["title"] = title_map.get(v["video_id"], "Unknown")

    except Exception as exc:  # noqa: BLE001
        logger.error("Analytics API error: %s", exc)
        raise RuntimeError(f"Analytics API error: {exc}") from exc

    analytics_data = {
        "period": {
            "start_date": start_date.isoformat(),
            "end_date": end_date.isoformat(),
        },
        "summary": summary,
        "top_videos": top_videos,
    }

    logger.info("Analytics fetched successfully for %s to %s", start_date, end_date)
    return analytics_data


def generate_report(analytics_data: dict) -> str:
    """
    Generate a formatted Markdown analytics report.

    Parameters:
        analytics_data (dict): Data returned by get_channel_analytics().

    Returns:
        str: Path to the saved Markdown report file.
    """
    period = analytics_data.get("period", {})
    summary = analytics_data.get("summary", {})
    top_videos = analytics_data.get("top_videos", [])

    lines = [
        "# YouTube Channel Analytics Report",
        "",
        f"**Period:** {period.get('start_date')} → {period.get('end_date')}",
        f"**Generated:** {datetime.utcnow().strftime('%Y-%m-%d %H:%M UTC')}",
        "",
        "---",
        "",
        "## Summary",
        "",
        f"| Metric | Value |",
        f"|--------|-------|",
        f"| Total Views | {summary.get('views', 0):,} |",
        f"| Watch Time | {summary.get('watch_time_minutes', 0):,.1f} minutes |",
        f"| Subscribers Gained | {summary.get('subscribers_gained', 0):,} |",
        f"| Subscribers Lost | {summary.get('subscribers_lost', 0):,} |",
        f"| Avg. View Duration | {summary.get('average_view_duration_seconds', 0):.1f} seconds |",
    ]

    ctr = summary.get("estimated_ctr")
    if ctr is not None:
        lines.append(f"| Estimated CTR | {ctr:.2%} |")

    lines += [
        "",
        "---",
        "",
        "## Top 10 Videos",
        "",
        "| # | Video ID | Title | Views | Watch Time (min) |",
        "|---|----------|-------|-------|-----------------|",
    ]

    for i, video in enumerate(top_videos, start=1):
        lines.append(
            f"| {i} | {video.get('video_id')} | {video.get('title')} "
            f"| {video.get('views', 0):,} | {video.get('watch_time_minutes', 0):,.1f} |"
        )

    report_content = "\n".join(lines)

    os.makedirs(OUTPUT_DIR, exist_ok=True)
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    report_path = os.path.join(OUTPUT_DIR, f"analytics_report_{timestamp}.md")
    with open(report_path, "w", encoding="utf-8") as fh:
        fh.write(report_content)

    logger.info("Analytics report saved to %s", report_path)
    return report_path
