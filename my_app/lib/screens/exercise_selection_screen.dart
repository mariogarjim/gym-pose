import 'package:flutter/material.dart';
import 'package:my_app/custom_upper_bar.dart';
import 'package:my_app/screens/upload_video_screen.dart';  
import 'package:my_app/theme/text_styles.dart'; 
import 'package:my_app/widgets/exercise_image_switcher.dart';


final exercises = [
  {
    "name": "SQUATS",
    "description": "Lower body strength exercise",
    "image-first": "assets/images/squat1.png",
    "image-second": "assets/images/squat2.png"
  },
  {
    "name": "PULL-UPS",
    "description": "Upper body pulling exercise",
    "image-first": "assets/images/pull-up1.png",
    "image-second": "assets/images/pull-up2.png"
  },
  {
    "name": "LATERAL RAISES",
    "description": "Upper body pushing exercise",
    "image-first": "assets/images/lateral-raise1.png",
    "image-second": "assets/images/lateral-raise2.png"
  },
];

class ExerciseSelectionScreen extends StatefulWidget {
  const ExerciseSelectionScreen({super.key});

  @override
  State<ExerciseSelectionScreen> createState() =>
      _ExerciseSelectionScreenState();
}

class _ExerciseSelectionScreenState extends State<ExerciseSelectionScreen> {
  int? selectedIndex;

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: const CustomUpperBar(),
      backgroundColor: Colors.white,
      body: Column(
        children: [
          Expanded(
            child: ListView.builder(
              padding: const EdgeInsets.symmetric(horizontal: 16, vertical: 8),
              itemCount: exercises.length,
              itemBuilder: (context, index) {
                final exercise = exercises[index];
                final isSelected = selectedIndex == index;

                return GestureDetector(
                  onTap: () {
                    setState(() => selectedIndex = index);
                  },
                  child: Container(
                    margin: const EdgeInsets.symmetric(vertical: 10),
                    child: Row(
                      crossAxisAlignment: CrossAxisAlignment.center,
                      children: [
                        // first exercise image (preview)
                         ExerciseImageSwitcher(
                          first: exercise["image-first"] as String,
                          second: exercise["image-second"] as String,
                          play: isSelected,
                          interval: const Duration(milliseconds: 700),
                          fadeDuration: const Duration(milliseconds: 250),
                        ),
                        const SizedBox(width: 20),
                        // Exercise name
                        Container(
                           padding: const EdgeInsets.symmetric(horizontal: 8, vertical: 4),
                           decoration: BoxDecoration(
                              color: isSelected ? const Color(0xFFFFFF66) : Colors.transparent, // amarillo con opacidad
                              borderRadius: BorderRadius.circular(6),
                           ),
                           child: Text(
                             exercise["name"] as String,
                             style: AppTextStylesV2.exerciseNames,
                           ),
                        ),
                      ],
                    ),
                  ),
                );
              },
            ),
          ),

          // Continue button
          SafeArea(
            child: Padding(
              padding: const EdgeInsets.fromLTRB(32, 0, 32, 16), 
              child: SizedBox(
                width: double.infinity,
                child: ElevatedButton(
                  style: ElevatedButton.styleFrom(
                    backgroundColor: Colors.black,
                    foregroundColor: Colors.white,
                    padding: const EdgeInsets.symmetric(vertical: 16),
                    shape: RoundedRectangleBorder(
                      borderRadius: BorderRadius.circular(16),
                    ),
                  ),
                  onPressed: selectedIndex != null
                      ? () {
                          final selectedExercise = exercises[selectedIndex!]["name"] as String;
                          Navigator.push(
                            context,
                            MaterialPageRoute(builder: (context) => UploadRequiredVideosScreen(exerciseName: selectedExercise)),
                          );
                        }
                      : null,
                  child: const Text(
                    "Continue",
                    style:
                        TextStyle(fontSize: 16, fontWeight: FontWeight.w600),
                  ),
                ),
              ),
            ),
          ),
        ],
      ),
    );
  }
}
