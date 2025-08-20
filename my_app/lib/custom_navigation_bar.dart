import 'package:flutter/material.dart';
import 'package:my_app/screens/home_screen.dart';
import 'package:my_app/screens/exercise_selection_screen.dart';
import 'package:my_app/screens/feedback_exercise_selection.dart';

class CustomNavigationBar extends StatefulWidget {
  const CustomNavigationBar({super.key, this.initialIndex = 0});

  final int initialIndex;

  @override
  CustomNavigationBarState createState() => CustomNavigationBarState();
}


class CustomNavigationBarState extends State<CustomNavigationBar> {
  late int _selectedIndex;

  @override
  void initState() {
    super.initState();
    _selectedIndex = widget.initialIndex;
  }

  final Map<int, Widget> _pages = {
    0: const HomeScreen(),
    1: const ExerciseSelectionScreen(),
    2: const FeedbackExerciseSelection(),
  };

  void _onItemTapped(int index) {
    setState(() {
      if (index == _selectedIndex) {
        return;
      }
      _selectedIndex = index;
      Navigator.of(context, rootNavigator: true).push(
        MaterialPageRoute(builder: (_) => _pages[index]!),
      );
    });
  }  

  @override
  Widget build(BuildContext context) {
    final unselected = Colors.grey.shade400;
    const selected = Colors.black;

    return Scaffold(  
      // Big circular "+" button in the middle
      floatingActionButton: FloatingActionButton(
        onPressed: () {
          _onItemTapped(1);
        },
        backgroundColor: Colors.black,
        foregroundColor: Colors.white,
        elevation: 0,
        child: const Icon(Icons.add)
      ),
      floatingActionButtonLocation: FloatingActionButtonLocation.centerDocked,

      // White bottom bar with a notch for the FAB
      bottomNavigationBar: BottomAppBar(
        color: Colors.white,
        elevation: 2,
        shape: const CircularNotchedRectangle(),
        notchMargin: 8,
        child: SafeArea(
          top: false,
          child: SizedBox(
            height: 56,
            child: Row(
              children: [
                Padding(
                  padding: const EdgeInsets.only(left: 30),
                  child: 
                    IconButton(
                      tooltip: 'Home',
                      onPressed: () => _onItemTapped(0),
                      icon: Icon(
                        Icons.home_outlined,
                        color: _selectedIndex == 0 ? selected : unselected,
                        size: 35
                      ),
                    ),
                ),
                const Spacer(),
                Padding(
                  padding: const EdgeInsets.only(right: 30),
                  child: 
                    IconButton(
                      tooltip: 'Work',
                      onPressed: () => _onItemTapped(2),
                      icon: Icon(
                        Icons.book_outlined,
                        color: _selectedIndex == 2 ? selected : unselected, // black outline look
                        size: 35
                      ),
                    ),
                ),
              ],
            ),
          ),
        ),
      ),
    );
  }
}