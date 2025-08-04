// lib/widgets/animated_image_switcher.dart

import 'dart:async';
import 'package:flutter/material.dart';

class AnimatedImageSwitcher extends StatefulWidget {
  final String exerciseName;
  final bool isSelected;
  final List<String> exerciseImages;
  const AnimatedImageSwitcher({
    required this.exerciseName,
    required this.isSelected,
    required this.exerciseImages,
    Key? key,
  }) : super(key: key);

  @override
  AnimatedImageSwitcherState createState() => AnimatedImageSwitcherState();
}

class AnimatedImageSwitcherState extends State<AnimatedImageSwitcher> {
  late Timer _timer;
  int _imageIndex = 0;


  @override
  void initState() {
    super.initState();
    _timer = Timer.periodic(const Duration(milliseconds: 500), (timer) {
      setState(() {
        _imageIndex = (_imageIndex + 1) % widget.exerciseImages.length;
      });
    });
  }

  @override
  void dispose() {
    _timer.cancel();
    super.dispose();
  }

  @override
  Widget build(BuildContext context) {
    return Column(
      crossAxisAlignment: CrossAxisAlignment.stretch,
      children: [
        Expanded(
          child: ClipRRect(
            borderRadius: const BorderRadius.vertical(top: Radius.circular(14)),
            child: Image.asset(
              widget.exerciseImages[_imageIndex],
              fit: BoxFit.cover,
            ),
          ),
        ),
        Padding(
          padding: const EdgeInsets.all(12),
          child: Row(
            children: [
              Expanded(
                child: Text(
                  widget.exerciseName,
                  style: const TextStyle(
                    fontSize: 16,
                    fontWeight: FontWeight.w800,
                  ),
                  textAlign: TextAlign.center,
                ),
              ),
              if (widget.isSelected)
                Icon(
                  Icons.check_circle,
                  color: Theme.of(context).colorScheme.primary,
                ),
            ],
          ),
        ),
      ],
    );
  }
}
