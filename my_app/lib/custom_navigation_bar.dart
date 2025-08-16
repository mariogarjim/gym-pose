import 'package:flutter/material.dart';
import 'package:my_app/screens/configure_analysis_screen.dart';
import 'package:my_app/screens/home_screen.dart';

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
    1: const ConfigureAnalysisScreen(),
  };

  void _onItemTapped(int index) {
    setState(() {
      if (index == _selectedIndex) {
        return;
      }
      _selectedIndex = index;
      Navigator.push(
        context,
        MaterialPageRoute(builder: (context) => _pages[index]!),
      );
    });
  }  

  @override
  Widget build(BuildContext context) {
    return BottomNavigationBar(
        showSelectedLabels: true,
        showUnselectedLabels: true,
        type: BottomNavigationBarType.fixed,
        selectedItemColor: Theme.of(context).colorScheme.primary,
        unselectedItemColor: Colors.blueGrey,
        items: const <BottomNavigationBarItem>[
          BottomNavigationBarItem(
            icon: Icon(Icons.home),
            label: 'Home',
          ),
          BottomNavigationBarItem(
            icon: Icon(Icons.add_circle_outline),
            label: 'New analysis',
          ),
        ],
        currentIndex: _selectedIndex,
        onTap: _onItemTapped,
      );
  }
}