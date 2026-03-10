"""
screen_watcher.py — Watches the defined SCAN_REGION for new 🚀 rocket emojis.

Detection strategy (snapshot comparison):
  - On startup, grab a baseline image of the scan area.
  - Every CHECK_INTERVAL seconds, grab a new image and compare with the baseline.
  - Use colour-based detection: count pixels that match the distinctive
    orange/red/yellow palette of the TradingView rocket emoji.
  - If the rocket count increases AND the newest rocket is near the RIGHT EDGE
    of the scan area (i.e. it is on the most recent candle), fire the callback.
  - When rockets scroll off the LEFT edge (count decreases), silently update
    the baseline.

Usage:
    watcher = ScreenWatcher(on_new_rocket=my_callback)
    watcher.start()
    ...
    watcher.stop()
"""

import logging
import threading
import time
from collections.abc import Callable
from dataclasses import dataclass, field
from datetime import datetime

import numpy as np
from PIL import ImageGrab

import config

logger = logging.getLogger(__name__)

# ── Rocket colour detection ───────────────────────────────────────────────────
# TradingView's rocket emoji body is predominantly orange/red.
# We look for pixels with high Red channel, moderate Green, low Blue.
_ROCKET_R_MIN = 180
_ROCKET_G_MIN = 80
_ROCKET_G_MAX = 180
_ROCKET_B_MAX = 80
# Minimum cluster size (pixels) to count as one rocket instance
_MIN_CLUSTER_PX = 15
# Minimum horizontal gap (pixels) between distinct rocket clusters
_CLUSTER_GAP = 20
# A new rocket is considered "near the right edge" if its x-centre is within
# this fraction of the scan width from the right side
_RIGHT_EDGE_FRACTION = 0.35


@dataclass
class RocketInfo:
    count: int = 0
    positions: list[int] = field(default_factory=list)  # x-centres of rockets


@dataclass
class WatcherStatus:
    is_running: bool = False
    last_check: datetime | None = None
    last_signal: datetime | None = None
    rocket_count: int = 0


def _capture_region(region: list | tuple) -> np.ndarray:
    """Capture screen region and return as RGB numpy array."""
    x, y, w, h = region
    img = ImageGrab.grab(bbox=(x, y, x + w, y + h))
    return np.array(img.convert("RGB"))


def _detect_rockets(arr: np.ndarray) -> RocketInfo:
    """
    Return count and x-positions of rocket emoji clusters in the image array.
    """
    r = arr[:, :, 0].astype(np.int32)
    g = arr[:, :, 1].astype(np.int32)
    b = arr[:, :, 2].astype(np.int32)

    mask = (
        (r >= _ROCKET_R_MIN)
        & (g >= _ROCKET_G_MIN)
        & (g <= _ROCKET_G_MAX)
        & (b <= _ROCKET_B_MAX)
    )

    # Collapse to a horizontal projection (sum along y-axis)
    col_sums = mask.sum(axis=0)

    # Find columns that are part of a rocket cluster
    rocket_cols = np.where(col_sums >= 1)[0]
    if len(rocket_cols) == 0:
        return RocketInfo()

    # Group consecutive columns into clusters
    clusters: list[list[int]] = []
    current: list[int] = [rocket_cols[0]]
    for col in rocket_cols[1:]:
        if col - current[-1] <= _CLUSTER_GAP:
            current.append(col)
        else:
            clusters.append(current)
            current = [col]
    clusters.append(current)

    # Filter clusters by minimum pixel count
    valid: list[list[int]] = []
    for cluster in clusters:
        px = int(col_sums[cluster].sum())
        if px >= _MIN_CLUSTER_PX:
            valid.append(cluster)

    positions = [int(np.mean(c)) for c in valid]
    return RocketInfo(count=len(positions), positions=positions)


class ScreenWatcher:
    """Background thread that watches the scan region for new rockets."""

    def __init__(self, on_new_rocket: Callable[[], None] | None = None):
        self._on_new_rocket = on_new_rocket
        self._thread: threading.Thread | None = None
        self._stop_event = threading.Event()
        self._baseline: RocketInfo = RocketInfo()
        self.status = WatcherStatus()

    # ── Public API ────────────────────────────────────────────────────────

    def start(self) -> None:
        if self._thread and self._thread.is_alive():
            logger.warning("ScreenWatcher is already running.")
            return
        self._stop_event.clear()
        self._thread = threading.Thread(target=self._run, name="ScreenWatcher", daemon=True)
        self._thread.start()
        self.status.is_running = True
        logger.info("ScreenWatcher started.")

    def stop(self) -> None:
        self._stop_event.set()
        if self._thread:
            self._thread.join(timeout=15)
        self.status.is_running = False
        logger.info("ScreenWatcher stopped.")

    # ── Internal loop ─────────────────────────────────────────────────────

    def _run(self) -> None:
        region = config.get("SCAN_REGION")
        if not region:
            logger.error("SCAN_REGION not configured.  Run setup_regions.py first.")
            return

        interval = config.get("CHECK_INTERVAL", 10)
        logger.info(
            "Watching scan region %s every %s seconds…", region, interval
        )

        # Establish baseline on first run
        try:
            baseline_arr = _capture_region(region)
            self._baseline = _detect_rockets(baseline_arr)
            logger.info(
                "Baseline established: %d rocket(s) at positions %s",
                self._baseline.count,
                self._baseline.positions,
            )
        except Exception:  # noqa: BLE001
            logger.exception("Failed to capture baseline image.")
            return

        while not self._stop_event.is_set():
            time.sleep(interval)
            if self._stop_event.is_set():
                break
            self._check(region)

    def _check(self, region: list | tuple) -> None:
        try:
            arr = _capture_region(region)
        except Exception:  # noqa: BLE001
            logger.exception("Screen capture failed during check.")
            return

        self.status.last_check = datetime.now()
        current = _detect_rockets(arr)
        self.status.rocket_count = current.count

        logger.debug(
            "Check: %d rocket(s) at positions %s  (baseline: %d)",
            current.count,
            current.positions,
            self._baseline.count,
        )

        if current.count > self._baseline.count:
            # Determine whether the new rocket is near the right edge
            right_threshold = region[2] * (1 - _RIGHT_EDGE_FRACTION)
            new_positions = [
                p for p in current.positions if p not in self._baseline.positions
            ]
            if not new_positions:
                # Fallback: rightmost overall position
                new_positions = [max(current.positions)]

            rightmost_new = max(new_positions)

            if rightmost_new >= right_threshold:
                logger.info(
                    "🚀 NEW ROCKET detected at x=%d (threshold=%d).  "
                    "Total: %d → %d",
                    rightmost_new,
                    right_threshold,
                    self._baseline.count,
                    current.count,
                )
                self.status.last_signal = datetime.now()
                self._baseline = current
                if self._on_new_rocket:
                    try:
                        self._on_new_rocket()
                    except Exception:  # noqa: BLE001
                        logger.exception("on_new_rocket callback raised an exception.")
            else:
                logger.debug(
                    "Rocket count increased but new rocket is not near the right edge "
                    "(x=%d < threshold=%d) — ignoring.",
                    rightmost_new,
                    right_threshold,
                )
                # Update baseline anyway (chart may have shifted)
                self._baseline = current

        elif current.count < self._baseline.count:
            # Rockets scrolled off the left edge — update baseline silently
            logger.info(
                "Rocket count decreased %d → %d (scrolled off). Updating baseline.",
                self._baseline.count,
                current.count,
            )
            self._baseline = current

        # (If count unchanged, do nothing)
