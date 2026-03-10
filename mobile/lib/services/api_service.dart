import 'dart:convert';
import 'package:http/http.dart' as http;
import 'package:shared_preferences/shared_preferences.dart';
import '../models/signal.dart';

class ApiService {
  static const _baseUrlKey = 'server_base_url';
  static const _defaultBaseUrl = 'http://192.168.1.x:8000';
  static const _timeout = Duration(seconds: 5);

  /// Returns the base URL saved in SharedPreferences.
  static Future<String> getBaseUrl() async {
    final prefs = await SharedPreferences.getInstance();
    return prefs.getString(_baseUrlKey) ?? _defaultBaseUrl;
  }

  /// Persists [url] to SharedPreferences.
  static Future<void> saveBaseUrl(String url) async {
    final prefs = await SharedPreferences.getInstance();
    await prefs.setString(_baseUrlKey, url.trimRight().replaceAll(RegExp(r'/$'), ''));
  }

  // ---------------------------------------------------------------------------
  // Endpoints
  // ---------------------------------------------------------------------------

  /// GET /health — Returns true if server is reachable.
  static Future<bool> checkHealth() async {
    try {
      final base = await getBaseUrl();
      final response = await http
          .get(Uri.parse('$base/health'))
          .timeout(_timeout);
      return response.statusCode == 200;
    } catch (_) {
      return false;
    }
  }

  /// GET /status — Returns raw status map.
  static Future<Map<String, dynamic>?> getStatus() async {
    try {
      final base = await getBaseUrl();
      final response = await http
          .get(Uri.parse('$base/status'))
          .timeout(_timeout);
      if (response.statusCode == 200) {
        return jsonDecode(response.body) as Map<String, dynamic>;
      }
    } catch (_) {}
    return null;
  }

  /// GET /latest-signal — Returns the latest [Signal] or null.
  static Future<Signal?> getLatestSignal() async {
    try {
      final base = await getBaseUrl();
      final response = await http
          .get(Uri.parse('$base/latest-signal'))
          .timeout(_timeout);
      if (response.statusCode == 200) {
        final json = jsonDecode(response.body) as Map<String, dynamic>;
        return Signal.fromJson(json, base);
      }
    } catch (_) {}
    return null;
  }

  /// Returns the full URL for a screenshot file.
  static Future<String> getScreenshotUrl(String filename) async {
    final base = await getBaseUrl();
    return '$base/screenshot/$filename';
  }

  /// POST /trade — action: "BUY" or "SELL". Returns true on success.
  static Future<bool> sendTrade(String action) async {
    try {
      final base = await getBaseUrl();
      final response = await http
          .post(
            Uri.parse('$base/trade'),
            headers: {'Content-Type': 'application/json'},
            body: jsonEncode({'action': action}),
          )
          .timeout(_timeout);
      return response.statusCode == 200;
    } catch (_) {
      return false;
    }
  }

  /// POST /register-device — Registers the FCM token with the server.
  static Future<bool> registerDevice(String token) async {
    try {
      final base = await getBaseUrl();
      final response = await http
          .post(
            Uri.parse('$base/register-device'),
            headers: {'Content-Type': 'application/json'},
            body: jsonEncode({'token': token}),
          )
          .timeout(_timeout);
      return response.statusCode == 200;
    } catch (_) {
      return false;
    }
  }
}
