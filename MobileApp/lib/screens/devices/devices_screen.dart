import 'package:flutter/material.dart';
import 'package:provider/provider.dart';
import '../../providers/device_provider.dart';
import '../../widgets/device_card.dart';
import '../../widgets/core/state_widgets.dart';
import '../../widgets/core/custom_textfield.dart';
import '../../theme/app_colors.dart';
import '../../theme/app_text_styles.dart';
import '../../theme/app_radius.dart';

class DevicesScreen extends StatefulWidget {
  const DevicesScreen({super.key});

  @override
  State<DevicesScreen> createState() => _DevicesScreenState();
}

class _DevicesScreenState extends State<DevicesScreen> {
  final TextEditingController _searchController = TextEditingController();

  @override
  void initState() {
    super.initState();
    WidgetsBinding.instance.addPostFrameCallback((_) {
      context.read<DeviceProvider>().fetchDevices();
    });
  }

  @override
  void dispose() {
    _searchController.dispose();
    super.dispose();
  }

  @override
  Widget build(BuildContext context) {
    final provider = context.watch<DeviceProvider>();

    return Column(
      crossAxisAlignment: CrossAxisAlignment.stretch,
      children: [
        // Search bar
        Padding(
          padding: const EdgeInsets.fromLTRB(24, 24, 24, 16),
          child: CustomTextField(
            label: 'Tìm kiếm thiết bị',
            hint: 'Nhập tên, mã, loại thiết bị...',
            prefixIcon: Icons.search_rounded,
            controller: _searchController,
            onChanged: (value) => provider.search(value),
          ),
        ),
        
        // Filters
        SingleChildScrollView(
          scrollDirection: Axis.horizontal,
          padding: const EdgeInsets.symmetric(horizontal: 24),
          child: Row(
            children: [
              _buildFilterDropdown(
                hint: 'Phân loại',
                value: provider.selectedType,
                items: provider.availableTypes,
                onChanged: provider.setTypeFilter,
              ),
              const SizedBox(width: 12),
              _buildFilterDropdown(
                hint: 'Trạng thái',
                value: provider.selectedStatus,
                items: provider.availableStatuses,
                onChanged: provider.setStatusFilter,
              ),
              if (provider.selectedType != null || provider.selectedStatus != null)
                Padding(
                  padding: const EdgeInsets.only(left: 8.0),
                  child: TextButton.icon(
                    onPressed: () {
                      provider.setTypeFilter(null);
                      provider.setStatusFilter(null);
                      _searchController.clear();
                      provider.search('');
                    },
                    icon: const Icon(Icons.clear_all_rounded, size: 20),
                    label: const Text('Xóa bộ lọc'),
                  ),
                )
            ],
          ),
        ),
        const SizedBox(height: 16),

        // List
        Expanded(
          child: _buildListContent(provider),
        ),
      ],
    );
  }

  Widget _buildListContent(DeviceProvider provider) {
    if (provider.isLoading && provider.devices.isEmpty) {
      return const LoadingState(message: 'Đang tải danh sách thiết bị...');
    }

    if (provider.errorMessage != null) {
      return ErrorState(
        message: 'Đã xảy ra lỗi: ${provider.errorMessage}',
        onRetry: () => provider.fetchDevices(),
      );
    }

    if (provider.devices.isEmpty) {
      return const EmptyState(
        message: 'Không tìm thấy thiết bị nào phù hợp.',
        icon: Icons.devices_outlined,
      );
    }

    return RefreshIndicator(
      color: AppColors.primary,
      onRefresh: () => provider.fetchDevices(),
      child: ListView.builder(
        padding: const EdgeInsets.only(bottom: 24),
        physics: const AlwaysScrollableScrollPhysics(),
        itemCount: provider.devices.length,
        itemBuilder: (context, index) {
          final device = provider.devices[index];
          return DeviceCard(
            device: device,
            onTap: () {
              Navigator.of(context).pushNamed(
                '/device_detail', 
                arguments: device,
              );
            },
          );
        },
      ),
    );
  }

  Widget _buildFilterDropdown({
    required String hint,
    required String? value,
    required List<String> items,
    required Function(String?) onChanged,
  }) {
    return Container(
      padding: const EdgeInsets.symmetric(horizontal: 16, vertical: 4),
      decoration: BoxDecoration(
        color: value != null ? AppColors.primary.withValues(alpha: 0.1) : AppColors.surface,
        border: Border.all(
          color: value != null ? AppColors.primary : AppColors.divider,
        ),
        borderRadius: BorderRadius.circular(AppRadius.round),
      ),
      child: DropdownButtonHideUnderline(
        child: DropdownButton<String>(
          hint: Text(hint, style: AppTextStyles.bodySecondary),
          value: value,
          icon: Icon(
            Icons.keyboard_arrow_down_rounded, 
            size: 20,
            color: value != null ? AppColors.primary : AppColors.textSecondary,
          ),
          isDense: true,
          style: AppTextStyles.body.copyWith(
            color: value != null ? AppColors.primary : AppColors.textPrimary,
            fontWeight: value != null ? FontWeight.bold : FontWeight.normal,
          ),
          items: items.map((String item) {
            return DropdownMenuItem<String>(
              value: item,
              child: Text(item),
            );
          }).toList(),
          onChanged: onChanged,
        ),
      ),
    );
  }
}
