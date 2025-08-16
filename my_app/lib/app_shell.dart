import 'package:flutter/material.dart';
import 'package:flutter/services.dart';
import 'screens/home_screen.dart';
import 'screens/configure_analysis_screen.dart';
import 'screens/feedback_screen.dart';
import 'screens/full_screen_video_screen.dart';
import 'widgets/button_bar.dart';

class AppShell extends StatefulWidget {
  const AppShell({super.key});

  @override
  State<AppShell> createState() => _AppShellState();
}

class _AppShellState extends State<AppShell> {
  int _currentIndex = 0;

  @override
  Widget build(BuildContext context) {
    final pages = <Widget>[
      const HomeScreen(),
      const ConfigureAnalysisScreen(),
    ];

    return Scaffold(
      extendBody: true,
      body: SafeArea(
        child: AnimatedSwitcher(
          duration: const Duration(milliseconds: 250),
          switchInCurve: Curves.easeOutCubic,
          switchOutCurve: Curves.easeInCubic,
          child: pages[_currentIndex],
        ),
      ),
      floatingActionButtonLocation: FloatingActionButtonLocation.centerDocked,
      floatingActionButton: FloatingActionButton(
        tooltip: 'Add metric',
        elevation: 4,
        child: const Icon(Icons.add, size: 28),
        onPressed: () async {
          HapticFeedback.selectionClick();
          final result =
              await Navigator.of(context).pushNamed('/configure-analysis');
          if (!mounted) return;
          if (result == 'created') {
            final cs = Theme.of(context).colorScheme;
            ScaffoldMessenger.of(context).showSnackBar(
              SnackBar(
                content: const Text('Metric created'),
                backgroundColor: cs.primary,
                behavior: SnackBarBehavior.floating,
              ),
            );
          }
        },
      ),
      bottomNavigationBar: BottomBar(
        currentIndex: _currentIndex,
        onHomeTap: () {
          HapticFeedback.selectionClick();
          setState(() => _currentIndex = 0);
        },
      ),
    );
  }
}
