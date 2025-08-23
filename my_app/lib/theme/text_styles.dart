import 'package:flutter/material.dart';
import 'package:google_fonts/google_fonts.dart';
  
class AppTextStylesV2 {

  static TextStyle get screenSuperTitle => GoogleFonts.inter(
    fontWeight: FontWeight.w800,
    fontSize: 24,
    color: Colors.black,
  );

  static TextStyle get exerciseNames => GoogleFonts.inter(
    fontWeight: FontWeight.w800,
    fontSize: 20,
    color: Colors.black,
  );

  static TextStyle get screenTitle => GoogleFonts.inter(
    fontWeight: FontWeight.w600,
    fontSize: 24,
    color: Colors.black,
  );

  static TextStyle get homeScreenTitle => GoogleFonts.inter(
    fontWeight: FontWeight.w600,
    fontSize: 30,
    color: Colors.black,
  );

  static TextStyle get screenSubtitle => GoogleFonts.inter(
    fontWeight: FontWeight.w400,
    fontSize: 18,
    color: Colors.black,
  );

  static TextStyle get homeScreenSubtitle => GoogleFonts.inter(
    fontWeight: FontWeight.w400,
    fontSize: 20,
    color: Colors.black,
  );

  static TextStyle get textBody => GoogleFonts.inter(
    fontWeight: FontWeight.w400,
    fontSize: 20,
    color: Colors.black,
  );

  static TextStyle get textBodyGrey => GoogleFonts.inter(
    fontWeight: FontWeight.w400,
    fontSize: 20,
    color: Colors.grey[800],
  );

  static TextStyle get requirementLabel => GoogleFonts.inter(
        fontWeight: FontWeight.w700,
        fontSize: 16,
        color: Colors.black,
      );


  static TextStyle get requirementDescription => GoogleFonts.inter(
        fontWeight: FontWeight.w400,
        fontSize: 14,
        color: Colors.black87,
      );

  static TextStyle get homeWidgetTitle => GoogleFonts.inter(
        fontWeight: FontWeight.w600,
        fontSize: 16,
        color: Colors.black,
      );

  static TextStyle exerciseFeedbackRating(Color color) => GoogleFonts.inter(
    fontWeight: FontWeight.w700,
    fontSize: 20,
    color: color,
  );

  static TextStyle get tooltipText => GoogleFonts.inter(
    fontWeight: FontWeight.w400,
        fontSize: 16,
        color: Colors.black87,
      );

  static TextStyle get requirementHint => GoogleFonts.inter(
        fontWeight: FontWeight.w400,
        fontSize: 12,
        color: Colors.grey,
      );

  static TextStyle get statCardValue => GoogleFonts.inter(
        fontWeight: FontWeight.w700,
        fontSize: 24,
        color: Colors.black87,
      );

  static TextStyle get homeTabTitle => GoogleFonts.inter(
    fontWeight: FontWeight.w500,
    fontSize: 14,
    color: Colors.white,
  );

  
  
}

class AppTextStyles {

  static TextStyle get screenSuperTitle => TextStyle(
    fontSize: 30,
    fontWeight: FontWeight.bold,
    color: Colors.grey[800],
    letterSpacing: 0.5,
    height: 1.3,
  );

  static TextStyle get screenTitle => TextStyle(
    fontSize: 24,
    fontWeight: FontWeight.bold,
    color: Colors.grey[800],
    letterSpacing: 0.5,
    height: 1.3,
  );


  static TextStyle get screenSubtitleBlack => TextStyle(
    fontSize: 20,
    fontWeight: FontWeight.bold,
    color: Colors.grey[900],
    letterSpacing: 0.25,
    height: 1.5,
  );



  static TextStyle get screenSubtitle => TextStyle(
    fontSize: 20,
    fontWeight: FontWeight.w400,
    color: Colors.grey[600],
    letterSpacing: 0.25,
    height: 1.5,
  );

  static TextStyle get screenSubSubtitle => TextStyle(
    fontSize: 18,
    fontWeight: FontWeight.w400,
    color: Colors.grey[600],
    letterSpacing: 0.25,
    height: 1.5,
  );

  static const TextStyle screenText = TextStyle(
    fontSize: 18,
    fontWeight: FontWeight.w400,
    color: Colors.black,
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