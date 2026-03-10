import 'package:flutter/material.dart';
import '../models/signal.dart';
import '../services/api_service.dart';
import '../widgets/connection_status.dart';
import '../widgets/signal_card.dart';
import '../widgets/trade_buttons.dart';
import 'settings_screen.dart';

class HomeScreen extends StatefulWidget {
  const HomeScreen({super.key});

  @override
  State<HomeScreen> createState() => _HomeScreenState();
}

class _HomeScreenState extends State<HomeScreen> {
  bool _connected = false;
  bool _checkingConnection = false;
  Signal? _signal;
  bool _isNewSignal = false;
  bool _buyLoading = false;
  bool _sellLoading = false;

  @override
  void initState() {
    super.initState();
    _refresh();
  }

  Future<void> _refresh() async {
    setState(() => _checkingConnection = true);

    final health = await ApiService.checkHealth();
    Signal? latestSignal;
    if (health) {
      latestSignal = await ApiService.getLatestSignal();
    }

    if (!mounted) return;
    setState(() {
      _connected = health;
      _checkingConnection = false;
      if (latestSignal != null) {
        _isNewSignal = _signal == null ||
            latestSignal.timestamp.isAfter(_signal!.timestamp);
        _signal = latestSignal;
      }
    });
  }

  Future<void> _trade(String action) async {
    if (action == 'BUY') {
      setState(() => _buyLoading = true);
    } else {
      setState(() => _sellLoading = true);
    }

    final success = await ApiService.sendTrade(action);

    if (!mounted) return;
    setState(() {
      _buyLoading = false;
      _sellLoading = false;
    });

    final message = success
        ? '✅ $action order sent!'
        : '❌ Failed to send $action order';

    ScaffoldMessenger.of(context).showSnackBar(
      SnackBar(
        content: Text(message),
        backgroundColor: success
            ? (action == 'BUY' ? const Color(0xFF2962FF) : const Color(0xFFFF1744))
            : Colors.grey[800],
        behavior: SnackBarBehavior.floating,
        duration: const Duration(seconds: 2),
      ),
    );
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(
        title: const Text(
          '🚀 BTC Rocket Trader',
          style: TextStyle(fontWeight: FontWeight.bold),
        ),
        actions: [
          IconButton(
            icon: const Icon(Icons.settings),
            tooltip: 'Settings',
            onPressed: () async {
              await Navigator.push(
                context,
                MaterialPageRoute(builder: (_) => const SettingsScreen()),
              );
              // Refresh after returning from settings (URL may have changed).
              _refresh();
            },
          ),
        ],
      ),
      body: RefreshIndicator(
        onRefresh: _refresh,
        color: const Color(0xFF2962FF),
        child: CustomScrollView(
          physics: const AlwaysScrollableScrollPhysics(),
          slivers: [
            SliverPadding(
              padding: const EdgeInsets.only(top: 16, left: 16, right: 16),
              sliver: SliverToBoxAdapter(
                child: Row(
                  children: [
                    const Text(
                      'Server: ',
                      style: TextStyle(color: Colors.white54, fontSize: 13),
                    ),
                    ConnectionStatus(
                      connected: _connected,
                      checking: _checkingConnection,
                    ),
                  ],
                ),
              ),
            ),
            SliverToBoxAdapter(
              child: SignalCard(signal: _signal, isNew: _isNewSignal),
            ),
            SliverFillRemaining(
              hasScrollBody: false,
              child: Column(
                mainAxisAlignment: MainAxisAlignment.end,
                children: [
                  if (!_connected)
                    Padding(
                      padding: const EdgeInsets.symmetric(
                          horizontal: 16, vertical: 8),
                      child: Text(
                        'Not connected to server.\n'
                        'Go to ⚙️ Settings and enter your server URL.',
                        textAlign: TextAlign.center,
                        style: const TextStyle(
                            color: Colors.redAccent, fontSize: 13),
                      ),
                    ),
                  TradeButtons(
                    connected: _connected,
                    buyLoading: _buyLoading,
                    sellLoading: _sellLoading,
                    onTrade: _trade,
                  ),
                  const SizedBox(height: 16),
                ],
              ),
            ),
          ],
        ),
      ),
    );
  }
}
