import 'package:flutter/material.dart';
import 'package:my_app/widgets/stat_card.dart';
import 'package:my_app/widgets/todo_items_card.dart';
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
            Text('Welcome back! 👋', style: AppTextStylesV2.homeScreenTitle),
            Text('Ready to improve your form?', style: AppTextStylesV2.homeScreenSubtitle),
            const SizedBox(height: 20),
             Container(
              padding: const EdgeInsets.symmetric(horizontal: 14, vertical: 6),
              decoration: BoxDecoration(
                color: Colors.black,
                borderRadius: BorderRadius.circular(20),
              ),
              child: Text(
                "General",
                style: AppTextStylesV2.homeTabTitle,
              ),
            ),
            const SizedBox(height: 20),   
            const SingleChildScrollView(
              scrollDirection: Axis.horizontal,
              child: 
                Row(
                  children: [
                    StatCard(title: "Analyzed exercises:", value: "10"),
                    SizedBox(width: 12),
                    StatCard(title: "Improvements:", value: "8"),
                  ],
                )
            ),
            const SizedBox(height: 25),
           Container(
            padding: const EdgeInsets.all(16),
            decoration: BoxDecoration(
              color: Colors.white,
              borderRadius: BorderRadius.circular(12),
              border: Border.all(color: Colors.grey.shade300),
            ),
            child: Column(
              crossAxisAlignment: CrossAxisAlignment.start,
              children: [
                // Title row
                Text("Areas of improvement:",
                    style: AppTextStylesV2.homeWidgetTitle),
                const SizedBox(height: 12),
                const TodoItem(title: 'Back posture', subtitle: 'Squat', priority: 'high', completed: false),
                const TodoItem(title: 'Chin over the bar', subtitle: 'Pull up', priority: 'medium', completed: false),
                const TodoItem(title: 'Knee alignment', subtitle: 'Squat', priority: 'medium', completed: true),
              ],
            ),
           ),
          ],
          ),
        ),
      ),
    );
  }
}


