import 'package:flutter/material.dart';

/// A small indicator showing whether the app is connected to the desktop server.
class ConnectionStatus extends StatelessWidget {
  final bool connected;
  final bool checking;

  const ConnectionStatus({
    super.key,
    required this.connected,
    this.checking = false,
  });

  @override
  Widget build(BuildContext context) {
    return Container(
      padding: const EdgeInsets.symmetric(horizontal: 14, vertical: 6),
      decoration: BoxDecoration(
        color: const Color(0xFF2A2A2A),
        borderRadius: BorderRadius.circular(20),
      ),
      child: Row(
        mainAxisSize: MainAxisSize.min,
        children: [
          if (checking)
            const SizedBox(
              width: 10,
              height: 10,
              child: CircularProgressIndicator(strokeWidth: 1.5),
            )
          else
            Container(
              width: 10,
              height: 10,
              decoration: BoxDecoration(
                shape: BoxShape.circle,
                color: connected ? Colors.greenAccent : Colors.redAccent,
              ),
            ),
          const SizedBox(width: 8),
          Text(
            checking
                ? 'Checking…'
                : connected
                    ? 'Connected'
                    : 'Disconnected',
            style: TextStyle(
              color: checking
                  ? Colors.white70
                  : connected
                      ? Colors.greenAccent
                      : Colors.redAccent,
              fontSize: 13,
              fontWeight: FontWeight.w600,
            ),
          ),
        ],
      ),
    );
  }
}
