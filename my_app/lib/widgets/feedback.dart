import 'package:flutter/material.dart';
import 'package:my_app/models/feedback.dart';
import 'package:my_app/screens/configure_analysis_screen.dart';
import 'package:my_app/theme/text_styles.dart';
import 'package:my_app/widgets/progress_score.dart';
import 'package:my_app/widgets/text_separator.dart';
import 'package:my_app/widgets/video_player.dart';

Widget buildHeader(String exercise, BuildContext context) {
  return Padding(
    padding: const EdgeInsets.all(16),
    child: Column(
      children: [
        const Text('🎯', style: TextStyle(fontSize: 48)),
        const SizedBox(height: 8),
        Text(
          'Your Form Analysis Story',
          style: AppTextStyles.screenTitle,
          textAlign: TextAlign.center,
        ),
        textSeparator(),
      ],
    ),
  );
}

Widget buildGoodPoints(List<String> points, BuildContext context) {
  return Column(
    children: [
      const Text('🎉', style: TextStyle(fontSize: 48)),
      const SizedBox(height: 12),
      Text('What You Did Amazing!',
          style: AppTextStyles.screenTitle,
          textAlign: TextAlign.left,
        ),
      
      const SizedBox(height: 12),
      ...List.generate(points.length, (i) {
        return ListTile(
          leading: CircleAvatar(
            backgroundColor: const Color.fromARGB(255, 113, 152, 117),
            child: Text("${i + 1}", style: const TextStyle(fontSize: 24, color: AppTextStyles.lightGreen)),
          ),
          title: Text("✨ ${points[i]}", style: AppTextStyles.screenSubtitle),
        );
      }),
      textSeparator(),

    ],
  );
}

Widget buildImprovements(List<ImprovementPoint> improvements, BuildContext context) {
  return Column(
    children: [ 
      const SizedBox(height: 18),
      const Text('💡', style: TextStyle(fontSize: 48)),
      const SizedBox(height: 12),
      Text('Areas of Improvement',
          style: AppTextStyles.screenTitle,
          textAlign: TextAlign.left,
        ),
      const SizedBox(height: 12),
      Text('Every champion has room to grow! Here\'s where you can level up your technique 🚀', style: AppTextStyles.screenSubSubtitle, textAlign: TextAlign.center,),
      const SizedBox(height: 25),
      ...improvements.asMap().entries.map((improvement) => 
        Column(
          children: [
            Container(
              decoration: BoxDecoration(
                color: Colors.yellow[100], // pastel yellow
                borderRadius: BorderRadius.circular(20),
              ),
              padding: const EdgeInsets.all(12),
              child: Text('${improvement.key+1}. ${improvement.value.title}', style: AppTextStyles.screenSubtitleBlack, textAlign: TextAlign.left,),
            ),
            const SizedBox(height: 15),
            AdaptiveAspectVideoPlayer(videoPath: improvement.value.videoPath, severity: improvement.value.severity),  
            const SizedBox(height: 15),
            Text(improvement.value.feedback, style: AppTextStyles.screenSubtitle, textAlign: TextAlign.center,),
            const SizedBox(height: 30),
          ],
          
        )
      ),
      textSeparator(),
    ]
  );
}

Widget buildProgress(int currentScore, List<int> previousScores, BuildContext context) {
  int lastScore = previousScores.last;
  previousScores.add(currentScore);
  int score_difference = currentScore - lastScore;
  return Container(
    padding: const EdgeInsets.all(16),
    child: Column(
      children: [
        const SizedBox(height: 18),
        const Text('🏆', style: TextStyle(fontSize: 48)),
        Text(currentScore.toString(),
            style: Theme.of(context).textTheme.titleMedium?.copyWith(
                  fontSize: 64,
                ),
        ),
        Text('YOUR FORM SCORE',
            style: AppTextStyles.screenSubtitle,
            textAlign: TextAlign.center,
          ),
        const SizedBox(height: 30),
        Text('📊 Your progress journey',
            style: AppTextStyles.screenSubtitleBlack,
            textAlign: TextAlign.center,
          ),
        const SizedBox(height: 24),

        buildProgressScore(previousScores, context),
        const SizedBox(height: 18),
        Text(score_difference > 0 ? 'You improved by ${score_difference.abs()} to your last score 📈' : 'You regressed by ${score_difference.abs()} from your last score 📉',
            style: AppTextStyles.screenText,
            textAlign: TextAlign.center,
        ),
        const SizedBox(height: 20),
        textSeparator(),
      ],
    ),
    
  );
}

Widget buildCTA(BuildContext context) {
  return Padding(
    padding: const EdgeInsets.all(16),
    child: Column(
      children: [
      const Text('🎉', style: TextStyle(fontSize: 48)),
      const SizedBox(height: 12),
      Text('Keep Crushing It!',
          style: AppTextStyles.screenTitle,
          textAlign: TextAlign.left,
        ),
      const SizedBox(height: 12),
      Text('You\'re on fire! Ready to analyze another exercise and keep building that perfect form? 💪', style: AppTextStyles.screenSubSubtitle, textAlign: TextAlign.center,),
      const SizedBox(height: 30),
      ElevatedButton.icon(
        onPressed: () {
          Navigator.push(
            context,
            MaterialPageRoute(builder: (context) => const ConfigureAnalysisScreen()),
          );
        },
        label: const Text('Analyze Another'),
      ),
      ],
    ),
      
    
  );
}