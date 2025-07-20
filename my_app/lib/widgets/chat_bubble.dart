// lib/widgets/chat_bubble.dart

import 'package:flutter/material.dart';
import '../models/chat_message.dart';
import 'video_bubble.dart';

class ChatBubble extends StatelessWidget {
  final ChatMessage message;

  const ChatBubble({super.key, required this.message});

  @override
  Widget build(BuildContext context) {
    final isUser = message.type == MessageType.userVideo;

    return Container(
      margin: const EdgeInsets.symmetric(horizontal: 12, vertical: 6),
      alignment: isUser ? Alignment.centerRight : Alignment.centerLeft,
      child: Column(
        crossAxisAlignment:
            isUser ? CrossAxisAlignment.end : CrossAxisAlignment.start,
        children: [
          if (!isUser && message.text != null)
            Container(
              padding: const EdgeInsets.all(12),
              margin: const EdgeInsets.only(bottom: 6),
              decoration: BoxDecoration(
                color: Colors.grey[300],
                borderRadius: BorderRadius.circular(12),
              ),
              child: Text(message.text!),
            ),
          if (message.hasVideo)
            VideoBubble(file: message.videoFile!),
        ],
      ),
    );
  }
}
