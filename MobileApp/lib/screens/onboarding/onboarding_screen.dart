import 'package:flutter/material.dart';
import '../../theme/app_colors.dart';
import '../../theme/app_text_styles.dart';
import '../../theme/app_radius.dart';
import '../../widgets/core/custom_button.dart';

class OnboardingScreen extends StatefulWidget {
  const OnboardingScreen({super.key});

  @override
  State<OnboardingScreen> createState() => _OnboardingScreenState();
}

class _OnboardingScreenState extends State<OnboardingScreen> {
  final PageController _pageController = PageController();
  int _currentPage = 0;

  final List<Map<String, dynamic>> _pages = [
    {
      "title": "Quản lý thiết bị điện tử",
      "subtitle": "Theo dõi và kiểm soát toàn bộ danh mục thiết bị cho thuê một cách trực quan, chính xác và hiệu quả nhất.",
      "icon": Icons.devices_rounded,
      "color": Color(0xFF3B82F6),
    },
    {
      "title": "Quản lý hợp đồng",
      "subtitle": "Dễ dàng nắm bắt tình trạng hợp đồng, gia hạn tự động và tối ưu hóa quy trình bàn giao cho khách hàng.",
      "icon": Icons.assignment_rounded,
      "color": Color(0xFF10B981),
    },
    {
      "title": "Bảo trì và hỗ trợ",
      "subtitle": "Phản hồi sự cố nhanh chóng, điều phối nhân viên sửa chữa và đảm bảo thiết bị luôn trong trạng thái tốt nhất.",
      "icon": Icons.build_circle_rounded,
      "color": Color(0xFFF59E0B),
    },
  ];

  void _onSkipOrStart() {
    Navigator.pushReplacementNamed(context, '/login');
  }

  void _onNext() {
    if (_currentPage < _pages.length - 1) {
      _pageController.nextPage(
        duration: const Duration(milliseconds: 300),
        curve: Curves.easeInOutCubic,
      );
    }
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      backgroundColor: AppColors.background,
      appBar: AppBar(
        backgroundColor: Colors.transparent,
        elevation: 0,
        actions: [
          if (_currentPage < _pages.length - 1)
            TextButton(
              onPressed: _onSkipOrStart,
              child: Text("Bỏ qua", style: AppTextStyles.button.copyWith(color: AppColors.textSecondary)),
            ),
          const SizedBox(width: 8),
        ],
      ),
      body: Column(
        children: [
          Expanded(
            child: PageView.builder(
              controller: _pageController,
              onPageChanged: (idx) => setState(() => _currentPage = idx),
              itemCount: _pages.length,
              itemBuilder: (context, index) {
                final page = _pages[index];
                return Padding(
                  padding: const EdgeInsets.symmetric(horizontal: 32.0),
                  child: Column(
                    mainAxisAlignment: MainAxisAlignment.center,
                    children: [
                      Container(
                        padding: const EdgeInsets.all(40),
                        decoration: BoxDecoration(
                          color: page['color'].withValues(alpha: 0.1),
                          shape: BoxShape.circle,
                        ),
                        child: Icon(page['icon'], size: 100, color: page['color']),
                      ),
                      const SizedBox(height: 48),
                      Text(
                        page['title'],
                        textAlign: TextAlign.center,
                        style: AppTextStyles.h1,
                      ),
                      const SizedBox(height: 16),
                      Text(
                        page['subtitle'],
                        textAlign: TextAlign.center,
                        style: AppTextStyles.bodySecondary.copyWith(height: 1.5),
                      ),
                    ],
                  ),
                );
              },
            ),
          ),
          
          // Bottom Controls
          Padding(
            padding: const EdgeInsets.all(32.0),
            child: Column(
              children: [
                Row(
                  mainAxisAlignment: MainAxisAlignment.center,
                  children: List.generate(
                    _pages.length,
                    (index) => AnimatedContainer(
                      duration: const Duration(milliseconds: 300),
                      margin: const EdgeInsets.symmetric(horizontal: 4),
                      height: 8,
                      width: _currentPage == index ? 24 : 8,
                      decoration: BoxDecoration(
                        color: _currentPage == index ? AppColors.primary : AppColors.divider,
                        borderRadius: BorderRadius.circular(AppRadius.round),
                      ),
                    ),
                  ),
                ),
                const SizedBox(height: 32),
                CustomButton(
                  text: _currentPage == _pages.length - 1 ? "Bắt đầu sử dụng" : "Tiếp tục",
                  isFullWidth: true,
                  onPressed: _currentPage == _pages.length - 1 ? _onSkipOrStart : _onNext,
                ),
              ],
            ),
          )
        ],
      ),
    );
  }
}
