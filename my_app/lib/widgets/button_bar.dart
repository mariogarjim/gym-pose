import 'package:flutter/material.dart';

class BottomBar extends StatelessWidget {
  final int currentIndex;
  final VoidCallback onHomeTap;

  const BottomBar({
    super.key,
    required this.currentIndex,
    required this.onHomeTap,
  });

  @override
  Widget build(BuildContext context) {
    final cs = Theme.of(context).colorScheme;

    return Padding(
      padding: const EdgeInsets.fromLTRB(12, 0, 12, 12),
      child: ClipRRect(
        borderRadius: const BorderRadius.all(Radius.circular(20)),
        child: BottomAppBar(
          height: 72,
          elevation: 2,
          color: cs.surface,
          surfaceTintColor: cs.primary.withOpacity(0.08),
          shape: const CircularNotchedRectangle(),
          notchMargin: 8,
          child: Row(
            children: [
              const SizedBox(width: 8),
              _NavAction(
                label: 'Home',
                icon: Icons.home_rounded,
                selected: currentIndex == 0,
                onTap: onHomeTap,
              ),
              const Spacer(),
              // Right-side spacer for visual balance with the center FAB
              const SizedBox(width: 56),
              const SizedBox(width: 8),
            ],
          ),
        ),
      ),
    );
  }
}

class _NavAction extends StatelessWidget {
  final String label;
  final IconData icon;
  final bool selected;
  final VoidCallback onTap;

  const _NavAction({
    required this.label,
    required this.icon,
    required this.selected,
    required this.onTap,
  });

  @override
  Widget build(BuildContext context) {
    final cs = Theme.of(context).colorScheme;
    final color = selected ? cs.primary : cs.onSurfaceVariant;

    return InkWell(
      onTap: onTap,
      borderRadius: BorderRadius.circular(14),
      child: Padding(
        padding: const EdgeInsets.symmetric(horizontal: 14, vertical: 10),
        child: Column(
          mainAxisAlignment: MainAxisAlignment.center,
          children: [
            Icon(icon, size: 26, color: color),
            const SizedBox(height: 6),
            Text(
              label,
              style: TextStyle(
                fontSize: 12,
                fontWeight: FontWeight.w600,
                color: color,
                letterSpacing: 0.2,
              ),
            ),
          ],
        ),
      ),
    );
  }
}
