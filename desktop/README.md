# 🚀 BTC Rocket Trader — Desktop App

A Python desktop application that runs on your Windows laptop 24/7 to:

1. **Watch the screen** for new 🚀 rocket emojis on a TradingView chart (BTC/USDT 15m)
2. **Detect NEW rockets only** using snapshot comparison (ignores old ones)
3. **Take a screenshot** of the chart when a new rocket appears
4. **Send a push notification** to your Android phone via Firebase Cloud Messaging (FCM)
5. **Run a local FastAPI server** so your phone app can reach it (via ngrok)
6. **Click BUY or SELL** on TradingView when you tap the button in your phone app

---

## Architecture

```
┌──────────────────────────── YOUR LAPTOP (Windows) ──────────────────────────┐
│                                                                              │
│   TradingView Desktop App                                                    │
│   ┌────────────────────────┐                                                 │
│   │  🔵 BUY  🔴 SELL      │  ← pyautogui clicks these                      │
│   │                        │                                                 │
│   │   BTC/USDT 15m chart   │                                                 │
│   │                        │                                                 │
│   │   🚀 🚀 🚀  ←rockets  │  ← screen_watcher.py scans this area           │
│   └────────────────────────┘                                                 │
│                                                                              │
│   main.py  ──────┬──── screen_watcher.py  (background thread)               │
│                  ├──── screenshot.py       (saves PNG on signal)             │
│                  ├──── notifier.py         (sends FCM push notification)     │
│                  ├──── clicker.py          (pyautogui BUY/SELL clicks)       │
│                  └──── server.py           (FastAPI on 0.0.0.0:8000)         │
│                              │                                               │
│                          ngrok tunnel                                        │
└──────────────────────────────┼───────────────────────────────────────────────┘
                               │ Internet
                               ▼
                  ┌──────────────────────────┐
                  │  📱 Android App (Flutter) │
                  │  • Push notification      │
                  │  • Chart screenshot       │
                  │  • BUY / SELL buttons     │
                  └──────────────────────────┘
```

---

## Prerequisites

| Requirement | Version | Notes |
|---|---|---|
| Python | 3.11 or newer | [python.org](https://www.python.org/downloads/) |
| TradingView Desktop | Latest | Installed from [tradingview.com](https://www.tradingview.com/) |
| Firebase account | Free | [console.firebase.google.com](https://console.firebase.google.com/) |
| ngrok account | Free | [ngrok.com](https://ngrok.com/) |

---

## Installation

### 1. Clone the repository and navigate to the desktop folder

```bash
git clone https://github.com/SKNling/btc-rocket-trader.git
cd btc-rocket-trader/desktop
```

### 2. Create and activate a virtual environment (recommended)

```bash
python -m venv .venv
# Windows:
.venv\Scripts\activate
```

### 3. Install Python dependencies

```bash
pip install -r requirements.txt
```

---

## Firebase Setup (Push Notifications)

### Step 1 — Create a Firebase project

1. Go to [console.firebase.google.com](https://console.firebase.google.com/)
2. Click **"Add project"**, enter a name (e.g., `btc-rocket-trader`), and click through
3. Once created, open your project

### Step 2 — Enable Cloud Messaging

1. In the left sidebar click **"Project settings"** (gear icon)
2. Go to the **"Cloud Messaging"** tab
3. Note the **Server key** (you'll need it, or use the service-account approach below)

### Step 3 — Download the service-account JSON (recommended)

1. In **Project settings** → **Service accounts** tab
2. Click **"Generate new private key"** → **"Generate key"**
3. Save the downloaded JSON file somewhere safe on your laptop
   (e.g., `C:\Users\YourName\firebase-service-account.json`)

### Step 4 — Update config.json

Open `config.json` and set **one** of the following:

```json
{
  "FCM_SERVICE_ACCOUNT_JSON": "C:/Users/YourName/firebase-service-account.json"
}
```

*or* (legacy approach):

```json
{
  "FCM_SERVER_KEY": "AAAA...your-server-key..."
}
```

> **Security note:** Never commit your service-account JSON or server key to Git.

---

## ngrok Setup (Remote Access from Phone)

ngrok creates a secure public URL that forwards to your laptop's local server,
so your phone can reach it from anywhere.

### Step 1 — Create a free ngrok account

Go to [ngrok.com](https://ngrok.com/) and sign up (free tier is sufficient).

### Step 2 — Get your auth token

Log in → go to **"Your Authtoken"** page → copy the token.

### Step 3 — Add the token to config.json

```json
{
  "NGROK_AUTH_TOKEN": "your-ngrok-auth-token-here"
}
```

When you start `main.py`, it will print the public ngrok URL.
Enter that URL in your Flutter mobile app as the server address.

---

## First-Time Setup

Before running the main app you need to tell it **where on your screen**
the rocket emoji area and the BUY/SELL buttons are.

1. Open **TradingView Desktop App** and navigate to the BTC/USDT 15m chart
   with your rocket indicator active.
2. Run the setup tool:

```bash
python setup_regions.py
```

3. Follow the on-screen instructions:
   - **Step 1**: Draw a rectangle around the bottom area of the chart
     where 🚀 rockets appear.
   - **Step 2**: Click the center of the 🔵 **BUY** button (top-left of TradingView).
   - **Step 3**: Click the center of the 🔴 **SELL** button (top-left of TradingView).
   - **Step 4**: Draw a rectangle around the entire chart area (for screenshots).

4. Your settings are saved to `config.json`.

> You only need to run setup once, unless you move or resize the TradingView window.

---

## Running the Application

```bash
python main.py
```

The app will:
- Load your config
- Start watching the screen for rockets
- Print the ngrok URL (if configured)
- Start the API server at `http://127.0.0.1:8000`

Press **Ctrl+C** to stop.

---

## API Endpoints

| Method | Endpoint | Description |
|---|---|---|
| `GET` | `/health` | Liveness check |
| `GET` | `/status` | Watcher status, last signal time |
| `GET` | `/latest-signal` | Latest signal info + screenshot URL |
| `GET` | `/screenshot/{filename}` | Serve a chart screenshot |
| `POST` | `/trade` | Execute BUY or SELL on TradingView |
| `POST` | `/register-device` | Store the mobile app's FCM token |

Interactive docs: `http://127.0.0.1:8000/docs`

### POST /trade example

```json
{ "action": "BUY" }
```
or
```json
{ "action": "SELL" }
```

---

## Configuration Reference (`config.json`)

| Key | Default | Description |
|---|---|---|
| `SCAN_REGION` | `null` | `[x, y, width, height]` — screen area to watch for rockets |
| `CHART_REGION` | `null` | `[x, y, width, height]` — full chart area for screenshots |
| `BUY_BUTTON_POS` | `null` | `[x, y]` — screen position of the BUY button |
| `SELL_BUTTON_POS` | `null` | `[x, y]` — screen position of the SELL button |
| `CHECK_INTERVAL` | `10` | Seconds between scan checks (5–30 recommended) |
| `FCM_SERVICE_ACCOUNT_JSON` | `""` | Path to Firebase service-account JSON file |
| `FCM_SERVER_KEY` | `""` | Firebase legacy server key (alternative to JSON) |
| `FCM_DEVICE_TOKEN` | `""` | Mobile device FCM token (set automatically by the app) |
| `SERVER_HOST` | `"0.0.0.0"` | FastAPI bind address |
| `SERVER_PORT` | `8000` | FastAPI port |
| `SCREENSHOT_DIR` | `./screenshots` | Directory where chart screenshots are saved |
| `NGROK_AUTH_TOKEN` | `""` | ngrok auth token for remote access |

---

## Troubleshooting

### "Setup is incomplete" message at startup

Run `python setup_regions.py` to define the scan region and button positions.

### Rockets not being detected

- Make sure the **SCAN_REGION** covers the bottom part of the chart where rockets appear.
- Check that TradingView is **not minimised** — screen capture requires the window to be visible.
- Try reducing `CHECK_INTERVAL` to `5` seconds.
- Open `logs/btc_rocket_trader.log` to see detection debug output.

### BUY/SELL button click misses

- Re-run `setup_regions.py` to recalibrate button positions.
- Make sure you haven't moved or resized the TradingView window since setup.
- The app brings TradingView to the foreground automatically; ensure no other
  full-screen window is blocking it.

### Push notification not received

- Check that `FCM_SERVICE_ACCOUNT_JSON` or `FCM_SERVER_KEY` is set in `config.json`.
- Check that `FCM_DEVICE_TOKEN` is set (the mobile app sends this to `/register-device`).
- Look in `logs/btc_rocket_trader.log` for FCM error messages.

### pyautogui FailSafe triggered

Move the mouse away from the very top-left corner of your screen.
`pyautogui.FAILSAFE = True` means that if the mouse reaches (0, 0) it
raises an exception as an emergency stop.

### ngrok "tunnel not found"

- Make sure `NGROK_AUTH_TOKEN` is correct in `config.json`.
- Only one free ngrok tunnel can be open at a time.

---

## File Structure

```
desktop/
├── main.py            ← Start here
├── screen_watcher.py  ← Rocket detection (snapshot comparison)
├── screenshot.py      ← Chart screenshot capture
├── clicker.py         ← pyautogui BUY/SELL button clicker
├── server.py          ← FastAPI local server
├── notifier.py        ← Firebase Cloud Messaging push notifications
├── config.py          ← Config load/save (config.json)
├── setup_regions.py   ← Interactive first-time setup
├── requirements.txt   ← Python dependencies
├── README.md          ← This file
├── config.json        ← Generated by setup_regions.py (do not commit)
├── screenshots/       ← Saved chart screenshots
└── logs/              ← Application log files
```

---

## Phase 2 — Flutter Mobile App (Coming Next)

The Flutter Android app will:
- Receive push notifications when a rocket is detected
- Display the chart screenshot inside the notification and on the home screen
- Provide **BUY** and **SELL** buttons that send commands to the laptop's API
- Register its FCM token with the desktop app automatically

---

## Security Notes

- `config.json` contains sensitive keys — **never commit it to Git**
  (it is listed in `.gitignore`).
- The FastAPI server has no authentication by default.  Only expose it via
  ngrok to trusted users.
- `pyautogui.FAILSAFE = True` is enabled as a safety net for the clicker.
