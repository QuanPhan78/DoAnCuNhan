import 'package:flutter/material.dart';
import 'package:provider/provider.dart';
import '../../models/role_enum.dart';
import '../../providers/auth_provider.dart';
import '../../providers/app_config_provider.dart';
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
  TaskFilter _staffTaskFilter = TaskFilter.all;

  List<Widget> _getScreens(Role role) {
    void handleSelectTab(int index, [int? subFilter]) {
      setState(() {
        _currentIndex = index;
        if (subFilter != null) {
          switch (subFilter) {
            case 1:
              _staffTaskFilter = TaskFilter.pending;
              break;
            case 2:
              _staffTaskFilter = TaskFilter.processing;
              break;
            case 3:
              _staffTaskFilter = TaskFilter.completed;
              break;
            default:
              _staffTaskFilter = TaskFilter.all;
              break;
          }
        }
      });
    }

    switch (role) {
      case Role.customer:
        return [
          HomeScreen(onSelectTab: handleSelectTab),
          const DevicesScreen(),
          const ContractsScreen(),
          const IncidentListScreen(),
          const AccountScreen(),
        ];
      case Role.staff:
        return [
          HomeScreen(onSelectTab: handleSelectTab),
          TasksScreen(initialFilter: _staffTaskFilter, isActive: _currentIndex == 1),
          const MaintenanceListScreen(),
          NotificationsScreen(isActive: _currentIndex == 3),
          const AccountScreen(),
        ];
      case Role.admin:
        return [
          HomeScreen(onSelectTab: handleSelectTab),
          const DevicesScreen(),
          const ContractsScreen(),
          const ReportsScreen(),
          const AccountScreen(),
        ];
    }
  }

  List<NavigationDestination> _getNavBarItems(Role role, AppConfigProvider config) {
    switch (role) {
      case Role.customer:
        return [
          NavigationDestination(icon: const Icon(Icons.home_outlined), selectedIcon: const Icon(Icons.home), label: config.tr('Trang chủ')),
          NavigationDestination(icon: const Icon(Icons.devices_outlined), selectedIcon: const Icon(Icons.devices), label: config.tr('Thiết bị')),
          NavigationDestination(icon: const Icon(Icons.description_outlined), selectedIcon: const Icon(Icons.description), label: config.tr('Hợp đồng')),
          NavigationDestination(icon: const Icon(Icons.support_agent_outlined), selectedIcon: const Icon(Icons.support_agent), label: config.tr('Yêu cầu')),
          NavigationDestination(icon: const Icon(Icons.person_outline), selectedIcon: const Icon(Icons.person), label: config.tr('Tài khoản')),
        ];
      case Role.staff:
        return [
          NavigationDestination(icon: const Icon(Icons.home_outlined), selectedIcon: const Icon(Icons.home), label: config.tr('Trang chủ')),
          NavigationDestination(icon: const Icon(Icons.work_outline), selectedIcon: const Icon(Icons.work), label: config.tr('Công việc')),
          NavigationDestination(icon: const Icon(Icons.build_outlined), selectedIcon: const Icon(Icons.build), label: config.tr('Bảo trì')),
          NavigationDestination(icon: const Icon(Icons.notifications_outlined), selectedIcon: const Icon(Icons.notifications), label: config.tr('Thông báo')),
          NavigationDestination(icon: const Icon(Icons.person_outline), selectedIcon: const Icon(Icons.person), label: config.tr('Tài khoản')),
        ];
      case Role.admin:
        return [
          NavigationDestination(icon: const Icon(Icons.home_outlined), selectedIcon: const Icon(Icons.home), label: config.tr('Trang chủ')),
          NavigationDestination(icon: const Icon(Icons.devices_outlined), selectedIcon: const Icon(Icons.devices), label: config.tr('Thiết bị')),
          NavigationDestination(icon: const Icon(Icons.description_outlined), selectedIcon: const Icon(Icons.description), label: config.tr('Hợp đồng')),
          NavigationDestination(icon: const Icon(Icons.bar_chart_outlined), selectedIcon: const Icon(Icons.bar_chart), label: config.tr('Báo cáo')),
          NavigationDestination(icon: const Icon(Icons.person_outline), selectedIcon: const Icon(Icons.person), label: config.tr('Tài khoản')),
        ];
    }
  }

  String _getAppBarTitle(int index, Role role, AppConfigProvider config) {
    if (index == 0) return config.tr('Hệ Thống Quản Lý');
    final items = _getNavBarItems(role, config);
    if (index < items.length) {
      return items[index].label;
    }
    return config.tr('Hệ Thống Quản Lý');
  }

  @override
  Widget build(BuildContext context) {
    final user = context.watch<AuthProvider>().currentUser;
    final config = context.watch<AppConfigProvider>();

    if (user == null) {
      return const Scaffold(body: Center(child: CircularProgressIndicator()));
    }
    
    final screens = _getScreens(user.role);
    final items = _getNavBarItems(user.role, config);
    final title = _getAppBarTitle(_currentIndex, user.role, config);

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
