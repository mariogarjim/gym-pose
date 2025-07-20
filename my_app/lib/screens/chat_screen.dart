// lib/screens/video_chat_screen.dart

import 'dart:io';

import 'package:flutter/material.dart';
import 'package:image_picker/image_picker.dart';
import 'package:path/path.dart' as path;
import 'package:path_provider/path_provider.dart';

import '../models/chat_message.dart';
import '../widgets/chat_bubble.dart';
import '../core/api/video_upload_service.dart';

class ChatScreen extends StatefulWidget {
  const ChatScreen({super.key});

  @override
  State<ChatScreen> createState() => _ChatScreenState();
}

class _ChatScreenState extends State<ChatScreen> {
  final List<ChatMessage> _chatMessages = [];
  final ImagePicker _picker = ImagePicker();
  bool _isUploading = false;
  final ScrollController _scrollController = ScrollController();

  void _scrollToBottom() {
    WidgetsBinding.instance.addPostFrameCallback((_) {
      _scrollController.animateTo(
        _scrollController.position.maxScrollExtent,
        duration: const Duration(milliseconds: 300),
        curve: Curves.easeOut,
      );
    });
  }

  Future<void> _pickAndUploadVideo() async {
    final XFile? video = await _picker.pickVideo(source: ImageSource.gallery);
    if (video == null) return;

    final ext = path.extension(video.path).toLowerCase();
    if (ext != '.mp4') {
      _showSnackBar('Only MP4 videos are supported.');
      return;
    }

    final userFile = File(video.path);

    setState(() {
      _chatMessages.add(ChatMessage(type: MessageType.userVideo, userVideo: userFile));
    });
    _scrollToBottom();

    setState(() => _isUploading = true);

    try {
      final responseBytes = await VideoUploadService.uploadVideo(userFile);

      final outputFile = await _saveProcessedVideo(responseBytes);

      // Dummy response text for now
      const responseText = 'Here is your processed video response!';

      setState(() {
        _chatMessages.add(ChatMessage(
          type: MessageType.systemReply,
          text: responseText,
          systemVideo: outputFile,
        ));
      });

      _scrollToBottom();
    } catch (e) {
      _showSnackBar('Upload failed: $e');
    } finally {
      setState(() => _isUploading = false);
    }
  }

  Future<File> _saveProcessedVideo(List<int> bytes) async {
    final tempDir = await getTemporaryDirectory();
    final filePath = path.join(tempDir.path, 'response_${DateTime.now().millisecondsSinceEpoch}.mp4');
    final file = File(filePath);
    return await file.writeAsBytes(bytes);
  }

  void _showSnackBar(String message) {
    ScaffoldMessenger.of(context).showSnackBar(SnackBar(content: Text(message)));
  }

  @override
  void dispose() {
    _scrollController.dispose();
    super.dispose();
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(
        title: const Text('Video Chat'),
        backgroundColor: Theme.of(context).colorScheme.inversePrimary,
      ),
      body: Column(
        children: [
          Expanded(
            child: ListView.builder(
              controller: _scrollController,
              itemCount: _chatMessages.length,
              itemBuilder: (context, index) {
                final message = _chatMessages[index];
                return ChatBubble(message: message);
              },
            ),
          ),
          if (_isUploading)
            const Padding(
              padding: EdgeInsets.all(12.0),
              child: CircularProgressIndicator(),
            ),
          Padding(
            padding: const EdgeInsets.all(12.0),
            child: ElevatedButton.icon(
              onPressed: _isUploading ? null : _pickAndUploadVideo,
              icon: const Icon(Icons.upload),
              label: const Text('Upload Video'),
            ),
          ),
        ],
      ),
    );
  }
}
