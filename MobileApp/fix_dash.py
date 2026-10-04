import os

dash_code = """import 'package:flutter/material.dart';
import 'package:provider/provider.dart';
import '../../models/role_enum.dart';
import '../../providers/auth_provider.dart';
import '../../widgets/core/fade_indexed_stack.dart';
import '../../widgets/core/custom_app_bar.dart';
import '../home/home_screen.dart';
import '../devices/devices_screen.dart';
import '../contracts/contracts_screen.dart';
import '../incidents/incident_list_screen.dart';
import '../account/account_screen.dart';
import '../tasks/tasks_screen.dart';
import '../maintenance/maintenance_list_screen.dart';
import '../notifications/notifications_screen.dart';
import '../reports/reports_screen.dart';

class DashboardScreen extends StatefulWidget {
  const DashboardScreen({super.key});
  @override
  State<DashboardScreen> createState() => _DashboardScreenState();
}

class _DashboardScreenState extends State<DashboardScreen> {
  int _currentIndex = 0;

  List<Widget> _getScreens(Role role) {
    switch (role) {
      case Role.customer:
        return const [HomeScreen(), DevicesScreen(), ContractsScreen(), IncidentListScreen(), AccountScreen()];
      case Role.staff:
        return const [HomeScreen(), TasksScreen(), MaintenanceListScreen(), NotificationsScreen(), AccountScreen()];
      case Role.admin:
        return const [HomeScreen(), DevicesScreen(), ContractsScreen(), ReportsScreen(), AccountScreen()];
    }
  }

  List<NavigationDestination> _getNavBarItems(Role role) {
    switch (role) {
      case Role.customer:
        return const [
          NavigationDestination(icon: Icon(Icons.home_outlined), selectedIcon: Icon(Icons.home), label: 'Trang chủ'),
          NavigationDestination(icon: Icon(Icons.devices_outlined), selectedIcon: Icon(Icons.devices), label: 'Thiết bị'),
          NavigationDestination(icon: Icon(Icons.description_outlined), selectedIcon: Icon(Icons.description), label: 'Hợp đồng'),
          NavigationDestination(icon: Icon(Icons.support_agent_outlined), selectedIcon: Icon(Icons.support_agent), label: 'Yêu cầu'),
          NavigationDestination(icon: Icon(Icons.person_outline), selectedIcon: Icon(Icons.person), label: 'Tài khoản'),
        ];
      case Role.staff:
        return const [
          NavigationDestination(icon: Icon(Icons.home_outlined), selectedIcon: Icon(Icons.home), label: 'Trang chủ'),
          NavigationDestination(icon: Icon(Icons.work_outline), selectedIcon: Icon(Icons.work), label: 'Công việc'),
          NavigationDestination(icon: Icon(Icons.build_outlined), selectedIcon: Icon(Icons.build), label: 'Bảo trì'),
          NavigationDestination(icon: Icon(Icons.notifications_outlined), selectedIcon: Icon(Icons.notifications), label: 'Thông báo'),
          NavigationDestination(icon: Icon(Icons.person_outline), selectedIcon: Icon(Icons.person), label: 'Tài khoản'),
        ];
      case Role.admin:
        return const [
          NavigationDestination(icon: Icon(Icons.home_outlined), selectedIcon: Icon(Icons.home), label: 'Trang chủ'),
          NavigationDestination(icon: Icon(Icons.devices_outlined), selectedIcon: Icon(Icons.devices), label: 'Thiết bị'),
          NavigationDestination(icon: Icon(Icons.description_outlined), selectedIcon: Icon(Icons.description), label: 'Hợp đồng'),
          NavigationDestination(icon: Icon(Icons.bar_chart_outlined), selectedIcon: Icon(Icons.bar_chart), label: 'Báo cáo'),
          NavigationDestination(icon: Icon(Icons.person_outline), selectedIcon: Icon(Icons.person), label: 'Tài khoản'),
        ];
    }
  }

  String _getAppBarTitle(int index, Role role) {
    if (index == 0) return 'Hệ Thống Quản Lý';
    final items = _getNavBarItems(role);
    if (index < items.length) {
      return items[index].label;
    }
    return 'Hệ Thống Quản Lý';
  }

  @override
  Widget build(BuildContext context) {
    final user = context.watch<AuthProvider>().currentUser;
    if (user == null) {
      return const Scaffold(body: Center(child: CircularProgressIndicator()));
    }
    
    final screens = _getScreens(user.role);
    final items = _getNavBarItems(user.role);
    final title = _getAppBarTitle(_currentIndex, user.role);

    return Scaffold(
      appBar: CustomAppBar(
        title: title,
        actions: [
          IconButton(
            icon: const Icon(Icons.search_rounded),
            onPressed: () => Navigator.pushNamed(context, '/search'),
          ),
          const SizedBox(width: 8),
        ],
      ),
      body: FadeIndexedStack(
        index: _currentIndex,
        children: screens,
      ),
      bottomNavigationBar: NavigationBar(
        selectedIndex: _currentIndex,
        onDestinationSelected: (index) => setState(() => _currentIndex = index),
        destinations: items,
      ),
    );
  }
}
"""

with open("lib/screens/dashboard/dashboard_screen.dart", "w", encoding="utf-8") as f:
    f.write(dash_code)

print("Dashboard Screen Fixed.")