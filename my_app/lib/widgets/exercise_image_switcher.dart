import 'dart:async';
import 'package:flutter/material.dart';

class ExerciseImageSwitcher extends StatefulWidget {
  const ExerciseImageSwitcher({
    super.key,
    required this.first,
    required this.second,
    this.play = true,
    this.height = 145,
    this.width = 145,
    this.fit = BoxFit.contain,
    this.interval = const Duration(milliseconds: 700),
    this.fadeDuration = const Duration(milliseconds: 250),
  });

  final String first;
  final String second;
  final bool play;
  final double height;
  final double width;
  final BoxFit fit;
  final Duration interval;
  final Duration fadeDuration;

  @override
  State<ExerciseImageSwitcher> createState() => _ExerciseImageSwitcherState();
}

class _ExerciseImageSwitcherState extends State<ExerciseImageSwitcher> {
  late bool _showSecond;
  Timer? _timer;

  @override
  void initState() {
    super.initState();
    _showSecond = false;
    _maybeStart();
  }

  @override
  void didUpdateWidget(covariant ExerciseImageSwitcher oldWidget) {
    super.didUpdateWidget(oldWidget);
    if (oldWidget.play != widget.play || oldWidget.interval != widget.interval) {
      _maybeStart();
    }
  }

  void _maybeStart() {
    _timer?.cancel();
    if (widget.play) {
      _timer = Timer.periodic(widget.interval, (_) {
        if (mounted) setState(() => _showSecond = !_showSecond);
      });
    } else {
      setState(() => _showSecond = false);
    }
  }

  @override
  void dispose() {
    _timer?.cancel();
    super.dispose();
  }

  @override
  Widget build(BuildContext context) {
    final path = _showSecond ? widget.second : widget.first;
    final dpr = MediaQuery.of(context).devicePixelRatio;

    return SizedBox(
      width: widget.width,
      height: widget.height,
      child: AnimatedSwitcher(
        duration: widget.fadeDuration,
        switchInCurve: Curves.easeOut,
        switchOutCurve: Curves.easeIn,
        // evita pequeños “empujes” al hacer fade
        layoutBuilder: (current, previous) => Stack(
          alignment: Alignment.center,
          children: [
            ...previous,
            if (current != null) current,
          ],
        ),
        transitionBuilder: (child, anim) =>
            FadeTransition(opacity: anim, child: child),
        child: Image.asset(
          path,
          key: ValueKey(path),
          fit: widget.fit,
          alignment: Alignment.center,
          gaplessPlayback: true,
          // decodifica a un tamaño coherente con tu caja (ahorra memoria y artefactos)
          cacheWidth: (widget.width * dpr).round(),
          cacheHeight: (widget.height * dpr).round(),
        ),
      ),
    );
  }
}
