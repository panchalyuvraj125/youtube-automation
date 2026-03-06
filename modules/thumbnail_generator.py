"""
Thumbnail Generator Module.

Creates YouTube thumbnails (1280x720 PNG) using Pillow.
"""

import logging
import os
from datetime import datetime

from PIL import Image, ImageDraw, ImageFont

logger = logging.getLogger(__name__)

OUTPUT_DIR = os.path.join(os.path.dirname(os.path.dirname(__file__)), "output", "thumbnails")

THUMBNAIL_WIDTH = 1280
THUMBNAIL_HEIGHT = 720


def _hex_to_rgb(hex_color: str) -> tuple:
    """Convert a hex color string to an (R, G, B) tuple."""
    hex_color = hex_color.lstrip("#")
    if len(hex_color) == 3:
        hex_color = "".join(c * 2 for c in hex_color)
    return tuple(int(hex_color[i : i + 2], 16) for i in (0, 2, 4))


def _get_font(size: int) -> ImageFont.FreeTypeFont:
    """
    Try to load a TrueType font; fall back to the default bitmap font.

    Parameters:
        size (int): Desired font size in points.

    Returns:
        ImageFont.FreeTypeFont or ImageFont.ImageFont: A usable font object.
    """
    font_candidates = [
        "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf",
        "/usr/share/fonts/truetype/liberation/LiberationSans-Bold.ttf",
        "/usr/share/fonts/truetype/freefont/FreeSansBold.ttf",
        "/System/Library/Fonts/Helvetica.ttc",
        "C:\\Windows\\Fonts\\arialbd.ttf",
    ]
    for path in font_candidates:
        if os.path.exists(path):
            try:
                return ImageFont.truetype(path, size)
            except OSError:
                continue
    # Fall back to default font
    return ImageFont.load_default()


def _wrap_text(text: str, font: ImageFont.FreeTypeFont, max_width: int, draw: ImageDraw.ImageDraw) -> list:
    """
    Wrap text into lines that fit within max_width pixels.

    Parameters:
        text (str): Text to wrap.
        font: Font used for measuring text width.
        max_width (int): Maximum line width in pixels.
        draw (ImageDraw.ImageDraw): Draw object used for text size measurement.

    Returns:
        list: List of string lines.
    """
    words = text.split()
    lines = []
    current_line = ""
    for word in words:
        test_line = f"{current_line} {word}".strip()
        bbox = draw.textbbox((0, 0), test_line, font=font)
        if bbox[2] <= max_width:
            current_line = test_line
        else:
            if current_line:
                lines.append(current_line)
            current_line = word
    if current_line:
        lines.append(current_line)
    return lines


def create_thumbnail(
    title: str,
    subtitle: str = "",
    bg_color: str = "#FF0000",
    text_color: str = "#FFFFFF",
    output_path: str = None,
) -> str:
    """
    Create a 1280x720 YouTube thumbnail image.

    Parameters:
        title (str): Main title text displayed prominently on the thumbnail.
        subtitle (str): Optional subtitle text displayed below the title.
        bg_color (str): Background hex color (default: "#FF0000").
        text_color (str): Text hex color (default: "#FFFFFF").
        output_path (str): Optional custom output file path. If None, a timestamped
            file is created in output/thumbnails/.

    Returns:
        str: Absolute path of the saved thumbnail PNG file.
    """
    logger.info("Creating thumbnail for title='%s'", title)

    bg_rgb = _hex_to_rgb(bg_color)
    text_rgb = _hex_to_rgb(text_color)

    img = Image.new("RGB", (THUMBNAIL_WIDTH, THUMBNAIL_HEIGHT), color=bg_rgb)
    draw = ImageDraw.Draw(img)

    padding = 60
    max_text_width = THUMBNAIL_WIDTH - 2 * padding

    # Auto-size title font to fit
    title_font_size = 120
    while title_font_size > 24:
        font = _get_font(title_font_size)
        lines = _wrap_text(title, font, max_text_width, draw)
        # Estimate total height
        line_height = title_font_size + 10
        total_height = len(lines) * line_height
        if total_height <= (THUMBNAIL_HEIGHT - 2 * padding - (80 if subtitle else 0)):
            break
        title_font_size -= 8

    title_font = _get_font(title_font_size)
    title_lines = _wrap_text(title, title_font, max_text_width, draw)

    # Calculate vertical centering
    line_height = title_font_size + 10
    title_block_height = len(title_lines) * line_height

    subtitle_font = None
    subtitle_lines = []
    subtitle_line_height = 0
    if subtitle:
        subtitle_font_size = max(24, title_font_size // 3)
        subtitle_font = _get_font(subtitle_font_size)
        subtitle_lines = _wrap_text(subtitle, subtitle_font, max_text_width, draw)
        subtitle_line_height = subtitle_font_size + 8

    total_content_height = title_block_height + (len(subtitle_lines) * subtitle_line_height + 20 if subtitle_lines else 0)
    y_start = (THUMBNAIL_HEIGHT - total_content_height) // 2

    # Draw title lines
    y = y_start
    for line in title_lines:
        bbox = draw.textbbox((0, 0), line, font=title_font)
        line_width = bbox[2] - bbox[0]
        x = (THUMBNAIL_WIDTH - line_width) // 2
        draw.text((x, y), line, font=title_font, fill=text_rgb)
        y += line_height

    # Draw subtitle lines
    if subtitle_lines and subtitle_font:
        y += 20
        for line in subtitle_lines:
            bbox = draw.textbbox((0, 0), line, font=subtitle_font)
            line_width = bbox[2] - bbox[0]
            x = (THUMBNAIL_WIDTH - line_width) // 2
            draw.text((x, y), line, font=subtitle_font, fill=text_rgb)
            y += subtitle_line_height

    # Determine output path
    if output_path is None:
        os.makedirs(OUTPUT_DIR, exist_ok=True)
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        safe_title = "".join(c if c.isalnum() or c in "-_" else "_" for c in title)[:40]
        filename = f"thumbnail_{safe_title}_{timestamp}.png"
        output_path = os.path.join(OUTPUT_DIR, filename)

    img.save(output_path, "PNG")
    logger.info("Thumbnail saved to %s", output_path)
    return output_path
