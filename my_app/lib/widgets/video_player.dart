import 'package:flutter/material.dart';
import 'package:flutter/services.dart';
import 'package:video_player/video_player.dart';

/// Video vertical adaptable que calcula su tamaño según:
/// - fracción del ancho disponible (widthFraction)
/// - relación altura/ancho (aspectHOverW), p.ej. 5/4
/// - altura máxima (maxHeight)
/// Se centra dentro de su contenedor padre.
class AdaptiveAspectVideoPlayer extends StatefulWidget {
  const AdaptiveAspectVideoPlayer({
    super.key,
    required this.videoPath,
    required this.severity,
    this.autoplay = false,
    this.loop = false,
    this.aspectHOverW = 4 / 3, // 5:4 ⇒ más “altura” que 1:1 y más ancho que 9:16
    this.maxHeight = 400,
  });

  final String videoPath;
  final String severity; // "warning" / "harmful" (ajusta a tu modelo)
  final bool autoplay;
  final bool loop;

  /// Relación ALTURA/ANCHO (no ancho/altura). 5/4 => 1.25.
  final double aspectHOverW;

  /// Altura máxima absoluta permitida (px).
  final double maxHeight;

  @override
  State<AdaptiveAspectVideoPlayer> createState() => _AdaptiveAspectVideoPlayerState();
}

class _AdaptiveAspectVideoPlayerState extends State<AdaptiveAspectVideoPlayer> {
  late final VideoPlayerController _controller;
  bool _isInitialized = false;
  bool _isPlaying = false;

  @override
  void initState() {
    super.initState();

    _controller = VideoPlayerController.asset(widget.videoPath);
    _controller.addListener(_onControllerTick);

    _controller.initialize().then((_) async {
      if (!mounted) return;
      if (widget.loop) await _controller.setLooping(true);
      if (widget.autoplay) {
        await _controller.play();
        _isPlaying = true;
      }
      setState(() => _isInitialized = true);
    });
  }

  void _onControllerTick() {
    if (!mounted || !_controller.value.isInitialized) return;

    final bool playing = _controller.value.isPlaying;
    if (playing != _isPlaying) {
      setState(() {
        _isPlaying = playing;
        
      });
    }

    // Si no hace loop y terminó, mostrar overlay de play otra vez.
    if (!widget.loop &&
        !_controller.value.isPlaying &&
        _controller.value.position >= _controller.value.duration) {
      if (mounted && _isPlaying) {
        setState(() => _isPlaying = false);
      }
    }
  }

  Future<void> _togglePlayPause() async {
    if (!_isInitialized) return;
    if (_isPlaying) {
      await _controller.pause();
    } else {
      await _controller.play();
    }
    if (mounted) setState(() => _isPlaying = !_isPlaying);
  }

  Future<void> _openFullscreen() async {
    // Forzamos landscape y UI inmersiva durante el fullscreen.
    
    SystemChrome.setEnabledSystemUIMode(SystemUiMode.immersiveSticky);

    if (!mounted) return;

    await Navigator.of(context).push<void>(
      MaterialPageRoute<void>(
        builder: (_) => _FullscreenScaffold(controller: _controller),
      ),
    );

    SystemChrome.setEnabledSystemUIMode(SystemUiMode.edgeToEdge);

    if (mounted) {
      setState(() {
        _isPlaying = _controller.value.isPlaying;
      });
    }
  }

  @override
  void dispose() {
    _controller.removeListener(_onControllerTick);
    _controller.dispose();
    super.dispose();
  }

  @override
  Widget build(BuildContext context) {
    // Calculamos tamaño destino (centrado) manteniendo la relación y respetando maxHeight.
    return LayoutBuilder(
      builder: (BuildContext context, BoxConstraints constraints) {
        final double maxW = constraints.maxWidth;
        double width = maxW;
        double height = width * widget.aspectHOverW;

        if (height > widget.maxHeight) {
          height = widget.maxHeight;
          width = height / widget.aspectHOverW;
        }

        return Align(
          alignment: Alignment.center, // centrado dentro del “box” implícito
          child: SizedBox(
            width: width,
            height: height,
            child: ClipRRect(
              child: _isInitialized
                  ? GestureDetector(
                      behavior: HitTestBehavior.opaque,
                      onTap: _togglePlayPause,
                      child: Stack(
                        alignment: Alignment.center,
                        children: <Widget>[
                          Container(
                            height: double.infinity,
                            width: double.infinity,
                            color: Colors.black,
                            alignment: Alignment.center,
                            child: const Icon(Icons.play_arrow, color: Colors.white, size: 64),
                          ),
                          FittedBox(
                            fit: BoxFit.cover,
                            child: SizedBox(
                              width: _controller.value.size.width,
                              height: _controller.value.size.height,
                              child: VideoPlayer(_controller),
                            ),
                          ),
                          // Overlay de play (visible cuando está en pausa)
                          IgnorePointer(
                            ignoring: true, // let taps reach the GestureDetector
                            child: AnimatedOpacity(
                              opacity: _isPlaying ? 0.0 : 1.0,
                              duration: const Duration(milliseconds: 180),
                              child: const Center(
                                child: Icon(Icons.play_arrow, color: Colors.white, size: 64),
                              ),
                            ),
                          ),
                          Positioned(
                            bottom: 0,
                            right: 0,
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
                          Positioned(
                            top: 0,
                            right: 0,
                            child: IconButton(
                              icon: const Icon(Icons.file_download_outlined, color: Colors.white, size: 28),
                              onPressed: _openFullscreen,
                              tooltip: 'Fullscreen',
                            ),
                          ),
                        ],
                      ),
                    )
                  : Container(
                      color: Colors.black12,
                      alignment: Alignment.center,
                      child: const CircularProgressIndicator(),
                    ),
            ),
          ),
        );
      },
    );
  }
}

/// Ejemplo sencillo de pantalla fullscreen reutilizando el mismo controller.
/// (Puedes sustituirlo por tu FullScreenVideoPage si lo prefieres.)
class _FullscreenScaffold extends StatelessWidget {
  const _FullscreenScaffold({required this.controller});

  final VideoPlayerController controller;

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      backgroundColor: Colors.black,
      body: GestureDetector(
        behavior: HitTestBehavior.opaque,
        onTap: () => Navigator.of(context).pop(),
        child: Center(
          child: AspectRatio(
            aspectRatio: controller.value.aspectRatio == 0
                ? 16 / 9
                : controller.value.aspectRatio,
            child: VideoPlayer(controller),
          ),
        ),
      ),
    );
  }
}
