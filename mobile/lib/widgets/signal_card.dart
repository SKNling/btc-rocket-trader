import 'package:flutter/material.dart';
import '../models/signal.dart';

/// Card that displays the latest chart screenshot and signal metadata.
class SignalCard extends StatelessWidget {
  final Signal? signal;
  final bool isNew;

  const SignalCard({super.key, this.signal, this.isNew = false});

  @override
  Widget build(BuildContext context) {
    return Card(
      color: const Color(0xFF2A2A2A),
      shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(16)),
      elevation: 4,
      margin: const EdgeInsets.symmetric(horizontal: 16, vertical: 8),
      child: ClipRRect(
        borderRadius: BorderRadius.circular(16),
        child: signal == null || signal!.screenshotUrl.isEmpty
            ? _Placeholder()
            : _SignalContent(signal: signal!, isNew: isNew),
      ),
    );
  }
}

// ---------------------------------------------------------------------------
// Placeholder shown when no signal has been received yet.
// ---------------------------------------------------------------------------
class _Placeholder extends StatelessWidget {
  @override
  Widget build(BuildContext context) {
    return SizedBox(
      height: 200,
      child: Column(
        mainAxisAlignment: MainAxisAlignment.center,
        children: const [
          Icon(Icons.rocket_launch, size: 56, color: Color(0xFF2962FF)),
          SizedBox(height: 16),
          Text(
            'Waiting for signals…',
            style: TextStyle(
              color: Colors.white70,
              fontSize: 16,
            ),
          ),
          SizedBox(height: 8),
          Text(
            'A 🚀 will appear here when detected',
            style: TextStyle(color: Colors.white38, fontSize: 13),
          ),
        ],
      ),
    );
  }
}

// ---------------------------------------------------------------------------
// Content shown when a signal is available.
// ---------------------------------------------------------------------------
class _SignalContent extends StatelessWidget {
  final Signal signal;
  final bool isNew;

  const _SignalContent({required this.signal, required this.isNew});

  @override
  Widget build(BuildContext context) {
    return Column(
      crossAxisAlignment: CrossAxisAlignment.stretch,
      children: [
        // Screenshot image
        Stack(
          children: [
            Image.network(
              signal.screenshotUrl,
              fit: BoxFit.cover,
              width: double.infinity,
              height: 200,
              errorBuilder: (_, __, ___) => Container(
                height: 200,
                color: const Color(0xFF1E1E1E),
                child: const Center(
                  child: Icon(Icons.broken_image, color: Colors.white38, size: 48),
                ),
              ),
              loadingBuilder: (_, child, progress) {
                if (progress == null) return child;
                return SizedBox(
                  height: 200,
                  child: Center(
                    child: CircularProgressIndicator(
                      value: progress.expectedTotalBytes != null
                          ? progress.cumulativeBytesLoaded /
                              progress.expectedTotalBytes!
                          : null,
                      color: const Color(0xFF2962FF),
                    ),
                  ),
                );
              },
            ),
            if (isNew)
              Positioned(
                top: 8,
                right: 8,
                child: Container(
                  padding: const EdgeInsets.symmetric(horizontal: 10, vertical: 4),
                  decoration: BoxDecoration(
                    color: Colors.amber,
                    borderRadius: BorderRadius.circular(20),
                  ),
                  child: const Text(
                    '🚀 New Signal!',
                    style: TextStyle(
                      color: Colors.black,
                      fontWeight: FontWeight.bold,
                      fontSize: 12,
                    ),
                  ),
                ),
              ),
          ],
        ),
        // Timestamp row
        Padding(
          padding: const EdgeInsets.all(12),
          child: Row(
            children: [
              const Icon(Icons.access_time, size: 14, color: Colors.white54),
              const SizedBox(width: 6),
              Text(
                _formatTimestamp(signal.timestamp),
                style: const TextStyle(color: Colors.white54, fontSize: 13),
              ),
            ],
          ),
        ),
      ],
    );
  }

  String _formatTimestamp(DateTime dt) {
    final local = dt.toLocal();
    return '${local.year}-${_pad(local.month)}-${_pad(local.day)}  '
        '${_pad(local.hour)}:${_pad(local.minute)}:${_pad(local.second)}';
  }

  String _pad(int n) => n.toString().padLeft(2, '0');
}
