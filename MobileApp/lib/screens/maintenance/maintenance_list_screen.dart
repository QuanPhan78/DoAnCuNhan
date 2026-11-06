import 'package:flutter/material.dart';
import 'package:provider/provider.dart';
import '../../providers/auth_provider.dart';
import '../../providers/maintenance_provider.dart';
import '../../widgets/maintenance_card.dart';
import '../../widgets/core/state_widgets.dart';
import '../../widgets/core/custom_app_bar.dart';
import '../../theme/app_colors.dart';

class MaintenanceListScreen extends StatefulWidget {
  const MaintenanceListScreen({super.key});

  @override
  State<MaintenanceListScreen> createState() => _MaintenanceListScreenState();
}

class _MaintenanceListScreenState extends State<MaintenanceListScreen> {
  @override
  void initState() {
    super.initState();
    WidgetsBinding.instance.addPostFrameCallback((_) {
      _loadData();
    });
  }

  Future<void> _loadData() async {
    final user = context.read<AuthProvider>().currentUser;
    if (user != null) {
      await context.read<MaintenanceProvider>().fetchMaintenances(user.id, user.role, user.name);
    }
  }

  @override
  Widget build(BuildContext context) {
    final provider = context.watch<MaintenanceProvider>();

    return Scaffold(
      backgroundColor: AppColors.background,
      appBar: const CustomAppBar(title: 'Bảo trì & Sửa chữa'),
      body: _buildContent(provider),
    );
  }

  Widget _buildContent(MaintenanceProvider provider) {
    if (provider.isLoading && provider.maintenances.isEmpty) {
      return const LoadingState(message: 'Đang tải danh sách bảo trì...');
    }
    if (provider.errorMessage != null) {
      return ErrorState(message: 'Lỗi: ${provider.errorMessage}', onRetry: _loadData);
    }
    return RefreshIndicator(
      color: AppColors.primary,
      onRefresh: _loadData,
      child: provider.maintenances.isEmpty
          ? ListView(
              physics: const AlwaysScrollableScrollPhysics(),
              children: const [EmptyState(message: 'Không có yêu cầu bảo trì nào.', icon: Icons.build_circle_outlined)],
            )
          : ListView.builder(
        physics: const AlwaysScrollableScrollPhysics(),
        padding: const EdgeInsets.symmetric(horizontal: 24, vertical: 16),
        itemCount: provider.maintenances.length,
        itemBuilder: (context, index) {
          final m = provider.maintenances[index];
          return MaintenanceCard(
            maintenance: m,
            onTap: () async {
              await Navigator.pushNamed(context, '/maintenance_detail', arguments: m);
              _loadData();
            },
          );
        },
      ),
    );
  }
}
