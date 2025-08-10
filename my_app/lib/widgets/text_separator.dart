import 'package:flutter/material.dart';

Widget textSeparator() {
  return Container(
          height: 2,
          margin: const EdgeInsets.symmetric(vertical: 16),
          decoration: BoxDecoration(
            gradient: LinearGradient(
              colors: [Colors.transparent, Colors.grey.shade400, Colors.transparent],
            ),
          ),
        );
}