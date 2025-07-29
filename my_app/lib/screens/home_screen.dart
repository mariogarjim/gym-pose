import 'dart:io';

import 'package:flutter/material.dart';
import 'package:image_picker/image_picker.dart';
import 'package:path/path.dart' as path;
import 'package:path_provider/path_provider.dart';

import '../models/chat_message.dart';
import '../core/api/video_upload_service.dart';

class HomeScreen extends StatefulWidget {
  const HomeScreen({super.key});

  @override
  State<HomeScreen> createState() => _HomeScreenState();
}

class _HomeScreenState extends State<HomeScreen> {
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
        title: const Text('SmartPose', style: TextStyle(color: Colors.white, fontWeight: FontWeight.bold)),
        backgroundColor: Theme.of(context).colorScheme.primary,
      ),
      body: SingleChildScrollView(
        child: Column(
          children: [
            const HeroSection(),
            Padding(
              padding: const EdgeInsets.all(20.0),
              child: InkWell(
                onTap: _isUploading ? null : _pickAndUploadVideo,
                borderRadius: BorderRadius.circular(16),
                child: AnimatedContainer(
                  duration: const Duration(milliseconds: 300),
                  padding: const EdgeInsets.all(24),
                  width: double.infinity,
                  decoration: BoxDecoration(
                    color: Colors.white,
                    border: Border.all(
                      color: Colors.grey.shade400,
                      width: 2,
                      style: BorderStyle.solid,
                    ),
                    borderRadius: BorderRadius.circular(16),
                  ),
                  child: Column(
                    mainAxisSize: MainAxisSize.min,
                    children: [
                      Icon(Icons.video_library, size: 60, color: Theme.of(context).colorScheme.primary),
                      const SizedBox(height: 16),
                      const Text(
                        'Upload your workout video',
                        style: TextStyle(fontSize: 20, fontWeight: FontWeight.bold),
                      ),
                      const SizedBox(height: 8),
                      const Text(
                        'Tap to select a video from your gallery. \nSupports MP4, MOV, AVI up to 100MB',
                        textAlign: TextAlign.center,
                        style: TextStyle(color: Colors.grey),
                      ),
                      const SizedBox(height: 24),
                      if (_isUploading)
                        const CircularProgressIndicator()
                      else
                        ElevatedButton.icon(
                          onPressed: _pickAndUploadVideo,
                          icon: const Row(
                            mainAxisSize: MainAxisSize.min,
                            children: [
                              Icon(Icons.upload, size: 18, color: Colors.white),
                            ],
                          ),
                          label: const Text('Choose Video File', style: TextStyle(color: Colors.white)),
                          style: ElevatedButton.styleFrom(
                            backgroundColor: Theme.of(context).colorScheme.primary,
                            padding: const EdgeInsets.symmetric(
                              vertical: 16, horizontal: 24),
                          ),
                        ),
                    ],
                  ),
                ),
              ),
            ),
          ],
        ),
      ),
    );
  }
}

// Hero Section with fade-in animation
class HeroSection extends StatefulWidget {
  const HeroSection({super.key});

  @override
  State<HeroSection> createState() => _HeroSectionState();
}

class _HeroSectionState extends State<HeroSection>
    with SingleTickerProviderStateMixin {
  late AnimationController _controller;
  late Animation<double> _fadeIn;

  @override
  void initState() {
    super.initState();
    _controller = AnimationController(
      duration: const Duration(seconds: 2),
      vsync: this,
    );
    _fadeIn = Tween<double>(begin: 0, end: 1).animate(
      CurvedAnimation(parent: _controller, curve: Curves.easeIn),
    );
    _controller.forward();
  }

  @override
  void dispose() {
    _controller.dispose();
    super.dispose();
  }

  @override
  Widget build(BuildContext context) {
    final theme = Theme.of(context);
    final foreground = theme.colorScheme.onSurface;
    final primary = theme.colorScheme.primary;
    final muted = Colors.grey.shade600;

    return FadeTransition(
      opacity: _fadeIn,
      child: Container(
        padding: const EdgeInsets.symmetric(vertical: 40, horizontal: 20),
        child: Column(
          children: [
            // Title
            RichText(
              textAlign: TextAlign.center,
              text: TextSpan(
                children: [
                  TextSpan(
                    text: 'Perfect your form\n',
                    style: TextStyle(
                      fontSize: 36,
                      fontWeight: FontWeight.w800,
                      color: foreground,
                      height: 1.2,
                      letterSpacing: -0.5,
                    ),
                  ),
                  TextSpan(
                    text: 'with AI guidance',
                    style: TextStyle(
                      fontSize: 36,
                      fontWeight: FontWeight.w800,
                      color: primary,
                      shadows: [
                        Shadow(
                          offset: const Offset(0, 1),
                          blurRadius: 4,
                          color: primary.withValues(alpha: 0.3),
                        ),
                      ],
                    ),
                  ),
                  const TextSpan(
                    text: '\n',
                  ),
                  TextSpan(
                    style: TextStyle(
                      fontSize: 18,
                      height: 1.5,
                      color: muted,
                    ),
                    children: const [
                      TextSpan(
                        text: '\nUpload a video of your exercise and receive feedback with corrections.',
                        style: TextStyle(
                          fontSize: 20,
                          fontWeight: FontWeight.w600,
                        ),
                      ),
                    ],
                  ),
                ],
              ),
            ),

          ],
        ),
      ),
    );
  }
}
