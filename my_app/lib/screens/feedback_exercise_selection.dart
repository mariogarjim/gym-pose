import 'package:flutter/material.dart';
import 'package:my_app/app_shell.dart';

class FeedbackExerciseSelection extends StatelessWidget {
  const FeedbackExerciseSelection({super.key, this.exerciseName = ""});
  final String exerciseName;

  @override
  Widget build(BuildContext context) {
    WidgetsBinding.instance.addPostFrameCallback((_) {
      AppShell.of(context)?.setTextToShow(exerciseName);
    });
    return const Scaffold(
      body:  Center(child: Text('Feedback Exercise Selection')),
    );
  }
}
