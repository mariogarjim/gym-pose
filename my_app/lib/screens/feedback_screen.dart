import 'package:flutter/material.dart';
import 'dart:io';
import 'package:my_app/models/upload_video.dart';
import 'package:my_app/screens/configure_analysis_screen.dart';
import 'package:video_player/video_player.dart';
import 'package:path/path.dart' as path;

class FeedbackScreen extends StatefulWidget {
  const FeedbackScreen({super.key, required this.videoResponse});
  final UploadVideoResult videoResponse;

  @override
  State<FeedbackScreen> createState() => _FeedbackScreenState();
}


class _FeedbackScreenState extends State<FeedbackScreen> {
  List<Map<String, dynamic>> videos = [];
  int overallScore = 85;
  Map<String, dynamic> _createVideoData(String type, String title, String videoPath, List<String> feedback) {
    return {
      "type": type,
      "title": title,
      "videoPath": videoPath,
      "feedback": feedback,
      "severity": "high",
      "timestamp": "0:00" 
    };
  }

  void _getFeedback() {
    final extractedDirectory = widget.videoResponse.extractedDirectory;
    final Directory videosDir = Directory(path.join(extractedDirectory.path, "videos"));

    final List<Directory> feedbackDirs = videosDir
    .listSync(recursive: false)
    .whereType<Directory>()
    .toList();

    final List<Map<String, dynamic>> newVideos = [];

    for (final dir in feedbackDirs) {

      final List<FileSystemEntity> videoFiles = dir.listSync(recursive: false)
      .whereType<File>()
      .toList();

      for (final file in videoFiles) {
        final String type = dir.path.split('/').last.split('_').first;
        final String title = file.path.split('/').last.split('.').first;
        final String videoPath = file.path;
        const List<String> feedback = [];
        final videoData = _createVideoData(type, title, videoPath, feedback);
        newVideos.add(videoData);
      }
    }
    setState(() {
      overallScore = 85;
      videos = newVideos;
    });
  }

  @override
  void initState() {
    super.initState();
    _getFeedback();
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(
        title: const Text('FormCheck')
      ),
      body: Column(
        children: [
          Container(
            padding: const EdgeInsets.all(16),
            color: Theme.of(context).cardColor,
            child: Column(
              children: [
                Text(
                  "$overallScore%",
                  style: TextStyle(
                    fontSize: 32,
                    fontWeight: FontWeight.bold,
                    color: Theme.of(context).colorScheme.primary,
                  ),
                ),
                const SizedBox(height: 4),
                const Text("Form Score for Squat"),
              ],
            ),
          ),
          Expanded(
            child: PageView.builder(
              itemCount: videos.length,
              scrollDirection: Axis.vertical,
              itemBuilder: (context, index) {
                return _VideoCard(data: videos[index]);
              },
            ),
          ),
        ],
      ),
      bottomNavigationBar: Container(
        padding: const EdgeInsets.all(16),
        decoration: BoxDecoration(
          border: Border(top: BorderSide(color: Colors.grey.shade300)),
          color: Theme.of(context).scaffoldBackgroundColor,
        ),
        child: Row(
          children: [
            Expanded(
              child: ElevatedButton.icon(
                onPressed: () {
                  Navigator.push(context, MaterialPageRoute(builder: (context) => const ConfigureAnalysisScreen()));
                },
                icon: const Icon(Icons.replay, color: Colors.white),
                label: const Text("New Analysis", style: TextStyle(color: Colors.white)),
                style: ElevatedButton.styleFrom(
                  backgroundColor: Theme.of(context).colorScheme.primary,
                  foregroundColor: Colors.white,
                ),
              ),
            ),
            const SizedBox(width: 10),
            Expanded(
              child: OutlinedButton.icon(
                onPressed: () {},
                icon: const Icon(Icons.save),
                label: const Text("Save Results"),
              ),
            ),
          ],
        ),
      ),
    );
  }
}

class _VideoCard extends StatefulWidget {
  final Map<String, dynamic> data;

  const _VideoCard({required this.data});

  @override
  State<_VideoCard> createState() => _VideoCardState();
}

class _VideoCardState extends State<_VideoCard> {
  late VideoPlayerController _controller;

  @override
  void initState() {
    super.initState();
    _controller = VideoPlayerController.file(File(widget.data['videoPath']))
      ..initialize().then((_) {
        setState(() {});
        _controller.setLooping(true);
        _controller.play();
      });
  }

  @override
  void dispose() {
    _controller.dispose();
    super.dispose();
  }

  Widget _buildBadge(String type, [String? severity]) {
    Icon icon;
    Color color;

    switch (type) {
      case "positive":
        icon = const Icon(Icons.check_circle, size: 16, color: Colors.green);
        color = Colors.green;
        break;
      case "improvement":
        icon = const Icon(Icons.warning, size: 16, color: Colors.orange);
        color = severity == "high" ? Colors.red : Colors.orange;
        break;
      case "negative":
        icon = const Icon(Icons.play_arrow, size: 16, color: Colors.blue);
        color = Colors.blue;
        break;
      default:
        icon = const Icon(Icons.info);
        color = Colors.grey;
    }

    return Container(
      padding: const EdgeInsets.symmetric(horizontal: 8, vertical: 4),
      decoration: BoxDecoration(
        color: color.withValues(alpha: 0.2),
        borderRadius: BorderRadius.circular(20),
      ),
      child: Row(
        mainAxisSize: MainAxisSize.min,
        children: [icon, const SizedBox(width: 4), Text(type.toUpperCase())],
      ),
    );
  }

  @override
  Widget build(BuildContext context) {
    final data = widget.data;
    return Stack(
      fit: StackFit.expand,
      children: [
        // Video
        _controller.value.isInitialized
            ? FittedBox(
                fit: BoxFit.cover,
                child: SizedBox(
                  width: _controller.value.size.width,
                  height: _controller.value.size.height,
                  child: VideoPlayer(_controller),
                ),
              )
            : const Center(child: CircularProgressIndicator()),

        // Overlay info
        Positioned(
          top: 40,
          left: 16,
          child: _buildBadge(data['type'], data['severity']),
        ),
        Positioned(
          top: 40,
          right: 16,
          child: Container(
            padding: const EdgeInsets.symmetric(horizontal: 8, vertical: 4),
            color: Colors.black54,
            child: Text(
              data['timestamp'],
              style: const TextStyle(color: Colors.white),
            ),
          ),
        ),
        Positioned(
          bottom: 100,
          left: 16,
          right: 16,
          child: Column(
            crossAxisAlignment: CrossAxisAlignment.start,
            children: [
              Text(
                data['title'],
                style: const TextStyle(
                  fontSize: 20,
                  fontWeight: FontWeight.bold,
                  color: Colors.white,
                ),
              ),
              const SizedBox(height: 8),
              ...List.generate(
                (data['feedback'] as List).length,
                (index) => Padding(
                  padding: const EdgeInsets.symmetric(vertical: 4),
                  child: Row(
                    children: [
                      Icon(
                        data['type'] == 'positive' ? Icons.check : Icons.warning,
                        color: data['type'] == 'positive' ? Colors.green : Colors.orange,
                        size: 16,
                      ),
                      const SizedBox(width: 8),
                      Expanded(
                        child: Text(
                          data['feedback'][index],
                          style: const TextStyle(color: Colors.white),
                        ),
                      ),
                    ],
                  ),
                ),
              ),
            ],
          ),
        ),
      ],
    );
  }
}
