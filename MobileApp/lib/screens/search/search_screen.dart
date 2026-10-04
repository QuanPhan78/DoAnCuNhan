import 'package:flutter/material.dart';
import 'package:provider/provider.dart';
import '../../providers/auth_provider.dart';
import '../../providers/search_provider.dart';
import '../../theme/app_colors.dart';
import '../../theme/app_text_styles.dart';
import '../../theme/app_radius.dart';
import '../../theme/app_shadows.dart';
import '../../widgets/core/state_widgets.dart';

class SearchScreen extends StatefulWidget {
  const SearchScreen({super.key});

  @override
  State<SearchScreen> createState() => _SearchScreenState();
}

class _SearchScreenState extends State<SearchScreen> {
  final _searchController = TextEditingController();

  @override
  void initState() {
    super.initState();
    WidgetsBinding.instance.addPostFrameCallback((_) {
      context.read<SearchProvider>().clearSearch();
    });
  }

  @override
  void dispose() {
    _searchController.dispose();
    super.dispose();
  }

  void _onChanged(String query) {
    final user = context.read<AuthProvider>().currentUser;
    context.read<SearchProvider>().onSearchChanged(query, user?.id, user?.role);
  }

  void _onFilterChanged(String filter) {
    final user = context.read<AuthProvider>().currentUser;
    context.read<SearchProvider>().setFilter(filter, user?.id, user?.role);
  }

  @override
  Widget build(BuildContext context) {
    final provider = context.watch<SearchProvider>();

    return Scaffold(
      backgroundColor: AppColors.background,
      appBar: AppBar(
        backgroundColor: Colors.transparent,
        elevation: 0,
        iconTheme: const IconThemeData(color: AppColors.textPrimary),
        title: _buildSearchBar(),
        titleSpacing: 0,
      ),
      body: Column(
        children: [
          SingleChildScrollView(
            scrollDirection: Axis.horizontal,
            padding: const EdgeInsets.symmetric(horizontal: 24, vertical: 12),
            child: Row(
              children: [
                _buildChip('Tất cả', 'all', provider),
                const SizedBox(width: 8),
                _buildChip('Thiết bị', 'device', provider),
                const SizedBox(width: 8),
                _buildChip('Hợp đồng', 'contract', provider),
                const SizedBox(width: 8),
                _buildChip('Sự cố', 'incident', provider),
                const SizedBox(width: 8),
                _buildChip('Bảo trì', 'maintenance', provider),
              ],
            ),
          ),
          const Divider(color: AppColors.divider, height: 1),
          Expanded(
            child: _buildResults(provider),
          ),
        ],
      ),
    );
  }

  Widget _buildSearchBar() {
    return Container(
      margin: const EdgeInsets.only(right: 24),
      decoration: BoxDecoration(
        color: AppColors.surface,
        borderRadius: BorderRadius.circular(100),
        boxShadow: AppShadows.cardShadow,
      ),
      child: TextField(
        controller: _searchController,
        autofocus: true,
        style: AppTextStyles.body,
        decoration: InputDecoration(
          hintText: 'Tìm kiếm thiết bị, hợp đồng...',
          hintStyle: AppTextStyles.bodySecondary,
          border: InputBorder.none,
          contentPadding: const EdgeInsets.symmetric(horizontal: 20, vertical: 14),
          suffixIcon: _searchController.text.isNotEmpty
              ? IconButton(
                  icon: const Icon(Icons.clear_rounded, color: AppColors.textSecondary),
                  onPressed: () {
                    _searchController.clear();
                    _onChanged('');
                  },
                )
              : const Icon(Icons.search_rounded, color: AppColors.textSecondary),
        ),
        onChanged: _onChanged,
      ),
    );
  }

  Widget _buildChip(String label, String value, SearchProvider provider) {
    final isSelected = provider.currentFilter == value;
    return ChoiceChip(
      label: Text(label),
      labelStyle: AppTextStyles.body.copyWith(
        color: isSelected ? Colors.white : AppColors.textPrimary,
        fontWeight: isSelected ? FontWeight.bold : FontWeight.normal,
      ),
      selectedColor: AppColors.primary,
      backgroundColor: AppColors.surface,
      shape: RoundedRectangleBorder(
        borderRadius: BorderRadius.circular(100),
        side: BorderSide(color: isSelected ? AppColors.primary : AppColors.divider),
      ),
      showCheckmark: false,
      selected: isSelected,
      onSelected: (selected) {
        if (selected) _onFilterChanged(value);
      },
    );
  }

  Widget _buildResults(SearchProvider provider) {
    if (provider.isLoading) {
      return const LoadingState(message: 'Đang tìm kiếm...');
    }

    if (provider.errorMessage != null) {
      return ErrorState(
        message: 'Lỗi: ${provider.errorMessage}',
        onRetry: () {
          final user = context.read<AuthProvider>().currentUser;
          provider.search(provider.currentQuery, userId: user?.id, role: user?.role);
        }
      );
    }

    if (provider.currentQuery.trim().isEmpty) {
      return const EmptyState(
        message: 'Nhập từ khóa để bắt đầu tìm kiếm',
        icon: Icons.search_rounded,
      );
    }

    if (provider.results.isEmpty) {
      return const EmptyState(
        message: 'Không tìm thấy kết quả phù hợp.',
        icon: Icons.manage_search_rounded,
      );
    }

    return ListView.builder(
      padding: const EdgeInsets.symmetric(horizontal: 24, vertical: 16),
      itemCount: provider.results.length,
      itemBuilder: (context, index) {
        final result = provider.results[index];
        return Container(
          margin: const EdgeInsets.only(bottom: 12),
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
              onTap: () {
                switch (result.type) {
                  case 'device':
                    Navigator.pushNamed(context, '/device_detail', arguments: result.originalData);
                    break;
                  case 'contract':
                    Navigator.pushNamed(context, '/contract_detail', arguments: result.originalData);
                    break;
                  case 'incident':
                    Navigator.pushNamed(context, '/incident_detail', arguments: result.originalData);
                    break;
                  case 'maintenance':
                    Navigator.pushNamed(context, '/maintenance_detail', arguments: result.originalData);
                    break;
                }
              },
              child: Padding(
                padding: const EdgeInsets.all(16),
                child: Row(
                  children: [
                    Container(
                      padding: const EdgeInsets.all(12),
                      decoration: BoxDecoration(
                        color: _getColorForType(result.type).withValues(alpha: 0.1),
                        borderRadius: AppRadius.mdRadius,
                      ),
                      child: Icon(_getIconForType(result.type), color: _getColorForType(result.type), size: 24),
                    ),
                    const SizedBox(width: 16),
                    Expanded(
                      child: Column(
                        crossAxisAlignment: CrossAxisAlignment.start,
                        children: [
                          Text(
                            result.title,
                            style: AppTextStyles.h2.copyWith(fontSize: 16),
                            maxLines: 1, overflow: TextOverflow.ellipsis,
                          ),
                          const SizedBox(height: 4),
                          Text(
                            result.subtitle,
                            style: AppTextStyles.bodySecondary,
                            maxLines: 2, overflow: TextOverflow.ellipsis,
                          ),
                        ],
                      ),
                    ),
                    if (result.status != null && result.status!.isNotEmpty) ...[
                      const SizedBox(width: 8),
                      Container(
                        padding: const EdgeInsets.symmetric(horizontal: 8, vertical: 4),
                        decoration: BoxDecoration(
                          color: AppColors.background,
                          borderRadius: AppRadius.smRadius,
                          border: Border.all(color: AppColors.divider),
                        ),
                        child: Text(
                          result.status!,
                          style: AppTextStyles.bodySecondary.copyWith(fontSize: 11, fontWeight: FontWeight.bold),
                        ),
                      )
                    ]
                  ],
                ),
              ),
            ),
          ),
        );
      },
    );
  }

  IconData _getIconForType(String type) {
    switch (type) {
      case 'device': return Icons.devices_rounded;
      case 'contract': return Icons.description_rounded;
      case 'incident': return Icons.warning_rounded;
      case 'maintenance': return Icons.build_rounded;
      default: return Icons.insert_drive_file_rounded;
    }
  }

  Color _getColorForType(String type) {
    switch (type) {
      case 'device': return Colors.blue;
      case 'contract': return Colors.purple;
      case 'incident': return AppColors.error;
      case 'maintenance': return AppColors.success;
      default: return AppColors.textSecondary;
    }
  }
}
