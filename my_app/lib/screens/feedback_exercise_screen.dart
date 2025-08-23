import 'package:flutter/material.dart';
import 'package:my_app/widgets/video_player.dart'; // AdaptiveAspectVideoPlayer
import 'package:my_app/theme/text_styles.dart';

class FeedbackExerciseScreen extends StatelessWidget {
  const FeedbackExerciseScreen({super.key, required this.exerciseName});

  final String exerciseName;

  @override
  Widget build(BuildContext context) {
    return DefaultTabController(
      length: 3,
      child: Builder(
        builder: (BuildContext context) {
           final TabController controller = DefaultTabController.of(context);

          return AnimatedBuilder(
            // Si TabController.animation es null, usamos el propio controller como Listenable
            animation: controller.animation ?? controller,
            builder: (BuildContext context, _) {
              final int idx = controller.index;
              final Color edgeColor = _ledColorForTab(idx);

              return Stack(
                children: <Widget>[
                  // ── LED laterales (detrás del contenido) ───────────────────
                  const Positioned.fill(
                    child: IgnorePointer(
                      child: Row(
                        children: <Widget>[
                          // placeholder para mantener estructura con Expanded central
                        ],
                      ),
                    ),
                  ),
                  Positioned.fill(
                    child: IgnorePointer(
                      child: Row(
                        children: <Widget>[
                          _EdgeStrip(color: edgeColor),
                          const Expanded(child: SizedBox.shrink()),
                          _EdgeStrip(color: edgeColor),
                        ],
                      ),
                    ),
                  ),

                  // ── Contenido ──────────────────────────────────────────────
                  const Column(
                    children: <Widget>[
                      TabBar(
                        labelColor: Colors.black,
                        unselectedLabelColor: Colors.grey,
                        indicatorColor: Colors.black,
                        dividerColor: Colors.transparent,
                        tabs: <Widget>[
                          Tab(text: 'FIXES'),
                          Tab(text: 'WARNING'),
                          Tab(text: 'HARMFUL'),
                        ],
                      ),
                      SizedBox(height: 16),
                      Expanded(
                        child: TabBarView(
                          children: <Widget>[
                            _FeedbackList(
                              items: <_FeedbackItem>[
                                _FeedbackItem(
                                  title: 'BACK POSTURE',
                                  description:
                                      'The position of you back is not correct. Your back should be straight. Check the video to see the problem.',
                                ),
                                _FeedbackItem(
                                  title: 'DEPTH',
                                  description: 'Depth is consistent, great job!',
                                ),
                              ],
                            ),
                            _FeedbackList(
                              items: <_FeedbackItem>[
                                _FeedbackItem(
                                  title: 'KNEE POSITION',
                                  description:
                                      'Your knees are going too far forward.',
                                ),
                                _FeedbackItem(
                                  title: 'SPINE ALIGNMENT',
                                  description:
                                      'Your back is rounding slightly.',
                                ),
                              ],
                            ),
                            _FeedbackList(
                              items: <_FeedbackItem>[
                                _FeedbackItem(
                                  title: 'DEPTH ISSUE',
                                  description:
                                      'Your squat depth is harmful, try reducing the load.',
                                ),
                              ],
                            ),
                          ],
                        ),
                      ),
                    ],
                  ),
                ],
              );
            },
          );
        },
      ),
    );
  }
}

class _EdgeStrip extends StatelessWidget {
  const _EdgeStrip({
    required this.color,
  });


  final double width = 4.0;
  final Color color;

  @override
  Widget build(BuildContext context) {
    return Container(
      width: width,
      decoration: BoxDecoration(
        // Gradiente vertical tipo “neón/LED”
        gradient: LinearGradient(
          begin: Alignment.topCenter,
          end: Alignment.bottomCenter,
          colors: <Color>[
            color.withAlpha(0),
            color.withAlpha(230),
            color.withAlpha(0),
          ],
          stops: const <double>[0.0, 0.5, 1.0],
        ),
        boxShadow: <BoxShadow>[
          // halo suave alrededor de la tira
          BoxShadow(
            color: color.withAlpha(89),
            blurRadius: 10,
            spreadRadius: 0.5,
          ),
        ],
      ),
    );
  }
}

Color _ledColorForTab(int index) {
  switch (index) {
    case 0: // FIXES
      return const Color(0xFF22C55E); // green
    case 1: // WARNING
      return const Color(0xFFF59E0B); // amber/yellow
    case 2: // HARMFUL
      return const Color(0xFFEF4444); // red
    default:
      return Colors.grey;
  }
}

class _FeedbackList extends StatelessWidget {
  const _FeedbackList({required this.items});

  final List<_FeedbackItem> items;

  @override
  Widget build(BuildContext context) {
    return ListView.separated(
      padding: const EdgeInsets.symmetric(horizontal: 16, vertical: 12),
      itemCount: items.length,
      separatorBuilder: (_, __) => const SizedBox(height: 24),
      itemBuilder: (BuildContext context, int index) {
        final _FeedbackItem item = items[index];

        return Column(
          crossAxisAlignment: CrossAxisAlignment.center,
          children: <Widget>[
            // Player adaptable (centrado, 5:4 o lo que uses en tu widget)
            Text(
              item.title,
              style: AppTextStylesV2.exerciseNames,
              textAlign: TextAlign.center,
            ),
            const SizedBox(height: 12),
            const AdaptiveAspectVideoPlayer(
              videoPath: 'assets/videos/vertical.mp4',
              severity: 'harmful',
            ),
            const SizedBox(height: 17),
            Text(
              item.description,
              style: AppTextStylesV2.textBody,
              textAlign: TextAlign.justify,
            ),
            const SizedBox(height: 12),
          ],
        );
      },
    );
  }
}

class _FeedbackItem {
  const _FeedbackItem({required this.title, required this.description});
  final String title;
  final String description;
}
