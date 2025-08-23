import 'package:flutter/material.dart';
import 'package:my_app/theme/text_styles.dart';
import 'package:my_app/app_shell.dart';

class CustomUpperBar extends StatelessWidget implements PreferredSizeWidget {
  const CustomUpperBar({super.key, this.title = "", this.returnButton = true});
  final String title;
  final bool returnButton;

  @override
  Size get preferredSize => const Size.fromHeight(kToolbarHeight);

  @override
  Widget build(BuildContext context) {
    return AppBar(
      automaticallyImplyLeading: false,
      leading: returnButton
          ? IconButton(
              icon: const Icon(Icons.arrow_back_ios_new),
              onPressed: () async {
                
                // 1) Try to pop inside the CURRENT TAB navigator (owned by AppShell)
                final shell = AppShell.of(context);

                if (shell?.currentIndex == 2) {
                  shell?.setTextToShow("RESULTS");
                }

                final nearestNavigator = Navigator.of(context);
                final root = Navigator.of(context, rootNavigator: true);

                final didPopTab = await (shell?.popCurrentTab() ?? Future<bool>.value(false));
                if (didPopTab) return;

                // 2) Try the nearest (page) navigator
                if (await nearestNavigator.maybePop()) return;

                // 3) Try the ROOT navigator (full-screen flows)
                if (root.canPop()) {
                  root.pop();
                  return;
                }

                // 4) Nothing to pop: do nothing (or SystemNavigator.pop if you prefer)
              },
            )
          : null,
      title: Text(
        title.toUpperCase(),
        style: AppTextStylesV2.screenSuperTitle,
        textAlign: TextAlign.center,
      ),
      centerTitle: true,
      elevation: 0,
      backgroundColor: Colors.white,
      foregroundColor: Colors.black,
      bottom: const PreferredSize(
        preferredSize: Size.fromHeight(1),
        child: Divider(height: 1, thickness: 1, color: Color(0xFFE0E0E0)),
      ),
    );
  }
}
