import os

code = """import 'package:flutter/material.dart';
import 'package:provider/provider.dart';
import '../../providers/auth_provider.dart';
import '../../providers/contract_provider.dart';
import '../../widgets/contract_card.dart';
import '../../widgets/core/state_widgets.dart';
import '../../widgets/core/custom_textfield.dart';
import '../../theme/app_colors.dart';
import '../../theme/app_text_styles.dart';
import '../../theme/app_radius.dart';

class ContractsScreen extends StatefulWidget {
  const ContractsScreen({super.key});

  @override
  State<ContractsScreen> createState() => _ContractsScreenState();
}

class _ContractsScreenState extends State<ContractsScreen> {
  final TextEditingController _searchController = TextEditingController();

  @override
  void initState() {
    super.initState();
    WidgetsBinding.instance.addPostFrameCallback((_) {
      _loadData();
    });
  }

  void _loadData() {
    final user = context.read<AuthProvider>().currentUser;
    if (user != null) {
      context.read<ContractProvider>().fetchContracts(user.role, user.id);
    }
  }

  @override
  void dispose() {
    _searchController.dispose();
    super.dispose();
  }

  @override
  Widget build(BuildContext context) {
    final provider = context.watch<ContractProvider>();

    return Column(
      crossAxisAlignment: CrossAxisAlignment.stretch,
      children: [
        // Search bar
        Padding(
          padding: const EdgeInsets.fromLTRB(24, 24, 24, 16),
          child: CustomTextField(
            label: 'Tìm kiếm hợp đồng',
            hint: 'Nhập mã, tên khách hàng...',
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
                hint: 'Trạng thái',
                value: provider.selectedStatus,
                items: provider.availableStatuses,
                onChanged: provider.setStatusFilter,
              ),
              if (provider.selectedStatus != null)
                Padding(
                  padding: const EdgeInsets.only(left: 8.0),
                  child: TextButton.icon(
                    onPressed: () {
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

  Widget _buildListContent(ContractProvider provider) {
    if (provider.isLoading && provider.contracts.isEmpty) {
      return const LoadingState(message: 'Đang tải danh sách hợp đồng...');
    }

    if (provider.errorMessage != null) {
      return ErrorState(
        message: 'Đã xảy ra lỗi: ${provider.errorMessage}',
        onRetry: _loadData,
      );
    }

    if (provider.contracts.isEmpty) {
      return const EmptyState(
        message: 'Không tìm thấy hợp đồng nào phù hợp.',
        icon: Icons.assignment_outlined,
      );
    }

    return RefreshIndicator(
      color: AppColors.primary,
      onRefresh: () async => _loadData(),
      child: ListView.builder(
        padding: const EdgeInsets.only(bottom: 24),
        physics: const AlwaysScrollableScrollPhysics(),
        itemCount: provider.contracts.length,
        itemBuilder: (context, index) {
          final contract = provider.contracts[index];
          return ContractCard(
            contract: contract,
            onTap: () {
              Navigator.of(context).pushNamed(
                '/contract_detail', 
                arguments: contract,
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
"""

with open("lib/screens/contracts/contracts_screen.dart", "w", encoding="utf-8") as f:
    f.write(code)

print("ContractsScreen Updated.")