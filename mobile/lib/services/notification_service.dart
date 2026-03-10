import 'package:flutter_local_notifications/flutter_local_notifications.dart';

/// Manages the local notification channel used to display in-app and background
/// signal alerts.
class NotificationService {
  static final _plugin = FlutterLocalNotificationsPlugin();
  static bool _initialised = false;

  static const _channelId = 'btc_signals';
  static const _channelName = 'BTC Signals';
  static const _channelDesc = 'Rocket signal alerts from BTC Rocket Trader';

  /// Must be called once during app startup (after Firebase.initializeApp).
  static Future<void> initialize() async {
    if (_initialised) return;

    const androidSettings =
        AndroidInitializationSettings('@mipmap/ic_launcher');

    const initSettings = InitializationSettings(android: androidSettings);

    await _plugin.initialize(
      initSettings,
      onDidReceiveNotificationResponse: _onNotificationTap,
    );

    // Create the high-importance notification channel for Android 8+.
    const channel = AndroidNotificationChannel(
      _channelId,
      _channelName,
      description: _channelDesc,
      importance: Importance.high,
    );

    await _plugin
        .resolvePlatformSpecificImplementation<
            AndroidFlutterLocalNotificationsPlugin>()
        ?.createNotificationChannel(channel);

    _initialised = true;
  }

  /// Shows a notification with [title] and [body].
  static Future<void> showNotification({
    required String title,
    required String body,
  }) async {
    if (!_initialised) await initialize();

    const androidDetails = AndroidNotificationDetails(
      _channelId,
      _channelName,
      channelDescription: _channelDesc,
      importance: Importance.high,
      priority: Priority.high,
      icon: '@mipmap/ic_launcher',
    );

    const details = NotificationDetails(android: androidDetails);

    await _plugin.show(
      DateTime.now().millisecondsSinceEpoch ~/ 1000,
      title,
      body,
      details,
    );
  }

  static void _onNotificationTap(NotificationResponse response) {
    // Navigation is handled by the app's router via the pending-navigation
    // pattern; tapping opens the app which shows the home screen.
  }
}
