import 'package:flutter/material.dart';
import 'dart:io';
import 'package:my_app/models/feedback.dart';
import 'package:my_app/models/upload_video.dart';
import 'package:my_app/screens/configure_analysis_screen.dart';
import 'package:video_player/video_player.dart';
import 'package:path/path.dart' as path;
import 'package:my_app/widgets/feedback.dart';

class FeedbackScreen extends StatefulWidget {
  const FeedbackScreen({super.key, required this.videoResponse});
  final UploadVideoResult videoResponse;

  @override
  State<FeedbackScreen> createState() => _FeedbackScreenState();
}


class _FeedbackScreenState extends State<FeedbackScreen> {
  List<Map<String, dynamic>> videos = [];
  final String selectedExercise = 'Squat';
  final overallScore = 78;

  FeedbackModel setFeedback(String exercise, int overallScore) {
    return FeedbackModel(
      exercise: exercise,
      overallScore: overallScore,
      goodPoints: [
        "Good depth in the squat movement",
        "Knees properly aligned with toes",
        "Maintained neutral spine throughout"
      ],
      improvementPoints: [
        ImprovementPoint(
          title: "Weight Distribution",
          feedback: "Try to distribute your weight evenly between your feet",
          videoPath: "assets/videos/squat_10.mp4",
          severity: "high"
        ),
        ImprovementPoint(
          title: "Head Alignment",
          feedback: "Keep your head aligned with your spine",
          videoPath: "assets/videos/squat_10.mp4",
          severity: "warning"
        ),  
        ImprovementPoint(
          title: "Head Alignment",
          feedback: "Keep your head aligned with your spine",
          videoPath: "assets/videos/squat_10.mp4",
          severity: "high"
        ),  
      ],  
      previousScores: [70, 80, 81],
    );
  }

  @override
  Widget build(BuildContext context) {
    final FeedbackModel analysisResult = setFeedback("squat", 78);
    final scores = analysisResult.previousScores;

    return Scaffold(
      body: SafeArea(
        child: Column(
          children: [
            Expanded(
              child: SingleChildScrollView(
                child: Padding(
                padding: const EdgeInsets.all(16),
                child: Column(
                  children: [
                    buildHeader(analysisResult.exercise, context),
                    buildGoodPoints(analysisResult.goodPoints, context),
                    buildImprovements(analysisResult.improvementPoints, context),
                    buildProgress(analysisResult.overallScore, scores, context),
                    buildCTA(context),
                  ],
              ),
            ),
          ),
        ),
          ]
      ),
    ));
  }
}