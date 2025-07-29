import 'dart:async';
import 'dart:io';

import 'package:flutter/material.dart';

class SelectExerciseScreen extends StatefulWidget {
  const SelectExerciseScreen({super.key, required this.video});
  final File video;

  @override
  State<SelectExerciseScreen> createState() => _SelectExerciseScreenState();
}

class _SelectExerciseScreenState extends State<SelectExerciseScreen> {
  String? selectedExercise;
  bool isAnalyzing = false;
  double progress = 0;
  int currentStep = 0;
  Timer? timer;

  final exercises = [
    {"name": "Squats", "description": "Lower body strength exercise"},
    {"name": "Pull-ups", "description": "Upper body pulling exercise"},
    {"name": "Bench Press", "description": "Upper body pushing exercise"},
    {"name": "Deadlifts", "description": "Full body compound movement"},
    {"name": "Push-ups", "description": "Bodyweight upper body exercise"},
    {"name": "Bicep Curls", "description": "Isolated arm exercise"},
    {"name": "Tricep Extensions", "description": "Isolated arm exercise"},
    {"name": "Shoulder Press", "description": "Upper body pushing exercise"},
    {"name": "Leg Press", "description": "Lower body pushing exercise"},
    {"name": "Leg Extensions", "description": "Lower body pushing exercise"},
    {"name": "Leg Curls", "description": "Lower body pulling exercise"},
    {"name": "Leg Extensions", "description": "Lower body pushing exercise"},
  ];

  final analysisSteps = [
    "Uploading video...",
    "Detecting movement patterns...",
    "Analyzing form and technique...",
    "Comparing to optimal form...",
    "Generating personalized feedback...",
    "Preparing demonstration videos..."
  ];

  void startAnalysis() {
    if (selectedExercise == null) return;

    setState(() {
      isAnalyzing = true;
      progress = 0;
      currentStep = 0;
    });

    timer = Timer.periodic(const Duration(milliseconds: 100), (timer) {
      setState(() {
        progress += 2;
        currentStep =
            (progress / 100 * analysisSteps.length).floor().clamp(0, analysisSteps.length - 1);

        if (progress >= 100) {
          timer.cancel();
          // Navigate to results or handle after analysis
          Future.delayed(const Duration(milliseconds: 500), () {
            if (mounted) {
              Navigator.pushReplacementNamed(context, '/results');
            }
          });
        }
      });
    });
  }

  @override
  void dispose() {
    timer?.cancel();
    super.dispose();
  }

  @override
  Widget build(BuildContext context) {
    if (isAnalyzing) {
      return Scaffold(
        body: Center(
          child: Card(
            elevation: 8,
            margin: const EdgeInsets.symmetric(horizontal: 24),
            child: Padding(
              padding: const EdgeInsets.all(24),
              child: Column(
                mainAxisSize: MainAxisSize.min,
                children: [
                  const CircularProgressIndicator(),
                  const SizedBox(height: 16),
                  const Text(
                    'Analyzing your form',
                    style: TextStyle(fontSize: 20, fontWeight: FontWeight.bold),
                  ),
                  const SizedBox(height: 8),
                  Text(
                    'Our AI is reviewing your technique',
                    style: TextStyle(color: Colors.grey[600]),
                  ),
                  const SizedBox(height: 24),
                  LinearProgressIndicator(value: progress / 100),
                  const SizedBox(height: 16),
                  Text(
                    analysisSteps[currentStep],
                    style: const TextStyle(fontSize: 14),
                  ),
                  const SizedBox(height: 4),
                  Text('${progress.toStringAsFixed(0)}% complete',
                      style: const TextStyle(fontWeight: FontWeight.w600)),
                ],
              ),
            ),
          ),
        ),
      );
    }

    return Scaffold(
      appBar: AppBar(
        title: const Text("Select Exercise"),
        leading: IconButton(
          icon: const Icon(Icons.arrow_back),
          onPressed: () => Navigator.pop(context),
        ),
      ),
      body: Padding(
        padding: const EdgeInsets.all(16),
        child: Column(
          children: [
            const Text(
              "Choose the exercise you performed in your video",
              textAlign: TextAlign.center,
              style: TextStyle(fontSize: 18, fontWeight: FontWeight.w600),
            ),
            const SizedBox(height: 16),
            Expanded(
              child: ListView.builder(
                itemCount: exercises.length,
                itemBuilder: (context, index) {
                  final exercise = exercises[index];
                  final isSelected = selectedExercise == exercise["name"];

                  return GestureDetector(
                    onTap: () {
                      setState(() => selectedExercise = exercise["name"]);
                    },
                    child: Card(
                      shape: RoundedRectangleBorder(
                        side: BorderSide(
                          color: isSelected ? Theme.of(context).colorScheme.primary : Colors.grey[300]!,
                          width: 2,
                        ),
                        borderRadius: BorderRadius.circular(8),
                      ),
                      color: isSelected ? Colors.blue[50] : null,
                      margin: const EdgeInsets.symmetric(vertical: 8),
                      child: ListTile(
                        title: Text(
                          exercise["name"]!,
                          style: const TextStyle(fontWeight: FontWeight.bold),
                        ),
                        subtitle: Text(exercise["description"]!),
                        trailing: isSelected
                            ? Icon(Icons.check_circle, color: Theme.of(context).colorScheme.primary)
                            : null,
                      ),
                    ),
                  );
                },
              ),
            ),
            SizedBox(
              width: double.infinity,
              child: ElevatedButton.icon(
                onPressed: selectedExercise != null ? startAnalysis : null,
                icon: const Icon(Icons.account_tree_sharp, size: 20),
                label: const Text(
                  "Analyze My Form",
                  style: TextStyle(
                    fontSize: 16,
                    fontWeight: FontWeight.w600,
                    letterSpacing: 0.5,
                  ),
                ),
                style: ElevatedButton.styleFrom(
                  backgroundColor: selectedExercise != null ? Theme.of(context).colorScheme.primary : Colors.grey[400],
                  foregroundColor: Colors.white,
                  padding: const EdgeInsets.symmetric(horizontal: 36, vertical: 18),
                  shape: RoundedRectangleBorder(
                    borderRadius: BorderRadius.circular(30),
                  ),
                  elevation: 6,
                  shadowColor: Colors.black.withValues(alpha: 0.2),
                ),
              ),
            ),
            if (selectedExercise == null)
              const Padding(
                padding: EdgeInsets.only(top: 12),
                child: Text(
                  "Please select an exercise to continue",
                  style: TextStyle(color: Colors.grey),
                ),
              ),
          ],
        ),
      ),
    );
  }
}
