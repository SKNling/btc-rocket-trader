# 📱 BTC Rocket Trader — Flutter Android App

> **Phase 3** of BTC Rocket Trader — the Android companion app for the desktop Python server.

The app receives Firebase push notifications when a 🚀 rocket signal is detected on TradingView, displays a chart screenshot, and lets you tap **BUY** or **SELL** to remotely trigger the trade on your desktop.

---

## Table of Contents

1. [Prerequisites](#prerequisites)
2. [Setup](#setup)
3. [Placing `google-services.json`](#placing-google-servicesjson)
4. [Building the APK](#building-the-apk)
5. [Installing on Your Phone](#installing-on-your-phone)
6. [Configuring the App](#configuring-the-app)
7. [Connecting to the Desktop Server](#connecting-to-the-desktop-server)
8. [Troubleshooting](#troubleshooting)

---

## Prerequisites

| Tool | Version | Notes |
|---|---|---|
| Flutter | 3.x stable | `flutter doctor` must show ✅ Flutter |
| Android Studio | Latest | Provides Android SDK |
| Android SDK | API 35 | Installed via Android Studio |
| Java / JDK | 11+ | Bundled with Android Studio |
| Firebase project | — | Already created: `btc-rocket-trader` |

---

## Setup

### 1. Clone the repo (if not done already)

```bash
git clone https://github.com/SKNling/btc-rocket-trader.git
cd btc-rocket-trader/mobile
```

### 2. Install Flutter dependencies

```bash
flutter pub get
```

---

## Placing `google-services.json`

> ⚠️ **This file is NOT committed to the repo** (it's in `.gitignore`).  
> You must place it manually before building.

1. Go to the [Firebase Console](https://console.firebase.google.com/)
2. Open the **btc-rocket-trader** project
3. Click the ⚙️ gear icon → **Project settings**
4. Scroll down to **Your apps** → select the Android app (`com.sknling.btcrockettrader`)
5. Click **Download google-services.json**
6. **Copy the file** into:
   ```
   mobile/android/app/google-services.json
   ```

---

## Building the APK

### Debug build (for testing)

```bash
cd mobile
flutter build apk --debug
```

Output: `build/app/outputs/flutter-apk/app-debug.apk`

### Release build (for your phone)

```bash
flutter build apk --release
```

Output: `build/app/outputs/flutter-apk/app-release.apk`

---

## Installing on Your Phone

### Option A — USB (recommended)

1. Enable **Developer Options** on your Android phone:
   - Go to **Settings → About phone**
   - Tap **Build number** 7 times
   - Go back to Settings → you'll see **Developer options**
2. In Developer options, enable **USB debugging**
3. Connect your phone to your PC with a USB cable
4. Run:
   ```bash
   flutter run
   ```
   (This builds, installs, and opens the app on your phone)

### Option B — Transfer APK

1. Build the release APK (see above)
2. Copy `app-release.apk` to your phone (via USB, Google Drive, email, etc.)
3. On your phone, open the APK file
4. Allow installation from unknown sources when prompted
5. Install and open the app

---

## Configuring the App

1. Open the app → tap the **⚙️ Settings** icon (top right)
2. Enter your **Server URL**:
   - Local network: `http://192.168.1.X:8000` (replace X with your laptop's IP)
   - Or a ngrok URL: `https://xxxx-xx-xx.ngrok-free.app`
3. Tap **Test Connection** to verify
4. The URL is saved automatically between restarts

### Finding your laptop's IP address

On Windows, open Command Prompt and run:
```cmd
ipconfig
```
Look for the **IPv4 Address** under your Wi-Fi adapter (e.g., `192.168.1.5`).

> **Both your phone and laptop must be on the same Wi-Fi network** for local IP to work.
> Use ngrok if you need to connect over mobile data.

---

## Connecting to the Desktop Server

1. Start the Python server on your laptop:
   ```bash
   cd desktop
   python main.py
   ```
2. Make sure your phone and laptop are on the **same Wi-Fi network**
3. In the app, go to Settings and enter `http://<laptop-ip>:8000`
4. Test the connection — you should see **✅ Connected!**

### Using ngrok (for remote access)

If you want to connect over mobile data or from anywhere:

1. Sign up for a free account at [ngrok.com](https://ngrok.com)
2. Install ngrok on your laptop
3. Run:
   ```bash
   ngrok http 8000
   ```
4. Copy the `https://xxxx.ngrok-free.app` URL into the app settings

---

## Troubleshooting

### ❌ "Not connected to server"
- Check that `python main.py` is running on your laptop
- Verify the IP address/URL in Settings
- Ensure phone and laptop are on the same Wi-Fi
- Check Windows Firewall — allow port 8000

### ❌ Not receiving push notifications
- Make sure `google-services.json` is placed in `mobile/android/app/`
- Make sure Firebase is configured in the desktop server (`firebase-credentials.json`)
- Check that the FCM token in Settings was registered with the server
- On Android 13+, grant notification permission when prompted

### ❌ "flutter pub get" fails
- Run `flutter doctor` and fix any issues shown
- Make sure you have internet access

### ❌ Build fails with Gradle errors
- Run `flutter clean` then `flutter pub get`
- Make sure Android Studio is installed with the Android SDK (API 35)
- Run `flutter doctor --android-licenses` to accept SDK licenses

### ❌ App crashes on launch
- Make sure `google-services.json` is present in `mobile/android/app/`
- Check that `Firebase.initializeApp()` completes without errors (check logcat in Android Studio)

---

## Project Structure

```
mobile/
├── lib/
│   ├── main.dart                    ← App entry point, Firebase init, FCM setup
│   ├── screens/
│   │   ├── home_screen.dart         ← Main screen: status, signal, BUY/SELL
│   │   └── settings_screen.dart     ← Settings: server URL, FCM token, status
│   ├── services/
│   │   ├── api_service.dart         ← HTTP client for desktop server
│   │   ├── fcm_service.dart         ← Firebase Cloud Messaging
│   │   └── notification_service.dart ← Local notifications
│   ├── widgets/
│   │   ├── trade_buttons.dart       ← BUY/SELL buttons
│   │   ├── signal_card.dart         ← Chart screenshot + signal info
│   │   └── connection_status.dart   ← Server connection indicator
│   └── models/
│       └── signal.dart              ← Signal data model
├── android/
│   └── app/
│       └── google-services.json     ← ⚠️ YOU must place this file here (not committed)
├── pubspec.yaml
└── README.md
```

---

## Firebase Configuration Notes

- Firebase project: **btc-rocket-trader**
- Android package name: `com.sknling.btcrockettrader`
- The desktop server needs `firebase-credentials.json` (service account key) to send push notifications
- The mobile app needs `google-services.json` to receive them

Both files are in `.gitignore` — never commit them to the repository.
