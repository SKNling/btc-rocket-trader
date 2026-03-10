"""
server.py — FastAPI local server for BTC Rocket Trader.

Endpoints
---------
GET  /health              — Liveness check
GET  /status              — Watcher status + last signal info
GET  /latest-signal       — Latest signal info + screenshot filename
GET  /screenshot/{name}   — Serve a specific screenshot file
POST /trade               — Execute BUY or SELL on TradingView
POST /register-device     — Store the FCM device token from the mobile app

The server runs on 0.0.0.0:8000 by default (configurable in config.json).
For remote access from your phone, expose it via ngrok.
"""

import logging
import os
from datetime import datetime
from pathlib import Path
from typing import TYPE_CHECKING

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
from pydantic import BaseModel

import clicker
import config
import screenshot as screenshot_module

if TYPE_CHECKING:
    from screen_watcher import ScreenWatcher

logger = logging.getLogger(__name__)

app = FastAPI(
    title="BTC Rocket Trader",
    description="Desktop server for BTC Rocket Trader — detects signals and executes trades.",
    version="1.0.0",
)

# Allow localhost and ngrok origins so the Flutter mobile app can reach the server.
# Credentials (cookies/auth headers) are not used by this API, so
# allow_credentials is left False to avoid the CORS wildcard+credentials risk.
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=False,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Reference to the ScreenWatcher instance — set by main.py at startup
_watcher: "ScreenWatcher | None" = None


def set_watcher(watcher: "ScreenWatcher") -> None:
    global _watcher
    _watcher = watcher


# ── Pydantic models ───────────────────────────────────────────────────────────

class TradeRequest(BaseModel):
    action: str  # "BUY" or "SELL"


class RegisterDeviceRequest(BaseModel):
    token: str


# ── Endpoints ─────────────────────────────────────────────────────────────────

@app.get("/health", tags=["system"])
def health_check():
    return {"status": "ok", "timestamp": datetime.now().isoformat()}


@app.get("/status", tags=["system"])
def get_status():
    status_data: dict = {
        "watcher_running": False,
        "last_check": None,
        "last_signal": None,
        "rocket_count": 0,
        "scan_region": config.get("SCAN_REGION"),
        "check_interval": config.get("CHECK_INTERVAL", 10),
    }
    if _watcher is not None:
        s = _watcher.status
        status_data["watcher_running"] = s.is_running
        status_data["last_check"] = s.last_check.isoformat() if s.last_check else None
        status_data["last_signal"] = s.last_signal.isoformat() if s.last_signal else None
        status_data["rocket_count"] = s.rocket_count
    return status_data


@app.get("/latest-signal", tags=["signals"])
def latest_signal():
    screenshots = screenshot_module.list_screenshots()
    if not screenshots:
        return {
            "has_signal": False,
            "filename": None,
            "timestamp": None,
            "screenshot_url": None,
        }
    latest = screenshots[0]
    port = config.get("SERVER_PORT", 8000)
    return {
        "has_signal": True,
        "filename": latest,
        "timestamp": latest.removeprefix("signal_").removesuffix(".png"),
        "screenshot_url": f"http://127.0.0.1:{port}/screenshot/{latest}",
    }


@app.get("/screenshot/{filename}", tags=["signals"])
def serve_screenshot(filename: str):
    # Security: only allow filenames without directory separators
    if os.sep in filename or "/" in filename or "\\" in filename:
        raise HTTPException(status_code=400, detail="Invalid filename.")

    screenshot_dir = config.get("SCREENSHOT_DIR", "")
    filepath = os.path.join(screenshot_dir, filename)

    if not os.path.isfile(filepath):
        raise HTTPException(status_code=404, detail="Screenshot not found.")

    suffix = Path(filename).suffix.lower()
    media_type = "image/jpeg" if suffix in {".jpg", ".jpeg"} else "image/png"
    return FileResponse(filepath, media_type=media_type)


@app.post("/trade", tags=["trading"])
def execute_trade(req: TradeRequest):
    action = req.action.upper().strip()
    if action not in {"BUY", "SELL"}:
        raise HTTPException(status_code=400, detail="action must be 'BUY' or 'SELL'.")

    logger.info("Trade command received: %s", action)
    success = clicker.click_buy() if action == "BUY" else clicker.click_sell()

    if not success:
        raise HTTPException(status_code=500, detail=f"Failed to execute {action}.")

    return {
        "status": "ok",
        "action": action,
        "timestamp": datetime.now().isoformat(),
    }


@app.post("/register-device", tags=["notifications"])
def register_device(req: RegisterDeviceRequest):
    token = req.token.strip()
    if not token:
        raise HTTPException(status_code=400, detail="token must not be empty.")

    config.set("FCM_DEVICE_TOKEN", token)
    logger.info("FCM device token registered (length=%d).", len(token))
    return {"status": "ok", "message": "Device registered."}
