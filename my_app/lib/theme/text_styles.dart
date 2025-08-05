import 'package:flutter/material.dart';

class AppTextStyles {
  static TextStyle get screenTitle => TextStyle(
    fontSize: 24,
    fontWeight: FontWeight.bold,
    color: Colors.grey[800],
    letterSpacing: 0.5,
    height: 1.3,
  );

  static TextStyle get screenSubtitle => TextStyle(
    fontSize: 20,
    fontWeight: FontWeight.w400,
    color: Colors.grey[600],
    letterSpacing: 0.25,
    height: 1.5,
  );

  static const Color beigeColor = Color.fromARGB(255, 246, 240, 228);

  static const Color darkGreen = Color.fromARGB(255, 76, 161, 84);
  static const Color mediumGreen = Color.fromARGB(255, 159, 207, 164);
  static const Color lightGreen = Color.fromARGB(255, 200, 250, 213);

  static const Color lightRed = Color.fromARGB(255, 255, 235, 235);
  static const Color darkRed = Color.fromARGB(255, 200, 40, 40);

  static const Color lightBlue = Color.fromARGB(255, 242, 243, 249);
  static const Color mediumBlue = Color.fromARGB(255, 49, 98, 141);
}