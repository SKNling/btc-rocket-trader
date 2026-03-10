"""
config.py — Configuration management for BTC Rocket Trader desktop app.

Loads and saves settings from/to config.json in the desktop directory.
"""

import json
import logging
import os
from pathlib import Path

logger = logging.getLogger(__name__)

# Path to the config file (same directory as this script)
CONFIG_FILE = Path(__file__).parent / "config.json"

# ── Default values ──────────────────────────────────────────────────────────
DEFAULTS: dict = {
    # (x, y, width, height) of screen area to scan for rockets
    "SCAN_REGION": None,
    # (x, y) screen coordinates of the BUY button on TradingView
    "BUY_BUTTON_POS": None,
    # (x, y) screen coordinates of the SELL button on TradingView
    "SELL_BUTTON_POS": None,
    # Seconds between scan checks
    "CHECK_INTERVAL": 10,
    # Firebase Cloud Messaging server key (fill in after Firebase setup)
    "FCM_SERVER_KEY": "",
    # FCM device token received from the mobile app
    "FCM_DEVICE_TOKEN": "",
    # FastAPI server bind address
    "SERVER_HOST": "0.0.0.0",
    # FastAPI server port
    "SERVER_PORT": 8000,
    # Directory where chart screenshots are saved
    "SCREENSHOT_DIR": str(Path(__file__).parent / "screenshots"),
    # (x, y, width, height) of the full chart area for screenshots
    "CHART_REGION": None,
}

# ── In-memory config dict ────────────────────────────────────────────────────
_config: dict = {}


def load() -> dict:
    """Load configuration from config.json; fall back to DEFAULTS for missing keys."""
    global _config
    if CONFIG_FILE.exists():
        try:
            with open(CONFIG_FILE, "r", encoding="utf-8") as fh:
                data = json.load(fh)
            _config = {**DEFAULTS, **data}
            logger.info("Config loaded from %s", CONFIG_FILE)
        except (json.JSONDecodeError, OSError) as exc:
            logger.warning("Could not read config.json (%s); using defaults.", exc)
            _config = dict(DEFAULTS)
    else:
        _config = dict(DEFAULTS)
        logger.info("No config.json found — using defaults.")

    # Ensure screenshot directory exists
    os.makedirs(_config["SCREENSHOT_DIR"], exist_ok=True)
    return _config


def save(data: dict | None = None) -> None:
    """Persist the given (or current in-memory) config to config.json."""
    global _config
    if data is not None:
        _config.update(data)
    try:
        with open(CONFIG_FILE, "w", encoding="utf-8") as fh:
            json.dump(_config, fh, indent=2)
        logger.info("Config saved to %s", CONFIG_FILE)
    except OSError as exc:
        logger.error("Failed to save config.json: %s", exc)


def get(key: str, default=None):
    """Retrieve a single config value."""
    if not _config:
        load()
    return _config.get(key, default)


def set(key: str, value) -> None:  # noqa: A001
    """Update a single config value in memory and persist immediately."""
    if not _config:
        load()
    _config[key] = value
    save()


def is_setup_complete() -> bool:
    """Return True when the essential setup values have been configured."""
    cfg = _config if _config else load()
    return (
        cfg.get("SCAN_REGION") is not None
        and cfg.get("BUY_BUTTON_POS") is not None
        and cfg.get("SELL_BUTTON_POS") is not None
    )
