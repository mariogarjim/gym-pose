import 'package:flutter/material.dart';
import 'package:my_app/custom_navigation_bar.dart';
import 'package:my_app/models/feedback.dart';
import 'package:my_app/widgets/home_exercise_boxes.dart';
import 'package:my_app/widgets/home_summary_boxes.dart';
import 'package:my_app/theme/text_styles.dart';

class HomeScreen extends StatelessWidget {
  const HomeScreen({super.key, this.initialIndex = 0});

  final int initialIndex; 

  @override
  Widget build(BuildContext context) {

    return Scaffold(
      body: Padding(
        padding: const EdgeInsets.all(30),
        child: SingleChildScrollView(
          child: 
        Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            const SizedBox(height: 50),
            Text('Welcome back! 👋', style: AppTextStyles.screenSuperTitle),
            
            ],
          ),
        ),
      ),
    );
  }
}
