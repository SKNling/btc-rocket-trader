import 'package:firebase_messaging/firebase_messaging.dart';
import 'api_service.dart';
import 'notification_service.dart';

/// Handles Firebase Cloud Messaging setup, token management, and message routing.
class FcmService {
  static final _messaging = FirebaseMessaging.instance;

  /// Request notification permissions and wire up message handlers.
  static Future<void> initialize() async {
    // Request permission (required on iOS; shows permission dialog on Android 13+).
    await _messaging.requestPermission(
      alert: true,
      badge: true,
      sound: true,
    );

    // Get initial token and register with the server.
    final token = await _messaging.getToken();
    if (token != null) {
      await ApiService.registerDevice(token);
    }

    // Re-register whenever the token refreshes.
    _messaging.onTokenRefresh.listen((newToken) async {
      await ApiService.registerDevice(newToken);
    });

    // Foreground messages: show an in-app local notification.
    FirebaseMessaging.onMessage.listen((message) {
      NotificationService.showNotification(
        title: message.notification?.title ?? '🚀 BTC Signal',
        body: message.notification?.body ?? 'New signal detected!',
      );
    });

    // Background / terminated: handled by [firebaseMessagingBackgroundHandler]
    // registered in main.dart via FirebaseMessaging.onBackgroundMessage.
  }

  /// Returns the current FCM token, or null if unavailable.
  static Future<String?> getToken() => _messaging.getToken();
}

/// Top-level function required by Firebase for background message handling.
/// Must be a top-level (not inside a class) annotated function.
@pragma('vm:entry-point')
Future<void> firebaseMessagingBackgroundHandler(RemoteMessage message) async {
  // Firebase is already initialised in the isolate by the plugin.
  await NotificationService.showNotification(
    title: message.notification?.title ?? '🚀 BTC Signal',
    body: message.notification?.body ?? 'New signal detected!',
  );
}
