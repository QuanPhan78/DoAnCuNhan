import 'package:flutter/material.dart';
import 'package:provider/provider.dart';
import 'package:intl/intl.dart';
import '../../services/staff_task_service.dart';
import '../../models/maintenance_model.dart';
import '../../providers/auth_provider.dart';
import '../../providers/maintenance_provider.dart';
import '../../theme/app_colors.dart';
import '../../theme/app_text_styles.dart';
import '../../theme/app_radius.dart';
import '../../theme/app_shadows.dart';
import '../../widgets/dashboard_widgets.dart';
import '../../widgets/core/state_widgets.dart';

enum TaskFilter { all, pending, processing, completed, cancelled }

class StaffTaskItem {
  final String title;
  final String code;
  final String description;
  final String customer;
  final String date;
  final String status;
  final ManualTask? manual;
  final MaintenanceModel? maintenance;

  StaffTaskItem({
    required this.title,
    required this.code,
    required this.description,
    required this.customer,
    required this.date,
    required this.status,
    this.manual,
    this.maintenance,
  });

  TaskFilter get category {
    final code = maintenance?.statusCode;
    if (code == 4 || code == 5) return TaskFilter.completed;
    if (code == 2 || code == 3) return TaskFilter.processing;
    return switch (manual?.statusCode) {
      1 => TaskFilter.processing,
      2 => TaskFilter.completed,
      3 => TaskFilter.cancelled,
      _ => TaskFilter.pending,
    };
  }
}

class TasksScreen extends StatefulWidget {
  final TaskFilter initialFilter;
  final bool isActive;
  const TasksScreen({super.key, this.initialFilter = TaskFilter.all, this.isActive = true});

  @override
  State<TasksScreen> createState() => TasksScreenState();
}

class TasksScreenState extends State<TasksScreen> {
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
      if (widget.isActive) loadTasks();
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
    if (widget.isActive && !oldWidget.isActive) {
      WidgetsBinding.instance.addPostFrameCallback((_) => loadTasks());
    }
  }

  void setFilter(TaskFilter filter) {
    setState(() {
      _selectedFilter = filter;
    });
  }

  Future<void> loadTasks() async {
    if (!mounted) return;
    setState(() {
      _isLoading = true;
      _errorMessage = null;
    });

    try {
      final user = context.read<AuthProvider>().currentUser;
      if (user == null) throw Exception('Vui lòng đăng nhập lại.');

      final maintenanceProvider = context.read<MaintenanceProvider>();
      final (manual, _) = await (
        StaffTaskService.list(),
        maintenanceProvider.fetchMaintenances(user.id, user.role, user.name),
      ).wait;
      if (maintenanceProvider.errorMessage != null) {
        throw Exception(maintenanceProvider.errorMessage);
      }

      final dateFormat = DateFormat('dd/MM/yyyy');
      final items = manual.map((task) => StaffTaskItem(
        title: task.title,
        code: '#${task.id}',
        description: task.description,
        customer: task.customer ?? 'Công việc nội bộ',
        date: dateFormat.format(task.dueAt ?? task.assignedAt),
        status: task.status,
        manual: task,
      )).toList();

      // 2. Công việc Bảo trì
      for (final m in maintenanceProvider.maintenances.where((ticket) => ticket.assignedStaffId == user.id)) {
        items.add(StaffTaskItem(
          title: 'Bảo trì & Sửa chữa',
          code: m.requestCode ?? m.id,
          description: m.description ?? 'Kiểm tra và sửa chữa thiết bị',
          customer: m.customer ?? 'Khách hàng',
          date: m.createdAt ?? '---',
          status: m.statusCode == 1 ? 'Mới giao' : m.status ?? 'Chờ tiếp nhận',
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
          _errorMessage = e.toString().replaceFirst('Exception: ', '');
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
    if (s.contains('hoàn thành') || s.contains('đã nghiệm thu')) return BadgeStatus.success;
    if (s.contains('đang thực hiện') || s.contains('đang xử lý') || s.contains('chờ nghiệm thu')) return BadgeStatus.processing;
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
              const SizedBox(width: 8),
              _buildFilterChip('Đã hủy', TaskFilter.cancelled),
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
    return RefreshIndicator(
      color: AppColors.primary,
      onRefresh: loadTasks,
      child: tasks.isEmpty
          ? ListView(
              physics: const AlwaysScrollableScrollPhysics(),
              children: const [EmptyState(
                message: 'Không tìm thấy công việc nào phù hợp.',
                icon: Icons.task_alt_rounded,
              )],
            )
          : ListView.builder(
        physics: const AlwaysScrollableScrollPhysics(),
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
            if (item.manual case final task?) {
              final updated = await showDialog<bool>(
                context: context, builder: (_) => _ManualTaskDialog(task: task),
              );
              if (updated == true) await loadTasks();
            } else if (item.maintenance != null) {
              await Navigator.pushNamed(context, '/maintenance_detail', arguments: item.maintenance);
              await loadTasks();
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
                        color: (item.manual != null ? AppColors.primary : AppColors.warning).withValues(alpha: 0.12),
                        borderRadius: AppRadius.smRadius,
                      ),
                      child: Icon(
                        item.manual != null ? Icons.assignment_outlined : Icons.handyman_rounded,
                        color: item.manual != null ? AppColors.primary : AppColors.warning,
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


class _ManualTaskDialog extends StatefulWidget {
  const _ManualTaskDialog({required this.task});
  final ManualTask task;

  @override
  State<_ManualTaskDialog> createState() => _ManualTaskDialogState();
}

class _ManualTaskDialogState extends State<_ManualTaskDialog> {
  late int _status = widget.task.statusCode;
  late final _notes = TextEditingController(text: widget.task.notes);
  bool _saving = false;
  String? _error;

  @override
  void dispose() {
    _notes.dispose();
    super.dispose();
  }

  Future<void> _save() async {
    setState(() {
      _saving = true;
      _error = null;
    });
    try {
      await StaffTaskService.update(widget.task.id, _status, notes: _notes.text);
      if (mounted) Navigator.pop(context, true);
    } catch (error) {
      if (!mounted) return;
      setState(() {
        _error = error.toString().replaceFirst('Exception: ', '');
        _saving = false;
      });
    }
  }

  @override
  Widget build(BuildContext context) {
    final task = widget.task;
    return AlertDialog(
      title: Text(task.title),
      scrollable: true,
      content: Column(crossAxisAlignment: CrossAxisAlignment.start, mainAxisSize: MainAxisSize.min, children: [
        Text(task.description),
        if (task.contractId != null) Text('Hợp đồng #${task.contractId}'),
        if (task.ticketId != null) Text('Phiếu bảo trì #${task.ticketId}'),
        if (task.dueAt != null) Text('Hạn ${DateFormat('dd/MM/yyyy HH:mm').format(task.dueAt!)}'),
        if (task.completedAt != null)
          Text('Hoàn thành ${DateFormat('dd/MM/yyyy HH:mm').format(task.completedAt!)}'),
        const SizedBox(height: 16),
        DropdownButtonFormField<int>(
          initialValue: _status >= 0 && _status <= 3 ? _status : null,
          decoration: const InputDecoration(labelText: 'Trạng thái'),
          items: const [
            DropdownMenuItem(value: 0, child: Text('Mới')),
            DropdownMenuItem(value: 1, child: Text('Đang thực hiện')),
            DropdownMenuItem(value: 2, child: Text('Hoàn thành')),
            DropdownMenuItem(value: 3, child: Text('Đã hủy')),
          ],
          onChanged: _saving ? null : (value) => setState(() => _status = value!),
        ),
        const SizedBox(height: 12),
        TextField(controller: _notes, enabled: !_saving, maxLines: 3,
          decoration: const InputDecoration(labelText: 'Ghi chú tiến độ')),
        if (_error != null) Text(_error!, style: const TextStyle(color: AppColors.error)),
      ]),
      actions: [
        TextButton(onPressed: _saving ? null : () => Navigator.pop(context), child: const Text('Đóng')),
        FilledButton(onPressed: _saving || _status < 0 || _status > 3 ? null : _save,
          child: Text(_saving ? 'Đang lưu' : 'Lưu')),
      ],
    );
  }
}
