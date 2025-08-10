import 'package:flutter/material.dart';

Widget buildProgressScore(List<int> previousScores, BuildContext context) {
  const maxH = 150.0;
  const borderColor = Color(0xFF4285F4); // bright blue
  const fillColor = Color(0xFFD6E8FF);   // pastel blue

  return Container(
    padding: const EdgeInsets.all(16),
    color: Theme.of(context).colorScheme.surface,
    child: Row(
      crossAxisAlignment: CrossAxisAlignment.end,
      children: List.generate(previousScores.length, (i) {
        final h = (previousScores[i] / 100.0) * maxH;
        final isLast = i == previousScores.length - 1;

        return Expanded(
          child: Column(
            mainAxisAlignment: MainAxisAlignment.end,
            children: [
              Container(
                height: h,
                decoration: BoxDecoration(
                  color: fillColor,
                  border: Border.all(
                    color: borderColor,
                    width: 2,
                  ),
                  borderRadius: const BorderRadius.vertical(
                    top: Radius.circular(16),
                  ),
                ),
                alignment: Alignment.center,
                child: Text(
                  '${previousScores[i]}',
                  style: const TextStyle(
                    fontWeight: FontWeight.bold,
                    color: borderColor,
                    fontSize: 14,
                  ),
                ),
              ),
              const SizedBox(height: 6),
              Text(
                isLast ? 'Today' : 'Session ${i + 1}',
                style: TextStyle(
                  fontSize: 10,
                  color: Theme.of(context).textTheme.bodySmall?.color,
                ),
              ),
            ],
          ),
        );
      }),
    ),
  );
}
