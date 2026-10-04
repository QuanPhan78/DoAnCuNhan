import 'package:flutter/material.dart';
import '../../widgets/core/state_widgets.dart';

class TasksScreen extends StatelessWidget {
  const TasksScreen({super.key});
  @override
  Widget build(BuildContext context) {
    return const Scaffold(
      body: EmptyState(
        message: 'Hiện tại bạn không có công việc nào cần xử lý.',
        icon: Icons.task_alt_rounded,
      ),
    );
  }
}
