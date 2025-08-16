class FeedbackModel {
  final String exercise;
  final int overallScore;
  final List<String> goodPoints;
  final List<ImprovementPoint> improvementPoints;
  final List<int> previousScores;

  FeedbackModel({
    required this.exercise,
    required this.overallScore,
    required this.goodPoints,
    required this.improvementPoints,
    required this.previousScores,
  });

  // Create from JSON (Map)
  factory FeedbackModel.fromJson(Map<String, dynamic> json) {
    return FeedbackModel(
      exercise: json['exercise'] as String,
      overallScore: json['overallScore'] as int,
      goodPoints: List<String>.from(json['goodPoints']),
      improvementPoints: (json['improvementPoints'] as List)
          .map((e) => ImprovementPoint.fromJson(e))
          .toList(),
      previousScores: List<int>.from(json['previousScores']),
    );
  }

  // Convert to JSON (Map)
  Map<String, dynamic> toJson() {
    return {
      'exercise': exercise,
      'overallScore': overallScore,
      'goodPoints': goodPoints,
      'improvementPoints':
          improvementPoints.map((e) => e.toJson()).toList(),
      'previousScores': previousScores,
    };
  }
}

class ImprovementPoint {
  final String title;
  final String feedback;
  final String videoPath;
  final String severity;

  ImprovementPoint({
    required this.title,
    required this.feedback,
    required this.videoPath,
    required this.severity,
  });

  factory ImprovementPoint.fromJson(Map<String, dynamic> json) {
    return ImprovementPoint(
      title: json['title'] as String,
      feedback: json['feedback'] as String,
      videoPath: json['videoPath'] as String,
      severity: json['severity'] as String,
    );
  }

  Map<String, dynamic> toJson() {
    return {
      'title': title,
      'feedback': feedback,
      'videoPath': videoPath,
      'severity': severity,
    };
  }
}


class ExerciseResult {
  final String id;
  final String name;
  final DateTime date;
  final int grade;
  final List<String> goodPoints;
  final List<String> improvements;

  ExerciseResult({
    required this.id,
    required this.name,
    required this.date,
    required this.grade,
    required this.goodPoints,
    required this.improvements,
  });
}

final mockExerciseResults = [
  ExerciseResult(
    id: '1',
    name: 'Squat',
    date: DateTime.now(),
    grade: 85,
    goodPoints: ['Good depth in the squat movement', 'Knees properly aligned with toes', 'Maintained neutral spine throughout'],
    improvements: ['Try to distribute your weight evenly between your feet', 'Keep your head aligned with your spine', 'Keep your head aligned with your spine'],
  ),
  ExerciseResult(
    id: '2',
    name: 'Push-up',
    date: DateTime.now(),
    grade: 75,
    goodPoints: ['Good depth in the push-up movement', 'Knees properly aligned with toes', 'Maintained neutral spine throughout'],
    improvements: ['Try to distribute your weight evenly between your feet', 'Keep your head aligned with your spine', 'Keep your head aligned with your spine'],
  ),
  ExerciseResult(
    id: '3',
    name: 'Pull-up',
    date: DateTime.now(),
    grade: 90,
    goodPoints: ['Good depth in the pull-up movement', 'Knees properly aligned with toes', 'Maintained neutral spine throughout'],
    improvements: ['Try to distribute your weight evenly between your feet', 'Keep your head aligned with your spine', 'Keep your head aligned with your spine'],
  ),
];