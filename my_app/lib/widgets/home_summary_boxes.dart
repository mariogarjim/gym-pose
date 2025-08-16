import 'package:flutter/material.dart';

class HomeFeedbackBox extends StatelessWidget {
  const HomeFeedbackBox({super.key});

  @override
  Widget build(BuildContext context) {
    final cs = Theme.of(context).colorScheme;
    
    return Column(
      children: [
        // Quick Stats Grid
        GridView.count(
          crossAxisCount: 1,
          shrinkWrap: true,
          physics: const NeverScrollableScrollPhysics(),
          childAspectRatio: 3.5,
          mainAxisSpacing: 16,
          children: [
            // Average Score Card
            _StatCard(
              icon: Icons.trending_up,
              iconColor: cs.primary,
              backgroundColor: cs.primary.withAlpha(6),
              title: 'Average Score',
              value: '85%',
            ),
            // Exercises Analyzed Card
            _StatCard(
              icon: Icons.check_circle_outline,
              iconColor: Colors.green.shade600,
              backgroundColor: Colors.green.shade100,
              title: 'Exercises Analyzed',
              value: '12',
            ),
            // Improvements Made Card
            _StatCard(
              icon: Icons.tune,
              iconColor: Colors.blue.shade600,
              backgroundColor: Colors.blue.shade100,
              title: 'Suggested improvements',
              value: '8',
            ),
          ],
        ),
      ],
    );
  }
}

class _StatCard extends StatelessWidget {
  final IconData icon;
  final Color iconColor;
  final Color backgroundColor;
  final String title;
  final String value;

  const _StatCard({
    required this.icon,
    required this.iconColor,
    required this.backgroundColor,
    required this.title,
    required this.value,
  });

  @override
  Widget build(BuildContext context) {
    final cs = Theme.of(context).colorScheme;
    
    return Card(
      elevation: 2,
      color: Colors.white,
      surfaceTintColor: cs.primary.withAlpha(6),
      shape: RoundedRectangleBorder(
        borderRadius: BorderRadius.circular(16),
        side: BorderSide(color: cs.outlineVariant),
      ),
      child: Padding(
        padding: const EdgeInsets.all(20),
        child: Row(
          children: [
            // Icon Container
            Container(
              padding: const EdgeInsets.all(12),
              decoration: BoxDecoration(
                color: backgroundColor,
                shape: BoxShape.circle,
              ),
              child: Icon(
                icon,
                size: 24,
                color: iconColor,
              ),
            ),
            const SizedBox(width: 16),
            // Text Content
            Expanded(
              child: Column(
                crossAxisAlignment: CrossAxisAlignment.start,
                mainAxisAlignment: MainAxisAlignment.center,
                children: [
                  Text(
                    title,
                    style: Theme.of(context).textTheme.bodySmall?.copyWith(
                      color: cs.onSurfaceVariant,
                    ),
                  ),
                  const SizedBox(height: 4),
                  Text(
                    value,
                    style: Theme.of(context).textTheme.headlineSmall?.copyWith(
                      fontWeight: FontWeight.bold,
                      color: cs.onSurface,
                    ),
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
