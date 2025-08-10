import 'dart:async';
import 'dart:developer';
import 'package:flutter/material.dart';
import 'package:my_app/theme/text_styles.dart';
import 'package:my_app/core/api/video_upload_service.dart';
import 'package:my_app/screens/feedback_screen.dart';
import 'package:my_app/widgets/animated_image_switcher.dart';
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

final exercises = [
    {"name": "Squats", "description": "Lower body strength exercise", "images": ["assets/images/squat1.png", "assets/images/squat2.png"]},
    {"name": "Pull-ups", "description": "Upper body pulling exercise", "images": ["assets/images/pull-up1.png", "assets/images/pull-up2.png"]},
    {"name": "Bench Press", "description": "Upper body pushing exercise", "images": ["assets/images/bench-press.png"]},
  ];

  final analysisSteps = [
    "Uploading video...",
    "Detecting movement patterns...",
    "Analyzing form and technique...",
    "Comparing to optimal form...",
    "Generating personalized feedback...",
    "Preparing demonstration videos..."
  ];

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

  void _pickVideo(String reqId) async {
    final picker = ImagePicker();
    final picked = await picker.pickVideo(source: ImageSource.gallery, maxDuration: const Duration(seconds: 60));
    if (picked != null) {
      setState(() => uploadedVideos[reqId] = picked);
      if (uploadedVideos.values.where((v) => v != null).length == requiredVideos[selectedExercise]!.length) {
        log("Correct number of videos: ${uploadedVideos.length}");
        log("Correct number of videos: $uploadedVideos");

        log("Required number of videos: ${requiredVideos[selectedExercise]!.length}");
        setState(() => isCorrectNumberOfVideos = true);
      }
    }
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
          title: Text("Upload your videos", style: AppTextStyles.screenTitle),
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
      leading: Icon(Icons.sports_gymnastics, size: 30, color: Theme.of(context).colorScheme.primary),
                  title: Text(
              "Exercise selection",
              style: AppTextStyles.screenTitle,
            ),
      ),
    body: Padding(
      padding: const EdgeInsets.all(16),
      child: Column(
        children: [
          Text(
            "Choose the exercise you want to analyze",
                        style: AppTextStyles.screenSubtitle,
          ),
          const SizedBox(height: 32),
          Expanded(
            child: GridView.builder(
              itemCount: exercises.length,
              gridDelegate: const SliverGridDelegateWithFixedCrossAxisCount(
                crossAxisCount: 2,
                mainAxisSpacing: 16,
                crossAxisSpacing: 16,
                childAspectRatio: 3 / 4,
              ),
              itemBuilder: (context, index) {
                final exercise = exercises[index];
                final isSelected = selectedExercise == exercise['name'];

                return GestureDetector(
                  onTap: () => handleSelectExercise(exercise['name'] as String),
                  child: Container(
                    decoration: BoxDecoration(
                      borderRadius: BorderRadius.circular(16),
                      border: Border.all(
                        color: isSelected
                            ? Theme.of(context).colorScheme.primary
                            : Colors.grey.shade300,
                        width: 2,
                      ),
                      color: isSelected ? Colors.blue[50] : Colors.white,
                      boxShadow: const [
                        BoxShadow(
                          color: Colors.black12,
                          blurRadius: 6,
                          offset: Offset(0, 2),
                        ),
                      ],
                    ),
                    child: Column(
                      crossAxisAlignment: CrossAxisAlignment.stretch,
                      children: [
                        Expanded(
                          child: ClipRRect(
                            borderRadius: const BorderRadius.vertical(top: Radius.circular(14)),
                            child: AnimatedImageSwitcher(
                              exerciseName: exercise['name'] as String,
                              isSelected: isSelected,
                              exerciseImages: exercise['images'] as List<String>,
                            ),
                          ),
                        )
                      ],
                    ),
                  ),
                );
              },
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
        Text(
            "We need specific camera angles to analyze your form accurately",
            textAlign: TextAlign.center,
            style: AppTextStyles.screenSubtitle,
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
                elevation: 3,
                shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(20)),
                margin: const EdgeInsets.symmetric(vertical: 8),
                color: Colors.white,
                child: Padding(
                  padding: const EdgeInsets.all(16),
                  child: Column(
                    children: [
                      uploadedFile != null
                          ? Container(
                              width: double.infinity,
                              padding: const EdgeInsets.symmetric(vertical: 16),
                              decoration: BoxDecoration(
                                border: Border.all(color: Colors.white),
                                borderRadius: BorderRadius.circular(12),
                              ),
                              child: Column(
                                mainAxisAlignment: MainAxisAlignment.spaceBetween,
                                children: [
                                    const CircleAvatar(
                                        radius: 30,
                                        backgroundColor: AppTextStyles.lightGreen,
                                        child: Icon(
                                          Icons.cloud_done_outlined,
                                          size: 30,
                                          color: AppTextStyles.darkGreen,
                                        ),
                                      ),
                                    const SizedBox(height: 8),
                                    Text(
                                      uploadedFile.name.length > 20 ? "${uploadedFile.name.substring(0, 20)}..." : uploadedFile.name,
                                      style: const TextStyle(fontWeight: FontWeight.bold, fontSize: 20, color: AppTextStyles.darkGreen),
                                    ),
                                    const SizedBox(height: 4),
                                    const Text(
                                      "Video uploaded successfully",
                                      style: TextStyle(color: Colors.grey, fontSize: 16),
                                    ),
                                    const SizedBox(height: 16),
                                    ElevatedButton(
                                      onPressed: () => setState(() {
                                        uploadedVideos[req['id']!] = null;
                                        isCorrectNumberOfVideos = false;
                                      }),
                                      style: ElevatedButton.styleFrom(
                                        backgroundColor: AppTextStyles.lightRed,
                                        shape: RoundedRectangleBorder(
                                          borderRadius: BorderRadius.circular(12),
                                        ),
                                      ),
                                      child: const Row(
                                        mainAxisAlignment: MainAxisAlignment.center,
                                        children: [
                                          Icon(Icons.delete_outline, size: 20, color: AppTextStyles.darkRed),
                                          Text("  Remove Video", style: TextStyle(fontSize: 16, fontWeight: FontWeight.bold, color: AppTextStyles.darkRed)),
                                        ],
                                      ),
                                    )
                                  
  
                                ],
                              ),
                            )
                          : GestureDetector(
                              onTap: () => _pickVideo(req['id']!),
                              child: Container(
                                width: double.infinity,
                                padding: const EdgeInsets.symmetric(vertical: 16),
                                decoration: BoxDecoration(
                                  border: Border.all(color: Colors.white),
                                  borderRadius: BorderRadius.circular(12),
                                ),
                                child: Column(
                                  mainAxisAlignment: MainAxisAlignment.center,
                                  children: [
                                    const CircleAvatar(
                                        radius: 30,
                                        backgroundColor: AppTextStyles.beigeColor,
                                        child: Icon(
                                          Icons.camera_alt_outlined,
                                          size: 30,
                                          color: Colors.black,
                                        ),
                                      ),
                                    const SizedBox(height: 8),
                                    Text(
                                      req['label']!,
                                      style: const TextStyle(fontWeight: FontWeight.bold, fontSize: 20),
                                    ),
                                    const SizedBox(height: 4),
                                    Text(
                                      req['description']!,
                                      style: const TextStyle(color: Colors.grey, fontSize: 16),
                                    ),
                                    const SizedBox(height: 16),
                                    ElevatedButton(
                                      onPressed: () => _pickVideo(req['id']!),
                                      child: const Row(
                                        mainAxisAlignment: MainAxisAlignment.center,
                                        children: [
                                          Icon(Icons.file_upload_outlined, size: 20),
                                          Text("  Upload Video", style: TextStyle(fontSize: 16, fontWeight: FontWeight.bold)),
                                        ],
                                      ),
                                    )
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

        ElevatedButton.icon(
          onPressed: isCorrectNumberOfVideos ? () => startAnalysis(uploadedVideos.values.map((v) => v!.path).toList()) : null,
          icon: Icon(Icons.check, size: 20, color: isCorrectNumberOfVideos ? AppTextStyles.lightBlue :  Colors.grey),
          label: Text("Continue", style: TextStyle(fontSize: 16, color: isCorrectNumberOfVideos ? AppTextStyles.lightBlue : Colors.grey)),
           style: ElevatedButton.styleFrom(
                padding: const EdgeInsets.symmetric(horizontal: 36, vertical: 18),
                shape: RoundedRectangleBorder(
                  borderRadius: BorderRadius.circular(30),
                ),
                backgroundColor: isCorrectNumberOfVideos ? AppTextStyles.mediumBlue : AppTextStyles.mediumBlue,
              ),
        ),
      ],
    ),
  );
}
}



