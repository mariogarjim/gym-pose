import 'package:flutter/material.dart';
import 'package:flutter/services.dart';
import 'package:my_app/screens/full_screen_video_screen.dart';
import 'package:video_player/video_player.dart';

class SquareVideoPlayer extends StatefulWidget {
  final String videoPath;
  final String severity;
  final bool autoplay;
  final bool loop;

  const SquareVideoPlayer({
    Key? key,
    required this.videoPath,
    required this.severity,
    this.autoplay = false,
    this.loop = false,
  }) : super(key: key);

  @override
  SquareVideoPlayerState createState() => SquareVideoPlayerState();
}

class SquareVideoPlayerState extends State<SquareVideoPlayer> {
  late VideoPlayerController _controller;
  bool _isInitialized = false;
  bool _isPlaying = false;

  @override
  void initState() {
    super.initState();

    _controller = VideoPlayerController.asset(widget.videoPath)
      ..initialize().then((_) {
        if (widget.autoplay) {
          _controller.play();
          _isPlaying = true;
        }
        if (widget.loop) _controller.setLooping(true);
        setState(() {
          _isInitialized = true;
        });
      });

      if (!mounted || !_controller.value.isInitialized) return;
      final playing = _controller.value.isPlaying;
      if (playing != _isPlaying) {
        setState(() => _isPlaying = playing);
      }
      // If not looping and reached the end, ensure play button is shown again.
      if (!widget.loop &&
          !_controller.value.isPlaying &&
          _controller.value.position >= _controller.value.duration) {
        if (mounted && _isPlaying) setState(() => _isPlaying = false);
      }

  }

  Future<void> _togglePlayPause() async {
    if (!_isInitialized) return;
    if (_isPlaying) {
      await _controller.pause();
    } else {
      await _controller.play();
    }
    setState(() => _isPlaying = !_isPlaying);
  }

  Future<void> _openFullscreen() async {
    await SystemChrome.setPreferredOrientations([
      DeviceOrientation.landscapeRight,
      DeviceOrientation.landscapeLeft,
    ]);
    SystemChrome.setEnabledSystemUIMode(SystemUiMode.immersiveSticky);

    if (!mounted) return;

    await Navigator.push(
      context,
      MaterialPageRoute(
        builder: (_) => FullScreenVideoPage(videoPath: widget.videoPath),
      ),
    );

    // Restore portrait after exit
    await SystemChrome.setPreferredOrientations([
      DeviceOrientation.portraitUp,
    ]);
    SystemChrome.setEnabledSystemUIMode(SystemUiMode.edgeToEdge);
    setState(() {
      _isPlaying = false;
    });
  }

  @override
  void dispose() {
    _controller.dispose();
    super.dispose();
  }

  @override
  Widget build(BuildContext context) {
    return AspectRatio(
      aspectRatio: 1, // square
      child: ClipRRect(
        borderRadius: BorderRadius.circular(12), // rounded corners
        child: _isInitialized
            ? GestureDetector(
                behavior: HitTestBehavior.opaque,
                onTap: _togglePlayPause, // tap anywhere to play/pause
                child: Stack(
                  alignment: Alignment.center,
                  children: [
                    VideoPlayer(_controller),
                    // White play button overlay (visible when paused)
                    AnimatedOpacity(
                      opacity: _isPlaying ? 0.0 : 1.0,
                      duration: const Duration(milliseconds: 180),
                      child: SizedBox.expand(
                          child: Stack(
                            children: [
                            Container(
                              width: double.infinity,
                              height: double.infinity,
                              color: Colors.black38, // subtle dim for contrast
                              alignment: Alignment.center,
                              child: const Icon(
                                Icons.play_arrow,
                                color: Colors.white,
                                size: 64,
                              ),
                            ),
                            Align(
                              alignment: Alignment.topLeft,
                              child: Padding(
                                padding: const EdgeInsets.all(8),
                                child: Container(
                                  alignment: Alignment.center,
                                  decoration: BoxDecoration(
                                    color: widget.severity == "warning" ? Colors.yellow.withAlpha(80) : Colors.red.withAlpha(80),
                                    borderRadius: BorderRadius.circular(12),
                                  ),
                                  width: 100,
                                  height: 40,
                                  child: Text(widget.severity == "warning" ? "⚠️ Improve" : "🚨 Fix this!", style: const TextStyle(color: Colors.white, fontSize: 16, fontWeight: FontWeight.bold)),
                                ),
                              ),
                            ),
                          ],
                        ),
                      ),
                    ),
                    Positioned(
                      bottom: 8,
                      right: 8,
                      child: IconButton(
                        icon: const Icon(
                          Icons.fullscreen_outlined,
                          color: Colors.white,
                          size: 28,
                        ),
                        onPressed: _openFullscreen,
                        tooltip: 'Fullscreen',
                      ),
                    ),
                  ],
                ),
              )
            : Container(
                color: Colors.black12, // placeholder color
                child: const Center(
                  child: CircularProgressIndicator(),
                ),
              ),
      ),
    );
  }
}
