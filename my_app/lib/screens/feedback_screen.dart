import 'package:flutter/material.dart';
import 'package:my_app/models/upload_video.dart';
import 'package:video_player/video_player.dart';

class FeedbackScreen extends StatelessWidget {
  FeedbackScreen({super.key, required this.videoResponse});
  final UploadVideoResult videoResponse;

  final List<Map<String, dynamic>> videos = [
    {
      "type": "good",
      "title": "What You Did Well",
      "videoPath": "assets/videos/squat_10.mp4",
      "feedback": [
        "Good depth in the squat movement",
        "Knees properly aligned with toes",
        "Maintained neutral spine throughout"
      ],
      "timestamp": "0:15"
    },
    {
      "type": "improvement",
      "title": "Area for Improvement",
      "videoPath": "assets/videos/squat_10.mp4",
      "feedback": [
        "Weight distribution slightly forward",
        "Focus on keeping weight centered over mid-foot"
      ],
      "severity": "medium",
      "timestamp": "0:08"
    },
    {
      "type": "improvement",
      "title": "Critical Fix Needed",
      "videoPath": "assets/videos/squat_10.mp4",
      "feedback": [
        "Slight knee cave on ascent",
        "Engage glutes more actively during upward movement"
      ],
      "severity": "high",
      "timestamp": "0:12"
    },
    {
      "type": "demonstration",
      "title": "Perfect Form Example",
      "videoPath": "assets/videos/squat_10.mp4",
      "feedback": [
        "This is how it should look",
        "Notice the controlled movement and proper alignment"
      ],
      "timestamp": "0:20"
    }
  ];

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(
        title: const Text('FormCheck'),
        actions: [
          IconButton(
            icon: const Icon(Icons.refresh),
            onPressed: () {},
          )
        ],
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
                  Navigator.pop(context);
                },
                icon: const Icon(Icons.replay),
                label: const Text("New Analysis"),
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
    _controller = VideoPlayerController.asset(widget.data['videoPath'])
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
      case "good":
        icon = const Icon(Icons.check_circle, size: 16, color: Colors.green);
        color = Colors.green;
        break;
      case "improvement":
        icon = const Icon(Icons.warning, size: 16, color: Colors.orange);
        color = severity == "high" ? Colors.red : Colors.orange;
        break;
      case "demonstration":
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
        color: color.withOpacity(0.2),
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
                        data['type'] == 'good' ? Icons.check : Icons.warning,
                        color: data['type'] == 'good' ? Colors.green : Colors.orange,
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
