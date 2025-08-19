import 'package:flutter/material.dart';
import 'package:my_app/screens/home_screen.dart';

class CustomUpperBar extends StatelessWidget implements PreferredSizeWidget {
  const CustomUpperBar({super.key});

  @override
  Size get preferredSize => const Size.fromHeight(kToolbarHeight);

  @override
  Widget build(BuildContext context) {
    return AppBar(
      leading: IconButton(
        icon: const Icon(Icons.arrow_back_ios_new),
        onPressed: () {
          Navigator.push(
            context,
            MaterialPageRoute(
              builder: (context) => const HomeScreen(initialIndex: 0),
            ),
          );
        },
      ),
      elevation: 0,
      backgroundColor: Colors.white,
      foregroundColor: Colors.black,
      bottom: const PreferredSize(
      preferredSize: Size.fromHeight(1),
      child: Divider(
        height: 1,
        thickness: 1,
        color: Color(0xFFE0E0E0), // thin grey line
      ),
    ),
    );
  }
}