// lib/screens/feedback_exercise_selection.dart
import 'dart:async';
import 'package:flutter/material.dart';
import 'package:my_app/screens/feedback_exercise_screen.dart';
import 'package:my_app/theme/text_styles.dart';
import 'package:my_app/app_shell.dart';

final List<Map<String, dynamic>> mockAnalysis = [
  {
    "exerciseName": "Lateral Raise",
    "date": "25-12-2024",
    "exerciseRating": 90,
  },
  {
    "exerciseName": "Squats",
    "date": "22-05-2024",
    "exerciseRating": 20,
  },
  {
    "exerciseName": "Pull Ups",
    "date": "20-11-2024",
    "exerciseRating": 50,
  },
];

class FeedbackExerciseSelectionsScreen extends StatelessWidget {
  const FeedbackExerciseSelectionsScreen({
    super.key,
    this.exerciseName = '',   // <-- add this
  });

  final String exerciseName;  // <-- and this

  Color getCircleColor(exerciseRating) {
    // Interpolate between red → yellow → green
    double t = (exerciseRating.clamp(0, 100)) / 100.0;

    if (t < 0.5) {
      // From red (0) to yellow (50)
      return Color.lerp(Colors.red, Colors.yellow, t * 2)!;
    } else {
      // From yellow (50) to green (100)
      return Color.lerp(Colors.yellow, Colors.green, (t - 0.5) * 2)!;
    }
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      body: SafeArea(
        child: Padding(
          padding: const EdgeInsets.all(20),
          child: ListView.separated(
            itemCount: mockAnalysis.length,
            separatorBuilder: (_, __) => const SizedBox(height: 16),
            itemBuilder: (context, index) {
              final item = mockAnalysis[index];
              final String name = (item['exerciseName'] as String?) ?? '';
              final String dateStr = (item['date'] as String?) ?? '';
              final int exerciseRating = item['exerciseRating'] as int? ?? 0;
              final bool isDimmed = name.trim().toLowerCase().replaceAll(RegExp(r'[^a-z0-9]'), '') == 'pullups'; // dim only Pull Ups items

              return GestureDetector(
                onTap: isDimmed ? () {
                  showDialog(
                    context: context,
                    builder: (context) => AlertDialog(
                      title: Text("Your videos are being analysed by our AI models. This process may take a few minutes.", style: AppTextStylesV2.requirementDescription,),
                    ),
                  );
                } : () {
                  final shell = AppShell.of(context);
                  shell?.setTextToShow(name);
                  shell?.pushOnTab(
                    2,
                    MaterialPageRoute(
                      builder: (_) => FeedbackExerciseScreen(exerciseName: name),
                    ),
                  );
                },
                child: Material(
                  color: Colors.white,
                  borderRadius: BorderRadius.circular(12),
                  clipBehavior: Clip.antiAlias,
                  child: Stack(
                    children: [
                      Padding(
                        padding: const EdgeInsets.all(20),
                        child: Row(
                          crossAxisAlignment: CrossAxisAlignment.center,
                          children: [
                          isDimmed ? Container(
                            width: 100,
                            height: 100,
                            decoration: const BoxDecoration(
                              color: Colors.white,
                            ),
                          ) : Container(
                            width: 100,
                            height: 100,
                            decoration: BoxDecoration(
                              color: Colors.white,
                              borderRadius: BorderRadius.circular(100),
                              border: Border.all(
                                color: getCircleColor(exerciseRating),
                                width: 2,
                              ),
                            ),
                            child: Center(child: Text(exerciseRating.toString(), style: AppTextStylesV2.exerciseFeedbackRating(getCircleColor(exerciseRating)))),
                          ),
                          const SizedBox(width: 20),
                          Expanded(
                            child: Column(
                              crossAxisAlignment: CrossAxisAlignment.start,
                              mainAxisSize: MainAxisSize.min,
                              children: [
                                Text(name, style: AppTextStylesV2.requirementLabel),
                                const SizedBox(height: 4),
                                Text(dateStr, style: AppTextStylesV2.requirementDescription),
                              ],
                            ),
                          ),
                            isDimmed ? const Icon(Icons.info_outline) : const Icon(Icons.chevron_right),
                          ],
                        ),
                      ),
                    if (isDimmed)
                      Positioned.fill(
                        child: Container(
                          color: Colors.grey[600]!.withValues(alpha: 0.15),
                          alignment: Alignment.topLeft,
                          child: Container(
                            padding: const EdgeInsets.symmetric(horizontal: 10, vertical: 6),
                            decoration: BoxDecoration(
                              color: Colors.black87,
                              borderRadius: BorderRadius.circular(6),
                            ),
                            child: const _DotCyclerText(
                              baseText: 'ANALYSING',
                              style: TextStyle(color: Colors.white, fontWeight: FontWeight.w700),
                            ),
                          ),
                        ),
                      ),
                    ],
                  ),
                ),
              );
            },
          ),
        ),
      ),
    );
  }
}

class _DotCyclerText extends StatefulWidget {
  const _DotCyclerText({
    required this.baseText,
    this.style,
  });

  final String baseText;
  final TextStyle? style;
  static const Duration _period = Duration(milliseconds: 500);
  static const int _maxDots = 3;

  @override
  State<_DotCyclerText> createState() => _DotCyclerTextState();
}

class _DotCyclerTextState extends State<_DotCyclerText> {
  Timer? _timer;
  int _tick = 0;

  @override
  void initState() {
    super.initState();
    _timer = Timer.periodic(_DotCyclerText._period, (_) {
      if (!mounted) return;
      setState(() => _tick = (_tick + 1) % _DotCyclerText._maxDots);
    });
  }

  @override
  void dispose() {
    _timer?.cancel();
    super.dispose();
  }

  @override
  Widget build(BuildContext context) {
    final dots = '.' * (_tick + 1);
    return Text('${widget.baseText}$dots', style: widget.style);
  }
}
