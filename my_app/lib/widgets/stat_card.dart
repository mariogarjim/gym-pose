import 'package:flutter/material.dart';
import 'package:my_app/theme/text_styles.dart';

class StatCard extends StatelessWidget {
  const StatCard({super.key, required this.title, required this.value});

  final String title;
  final String value;

  @override
  Widget build(BuildContext context) {
    return Container(
      width: 220, 
      padding: const EdgeInsets.all(16),
      decoration: BoxDecoration(
        color: Colors.white,
        borderRadius: BorderRadius.circular(12),
        border: Border.all(color: Colors.grey.shade300),
      ),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          Text(title, style: AppTextStylesV2.homeWidgetTitle),
          const SizedBox(height: 6),
          Text(value, style: AppTextStylesV2.statCardValue),
        ],
      ),
    );
  }
}