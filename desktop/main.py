"""
main.py — Main entry point for the BTC Rocket Trader desktop application.

Startup sequence:
  1. Load config from config.json.
  2. If essential setup (scan region + button positions) is missing, run
     setup_regions.py interactively.
  3. Start the screen watcher in a background daemon thread.
  4. (Optional) Start an ngrok tunnel for remote phone access.
  5. Start the FastAPI server (blocks on this call — Ctrl+C to exit).

Usage:
    python main.py
"""

import logging
import os
import sys
import threading
from pathlib import Path

import uvicorn

import config
import notifier
import screenshot as screenshot_module
import server as server_module
from screen_watcher import ScreenWatcher

# ── Logging setup ─────────────────────────────────────────────────────────────
LOG_DIR = Path(__file__).parent / "logs"
LOG_DIR.mkdir(exist_ok=True)

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
    handlers=[
        logging.StreamHandler(sys.stdout),
        logging.FileHandler(LOG_DIR / "btc_rocket_trader.log", encoding="utf-8"),
    ],
)
logger = logging.getLogger(__name__)


# ── Signal callback ────────────────────────────────────────────────────────────

def on_new_rocket() -> None:
    """Called by ScreenWatcher when a new 🚀 rocket is detected."""
    logger.info("🚀 New rocket signal!  Taking screenshot and sending notification…")
    filepath = screenshot_module.take_chart_screenshot()
    filename = os.path.basename(filepath) if filepath else None
    sent = notifier.send_signal_notification(filename)
    if sent:
        logger.info("Push notification sent.")
    else:
        logger.warning("Push notification could NOT be sent (check FCM config).")


# ── ngrok tunnel (optional) ────────────────────────────────────────────────────

def _start_ngrok(port: int) -> None:
    """
    Start an ngrok tunnel if pyngrok is installed and an auth token is set.
    Prints the public URL so the user can enter it in the mobile app.
    """
    ngrok_token = config.get("NGROK_AUTH_TOKEN", "")
    if not ngrok_token:
        logger.info(
            "NGROK_AUTH_TOKEN not set — skipping ngrok tunnel.  "
            "The server is only reachable on your local network."
        )
        return
    try:
        from pyngrok import conf, ngrok  # noqa: PLC0415
        conf.get_default().auth_token = ngrok_token
        tunnel = ngrok.connect(port, "http")
        logger.info("🌍 ngrok tunnel active: %s", tunnel.public_url)
        print(f"\n  ┌─────────────────────────────────────────────────────┐")
        print(f"  │  🌍 ngrok URL: {tunnel.public_url:<38}│")
        print(f"  │  Enter this URL in your BTC Rocket Trader mobile app │")
        print(f"  └─────────────────────────────────────────────────────┘\n")
    except ImportError:
        logger.warning("pyngrok not installed — ngrok tunnel not started.")
    except Exception:  # noqa: BLE001
        logger.exception("Failed to start ngrok tunnel.")


# ── Main ───────────────────────────────────────────────────────────────────────

def main() -> None:
    logger.info("=" * 60)
    logger.info("  BTC Rocket Trader — Starting up")
    logger.info("=" * 60)

    # 1. Load config
    cfg = config.load()
    logger.info("Config loaded.")

    # 2. Run first-time setup if needed
    if not config.is_setup_complete():
        logger.warning(
            "Setup is incomplete.  Launching setup_regions.py…"
        )
        try:
            import setup_regions  # noqa: PLC0415
            setup_regions.run_setup()
            config.load()  # reload after setup
        except Exception:  # noqa: BLE001
            logger.exception("Setup failed.")
            sys.exit(1)

        if not config.is_setup_complete():
            logger.error("Setup still incomplete.  Exiting.")
            sys.exit(1)

    # 3. Start screen watcher
    watcher = ScreenWatcher(on_new_rocket=on_new_rocket)
    server_module.set_watcher(watcher)
    watcher.start()

    # 4. Start ngrok (non-blocking, best-effort)
    port = cfg.get("SERVER_PORT", 8000)
    ngrok_thread = threading.Thread(
        target=_start_ngrok, args=(port,), name="ngrok", daemon=True
    )
    ngrok_thread.start()
    ngrok_thread.join(timeout=10)  # give ngrok up to 10 seconds to connect

    # 5. Start FastAPI server (blocks until Ctrl+C)
    host = cfg.get("SERVER_HOST", "0.0.0.0")
    logger.info("Starting FastAPI server on %s:%d …", host, port)
    print(f"\n  BTC Rocket Trader is running.")
    print(f"  API server: http://127.0.0.1:{port}/docs")
    print(f"  Press Ctrl+C to stop.\n")

    try:
        uvicorn.run(
            server_module.app,
            host=host,
            port=port,
            log_level="info",
        )
    except KeyboardInterrupt:
        logger.info("Shutdown requested by user (Ctrl+C).")
    finally:
        logger.info("Stopping screen watcher…")
        watcher.stop()
        logger.info("BTC Rocket Trader stopped.  Goodbye! 👋")


if __name__ == "__main__":
    main()
