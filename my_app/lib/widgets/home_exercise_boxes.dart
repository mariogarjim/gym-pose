import 'package:flutter/material.dart';
import 'package:my_app/models/feedback.dart';


// Utility: Get grade color based on grade %
Color getGradeColor(int grade) {
  if (grade >= 80) return Colors.green;
  if (grade >= 50) return Colors.orange;
  return Colors.red;
}

String getGradeLabel(int grade) {
  if (grade >= 80) return "Excellent";
  if (grade >= 50) return "Good";
  return "Needs Work";
}

// Widget
class HomeExerciseBoxes extends StatelessWidget {
  final List<ExerciseResult> recentExercises;

  const HomeExerciseBoxes({
    super.key,
    required this.recentExercises,
  });

  @override
  Widget build(BuildContext context) {
    return Column(
      crossAxisAlignment: CrossAxisAlignment.start,
      children: [
        const SizedBox(height: 16),
        ...recentExercises.asMap().entries.map((entry) {
          final index = entry.key;
          final exercise = entry.value;

          return AnimatedContainer(
            duration: Duration(milliseconds: 300 + (index * 100)),
            curve: Curves.easeOut,
            margin: const EdgeInsets.only(bottom: 16),
            child: Card(
              shape: RoundedRectangleBorder(
                borderRadius: BorderRadius.circular(16),
              ),
              elevation: 3,
              child: Padding(
                padding: const EdgeInsets.all(16.0),
                child: Column(
                  crossAxisAlignment: CrossAxisAlignment.start,
                  children: [
                    // Header Row
                    Row(
                      mainAxisAlignment: MainAxisAlignment.spaceBetween,
                      children: [
                        // Title + Date
                        Column(
                          crossAxisAlignment: CrossAxisAlignment.start,
                          children: [
                            Text(
                              exercise.name,
                              style: const TextStyle(
                                fontSize: 18,
                                fontWeight: FontWeight.w600,
                              ),
                            ),
                            Text(
                              "${exercise.date.month}/${exercise.date.day}/${exercise.date.year}",
                              style: TextStyle(
                                fontSize: 14,
                                color: Colors.grey[600],
                              ),
                            ),
                          ],
                        ),
                        // Grade + Progress
                        Column(
                          crossAxisAlignment: CrossAxisAlignment.end,
                          children: [
                            Container(
                              padding: const EdgeInsets.symmetric(
                                  horizontal: 12, vertical: 6),
                              decoration: BoxDecoration(
                                border: Border.all(
                                    color: getGradeColor(exercise.grade)),
                                borderRadius: BorderRadius.circular(20),
                              ),
                              child: Text(
                                "${exercise.grade}% - ${getGradeLabel(exercise.grade)}",
                                style: TextStyle(
                                  fontSize: 13,
                                  fontWeight: FontWeight.w500,
                                  color: getGradeColor(exercise.grade),
                                ),
                              ),
                            ),
                            const SizedBox(height: 6),
                            SizedBox(
                              width: 80,
                              child: LinearProgressIndicator(
                                value: exercise.grade / 100,
                                backgroundColor: Colors.grey[200],
                                color: getGradeColor(exercise.grade),
                              ),
                            ),
                          ],
                        ),
                      ],
                    ),
                    const SizedBox(height: 16),

                    // Good Points + Improvements
                    Column(
                      crossAxisAlignment: CrossAxisAlignment.start,
                      children: [
                        // Good Points
                        Column(
                          crossAxisAlignment: CrossAxisAlignment.start,
                          children: [
                            const Row(
                              children: [
                                Icon(Icons.check_circle_outline,
                                    color: Colors.green, size: 18),
                                SizedBox(width: 6),
                                Text(
                                  "What You Did Well",
                                  style: TextStyle(
                                    fontWeight: FontWeight.w600,
                                  ),
                                ),
                              ],
                            ),
                            const SizedBox(height: 8),
                            ...exercise.goodPoints.map(
                              (point) => Padding(
                                padding:
                                    const EdgeInsets.symmetric(vertical: 2.0),
                                child: Row(
                                  children: [
                                    const Text("✓ ",
                                        style: TextStyle(
                                            color: Colors.green,
                                            fontSize: 14)),
                                    Expanded(
                                      child: Text(
                                        point,
                                        style: TextStyle(
                                            color: Colors.grey[700],
                                            fontSize: 13),
                                      ),
                                    ),
                                  ],
                                ),
                              ),
                            ),
                          ],
                        ),
                        const SizedBox(height: 16),
                        // Improvements
                        Column(
                          crossAxisAlignment: CrossAxisAlignment.start,
                          children: [
                            const Row(
                              children: [
                                Icon(Icons.warning_amber_rounded,
                                    color: Colors.amber, size: 18),
                                SizedBox(width: 6),
                                Text(
                                  "Areas for Improvement",
                                  style: TextStyle(
                                    fontWeight: FontWeight.w600,
                                  ),
                                ),
                              ],
                            ),
                            const SizedBox(height: 8),
                            ...exercise.improvements.map(
                              (improvement) => Padding(
                                padding:
                                    const EdgeInsets.symmetric(vertical: 2.0),
                                child: Row(
                                  children: [
                                    const Text("⚡ ",
                                        style: TextStyle(
                                            color: Colors.amber,
                                            fontSize: 14)),
                                    Expanded(
                                      child: Text(
                                        improvement,
                                        style: TextStyle(
                                            color: Colors.grey[700],
                                            fontSize: 13),
                                      ),
                                    ),
                                  ],
                                ),
                              ),
                            ),
                          ],
                        ),
                      ],
                    ),
                    const SizedBox(height: 16),
                    const Divider(),

                    // Demo Video Section
                    Container(
                      margin: const EdgeInsets.only(top: 12),
                      padding: const EdgeInsets.all(12),
                      decoration: BoxDecoration(
                        color: Colors.grey.withOpacity(0.1),
                        borderRadius: BorderRadius.circular(12),
                      ),
                      child: const Row(
                        mainAxisAlignment: MainAxisAlignment.spaceBetween,
                        children: [
                          Row(
                            children: [
                              Icon(Icons.play_arrow,
                                  color: Colors.blue, size: 20),
                              SizedBox(width: 8),
                              Column(
                                crossAxisAlignment: CrossAxisAlignment.start,
                                children: [
                                  Text(
                                    "Watch Improvement Demo",
                                    style:
                                        TextStyle(fontWeight: FontWeight.w600),
                                  ),
                                  Text(
                                    "Personalized technique video",
                                    style: TextStyle(
                                      fontSize: 12,
                                      color: Colors.grey,
                                    ),
                                  ),
                                ],
                              ),
                            ],
                          ),
                        ],
                      ),
                    ),
                  ],
                ),
              ),
            ),
          );
        }),
      ],
    );
  }
}
