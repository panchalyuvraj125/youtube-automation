"""
YouTube Automation System — CLI Entry Point.

Usage examples:
  python main.py script --topic "AI Tools" --niche "tech"
  python main.py seo --topic "AI Tools" --niche "tech"
  python main.py thumbnail --title "10 AI Tools"
  python main.py calendar --niche "tech" --days 30
  python main.py upload --video path/to/video.mp4 --title "My Video" --description "..."
  python main.py analytics --days 30
  python main.py all --topic "AI Tools" --niche "tech"
"""

import argparse
import sys

# ANSI color codes
GREEN = "\033[92m"
YELLOW = "\033[93m"
RED = "\033[91m"
CYAN = "\033[96m"
BOLD = "\033[1m"
RESET = "\033[0m"


def print_success(message: str) -> None:
    """Print a green success message."""
    print(f"{GREEN}{BOLD}✓ {message}{RESET}")


def print_info(message: str) -> None:
    """Print a cyan informational message."""
    print(f"{CYAN}ℹ {message}{RESET}")


def print_error(message: str) -> None:
    """Print a red error message."""
    print(f"{RED}{BOLD}✗ {message}{RESET}", file=sys.stderr)


def cmd_script(args: argparse.Namespace) -> None:
    """Run the script generator."""
    from modules.script_generator import generate_script

    print_info(f"Generating script for topic='{args.topic}', niche='{args.niche}'...")
    result = generate_script(
        topic=args.topic,
        niche=args.niche,
        tone=args.tone,
        duration_minutes=args.duration,
    )
    print_success(f"Script generated and saved to: {result.get('_output_file', 'output/scripts/')}")


def cmd_seo(args: argparse.Namespace) -> None:
    """Run the SEO optimizer."""
    from modules.seo_optimizer import optimize_seo

    print_info(f"Optimizing SEO for topic='{args.topic}', niche='{args.niche}'...")
    result = optimize_seo(
        topic=args.topic,
        niche=args.niche,
        target_audience=args.audience,
    )
    print_success(f"SEO metadata saved to: {result.get('_output_file', 'output/seo/')}")
    print_info(f"Best title: {result['titles'][0] if result.get('titles') else 'N/A'}")


def cmd_thumbnail(args: argparse.Namespace) -> None:
    """Run the thumbnail generator."""
    from modules.thumbnail_generator import create_thumbnail

    print_info(f"Creating thumbnail for title='{args.title}'...")
    filepath = create_thumbnail(
        title=args.title,
        subtitle=args.subtitle,
        bg_color=args.bg_color,
        text_color=args.text_color,
    )
    print_success(f"Thumbnail saved to: {filepath}")


def cmd_calendar(args: argparse.Namespace) -> None:
    """Run the content calendar generator."""
    from modules.content_calendar import generate_calendar

    print_info(f"Generating {args.days}-day calendar for niche='{args.niche}'...")
    calendar = generate_calendar(
        niche=args.niche,
        days=args.days,
        videos_per_week=args.videos_per_week,
    )
    if calendar:
        print_success(
            f"Calendar with {len(calendar)} entries saved to: "
            f"{calendar[0].get('_json_file', 'output/calendars/')}"
        )
    else:
        print_error("Calendar generation returned no entries.")


def cmd_upload(args: argparse.Namespace) -> None:
    """Run the video uploader."""
    from modules.upload_scheduler import upload_video

    tags = [t.strip() for t in args.tags.split(",")] if args.tags else []
    print_info(f"Uploading video: '{args.title}'...")
    result = upload_video(
        video_path=args.video,
        title=args.title,
        description=args.description,
        tags=tags,
        category_id=args.category,
        privacy_status=args.privacy,
        publish_at=args.publish_at,
    )
    print_success(f"Upload successful! Video URL: {result.get('url')}")


def cmd_analytics(args: argparse.Namespace) -> None:
    """Run the analytics dashboard."""
    from modules.analytics_dashboard import get_channel_analytics, generate_report

    print_info(f"Fetching analytics for the past {args.days} days...")
    data = get_channel_analytics(days=args.days)
    report_path = generate_report(data)
    print_success(f"Analytics report saved to: {report_path}")
    summary = data.get("summary", {})
    print_info(f"Views: {summary.get('views', 0):,} | Watch time: {summary.get('watch_time_minutes', 0):,.1f} min")


def cmd_all(args: argparse.Namespace) -> None:
    """Run script generator + SEO optimizer + thumbnail generator together."""
    from modules.script_generator import generate_script
    from modules.seo_optimizer import optimize_seo
    from modules.thumbnail_generator import create_thumbnail

    print_info(f"Running full pipeline for topic='{args.topic}', niche='{args.niche}'...")

    print_info("Step 1/3: Generating script...")
    script = generate_script(topic=args.topic, niche=args.niche)
    print_success(f"Script saved to: {script.get('_output_file', 'output/scripts/')}")

    print_info("Step 2/3: Optimizing SEO...")
    seo = optimize_seo(topic=args.topic, niche=args.niche)
    print_success(f"SEO saved to: {seo.get('_output_file', 'output/seo/')}")

    print_info("Step 3/3: Creating thumbnail...")
    best_title = seo["titles"][0] if seo.get("titles") else args.topic
    thumbnail_path = create_thumbnail(title=best_title)
    print_success(f"Thumbnail saved to: {thumbnail_path}")

    print_success("All pipeline steps completed successfully!")


def build_parser() -> argparse.ArgumentParser:
    """Build and return the CLI argument parser."""
    parser = argparse.ArgumentParser(
        prog="youtube-automation",
        description=f"{BOLD}🎬 YouTube Automation System{RESET}",
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    subparsers = parser.add_subparsers(dest="command", metavar="command")
    subparsers.required = True

    # script
    p_script = subparsers.add_parser("script", help="Generate a video script")
    p_script.add_argument("--topic", required=True, help="Video topic")
    p_script.add_argument("--niche", required=True, help="Channel niche")
    p_script.add_argument("--tone", default="engaging", help="Script tone (default: engaging)")
    p_script.add_argument("--duration", type=int, default=10, help="Duration in minutes (default: 10)")
    p_script.set_defaults(func=cmd_script)

    # seo
    p_seo = subparsers.add_parser("seo", help="Generate SEO metadata")
    p_seo.add_argument("--topic", required=True, help="Video topic")
    p_seo.add_argument("--niche", required=True, help="Channel niche")
    p_seo.add_argument("--audience", default="general", help="Target audience (default: general)")
    p_seo.set_defaults(func=cmd_seo)

    # thumbnail
    p_thumb = subparsers.add_parser("thumbnail", help="Create a thumbnail image")
    p_thumb.add_argument("--title", required=True, help="Thumbnail title text")
    p_thumb.add_argument("--subtitle", default="", help="Optional subtitle text")
    p_thumb.add_argument("--bg-color", default="#FF0000", help="Background color (default: #FF0000)")
    p_thumb.add_argument("--text-color", default="#FFFFFF", help="Text color (default: #FFFFFF)")
    p_thumb.set_defaults(func=cmd_thumbnail)

    # calendar
    p_cal = subparsers.add_parser("calendar", help="Generate a content calendar")
    p_cal.add_argument("--niche", required=True, help="Channel niche")
    p_cal.add_argument("--days", type=int, default=30, help="Number of days (default: 30)")
    p_cal.add_argument("--videos-per-week", type=int, default=3, dest="videos_per_week",
                       help="Videos per week (default: 3)")
    p_cal.set_defaults(func=cmd_calendar)

    # upload
    p_upload = subparsers.add_parser("upload", help="Upload a video to YouTube")
    p_upload.add_argument("--video", required=True, help="Path to video file")
    p_upload.add_argument("--title", required=True, help="Video title")
    p_upload.add_argument("--description", required=True, help="Video description")
    p_upload.add_argument("--tags", default="", help="Comma-separated tags")
    p_upload.add_argument("--category", default="22", help="Category ID (default: 22)")
    p_upload.add_argument("--privacy", default="private",
                          choices=["private", "public", "unlisted"], help="Privacy status")
    p_upload.add_argument("--publish-at", default=None, dest="publish_at",
                          help="Scheduled publish time (ISO 8601)")
    p_upload.set_defaults(func=cmd_upload)

    # analytics
    p_analytics = subparsers.add_parser("analytics", help="Fetch and report analytics")
    p_analytics.add_argument("--days", type=int, default=30, help="Days of history (default: 30)")
    p_analytics.set_defaults(func=cmd_analytics)

    # all
    p_all = subparsers.add_parser("all", help="Run script + SEO + thumbnail pipeline")
    p_all.add_argument("--topic", required=True, help="Video topic")
    p_all.add_argument("--niche", required=True, help="Channel niche")
    p_all.set_defaults(func=cmd_all)

    return parser


def main() -> None:
    """Main CLI entry point."""
    parser = build_parser()
    args = parser.parse_args()
    try:
        args.func(args)
    except Exception as exc:  # noqa: BLE001
        print_error(str(exc))
        sys.exit(1)


if __name__ == "__main__":
    main()
