import 'package:flutter/material.dart';
import 'package:my_app/theme/text_styles.dart';

class TodoItem extends StatelessWidget {
  final String title;
  final String subtitle;
  final String priority;
  final bool completed;

  const TodoItem({super.key, required this.title, required this.subtitle, required this.priority, required this.completed});

  @override
  Widget build(BuildContext context) {
    return buildTodoItem(title, subtitle, priority, completed);
  }
}

Widget buildTodoItem(String title, String subtitle, String priority, bool completed) {
    final colorMap = {
      "high": Colors.red.shade700,
      "medium": Colors.yellow.shade700,
    };

    final bgMap = {
      "high": Colors.red.shade100,
      "medium": Colors.yellow.shade100,
    };

    return Container(
      margin: const EdgeInsets.only(bottom: 12),
      padding: const EdgeInsets.all(12),
      decoration: BoxDecoration(
        color: completed ? Colors.green.shade50 : Colors.white,
        border: Border.all(color: Colors.grey.shade300),
        borderRadius: BorderRadius.circular(8),
      ),
      child: Row(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          // Radio/check
          Icon(
            completed ? Icons.check_circle : Icons.radio_button_unchecked,
            color: completed ? Colors.green : Colors.grey.shade400,
          ),
          const SizedBox(width: 12),
          Expanded(
            child: Column(
              crossAxisAlignment: CrossAxisAlignment.start,
              children: [
                Row(
                  children: [
                    Text(title, style: AppTextStylesV2.homeWidgetTitle),
                    const SizedBox(width: 8),
                    Container(
                      padding: const EdgeInsets.symmetric(horizontal: 8, vertical: 2),
                      decoration: BoxDecoration(
                        color: bgMap[priority],
                        borderRadius: BorderRadius.circular(6),
                      ),
                      child: Text(priority,
                          style: TextStyle(
                              color: colorMap[priority],
                              fontWeight: FontWeight.w600,
                              fontSize: 12)),
                    ),
                  ],
                ),
                const SizedBox(height: 4),
                Text(
                  subtitle,
                  style: TextStyle(
                    color: Colors.grey.shade700,
                    fontSize: 13,
                    decoration: completed ? TextDecoration.lineThrough : null,
                  ),
                ),
              ],
            ),
          ),
        ],
      ),
    );
}