import 'dart:io';

enum MessageType {
  userVideo,
  systemReply,
}

class ChatMessage {
  final MessageType type;

  // For user messages (upload)
  final File? userVideo;

  // For system replies (response)
  final File? systemVideo;
  final String? text;

  ChatMessage({
    required this.type,
    this.userVideo,
    this.systemVideo,
    this.text,
  });

  /// Helper: checks if message has a video file
  bool get hasVideo => userVideo != null || systemVideo != null;

  /// Helper: returns the video file (user or system)
  File? get videoFile => userVideo ?? systemVideo;
}