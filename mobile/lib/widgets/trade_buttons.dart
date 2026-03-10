import 'package:flutter/material.dart';
import 'package:flutter/services.dart';

typedef TradeCallback = Future<void> Function(String action);

/// Side-by-side BUY (blue) and SELL (red) action buttons.
class TradeButtons extends StatelessWidget {
  final bool connected;
  final bool buyLoading;
  final bool sellLoading;
  final TradeCallback onTrade;

  const TradeButtons({
    super.key,
    required this.connected,
    required this.buyLoading,
    required this.sellLoading,
    required this.onTrade,
  });

  @override
  Widget build(BuildContext context) {
    return Padding(
      padding: const EdgeInsets.symmetric(horizontal: 16, vertical: 8),
      child: Row(
        children: [
          Expanded(child: _TradeButton(
            action: 'BUY',
            color: const Color(0xFF2962FF),
            icon: Icons.trending_up,
            isLoading: buyLoading,
            enabled: connected && !buyLoading && !sellLoading,
            onTap: () async {
              HapticFeedback.mediumImpact();
              await onTrade('BUY');
            },
          )),
          const SizedBox(width: 12),
          Expanded(child: _TradeButton(
            action: 'SELL',
            color: const Color(0xFFFF1744),
            icon: Icons.trending_down,
            isLoading: sellLoading,
            enabled: connected && !buyLoading && !sellLoading,
            onTap: () async {
              HapticFeedback.mediumImpact();
              await onTrade('SELL');
            },
          )),
        ],
      ),
    );
  }
}

class _TradeButton extends StatelessWidget {
  final String action;
  final Color color;
  final IconData icon;
  final bool isLoading;
  final bool enabled;
  final VoidCallback onTap;

  const _TradeButton({
    required this.action,
    required this.color,
    required this.icon,
    required this.isLoading,
    required this.enabled,
    required this.onTap,
  });

  @override
  Widget build(BuildContext context) {
    return SizedBox(
      height: 64,
      child: ElevatedButton(
        onPressed: enabled ? onTap : null,
        style: ElevatedButton.styleFrom(
          backgroundColor: enabled ? color : Colors.grey[700],
          foregroundColor: Colors.white,
          disabledBackgroundColor: Colors.grey[800],
          disabledForegroundColor: Colors.grey[600],
          shape: RoundedRectangleBorder(
            borderRadius: BorderRadius.circular(12),
          ),
          elevation: enabled ? 4 : 0,
        ),
        child: isLoading
            ? const SizedBox(
                width: 24,
                height: 24,
                child: CircularProgressIndicator(
                  strokeWidth: 2.5,
                  color: Colors.white,
                ),
              )
            : Row(
                mainAxisAlignment: MainAxisAlignment.center,
                children: [
                  Icon(icon, size: 22),
                  const SizedBox(width: 8),
                  Text(
                    action,
                    style: const TextStyle(
                      fontSize: 18,
                      fontWeight: FontWeight.bold,
                      letterSpacing: 1.2,
                    ),
                  ),
                ],
              ),
      ),
    );
  }
}
