import 'package:flutter/material.dart';
import '../../widgets/core/state_widgets.dart';

class NotificationsScreen extends StatelessWidget {
  const NotificationsScreen({super.key});
  @override
  Widget build(BuildContext context) {
    return const Scaffold(
      body: EmptyState(
        message: 'Bạn chưa có thông báo mới.',
        icon: Icons.notifications_none_rounded,
      ),
    );
  }
}
