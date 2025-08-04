import 'dart:async';
import 'dart:developer';
import 'package:flutter/material.dart';
import 'package:my_app/core/api/video_upload_service.dart';
import 'package:my_app/screens/feedback_screen.dart';
import 'package:image_picker/image_picker.dart';
import 'package:permission_handler/permission_handler.dart';

final exerciseType = {
  "Squats": "squat",
  "Pull-ups": "pull_up",
  "Bench Press": "bench_press",
};

final requiredVideos = {
  "Squats": [
    {"id": "front", "label": "Front View", "description": "Film yourself facing the camera"},
    {"id": "side", "label": "Side View", "description": "Film from your left or right side"},
  ],
  "Pull-ups": [
    {"id": "front", "label": "Front View", "description": "Film yourself facing the camera"},
    {"id": "side", "label": "Side View", "description": "Film from your left or right side"},
  ],
  "Bench Press": [
    {"id": "side", "label": "Side View", "description": "Film from the side"},
    {"id": "foot", "label": "Foot View", "description": "Film from the foot end"},
  ],
};

class ConfigureAnalysisScreen extends StatefulWidget {
  const ConfigureAnalysisScreen({super.key});

  @override
  State<ConfigureAnalysisScreen> createState() => _ConfigureAnalysisScreenState();
}

class _ConfigureAnalysisScreenState extends State<ConfigureAnalysisScreen> {
  String? selectedExercise;

  Map<String, XFile?> uploadedVideos = {};
  bool showUploadScreen = false;

  bool isCorrectNumberOfVideos = false;

  bool isAnalyzing = false;
  double progress = 0;
  int currentStep = 0;
  Timer? timer;

  final exercises = [
    {"name": "Squats", "description": "Lower body strength exercise"},
    {"name": "Pull-ups", "description": "Upper body pulling exercise"},
    {"name": "Bench Press", "description": "Upper body pushing exercise"},
  ];

  final analysisSteps = [
    "Uploading video...",
    "Detecting movement patterns...",
    "Analyzing form and technique...",
    "Comparing to optimal form...",
    "Generating personalized feedback...",
    "Preparing demonstration videos..."
  ];

  //handle permission request on init
  Future<void> _handlePermissionRequest() async {
    final videoPermissions = await Permission.videos.isGranted;
    final imagePermissions = await Permission.photos.isGranted;
    if (!videoPermissions || !imagePermissions) {
      await Permission.videos.request();
      await Permission.photos.request();
    }
  }

  @override
  void initState() {
    super.initState();
    _handlePermissionRequest();
  }

  void handleSelectExercise(String name) {
    setState(() {
      selectedExercise = name;
      uploadedVideos = {
        for (var req in requiredVideos[name]!) req['id']!: null
      };
      showUploadScreen = true;
    });
  }

  void startAnalysis(List<String> videoPaths) async {

    log("Selected exercise: $selectedExercise");

    setState(() {
      showUploadScreen = false;
      isAnalyzing = true;
      progress = 0;
      currentStep = 0;
    });

    // Start simulated progress timer
    timer = Timer.periodic(const Duration(milliseconds: 500), (timer) {
      setState(() {
        if (progress < 98) {
          progress += 2;
          currentStep = (progress / 100 * analysisSteps.length)
                .floor()
                .clamp(0, analysisSteps.length - 1);
          }
      });
    });

    final firstVideoPath = videoPaths.first;

    final videoResponse = await VideoUploadService.uploadAndProcessVideo(
      videoPath: firstVideoPath,
      exerciseType: exerciseType[selectedExercise]!,
    );
    log("Video uploaded: ${videoResponse.zipBytes.length} bytes");
    log("Feedback: ${videoResponse.feedback}");
    log("Clips generated: ${videoResponse.clipsGenerated}");

    // ✅ Upload complete — stop the timer and navigate
    timer?.cancel();

    if (mounted) {
      Navigator.pushReplacement(context, MaterialPageRoute(builder: (context) => FeedbackScreen(videoResponse: videoResponse)));
    }
  }

  @override
  void dispose() {
    timer?.cancel();
    super.dispose();
  }

  @override
  Widget build(BuildContext context) {
    if (showUploadScreen) {
      return Scaffold(
        appBar: AppBar(
          leading: IconButton(
            icon: const Icon(Icons.chevron_left),
            onPressed: () => setState(() => showUploadScreen = false),
          ),
          title: Text("Upload your ${selectedExercise!.toLowerCase()} videos")
        ),
        body: _buildUploadScreen(
          selectedExercise!,
        ),
      );
  }

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
                Text(
                  '${progress.toStringAsFixed(0)}% complete',
                  style: const TextStyle(fontWeight: FontWeight.w600),
                ),
              ],
            ),
          ),
        ),
      ),
    );
  }

  // Default: Exercise Selection
  return Scaffold(
    appBar: AppBar(
      title: const Text("Select Exercise"),
      leading: Icon(Icons.home, size: 30, color: Theme.of(context).colorScheme.primary),
    ),
    body: Padding(
      padding: const EdgeInsets.all(16),
      child: Column(
        children: [
          const Text(
            "Choose the exercise you want to analyze",
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
                  onTap: () => setState(() {
                    selectedExercise = exercise["name"];
                  }),
                  child: Card(
                    shape: RoundedRectangleBorder(
                      side: BorderSide(
                        color: isSelected
                            ? Theme.of(context).colorScheme.primary
                            : Colors.grey[300]!,
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
                          ? Icon(Icons.check_circle,
                              color: Theme.of(context).colorScheme.primary)
                          : null,
                    ),
                  ),
                );
              },
            ),
          ),
          SizedBox(
            width: double.infinity,
            height: 60,
            child: ElevatedButton.icon(
              onPressed: selectedExercise != null ? 
              () => setState(() => showUploadScreen = true) : 
              () => ScaffoldMessenger.of(context).showSnackBar(
                const SnackBar(
                  content: Text("Please select an exercise to continue"),
                  backgroundColor: Colors.red,
                  duration: Duration(seconds: 1),
                ),
              ),
              icon: Icon(Icons.account_tree_sharp, size: 20, color: selectedExercise != null ? Colors.white : Colors.black),
              label: Text(
                "Continue to analyze",
                style: TextStyle(color: selectedExercise != null ? Colors.white : Colors.black),
              ),
              style: ElevatedButton.styleFrom(
                  padding: const EdgeInsets.symmetric(horizontal: 36, vertical: 18),
                  shape: RoundedRectangleBorder(
                    borderRadius: BorderRadius.circular(30),
                  ),
                  backgroundColor: selectedExercise != null ? Theme.of(context).colorScheme.primary : Colors.grey[300],
              ),
            ),
          ),
        ],
      ),
    ),
  );
}


  Widget _buildUploadScreen(
    String selectedExercise,
  ) {

  final requirements = requiredVideos[selectedExercise]!;

  return Padding(
    padding: const EdgeInsets.all(16),
    child: Column(
      crossAxisAlignment: CrossAxisAlignment.stretch,
      children: [
        const Text(
            "We need specific camera angles to analyze your form accurately.",
            textAlign: TextAlign.center,
            style: TextStyle(fontSize: 18, fontWeight: FontWeight.w600),
        ),
        const SizedBox(height: 24),

        // Video Upload Cards
        Expanded(
          child: ListView.builder(
            itemCount: requirements.length,
            itemBuilder: (context, index) {
              final req = requirements[index];
              final uploadedFile = uploadedVideos[req['id']];

              return Card(
                elevation: 2,
                shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(12)),
                margin: const EdgeInsets.symmetric(vertical: 8),
                child: Padding(
                  padding: const EdgeInsets.all(16),
                  child: Column(
                    crossAxisAlignment: CrossAxisAlignment.start,
                    children: [
                      Row(
                        children: [
                          const Icon(Icons.camera_alt_outlined, color: Colors.blue),
                          const SizedBox(width: 8),
                          Expanded(
                            child: Column(
                              crossAxisAlignment: CrossAxisAlignment.start,
                              children: [
                                Text(req['label']!, style: const TextStyle(fontWeight: FontWeight.bold)),
                                Text(req['description']!, style: const TextStyle(color: Colors.grey)),
                              ],
                            ),
                          ),
                        ],
                      ),
                      const SizedBox(height: 16),
                      uploadedFile != null
                          ? Container(
                              padding: const EdgeInsets.all(12),
                              decoration: BoxDecoration(
                                color: Colors.green.withValues(alpha: 0.1),
                                border: Border.all(color: Colors.green),
                                borderRadius: BorderRadius.circular(8),
                              ),
                              child: Row(
                                mainAxisAlignment: MainAxisAlignment.spaceBetween,
                                children: [
                                  Row(
                                    children: [
                                      const Icon(Icons.check_circle, color: Colors.green),
                                      const SizedBox(width: 8),
                                      Column(
                                        crossAxisAlignment: CrossAxisAlignment.start,
                                        children: [
                                          Text(
                                            uploadedFile.name.length > 20 ? "${uploadedFile.name.substring(0, 20)}..." : uploadedFile.name,
                                            style: const TextStyle(
                                              color: Colors.green,
                                              fontWeight: FontWeight.bold,
                                            ),
                                          ),
                                          const Text(
                                            "Video uploaded successfully",
                                            style: TextStyle(color: Colors.green),
                                          ),
                                        ],
                                      ),
                                    ],
                                  ),
                                  IconButton(
                                    icon: const Icon(Icons.close, color: Colors.red),
                                    onPressed: () => setState(() => uploadedVideos[req['id']!] = null),
                                  ),
                                ],
                              ),
                            )
                          : GestureDetector(
                              onTap: () async {
                                final picker = ImagePicker();
                                final picked = await picker.pickVideo(source: ImageSource.gallery);
                                if (picked != null) {
                                  setState(() => uploadedVideos[req['id']!] = picked);
                                  if (uploadedVideos.length == requiredVideos[selectedExercise]!.length) {
                                    setState(() => isCorrectNumberOfVideos = true);
                                  }
                                }
                              },
                              child: Container(
                                width: double.infinity,
                                padding: const EdgeInsets.symmetric(vertical: 24),
                                decoration: BoxDecoration(
                                  border: Border.all(color: Colors.grey.shade400),
                                  borderRadius: BorderRadius.circular(12),
                                ),
                                child: const Column(
                                  mainAxisAlignment: MainAxisAlignment.center,
                                  children: [
                                    Icon(Icons.videocam, size: 36, color: Colors.grey),
                                    SizedBox(height: 8),
                                    Text(
                                      "Click to upload video",
                                      style: TextStyle(fontWeight: FontWeight.bold),
                                    ),
                                    SizedBox(height: 4),
                                    Text(
                                      "MP4, MOV, or AVI files accepted",
                                      style: TextStyle(color: Colors.grey),
                                    ),
                                  ],
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

        const SizedBox(height: 16),
        ElevatedButton.icon(
          onPressed: isCorrectNumberOfVideos ? () => startAnalysis(uploadedVideos.values.map((v) => v!.path).toList()) : null,
          icon: Icon(Icons.check, size: 20, color: isCorrectNumberOfVideos ? Colors.white : Colors.grey),
          label: Text("Analyze My Form", style: TextStyle(color: isCorrectNumberOfVideos ? Colors.white : Colors.grey)),
           style: ElevatedButton.styleFrom(
                padding: const EdgeInsets.symmetric(horizontal: 36, vertical: 18),
                shape: RoundedRectangleBorder(
                  borderRadius: BorderRadius.circular(30),
                ),
                backgroundColor: isCorrectNumberOfVideos ? Theme.of(context).colorScheme.primary : Colors.grey[300],
              ),
        ),
      ],
    ),
  );
}
}



