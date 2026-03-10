class Signal {
  final DateTime timestamp;
  final String screenshotFilename;
  final String screenshotUrl;

  const Signal({
    required this.timestamp,
    required this.screenshotFilename,
    required this.screenshotUrl,
  });

  factory Signal.fromJson(Map<String, dynamic> json, String baseUrl) {
    final filename = (json['screenshot_filename'] as String?) ?? '';
    return Signal(
      timestamp: json['timestamp'] != null
          ? DateTime.tryParse(json['timestamp'] as String) ?? DateTime.now()
          : DateTime.now(),
      screenshotFilename: filename,
      screenshotUrl: filename.isNotEmpty
          ? '$baseUrl/screenshot/$filename'
          : '',
    );
  }
}
