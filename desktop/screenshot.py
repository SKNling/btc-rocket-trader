"""
screenshot.py — Captures the TradingView chart area and saves it to disk.

The saved file path is returned so it can be sent via FCM or served by the
FastAPI server.
"""

import logging
import os
from datetime import datetime
from pathlib import Path

from PIL import Image, ImageGrab

import config

logger = logging.getLogger(__name__)

# Maximum width/height for the compressed notification image
_NOTIF_MAX_SIZE = (800, 600)
_NOTIF_QUALITY = 75  # JPEG quality (1–95)


def take_chart_screenshot() -> str | None:
    """
    Capture the chart region defined in config (CHART_REGION).
    Falls back to full screen if CHART_REGION is not set.

    Returns the file path of the saved PNG, or None on failure.
    """
    region = config.get("CHART_REGION") or config.get("SCAN_REGION")
    screenshot_dir = config.get("SCREENSHOT_DIR")
    os.makedirs(screenshot_dir, exist_ok=True)

    timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
    filename = f"signal_{timestamp}.png"
    filepath = os.path.join(screenshot_dir, filename)

    try:
        if region:
            x, y, w, h = region
            img = ImageGrab.grab(bbox=(x, y, x + w, y + h))
        else:
            img = ImageGrab.grab()  # full screen fallback

        img.save(filepath, format="PNG")
        logger.info("Screenshot saved: %s", filepath)
        return filepath

    except Exception:  # noqa: BLE001
        logger.exception("Failed to take chart screenshot.")
        return None


def get_compressed_path(original_path: str) -> str | None:
    """
    Return a compressed JPEG version of the screenshot suitable for FCM
    notification payloads.  The compressed file is saved alongside the
    original with a ``_thumb`` suffix.
    """
    if not original_path or not os.path.exists(original_path):
        return None

    try:
        p = Path(original_path)
        thumb_path = str(p.parent / (p.stem + "_thumb.jpg"))

        with Image.open(original_path) as img:
            img = img.convert("RGB")
            img.thumbnail(_NOTIF_MAX_SIZE, Image.LANCZOS)
            img.save(thumb_path, format="JPEG", quality=_NOTIF_QUALITY, optimize=True)

        logger.debug("Compressed screenshot saved: %s", thumb_path)
        return thumb_path

    except Exception:  # noqa: BLE001
        logger.exception("Failed to create compressed screenshot.")
        return None


def list_screenshots() -> list[str]:
    """Return a sorted list of screenshot filenames (newest first)."""
    screenshot_dir = config.get("SCREENSHOT_DIR", "")
    if not screenshot_dir or not os.path.isdir(screenshot_dir):
        return []
    files = sorted(
        (f for f in os.listdir(screenshot_dir) if f.endswith(".png") and not f.endswith("_thumb.png")),
        reverse=True,
    )
    return files
