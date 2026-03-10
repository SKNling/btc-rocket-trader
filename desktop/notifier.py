"""
notifier.py — Sends push notifications to the user's Android phone via
Firebase Cloud Messaging (FCM).

The notification includes:
  - Title:  "🚀 BTC Signal Detected!"
  - Body:   "New rocket signal on BTC/USDT 15m chart. Check it now!"
  - A data payload with the URL of the latest screenshot so the mobile app
    can fetch it from the local FastAPI server.

If FCM credentials are not yet configured the function logs a warning and
returns gracefully — it will not crash the application.

Setup (one-time):
  1. Create a Firebase project at https://console.firebase.google.com/
  2. Enable Cloud Messaging.
  3. Download the service-account JSON (Project settings → Service accounts
     → Generate new private key).
  4. Set FCM_SERVER_KEY in config.json to the path of that JSON file,
     OR set it to your Legacy Server Key string (v1 API uses the JSON file).
  5. The mobile app sends its registration token to POST /register-device;
     that token is stored as FCM_DEVICE_TOKEN in config.json.
"""

import logging
import os

import config

logger = logging.getLogger(__name__)


def send_signal_notification(screenshot_filename: str | None = None) -> bool:
    """
    Send a push notification to the registered device.

    Parameters
    ----------
    screenshot_filename:
        Filename (not full path) of the chart screenshot, e.g.
        ``"signal_2026-03-10_20-51-14.png"``.  If provided the notification
        data payload includes a URL the mobile app can use to fetch it.

    Returns
    -------
    bool
        True if the notification was sent successfully, False otherwise.
    """
    device_token = config.get("FCM_DEVICE_TOKEN", "")
    if not device_token:
        logger.warning(
            "FCM_DEVICE_TOKEN is not set.  Register the device first via "
            "POST /register-device."
        )
        return False

    server_key = config.get("FCM_SERVER_KEY", "")
    service_account_path = config.get("FCM_SERVICE_ACCOUNT_JSON", "")

    # Build data payload
    data_payload: dict = {"type": "signal"}
    if screenshot_filename:
        host = config.get("SERVER_HOST", "0.0.0.0")
        port = config.get("SERVER_PORT", 8000)
        # Use localhost for the URL — when accessed remotely via ngrok the
        # mobile app replaces the host, but locally this always works.
        display_host = "127.0.0.1" if host == "0.0.0.0" else host
        data_payload["screenshot_url"] = (
            f"http://{display_host}:{port}/screenshot/{screenshot_filename}"
        )
        data_payload["filename"] = screenshot_filename

    # ── Try firebase-admin SDK first (recommended, v1 API) ────────────────
    if service_account_path and os.path.isfile(service_account_path):
        return _send_via_admin_sdk(device_token, data_payload)

    # ── Fall back to Legacy HTTP API (v1 deprecated but widely used) ──────
    if server_key:
        return _send_via_legacy_http(device_token, server_key, data_payload)

    logger.warning(
        "Neither FCM_SERVICE_ACCOUNT_JSON nor FCM_SERVER_KEY is configured.  "
        "Notification not sent.  See desktop/README.md for Firebase setup."
    )
    return False


# ── firebase-admin SDK ────────────────────────────────────────────────────────

def _send_via_admin_sdk(device_token: str, data: dict) -> bool:
    try:
        import firebase_admin  # noqa: PLC0415
        from firebase_admin import credentials, messaging  # noqa: PLC0415
    except ImportError:
        logger.error(
            "firebase-admin is not installed.  Run: pip install firebase-admin"
        )
        return False

    service_account_path = config.get("FCM_SERVICE_ACCOUNT_JSON", "")

    # Initialise once
    if not firebase_admin._apps:  # noqa: SLF001
        try:
            cred = credentials.Certificate(service_account_path)
            firebase_admin.initialize_app(cred)
        except Exception:  # noqa: BLE001
            logger.exception("Failed to initialise Firebase Admin SDK.")
            return False

    try:
        message = messaging.Message(
            notification=messaging.Notification(
                title="🚀 BTC Signal Detected!",
                body="New rocket signal on BTC/USDT 15m chart. Check it now!",
            ),
            data={k: str(v) for k, v in data.items()},
            token=device_token,
            android=messaging.AndroidConfig(priority="high"),
        )
        response = messaging.send(message)
        logger.info("FCM notification sent (admin SDK).  Message ID: %s", response)
        return True
    except Exception:  # noqa: BLE001
        logger.exception("Failed to send FCM notification via admin SDK.")
        return False


# ── Legacy HTTP API ───────────────────────────────────────────────────────────

def _send_via_legacy_http(device_token: str, server_key: str, data: dict) -> bool:
    try:
        import requests  # noqa: PLC0415
    except ImportError:
        logger.error("requests is not installed.  Run: pip install requests")
        return False

    url = "https://fcm.googleapis.com/fcm/send"
    headers = {
        "Authorization": f"key={server_key}",
        "Content-Type": "application/json",
    }
    payload = {
        "to": device_token,
        "priority": "high",
        "notification": {
            "title": "🚀 BTC Signal Detected!",
            "body": "New rocket signal on BTC/USDT 15m chart. Check it now!",
            "sound": "default",
        },
        "data": data,
    }

    try:
        resp = requests.post(url, json=payload, headers=headers, timeout=10)
        resp.raise_for_status()
        result = resp.json()
        if result.get("failure", 0) > 0:
            logger.error("FCM legacy HTTP: notification failed — %s", result)
            return False
        logger.info("FCM notification sent (legacy HTTP).  Response: %s", result)
        return True
    except Exception:  # noqa: BLE001
        logger.exception("Failed to send FCM notification via legacy HTTP.")
        return False
