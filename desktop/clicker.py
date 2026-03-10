"""
clicker.py — Clicks the BUY or SELL button on TradingView using pyautogui.

Safety features:
  - pyautogui.FAILSAFE = True  (move mouse to screen corner to abort)
  - 0.5-second pause before each click to prevent accidental double-clicks
  - Every action is logged with a timestamp
  - On Windows, attempts to bring TradingView to the foreground before clicking
"""

import logging
import platform
import time
from datetime import datetime

import pyautogui

import config

logger = logging.getLogger(__name__)

# Safety: moving the mouse to the top-left corner raises FailSafeException
pyautogui.FAILSAFE = True
# Brief pause between individual pyautogui calls (on top of our own delay)
pyautogui.PAUSE = 0.1

_PRE_CLICK_DELAY = 0.5  # seconds to wait before clicking


def _bring_tradingview_to_front() -> bool:
    """
    On Windows, find the TradingView window and bring it to the foreground.
    Returns True on success, False if the window was not found or the
    platform is not Windows.
    """
    if platform.system() != "Windows":
        return False
    try:
        import pygetwindow as gw  # noqa: PLC0415
        windows = gw.getWindowsWithTitle("TradingView")
        if not windows:
            logger.warning("TradingView window not found — clicking anyway.")
            return False
        tv_win = windows[0]
        if tv_win.isMinimized:
            tv_win.restore()
        tv_win.activate()
        time.sleep(0.3)  # allow the OS to complete the focus change
        logger.debug("TradingView brought to foreground.")
        return True
    except Exception:  # noqa: BLE001
        logger.warning("Could not bring TradingView to foreground.", exc_info=True)
        return False


def _click_at(pos: list | tuple, label: str) -> bool:
    """
    Move the mouse to *pos* and click.  Returns True on success.
    """
    if not pos or len(pos) < 2:
        logger.error(
            "%s button position is not configured.  Run setup_regions.py first.",
            label,
        )
        return False

    x, y = int(pos[0]), int(pos[1])
    ts = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    logger.info("[%s] Clicking %s button at (%d, %d)", ts, label, x, y)

    _bring_tradingview_to_front()
    time.sleep(_PRE_CLICK_DELAY)

    try:
        pyautogui.moveTo(x, y, duration=0.2)
        pyautogui.click()
        logger.info("[%s] %s button clicked.", ts, label)
        return True
    except pyautogui.FailSafeException:
        logger.error(
            "pyautogui FailSafe triggered — mouse was in the corner.  "
            "Click aborted."
        )
        return False
    except Exception:  # noqa: BLE001
        logger.exception("Unexpected error while clicking %s button.", label)
        return False


def click_buy() -> bool:
    """Click the 🔵 BUY button on TradingView."""
    pos = config.get("BUY_BUTTON_POS")
    return _click_at(pos, "BUY")


def click_sell() -> bool:
    """Click the 🔴 SELL button on TradingView."""
    pos = config.get("SELL_BUTTON_POS")
    return _click_at(pos, "SELL")
