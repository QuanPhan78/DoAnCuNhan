import os

os.makedirs("lib/screens/onboarding", exist_ok=True)
ui = """import 'package:flutter/material.dart';

class OnboardingScreen extends StatefulWidget {
  const OnboardingScreen({super.key});

  @override
  State<OnboardingScreen> createState() => _OnboardingScreenState();
}

class _OnboardingScreenState extends State<OnboardingScreen> {
  final PageController _pageController = PageController();
  int _currentPage = 0;

  final List<Map<String, String>> _onboardingData = [
    {
      "title": "Chào mừng đến với hệ thống",
      "subtitle": "Quản lý thuê thiết bị điện tử chuyên nghiệp và tiện lợi.",
      "icon": "devices"
    },
    {
      "title": "Bảo trì & Hỗ trợ",
      "subtitle": "Dễ dàng theo dõi tiến độ bảo trì và sửa chữa thiết bị.",
      "icon": "build"
    },
    {
      "title": "Báo cáo thống kê",
      "subtitle": "Quản lý doanh thu và hợp đồng nhanh chóng, chính xác.",
      "icon": "bar_chart"
    },
  ];

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      body: SafeArea(
        child: Column(
          children: [
            Expanded(
              child: PageView.builder(
                controller: _pageController,
                onPageChanged: (value) {
                  setState(() {
                    _currentPage = value;
                  });
                },
                itemCount: _onboardingData.length,
                itemBuilder: (context, index) {
                  final data = _onboardingData[index];
                  IconData iconData = Icons.devices;
                  if (data['icon'] == 'build') iconData = Icons.build;
                  if (data['icon'] == 'bar_chart') iconData = Icons.bar_chart;

                  return Padding(
                    padding: const EdgeInsets.all(40.0),
                    child: Column(
                      mainAxisAlignment: MainAxisAlignment.center,
                      children: [
                        Icon(iconData, size: 100, color: Colors.blue),
                        const SizedBox(height: 40),
                        Text(
                          data['title']!,
                          textAlign: TextAlign.center,
                          style: const TextStyle(fontSize: 24, fontWeight: FontWeight.bold),
                        ),
                        const SizedBox(height: 20),
                        Text(
                          data['subtitle']!,
                          textAlign: TextAlign.center,
                          style: const TextStyle(fontSize: 16, color: Colors.grey),
                        ),
                      ],
                    ),
                  );
                },
              ),
            ),
            Row(
              mainAxisAlignment: MainAxisAlignment.center,
              children: List.generate(
                _onboardingData.length,
                (index) => buildDot(index, context),
              ),
            ),
            Padding(
              padding: const EdgeInsets.all(40.0),
              child: ElevatedButton(
                style: ElevatedButton.styleFrom(
                  minimumSize: const Size(double.infinity, 50),
                ),
                onPressed: () {
                  if (_currentPage == _onboardingData.length - 1) {
                    Navigator.pushReplacementNamed(context, '/login');
                  } else {
                    _pageController.nextPage(
                      duration: const Duration(milliseconds: 300),
                      curve: Curves.easeIn,
                    );
                  }
                },
                child: Text(
                  _currentPage == _onboardingData.length - 1 ? "Bắt đầu" : "Tiếp tục",
                ),
              ),
            )
          ],
        ),
      ),
    );
  }

  Container buildDot(int index, BuildContext context) {
    return Container(
      height: 10,
      width: _currentPage == index ? 25 : 10,
      margin: const EdgeInsets.only(right: 5),
      decoration: BoxDecoration(
        borderRadius: BorderRadius.circular(20),
        color: _currentPage == index ? Colors.blue : Colors.grey.shade300,
      ),
    );
  }
}
"""
with open("lib/screens/onboarding/onboarding_screen.dart", "w", encoding="utf-8") as f:
    f.write(ui)

# Update splash screen to navigate to onboarding if not logged in
splash_path = "lib/screens/splash/splash_screen.dart"
with open(splash_path, "r", encoding="utf-8") as f:
    s_content = f.read()

s_content = s_content.replace(
    "Navigator.pushReplacementNamed(context, '/login');",
    "Navigator.pushReplacementNamed(context, '/onboarding');"
)
with open(splash_path, "w", encoding="utf-8") as f:
    f.write(s_content)

# Update AppRouter
router_path = "lib/routes/app_router.dart"
with open(router_path, "r", encoding="utf-8") as f:
    r_content = f.read()

if "/onboarding" not in r_content:
    r_content = r_content.replace(
        "import '../screens/splash/splash_screen.dart';",
        "import '../screens/splash/splash_screen.dart';\nimport '../screens/onboarding/onboarding_screen.dart';"
    )
    r_content = r_content.replace(
        "if (settings.name == '/') return const SplashScreen();",
        "if (settings.name == '/') return const SplashScreen();\n           if (settings.name == '/onboarding') return const OnboardingScreen();"
    )
    r_content = r_content.replace(
        "if (settings.name == '/' || settings.name == '/login')",
        "if (settings.name == '/' || settings.name == '/login' || settings.name == '/onboarding')"
    )
    with open(router_path, "w", encoding="utf-8") as f:
        f.write(r_content)
        
print("Onboarding created.")