import 'package:flutter/material.dart';
import 'package:provider/provider.dart';
import '../../models/contract_model.dart';
import '../../models/installation_model.dart';
import '../../models/maintenance_model.dart';
import '../../providers/auth_provider.dart';
import '../../providers/contract_provider.dart';
import '../../providers/maintenance_provider.dart';
import '../../datasources/installation/local_installation_datasource.dart';
import '../../repositories/installation_repository.dart';
import '../../theme/app_colors.dart';
import '../../theme/app_text_styles.dart';
import '../../theme/app_radius.dart';
import '../../theme/app_shadows.dart';
import '../../widgets/dashboard_widgets.dart';
import '../../widgets/core/state_widgets.dart';

enum TaskFilter { all, pending, processing, completed }

class StaffTaskItem {
  final String id;
  final String title;
  final String code;
  final String description;
  final String customer;
  final String date;
  final String status;
  final bool isInstallation;
  final ContractModel? contract;
  final InstallationModel? installation;
  final MaintenanceModel? maintenance;

  StaffTaskItem({
    required this.id,
    required this.title,
    required this.code,
    required this.description,
    required this.customer,
    required this.date,
    required this.status,
    required this.isInstallation,
    this.contract,
    this.installation,
    this.maintenance,
  });

  TaskFilter get category {
    final s = status.toLowerCase();
    if (s.contains('hoàn thành')) return TaskFilter.completed;
    if (s.contains('đang thực hiện') || s.contains('đang xử lý')) return TaskFilter.processing;
    return TaskFilter.pending;
  }
}

class TasksScreen extends StatefulWidget {
  final TaskFilter initialFilter;
  const TasksScreen({super.key, this.initialFilter = TaskFilter.all});

  @override
  State<TasksScreen> createState() => TasksScreenState();
}

class TasksScreenState extends State<TasksScreen> {
  final InstallationRepository _installationRepo = InstallationRepository(LocalInstallationDataSource());
  final TextEditingController _searchController = TextEditingController();

  late TaskFilter _selectedFilter;
  bool _isLoading = true;
  String? _errorMessage;
  List<StaffTaskItem> _allTasks = [];
  String _searchQuery = '';

  @override
  void initState() {
    super.initState();
    _selectedFilter = widget.initialFilter;
    WidgetsBinding.instance.addPostFrameCallback((_) {
      loadTasks();
    });
  }

  @override
  void didUpdateWidget(TasksScreen oldWidget) {
    super.didUpdateWidget(oldWidget);
    if (oldWidget.initialFilter != widget.initialFilter) {
      setState(() {
        _selectedFilter = widget.initialFilter;
      });
    }
  }

  void setFilter(TaskFilter filter) {
    setState(() {
      _selectedFilter = filter;
    });
  }

  Future<void> loadTasks() async {
    setState(() {
      _isLoading = true;
      _errorMessage = null;
    });

    try {
      final user = context.read<AuthProvider>().currentUser;
      if (user == null) return;

      final contractProvider = context.read<ContractProvider>();
      final maintenanceProvider = context.read<MaintenanceProvider>();

      await Future.wait([
        contractProvider.fetchContracts(user.role, user.id),
        maintenanceProvider.fetchMaintenances(user.id, user.role, user.name),
      ]);

      final List<StaffTaskItem> items = [];

      // 1. Công việc Lắp đặt từ hợp đồng
      for (final contract in contractProvider.contracts) {
        final install = await _installationRepo.getInstallationByContractId(contract.id);
        if (install != null) {
          items.add(StaffTaskItem(
            id: 'INST_${contract.id}',
            title: 'Lắp đặt thiết bị',
            code: contract.contractCode ?? contract.id,
            description: install.notes?.isNotEmpty == true ? install.notes! : (contract.installationDetails ?? 'Lắp đặt bàn giao thiết bị'),
            customer: contract.customerName ?? 'Khách hàng',
            date: install.expectedDate ?? contract.rentalStart ?? '---',
            status: install.status,
            isInstallation: true,
            contract: contract,
            installation: install,
          ));
        }
      }

      // 2. Công việc Bảo trì
      for (final m in maintenanceProvider.maintenances) {
        items.add(StaffTaskItem(
          id: 'MAINT_${m.id}',
          title: 'Bảo trì & Sửa chữa',
          code: m.requestCode ?? m.id,
          description: m.description ?? 'Kiểm tra và sửa chữa thiết bị',
          customer: m.customer ?? 'Khách hàng',
          date: m.createdAt ?? '---',
          status: m.status ?? 'Chờ tiếp nhận',
          isInstallation: false,
          maintenance: m,
        ));
      }

      if (mounted) {
        setState(() {
          _allTasks = items;
          _isLoading = false;
        });
      }
    } catch (e) {
      if (mounted) {
        setState(() {
          _errorMessage = e.toString();
          _isLoading = false;
        });
      }
    }
  }

  List<StaffTaskItem> get _filteredTasks {
    return _allTasks.where((task) {
      if (_selectedFilter != TaskFilter.all && task.category != _selectedFilter) {
        return false;
      }
      if (_searchQuery.isNotEmpty) {
        final query = _searchQuery.toLowerCase();
        final matchCode = task.code.toLowerCase().contains(query);
        final matchTitle = task.title.toLowerCase().contains(query);
        final matchCustomer = task.customer.toLowerCase().contains(query);
        final matchDesc = task.description.toLowerCase().contains(query);
        return matchCode || matchTitle || matchCustomer || matchDesc;
      }
      return true;
    }).toList();
  }

  BadgeStatus _getBadgeStatus(String status) {
    final s = status.toLowerCase();
    if (s.contains('hoàn thành')) return BadgeStatus.success;
    if (s.contains('đang thực hiện') || s.contains('đang xử lý')) return BadgeStatus.processing;
    if (s.contains('tiếp nhận') || s.contains('bắt đầu')) return BadgeStatus.warning;
    return BadgeStatus.neutral;
  }

  @override
  void dispose() {
    _searchController.dispose();
    super.dispose();
  }

  @override
  Widget build(BuildContext context) {
    return Column(
      crossAxisAlignment: CrossAxisAlignment.stretch,
      children: [
        // Thanh tìm kiếm
        Padding(
          padding: const EdgeInsets.fromLTRB(24, 20, 24, 12),
          child: TextField(
            controller: _searchController,
            onChanged: (val) => setState(() => _searchQuery = val.trim()),
            decoration: InputDecoration(
              hintText: 'Tìm theo mã, khách hàng, nội dung...',
              prefixIcon: const Icon(Icons.search_rounded, color: AppColors.textSecondary),
              suffixIcon: _searchQuery.isNotEmpty
                  ? IconButton(
                      icon: const Icon(Icons.clear_rounded, size: 20),
                      onPressed: () {
                        _searchController.clear();
                        setState(() => _searchQuery = '');
                      },
                    )
                  : null,
              filled: true,
              fillColor: AppColors.surface,
              contentPadding: const EdgeInsets.symmetric(horizontal: 16, vertical: 12),
              border: OutlineInputBorder(
                borderRadius: AppRadius.mdRadius,
                borderSide: const BorderSide(color: AppColors.divider),
              ),
              enabledBorder: OutlineInputBorder(
                borderRadius: AppRadius.mdRadius,
                borderSide: const BorderSide(color: AppColors.divider),
              ),
              focusedBorder: OutlineInputBorder(
                borderRadius: AppRadius.mdRadius,
                borderSide: const BorderSide(color: AppColors.primary, width: 1.5),
              ),
            ),
          ),
        ),

        // Thanh chọn lọc theo trạng thái
        SingleChildScrollView(
          scrollDirection: Axis.horizontal,
          padding: const EdgeInsets.symmetric(horizontal: 24),
          child: Row(
            children: [
              _buildFilterChip('Tất cả', TaskFilter.all),
              const SizedBox(width: 8),
              _buildFilterChip('Đang chờ', TaskFilter.pending),
              const SizedBox(width: 8),
              _buildFilterChip('Đang xử lý', TaskFilter.processing),
              const SizedBox(width: 8),
              _buildFilterChip('Hoàn thành', TaskFilter.completed),
            ],
          ),
        ),
        const SizedBox(height: 12),

        // Danh sách công việc
        Expanded(
          child: _buildTaskList(),
        ),
      ],
    );
  }

  Widget _buildFilterChip(String label, TaskFilter filter) {
    final isSelected = _selectedFilter == filter;
    return ChoiceChip(
      label: Text(label),
      selected: isSelected,
      onSelected: (_) => setFilter(filter),
      selectedColor: AppColors.primary,
      backgroundColor: AppColors.surface,
      labelStyle: TextStyle(
        color: isSelected ? Colors.white : AppColors.textPrimary,
        fontWeight: isSelected ? FontWeight.bold : FontWeight.normal,
        fontSize: 13,
      ),
      shape: RoundedRectangleBorder(
        borderRadius: AppRadius.xlRadius,
        side: BorderSide(
          color: isSelected ? AppColors.primary : AppColors.divider,
        ),
      ),
    );
  }

  Widget _buildTaskList() {
    if (_isLoading) {
      return const LoadingState(message: 'Đang tải danh sách công việc...');
    }

    if (_errorMessage != null) {
      return ErrorState(message: 'Lỗi: $_errorMessage', onRetry: loadTasks);
    }

    final tasks = _filteredTasks;
    if (tasks.isEmpty) {
      return const EmptyState(
        message: 'Không tìm thấy công việc nào phù hợp.',
        icon: Icons.task_alt_rounded,
      );
    }

    return RefreshIndicator(
      color: AppColors.primary,
      onRefresh: loadTasks,
      child: ListView.builder(
        padding: const EdgeInsets.symmetric(horizontal: 24, vertical: 8),
        itemCount: tasks.length,
        itemBuilder: (context, index) {
          final item = tasks[index];
          return _buildTaskCard(item);
        },
      ),
    );
  }

  Widget _buildTaskCard(StaffTaskItem item) {
    return Container(
      margin: const EdgeInsets.only(bottom: 14),
      decoration: BoxDecoration(
        color: AppColors.surface,
        borderRadius: AppRadius.lgRadius,
        boxShadow: AppShadows.cardShadow,
        border: Border.all(color: AppColors.divider),
      ),
      child: Material(
        color: Colors.transparent,
        child: InkWell(
          borderRadius: AppRadius.lgRadius,
          onTap: () async {
            if (item.isInstallation && item.contract != null) {
              await Navigator.pushNamed(context, '/contract_detail', arguments: item.contract);
              loadTasks();
            } else if (!item.isInstallation && item.maintenance != null) {
              await Navigator.pushNamed(context, '/maintenance_detail', arguments: item.maintenance);
              loadTasks();
            }
          },
          child: Padding(
            padding: const EdgeInsets.all(16),
            child: Column(
              crossAxisAlignment: CrossAxisAlignment.start,
              children: [
                // Hàng tiêu đề & Loại công việc & Trạng thái
                Row(
                  crossAxisAlignment: CrossAxisAlignment.center,
                  children: [
                    Container(
                      padding: const EdgeInsets.all(8),
                      decoration: BoxDecoration(
                        color: (item.isInstallation ? AppColors.primary : AppColors.warning).withValues(alpha: 0.12),
                        borderRadius: AppRadius.smRadius,
                      ),
                      child: Icon(
                        item.isInstallation ? Icons.build_rounded : Icons.handyman_rounded,
                        color: item.isInstallation ? AppColors.primary : AppColors.warning,
                        size: 20,
                      ),
                    ),
                    const SizedBox(width: 10),
                    Expanded(
                      child: Column(
                        crossAxisAlignment: CrossAxisAlignment.start,
                        children: [
                          Text(
                            item.title,
                            style: AppTextStyles.subtitle.copyWith(fontSize: 15, fontWeight: FontWeight.bold),
                          ),
                          Text(
                            'Mã: ${item.code}',
                            style: AppTextStyles.bodySecondary.copyWith(fontSize: 12),
                          ),
                        ],
                      ),
                    ),
                    StatusBadge(
                      text: item.status,
                      status: _getBadgeStatus(item.status),
                    ),
                  ],
                ),
                const SizedBox(height: 12),

                // Mô tả công việc
                Text(
                  item.description,
                  style: AppTextStyles.body.copyWith(fontSize: 14, height: 1.4),
                  maxLines: 2,
                  overflow: TextOverflow.ellipsis,
                ),
                const SizedBox(height: 12),
                const Divider(height: 1, color: AppColors.divider),
                const SizedBox(height: 12),

                // Thông tin phụ: Khách hàng, Thời gian, mũi tên
                Row(
                  children: [
                    const Icon(Icons.person_outline, size: 16, color: AppColors.textSecondary),
                    const SizedBox(width: 4),
                    Expanded(
                      child: Text(
                        item.customer,
                        style: AppTextStyles.caption.copyWith(color: AppColors.textSecondary),
                        overflow: TextOverflow.ellipsis,
                      ),
                    ),
                    const Icon(Icons.calendar_today_outlined, size: 14, color: AppColors.textSecondary),
                    const SizedBox(width: 4),
                    Text(
                      item.date,
                      style: AppTextStyles.caption.copyWith(color: AppColors.textSecondary),
                    ),
                    const SizedBox(width: 8),
                    const Icon(Icons.arrow_forward_ios_rounded, size: 14, color: AppColors.primary),
                  ],
                ),
              ],
            ),
          ),
        ),
      ),
    );
  }
}
