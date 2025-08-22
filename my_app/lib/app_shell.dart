import 'package:flutter/material.dart';

// Your tab root screens (content-only widgets)
import 'package:my_app/screens/home_screen.dart';
import 'package:my_app/screens/exercise_selection_screen.dart';
import 'package:my_app/screens/feedback_exercise_selection_screen.dart';
import 'package:my_app/custom_upper_bar.dart';

class AppShell extends StatefulWidget {
  const AppShell({super.key, this.initialIndex = 0});
  final int initialIndex;

  static AppShellState? of(BuildContext context) =>
      context.findAncestorStateOfType<AppShellState>();
  @override
  State<AppShell> createState() => AppShellState();
}

class AppShellState extends State<AppShell> {
  late int _currentIndex;
  late String _textToShow;
  final _navKeys = [
    GlobalKey<NavigatorState>(),
    GlobalKey<NavigatorState>(),
    GlobalKey<NavigatorState>(),
  ];

  void setCurrentIndex(int index) {
    setState(() {
      _currentIndex = index;
    });
  }

  void setTextToShow(String text) {
    setState(() {
      _textToShow = text;
    });
  }

  Future<bool> popCurrentTab() async {
    return await _navKeys[_currentIndex].currentState?.maybePop() ?? false;
  }

  int get currentIndex => _currentIndex;

  @override
  void initState() {
    super.initState();
    _currentIndex = widget.initialIndex;
    _textToShow = "";
  }

  void _selectTab(int index) {
    if (index == _currentIndex) return;
    setState(() => _currentIndex = index);
  }

  Widget _buildTabNavigator(GlobalKey<NavigatorState> key, Widget root) {
    return Navigator(
      key: key,
      onGenerateRoute: (settings) =>
          MaterialPageRoute(builder: (_) => root, settings: settings),
    );
  }

  void pushOnTab(int index, Route route) {
    if (_currentIndex != index) {
      setState(() => _currentIndex = index);
    }
    // push after the frame, so the right tab's Navigator is active
    WidgetsBinding.instance.addPostFrameCallback((_) {
      _navKeys[index].currentState?.push(route);
    });
  }

  @override
  Widget build(BuildContext context) {
    final unselected = Colors.grey.shade400;
    const selected = Colors.black;

    // Hide ALL chrome on tab 1
    bool hideChrome = _currentIndex == 1;
    PreferredSizeWidget? appBar;

    // 👇 Decide which (if any) AppBar to show
    if (_currentIndex == 1 ) {
        appBar = const CustomUpperBar();
    }
    else if (_currentIndex == 2) {
      appBar = CustomUpperBar(
        title: _textToShow.isEmpty ? 'ANALYSIS' : _textToShow,
        returnButton: _textToShow == 'ANALYSIS' ? false : true,   
      );
      hideChrome = _textToShow != 'ANALYSIS';
  }

    return PopScope(
      canPop: false,
      onPopInvokedWithResult: (didPop, result) async {
        if (didPop) return;

        final NavigatorState rootNavigator = Navigator.of(context, rootNavigator: true);
        final NavigatorState? tabNavigator = _navKeys[_currentIndex].currentState;
        final bool didInnerPop = await (tabNavigator?.maybePop() ?? Future<bool>.value(false));
        if (didInnerPop) return;

        // 2) If tab stack is at root and we’re not on Home, switch to Home
        if (!mounted) return;
        if (_currentIndex != 0) {
          setState(() => _currentIndex = 0);
          return; // consume back
        }

        // 3) Already on Home root: allow app to pop (e.g., close)
        if (rootNavigator.canPop()) {
          rootNavigator.pop();
        }
      },
      child: Scaffold(
        appBar: appBar, // 👈 use the conditional app bar

        body: IndexedStack(
          index: _currentIndex,
          children: [
            _buildTabNavigator(_navKeys[0], const HomeScreen()),
            _buildTabNavigator(_navKeys[1], const ExerciseSelectionScreen()),
            _buildTabNavigator(_navKeys[2], const FeedbackExerciseSelectionsScreen()),
          ],
        ),

        // FAB hidden on tab 1
        floatingActionButton: hideChrome
            ? null
            : FloatingActionButton(
                onPressed: () {
                  _navKeys[1].currentState?.popUntil((route) => route.isFirst);
                  _selectTab(1);
                },
                backgroundColor: Colors.black,
                foregroundColor: Colors.white,
                elevation: 0,
                child: const Icon(Icons.add),
              ),
        floatingActionButtonLocation: FloatingActionButtonLocation.centerDocked,

        // Bottom bar hidden on tab 1
        bottomNavigationBar: hideChrome
            ? null
            : BottomAppBar(
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
                          child: IconButton(
                            tooltip: 'Home',
                            onPressed: () => _selectTab(0),
                            icon: Icon(
                              Icons.home_outlined,
                              color: _currentIndex == 0 ? selected : unselected,
                              size: 35,
                            ),
                          ),
                        ),
                        const Spacer(),
                        Padding(
                          padding: const EdgeInsets.only(right: 30),
                          child: IconButton(
                            tooltip: 'Work',
                            onPressed: () => _selectTab(2),
                            icon: Icon(
                              Icons.book_outlined,
                              color: _currentIndex == 2 ? selected : unselected,
                              size: 35,
                            ),
                          ),
                        ),
                      ],
                    ),
                  ),
                ),
              ),
      ),
    );
  }

}
