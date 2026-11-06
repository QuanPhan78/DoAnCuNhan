import 'package:flutter/material.dart';
import 'package:provider/provider.dart';
import '../../models/rental_request_model.dart';
import '../../models/rental_status.dart';
import '../../providers/rental_provider.dart';
import '../../theme/app_colors.dart';
import '../../theme/app_text_styles.dart';
import '../../theme/app_radius.dart';
import '../../theme/app_shadows.dart';
import 'package:intl/intl.dart';

class RequestsScreen extends StatefulWidget {
  const RequestsScreen({super.key});

  @override
  State<RequestsScreen> createState() => _RequestsScreenState();
}

class _RequestsScreenState extends State<RequestsScreen> with SingleTickerProviderStateMixin {
  late TabController _tabController;

  final List<String> _tabs = [
    'Tất cả',
    'Chờ xác nhận',
    'Đã xác nhận',
    'Đang thuê',
    'Hoàn thành',
    'Đã hủy',
  ];

  @override
  void initState() {
    super.initState();
    _tabController = TabController(length: _tabs.length, vsync: this);
    WidgetsBinding.instance.addPostFrameCallback((_) {
      context.read<RentalProvider>().loadRequests();
    });
  }

  @override
  void dispose() {
    _tabController.dispose();
    super.dispose();
  }

  List<RentalRequestModel> _filterRequests(List<RentalRequestModel> list, int tabIndex) {
    switch (tabIndex) {
      case 0:
        return list;
      case 1:
        return list.where((r) => r.status == RentalStatus.pending).toList();
      case 2:
        return list.where((r) => r.status == RentalStatus.confirmed || r.status == RentalStatus.preparing || r.status == RentalStatus.delivering || r.status == RentalStatus.installed).toList();
      case 3:
        return list.where((r) => r.status == RentalStatus.renting).toList();
      case 4:
        return list.where((r) => r.status == RentalStatus.completed).toList();
      case 5:
        return list.where((r) => r.status == RentalStatus.cancelled || r.status == RentalStatus.rejected).toList();
      default:
        return list;
    }
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      backgroundColor: AppColors.background,
      appBar: AppBar(
        title: const Text('Đơn Thuê', style: AppTextStyles.h2),
        backgroundColor: Colors.white,
        elevation: 0,
        bottom: TabBar(
          controller: _tabController,
          isScrollable: true,
          labelColor: AppColors.primary,
          unselectedLabelColor: AppColors.textSecondary,
          indicatorColor: AppColors.primary,
          tabs: _tabs.map((tab) => Tab(text: tab)).toList(),
        ),
      ),
      body: Consumer<RentalProvider>(
        builder: (context, provider, child) {
          if (provider.isLoading) {
            return const Center(child: CircularProgressIndicator());
          }
          if (provider.error != null) {
            return Center(child: Text(provider.error!));
          }

          return TabBarView(
            controller: _tabController,
            children: List.generate(_tabs.length, (tabIndex) {
              final items = _filterRequests(provider.requests, tabIndex);
              if (items.isEmpty) {
                return const Center(
                  child: Text('Không có đơn thuê nào.', style: AppTextStyles.body),
                );
              }
              return RefreshIndicator(
                onRefresh: () async => provider.loadRequests(),
                child: ListView.separated(
                  padding: const EdgeInsets.all(16),
                  itemCount: items.length,
                  separatorBuilder: (context, index) => const SizedBox(height: 16),
                  itemBuilder: (context, index) {
                    final req = items[index];
                    return _buildRequestCard(context, req);
                  },
                ),
              );
            }),
          );
        },
      ),
    );
  }

  Widget _buildRequestCard(BuildContext context, RentalRequestModel req) {
    final statusColor = _getStatusColor(req.status);
    
    return GestureDetector(
      onTap: () {
        Navigator.pushNamed(context, '/rental_detail', arguments: req);
      },
      child: Container(
        padding: const EdgeInsets.all(16),
        decoration: BoxDecoration(
          color: Colors.white,
          borderRadius: BorderRadius.circular(AppRadius.lg),
          boxShadow: AppShadows.cardShadow,
        ),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            Row(
              mainAxisAlignment: MainAxisAlignment.spaceBetween,
              children: [
                Text('Mã: ${req.id}', style: AppTextStyles.subtitle.copyWith(fontWeight: FontWeight.bold)),
                Container(
                  padding: const EdgeInsets.symmetric(horizontal: 12, vertical: 6),
                  decoration: BoxDecoration(
                    color: statusColor.withValues(alpha: 0.1),
                    borderRadius: BorderRadius.circular(AppRadius.round),
                  ),
                  child: Text(
                    req.status.displayName,
                    style: AppTextStyles.caption.copyWith(
                      color: statusColor,
                      fontWeight: FontWeight.bold,
                    ),
                  ),
                ),
              ],
            ),
            const Divider(height: 24),
            Row(
              children: [
                Container(
                  width: 60,
                  height: 60,
                  decoration: BoxDecoration(
                    borderRadius: BorderRadius.circular(AppRadius.md),
                    color: Colors.grey[200],
                  ),
                  child: const Icon(Icons.devices, color: Colors.grey),
                ),
                const SizedBox(width: 16),
                Expanded(
                  child: Column(
                    crossAxisAlignment: CrossAxisAlignment.start,
                    children: [
                      if (req.items.isNotEmpty)
                        Text(
                          req.items.first.deviceName,
                          style: AppTextStyles.body.copyWith(fontWeight: FontWeight.bold),
                          maxLines: 2,
                          overflow: TextOverflow.ellipsis,
                        ),
                      const SizedBox(height: 4),
                      Text(
                        'Hình thức: ${req.rentalType}',
                        style: AppTextStyles.caption.copyWith(color: AppColors.textSecondary),
                      ),
                      const SizedBox(height: 4),
                      Text(
                        'Tổng tiền dự kiến: ${_formatCurrency(req.estimatedAmount)}',
                        style: AppTextStyles.body.copyWith(
                          color: AppColors.primary,
                          fontWeight: FontWeight.bold,
                        ),
                      ),
                    ],
                  ),
                ),
              ],
            ),
          ],
        ),
      ),
    );
  }

  Color _getStatusColor(RentalStatus status) {
    switch (status) {
      case RentalStatus.pending:
        return Colors.orange;
      case RentalStatus.confirmed:
        return Colors.blue;
      case RentalStatus.preparing:
        return Colors.purple;
      case RentalStatus.delivering:
        return Colors.cyan;
      case RentalStatus.installed:
        return Colors.indigo;
      case RentalStatus.renting:
        return Colors.green;
      case RentalStatus.completed:
        return Colors.teal;
      case RentalStatus.rejected:
      case RentalStatus.cancelled:
        return Colors.red;
    }
  }

  String _formatCurrency(double amount) {
    return '${NumberFormat('#,###').format(amount)} VNĐ';
  }
}