import 'package:flutter/material.dart';
import 'package:flutter/services.dart';
import '../services/api_service.dart';
import '../services/fcm_service.dart';

class SettingsScreen extends StatefulWidget {
  const SettingsScreen({super.key});

  @override
  State<SettingsScreen> createState() => _SettingsScreenState();
}

class _SettingsScreenState extends State<SettingsScreen> {
  final _urlController = TextEditingController();
  bool _testingConnection = false;
  bool? _connectionResult;
  Map<String, dynamic>? _statusData;
  String? _fcmToken;

  @override
  void initState() {
    super.initState();
    _loadSettings();
  }

  Future<void> _loadSettings() async {
    final url = await ApiService.getBaseUrl();
    final token = await FcmService.getToken();
    if (!mounted) return;
    setState(() {
      _urlController.text = url;
      _fcmToken = token;
    });
  }

  Future<void> _saveUrl() async {
    await ApiService.saveBaseUrl(_urlController.text.trim());
    if (!mounted) return;
    ScaffoldMessenger.of(context).showSnackBar(
      const SnackBar(
        content: Text('✅ Server URL saved'),
        behavior: SnackBarBehavior.floating,
        duration: Duration(seconds: 1),
      ),
    );
  }

  Future<void> _testConnection() async {
    await ApiService.saveBaseUrl(_urlController.text.trim());
    setState(() {
      _testingConnection = true;
      _connectionResult = null;
      _statusData = null;
    });

    final ok = await ApiService.checkHealth();
    Map<String, dynamic>? status;
    if (ok) {
      status = await ApiService.getStatus();
    }

    if (!mounted) return;
    setState(() {
      _testingConnection = false;
      _connectionResult = ok;
      _statusData = status;
    });
  }

  @override
  void dispose() {
    _urlController.dispose();
    super.dispose();
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(
        title: const Text('⚙️ Settings'),
      ),
      body: ListView(
        padding: const EdgeInsets.all(16),
        children: [
          // ----------------------------------------------------------------
          // Server URL
          // ----------------------------------------------------------------
          _SectionHeader('Server URL'),
          const SizedBox(height: 8),
          TextField(
            controller: _urlController,
            keyboardType: TextInputType.url,
            autocorrect: false,
            style: const TextStyle(color: Colors.white),
            decoration: InputDecoration(
              hintText: 'http://192.168.1.x:8000',
              hintStyle: const TextStyle(color: Colors.white38),
              filled: true,
              fillColor: const Color(0xFF2A2A2A),
              border: OutlineInputBorder(
                borderRadius: BorderRadius.circular(10),
                borderSide: BorderSide.none,
              ),
              prefixIcon:
                  const Icon(Icons.link, color: Color(0xFF2962FF)),
              suffixIcon: IconButton(
                icon: const Icon(Icons.save_alt, color: Colors.white54),
                tooltip: 'Save',
                onPressed: _saveUrl,
              ),
            ),
          ),
          const SizedBox(height: 4),
          const Text(
            'Enter your laptop\'s IP (e.g. http://192.168.1.5:8000) '
            'or a ngrok URL (e.g. https://xxxx.ngrok-free.app)',
            style: TextStyle(color: Colors.white38, fontSize: 12),
          ),
          const SizedBox(height: 16),

          // ----------------------------------------------------------------
          // Test Connection
          // ----------------------------------------------------------------
          ElevatedButton.icon(
            onPressed: _testingConnection ? null : _testConnection,
            icon: _testingConnection
                ? const SizedBox(
                    width: 18,
                    height: 18,
                    child:
                        CircularProgressIndicator(strokeWidth: 2, color: Colors.white),
                  )
                : const Icon(Icons.wifi_find),
            label: Text(_testingConnection ? 'Testing…' : 'Test Connection'),
            style: ElevatedButton.styleFrom(
              backgroundColor: const Color(0xFF2962FF),
              foregroundColor: Colors.white,
              shape: RoundedRectangleBorder(
                  borderRadius: BorderRadius.circular(10)),
            ),
          ),

          if (_connectionResult != null) ...[
            const SizedBox(height: 12),
            _ResultBanner(success: _connectionResult!),
          ],

          // ----------------------------------------------------------------
          // Server status
          // ----------------------------------------------------------------
          if (_statusData != null) ...[
            const SizedBox(height: 24),
            _SectionHeader('Server Status'),
            const SizedBox(height: 8),
            _StatusCard(data: _statusData!),
          ],

          const SizedBox(height: 24),

          // ----------------------------------------------------------------
          // FCM Token
          // ----------------------------------------------------------------
          _SectionHeader('FCM Device Token'),
          const SizedBox(height: 8),
          Container(
            padding: const EdgeInsets.all(12),
            decoration: BoxDecoration(
              color: const Color(0xFF2A2A2A),
              borderRadius: BorderRadius.circular(10),
            ),
            child: Column(
              crossAxisAlignment: CrossAxisAlignment.start,
              children: [
                SelectableText(
                  _fcmToken ?? 'Loading…',
                  style: const TextStyle(
                      color: Colors.white70, fontSize: 11, fontFamily: 'monospace'),
                ),
                const SizedBox(height: 8),
                Align(
                  alignment: Alignment.centerRight,
                  child: TextButton.icon(
                    onPressed: _fcmToken == null
                        ? null
                        : () {
                            Clipboard.setData(
                                ClipboardData(text: _fcmToken!));
                            ScaffoldMessenger.of(context).showSnackBar(
                              const SnackBar(
                                content: Text('📋 Token copied'),
                                behavior: SnackBarBehavior.floating,
                                duration: Duration(seconds: 1),
                              ),
                            );
                          },
                    icon: const Icon(Icons.copy, size: 16),
                    label: const Text('Copy'),
                  ),
                ),
              ],
            ),
          ),

          const SizedBox(height: 24),

          // ----------------------------------------------------------------
          // About
          // ----------------------------------------------------------------
          _SectionHeader('About'),
          const SizedBox(height: 8),
          Container(
            padding: const EdgeInsets.all(12),
            decoration: BoxDecoration(
              color: const Color(0xFF2A2A2A),
              borderRadius: BorderRadius.circular(10),
            ),
            child: const Column(
              crossAxisAlignment: CrossAxisAlignment.start,
              children: [
                Text('BTC Rocket Trader',
                    style: TextStyle(
                        color: Colors.white,
                        fontWeight: FontWeight.bold,
                        fontSize: 15)),
                SizedBox(height: 4),
                Text('Version 1.0.0',
                    style: TextStyle(color: Colors.white54)),
                SizedBox(height: 4),
                Text('Phase 3 of BTC Rocket Trader',
                    style: TextStyle(color: Colors.white54)),
              ],
            ),
          ),

          const SizedBox(height: 32),
        ],
      ),
    );
  }
}

// ---------------------------------------------------------------------------
// Helper widgets
// ---------------------------------------------------------------------------

class _SectionHeader extends StatelessWidget {
  final String title;
  const _SectionHeader(this.title);

  @override
  Widget build(BuildContext context) {
    return Text(
      title,
      style: const TextStyle(
        color: Color(0xFF2962FF),
        fontWeight: FontWeight.bold,
        fontSize: 13,
        letterSpacing: 0.8,
      ),
    );
  }
}

class _ResultBanner extends StatelessWidget {
  final bool success;
  const _ResultBanner({required this.success});

  @override
  Widget build(BuildContext context) {
    return Container(
      padding: const EdgeInsets.symmetric(horizontal: 14, vertical: 10),
      decoration: BoxDecoration(
        color: success
            ? Colors.green.withAlpha(40)
            : Colors.red.withAlpha(40),
        borderRadius: BorderRadius.circular(10),
        border: Border.all(
          color: success ? Colors.greenAccent : Colors.redAccent,
        ),
      ),
      child: Row(
        children: [
          Icon(
            success ? Icons.check_circle : Icons.cancel,
            color: success ? Colors.greenAccent : Colors.redAccent,
            size: 18,
          ),
          const SizedBox(width: 8),
          Text(
            success ? '✅ Connected!' : '❌ Connection failed',
            style: TextStyle(
              color: success ? Colors.greenAccent : Colors.redAccent,
              fontWeight: FontWeight.w600,
            ),
          ),
        ],
      ),
    );
  }
}

class _StatusCard extends StatelessWidget {
  final Map<String, dynamic> data;
  const _StatusCard({required this.data});

  @override
  Widget build(BuildContext context) {
    return Container(
      padding: const EdgeInsets.all(12),
      decoration: BoxDecoration(
        color: const Color(0xFF2A2A2A),
        borderRadius: BorderRadius.circular(10),
      ),
      child: Column(
        children: data.entries.map((entry) {
          return Padding(
            padding: const EdgeInsets.symmetric(vertical: 2),
            child: Row(
              crossAxisAlignment: CrossAxisAlignment.start,
              children: [
                Text(
                  '${entry.key}: ',
                  style: const TextStyle(
                      color: Colors.white54, fontSize: 12),
                ),
                Expanded(
                  child: Text(
                    '${entry.value}',
                    style: const TextStyle(color: Colors.white70, fontSize: 12),
                  ),
                ),
              ],
            ),
          );
        }).toList(),
      ),
    );
  }
}
