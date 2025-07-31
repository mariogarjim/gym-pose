import 'package:flutter/material.dart';

class FeedbackScreen extends StatelessWidget {
  FeedbackScreen({super.key, required this.overallScore});
  
  final int overallScore;
  final String selectedExercise = "Squat";
    
  final List<String> strengths = [
    "Good depth in the squat movement",
    "Knees properly aligned with toes",
    "Maintained neutral spine throughout"
  ];

  final List<Map<String, String>> improvements = [
    {
      "issue": "Weight distribution slightly forward",
      "recommendation":
          "Focus on keeping weight centered over mid-foot. Imagine pushing the floor away with your heels.",
      "severity": "medium"
    },
    {
      "issue": "Slight knee cave on ascent",
      "recommendation":
          "Engage glutes more actively and think about pushing knees out during the upward movement.",
      "severity": "high"
    },
  ];

  final List<Map<String, String>> demonstrationVideos = [
    {
      "title": "Proper Weight Distribution",
      "description": "Learn how to maintain balance throughout the movement",
      "thumbnail":
          "https://images.unsplash.com/photo-1571019613454-1cb2f99b2d8b?w=400&h=300&fit=crop"
    },
    {
      "title": "Glute Activation Techniques",
      "description": "Exercises to improve glute engagement during squats",
      "thumbnail":
          "https://images.unsplash.com/photo-1574680096145-d05b474e2155?w=400&h=300&fit=crop"
    }
  ];

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(
        title: const Text("FormCheck"),
        actions: [
          IconButton(
            icon: const Icon(Icons.refresh),
            onPressed: () {
              // retry logic
            },
          )
        ],
      ),
      body: SingleChildScrollView(
        padding: const EdgeInsets.all(16),
        child: Column(
          children: [
            // Score
            Card(
              elevation: 4,
              child: Padding(
                padding: const EdgeInsets.all(24),
                child: Column(
                  children: [
                    const Text(
                      "Form Score",
                      style: TextStyle(fontSize: 18),
                    ),
                    Text(
                      "$overallScore%",
                      style: TextStyle(
                        fontSize: 48,
                        fontWeight: FontWeight.bold,
                        color: Theme.of(context).colorScheme.primary,
                      ),
                    ),
                  ],
                ),
              ),
            ),
            const SizedBox(height: 24),

            // Strengths
            Align(
              alignment: Alignment.centerLeft,
              child: Text(
                "What you did well:",
                style: Theme.of(context).textTheme.titleLarge,
              ),
            ),
            ...strengths.map((s) => ListTile(
                  leading: const Icon(Icons.check_circle, color: Colors.green),
                  title: Text(s),
                )),

            const SizedBox(height: 24),

            // Improvements
            Align(
              alignment: Alignment.centerLeft,
              child: Text(
                "Areas for improvement:",
                style: Theme.of(context).textTheme.titleLarge,
              ),
            ),
            ...improvements.map(
              (i) => Card(
                color: Colors.orange.withOpacity(0.1),
                margin: const EdgeInsets.symmetric(vertical: 8),
                child: ListTile(
                  title: Text(i["issue"]!),
                  subtitle: Text(i["recommendation"]!),
                  trailing: Chip(
                    label: Text(
                      i["severity"] == "high" ? "Priority" : "Minor",
                      style: const TextStyle(fontSize: 12),
                    ),
                    backgroundColor: i["severity"] == "high"
                        ? Colors.red[300]
                        : Colors.grey[300],
                  ),
                ),
              ),
            ),

            const SizedBox(height: 24),

            // Videos
            Align(
              alignment: Alignment.centerLeft,
              child: Text(
                "Recommended Videos:",
                style: Theme.of(context).textTheme.titleLarge,
              ),
            ),
            ...demonstrationVideos.map(
              (v) => Card(
                margin: const EdgeInsets.symmetric(vertical: 10),
                child: ListTile(
                  leading: Image.network(
                    v["thumbnail"]!,
                    width: 80,
                    height: 60,
                    fit: BoxFit.cover,
                  ),
                  title: Text(v["title"]!),
                  subtitle: Text(v["description"]!),
                  onTap: () {
                    // You could push to a video player page
                  },
                ),
              ),
            ),

            const SizedBox(height: 24),

            // Action Buttons
            Row(
              mainAxisAlignment: MainAxisAlignment.spaceEvenly,
              children: [
                ElevatedButton.icon(
                  icon: const Icon(Icons.play_circle),
                  label: const Text("Analyze Another Video"),
                  onPressed: () {
                    // Navigate back
                    Navigator.pop(context);
                  },
                ),
                OutlinedButton.icon(
                  icon: const Icon(Icons.save),
                  label: const Text("Save Results"),
                  onPressed: () {
                    // Save logic
                  },
                ),
              ],
            )
          ],
        ),
      ),
    );
  }
}
