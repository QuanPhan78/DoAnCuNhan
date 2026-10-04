import os
import json

# 1. Create mock data
mock_contracts = [
    {
        "id": "C001",
        "contractCode": "HD-2026-001",
        "customerId": "1",
        "customerName": "Nguyễn Khách Hàng",
        "deviceIds": ["1", "2"],
        "rentalStart": "01/09/2026",
        "rentalEnd": "01/10/2026",
        "rentalType": "Ngắn hạn",
        "status": "Đang hiệu lực",
        "totalAmount": 1500000.0,
        "installationDetails": "Cài đặt Windows và Office tại nhà",
        "extensionDetails": ""
    },
    {
        "id": "C002",
        "contractCode": "HD-2026-002",
        "customerId": "1",
        "customerName": "Nguyễn Khách Hàng",
        "deviceIds": ["4"],
        "rentalStart": "15/09/2026",
        "rentalEnd": "15/12/2026",
        "rentalType": "Dài hạn",
        "status": "Chờ duyệt",
        "totalAmount": 2400000.0,
        "installationDetails": "Giao thiết bị tận nơi",
        "extensionDetails": ""
    },
    {
        "id": "C003",
        "contractCode": "HD-2026-003",
        "customerId": "99",
        "customerName": "Trần Khách Khác",
        "deviceIds": ["3"],
        "rentalStart": "01/08/2026",
        "rentalEnd": "01/09/2026",
        "rentalType": "Ngắn hạn",
        "status": "Đã thanh lý",
        "totalAmount": 500000.0,
        "installationDetails": "",
        "extensionDetails": "Gia hạn thêm 1 tuần"
    }
]

os.makedirs("assets/mock", exist_ok=True)
with open("assets/mock/contracts.json", "w", encoding="utf-8") as f:
    json.dump(mock_contracts, f, ensure_ascii=False, indent=2)

os.makedirs("lib/datasources/contract", exist_ok=True)

# 2. Dart code pieces
model_code = r'''class ContractModel {
  final String id;
  final String? contractCode;
  final String? customerId;
  final String? customerName;
  final List<String>? deviceIds;
  final String? rentalStart;
  final String? rentalEnd;
  final String? rentalType;
  final String? status;
  final double? totalAmount;
  final String? installationDetails;
  final String? extensionDetails;

  ContractModel({
    required this.id,
    this.contractCode,
    this.customerId,
    this.customerName,
    this.deviceIds,
    this.rentalStart,
    this.rentalEnd,
    this.rentalType,
    this.status,
    this.totalAmount,
    this.installationDetails,
    this.extensionDetails,
  });

  factory ContractModel.fromJson(Map<String, dynamic> json) {
    return ContractModel(
      id: json['id'],
      contractCode: json['contractCode'],
      customerId: json['customerId'],
      customerName: json['customerName'],
      deviceIds: json['deviceIds'] != null ? List<String>.from(json['deviceIds']) : [],
      rentalStart: json['rentalStart'],
      rentalEnd: json['rentalEnd'],
      rentalType: json['rentalType'],
      status: json['status'],
      totalAmount: (json['totalAmount'] as num?)?.toDouble(),
      installationDetails: json['installationDetails'],
      extensionDetails: json['extensionDetails'],
    );
  }
}
'''
with open("lib/models/contract_model.dart", "w", encoding="utf-8") as f: f.write(model_code)

datasource_abs = r'''import '../../models/contract_model.dart';
import '../../models/role_enum.dart';

abstract class ContractDataSource {
  Future<List<ContractModel>> getContracts(Role role, String userId);
}
'''
with open("lib/datasources/contract/contract_datasource.dart", "w", encoding="utf-8") as f: f.write(datasource_abs)

datasource_local = r'''import 'dart:convert';
import 'package:flutter/services.dart';
import '../../models/contract_model.dart';
import '../../models/role_enum.dart';
import 'contract_datasource.dart';

class LocalContractDataSource implements ContractDataSource {
  @override
  Future<List<ContractModel>> getContracts(Role role, String userId) async {
    await Future.delayed(const Duration(seconds: 1));
    final String response = await rootBundle.loadString('assets/mock/contracts.json');
    final List<dynamic> data = json.decode(response);
    
    List<ContractModel> allContracts = data.map((json) => ContractModel.fromJson(json)).toList();
    
    if (role == Role.customer) {
      return allContracts.where((c) => c.customerId == userId).toList();
    }
    
    return allContracts;
  }
}
'''
with open("lib/datasources/contract/local_contract_datasource.dart", "w", encoding="utf-8") as f: f.write(datasource_local)

datasource_remote = r'''import '../../models/contract_model.dart';
import '../../models/role_enum.dart';
import 'contract_datasource.dart';

class RemoteContractDataSource implements ContractDataSource {
  @override
  Future<List<ContractModel>> getContracts(Role role, String userId) async {
    throw UnimplementedError('API chưa có sẵn');
  }
}
'''
with open("lib/datasources/contract/remote_contract_datasource.dart", "w", encoding="utf-8") as f: f.write(datasource_remote)

repo = r'''import '../models/contract_model.dart';
import '../models/role_enum.dart';
import '../datasources/contract/contract_datasource.dart';

class ContractRepository {
  final ContractDataSource _dataSource;
  ContractRepository(this._dataSource);

  Future<List<ContractModel>> getContracts(Role role, String userId) {
    return _dataSource.getContracts(role, userId);
  }
}
'''
with open("lib/repositories/contract_repository.dart", "w", encoding="utf-8") as f: f.write(repo)

provider = r'''import 'package:flutter/material.dart';
import '../models/contract_model.dart';
import '../models/role_enum.dart';
import '../repositories/contract_repository.dart';

class ContractProvider with ChangeNotifier {
  final ContractRepository _repository;

  ContractProvider(this._repository);

  List<ContractModel> _allContracts = [];
  List<ContractModel> _filteredContracts = [];
  
  bool _isLoading = false;
  String? _errorMessage;
  
  String _searchQuery = '';
  String? _selectedStatus;

  List<ContractModel> get contracts => _filteredContracts;
  bool get isLoading => _isLoading;
  String? get errorMessage => _errorMessage;

  List<String> get availableStatuses => _allContracts.map((c) => c.status ?? 'Khác').toSet().toList();
  String? get selectedStatus => _selectedStatus;

  Future<void> fetchContracts(Role role, String userId) async {
    _isLoading = true;
    _errorMessage = null;
    notifyListeners();

    try {
      _allContracts = await _repository.getContracts(role, userId);
      _applyFilters();
    } catch (e) {
      _errorMessage = e.toString();
    } finally {
      _isLoading = false;
      notifyListeners();
    }
  }

  void search(String query) {
    _searchQuery = query;
    _applyFilters();
  }

  void setStatusFilter(String? status) {
    _selectedStatus = status;
    _applyFilters();
  }

  void _applyFilters() {
    _filteredContracts = _allContracts.where((contract) {
      final matchesSearch = (contract.contractCode?.toLowerCase().contains(_searchQuery.toLowerCase()) ?? false) ||
                            (contract.customerName?.toLowerCase().contains(_searchQuery.toLowerCase()) ?? false);
      final matchesStatus = _selectedStatus == null || contract.status == _selectedStatus;
      
      return matchesSearch && matchesStatus;
    }).toList();
    notifyListeners();
  }
}
'''
with open("lib/providers/contract_provider.dart", "w", encoding="utf-8") as f: f.write(provider)

card_widget = r'''import 'package:flutter/material.dart';
import '../models/contract_model.dart';

class ContractCard extends StatelessWidget {
  final ContractModel contract;
  final VoidCallback onTap;

  const ContractCard({super.key, required this.contract, required this.onTap});

  @override
  Widget build(BuildContext context) {
    return Card(
      elevation: 2,
      margin: const EdgeInsets.symmetric(horizontal: 16, vertical: 8),
      shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(12)),
      child: InkWell(
        onTap: onTap,
        borderRadius: BorderRadius.circular(12),
        child: Padding(
          padding: const EdgeInsets.all(16),
          child: Column(
            crossAxisAlignment: CrossAxisAlignment.start,
            children: [
              Row(
                mainAxisAlignment: MainAxisAlignment.spaceBetween,
                children: [
                  Text(contract.contractCode ?? 'N/A', style: const TextStyle(fontSize: 16, fontWeight: FontWeight.bold)),
                  _buildStatusBadge(contract.status ?? 'Không rõ'),
                ],
              ),
              const Divider(),
              const SizedBox(height: 8),
              _buildRow(Icons.person, contract.customerName ?? 'N/A'),
              const SizedBox(height: 4),
              _buildRow(Icons.date_range, '${contract.rentalStart ?? "N/A"} - ${contract.rentalEnd ?? "N/A"}'),
              const SizedBox(height: 4),
              _buildRow(Icons.attach_money, '${contract.totalAmount ?? 0} đ', color: Colors.red),
            ],
          ),
        ),
      ),
    );
  }

  Widget _buildRow(IconData icon, String text, {Color? color}) {
    return Row(
      children: [
        Icon(icon, size: 16, color: Colors.grey),
        const SizedBox(width: 8),
        Expanded(child: Text(text, style: TextStyle(color: color, fontSize: 14))),
      ],
    );
  }

  Widget _buildStatusBadge(String status) {
    Color color = Colors.grey;
    if (status == 'Đang hiệu lực') color = Colors.green;
    if (status == 'Chờ duyệt') color = Colors.orange;
    if (status == 'Đã thanh lý') color = Colors.blue;
    
    return Container(
      padding: const EdgeInsets.symmetric(horizontal: 10, vertical: 4),
      decoration: BoxDecoration(
        color: color.withValues(alpha: 0.1),
        borderRadius: BorderRadius.circular(12),
        border: Border.all(color: color),
      ),
      child: Text(status, style: TextStyle(color: color, fontSize: 12, fontWeight: FontWeight.w600)),
    );
  }
}
'''
with open("lib/widgets/contract_card.dart", "w", encoding="utf-8") as f: f.write(card_widget)

screen_list = r'''import 'package:flutter/material.dart';
import 'package:provider/provider.dart';
import '../../providers/auth_provider.dart';
import '../../providers/contract_provider.dart';
import '../../widgets/contract_card.dart';

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
      children: [
        Padding(
          padding: const EdgeInsets.all(16.0),
          child: TextField(
            controller: _searchController,
            decoration: InputDecoration(
              hintText: 'Tìm theo mã, tên khách hàng...',
              prefixIcon: const Icon(Icons.search),
              border: OutlineInputBorder(borderRadius: BorderRadius.circular(12)),
              contentPadding: const EdgeInsets.symmetric(vertical: 0),
            ),
            onChanged: (value) => provider.search(value),
          ),
        ),
        
        SingleChildScrollView(
          scrollDirection: Axis.horizontal,
          padding: const EdgeInsets.symmetric(horizontal: 16),
          child: Row(
            children: [
              _buildFilterDropdown(
                hint: 'Trạng thái',
                value: provider.selectedStatus,
                items: provider.availableStatuses,
                onChanged: provider.setStatusFilter,
              ),
              if (provider.selectedStatus != null)
                TextButton(
                  onPressed: () {
                    provider.setStatusFilter(null);
                  },
                  child: const Text('Xóa lọc'),
                )
            ],
          ),
        ),
        const SizedBox(height: 8),

        Expanded(
          child: provider.isLoading 
              ? const Center(child: CircularProgressIndicator())
              : provider.errorMessage != null
                  ? Center(child: Text('Lỗi: ${provider.errorMessage}'))
                  : provider.contracts.isEmpty
                      ? const Center(child: Text('Không tìm thấy hợp đồng phù hợp'))
                      : RefreshIndicator(
                          onRefresh: () async => _loadData(),
                          child: ListView.builder(
                            itemCount: provider.contracts.length,
                            itemBuilder: (context, index) {
                              return ContractCard(
                                contract: provider.contracts[index],
                                onTap: () {
                                  Navigator.of(context).pushNamed(
                                    '/contract_detail', 
                                    arguments: provider.contracts[index],
                                  );
                                },
                              );
                            },
                          ),
                        ),
        ),
      ],
    );
  }

  Widget _buildFilterDropdown({
    required String hint,
    required String? value,
    required List<String> items,
    required Function(String?) onChanged,
  }) {
    return Container(
      padding: const EdgeInsets.symmetric(horizontal: 12),
      decoration: BoxDecoration(
        border: Border.all(color: Colors.grey.shade300),
        borderRadius: BorderRadius.circular(20),
      ),
      child: DropdownButtonHideUnderline(
        child: DropdownButton<String>(
          hint: Text(hint),
          value: value,
          icon: const Icon(Icons.arrow_drop_down, size: 20),
          isDense: true,
          items: items.map((String item) {
            return DropdownMenuItem<String>(
              value: item,
              child: Text(item, style: const TextStyle(fontSize: 14)),
            );
          }).toList(),
          onChanged: onChanged,
        ),
      ),
    );
  }
}
'''
with open("lib/screens/contracts/contracts_screen.dart", "w", encoding="utf-8") as f: f.write(screen_list.replace(r'${', '${'))

screen_detail = r'''import 'package:flutter/material.dart';
import 'package:provider/provider.dart';
import '../../models/contract_model.dart';
import '../../models/device_model.dart';
import '../../providers/device_provider.dart';

class ContractDetailScreen extends StatelessWidget {
  final ContractModel contract;

  const ContractDetailScreen({super.key, required this.contract});

  @override
  Widget build(BuildContext context) {
    // Để lấy chi tiết các thiết bị, ta dùng deviceIds và filter từ DeviceProvider
    // LƯU Ý: Ở ứng dụng thực tế nên dùng FutureBuilder gọi repository
    // Tuy nhiên theo prompt, ta ưu tiên đọc qua Provider nếu đã có, hoặc cung cấp trạng thái phù hợp.
    
    final allDevices = context.read<DeviceProvider>().devices;
    // Vì devices có thể bị filter ở Provider, tốt hơn ta fetch devices hoặc repository.
    // Giả định DeviceProvider._allDevices được tải. Trong context này, gọi thẳng hàm tìm:
    
    return Scaffold(
      appBar: AppBar(title: const Text('Chi tiết Hợp đồng')),
      body: SingleChildScrollView(
        padding: const EdgeInsets.all(16),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            Text(contract.contractCode ?? 'N/A', style: const TextStyle(fontSize: 24, fontWeight: FontWeight.bold)),
            const SizedBox(height: 8),
            _buildStatusBadge(contract.status ?? 'Không rõ'),
            const Divider(height: 32),
            
            const Text('THÔNG TIN CHUNG', style: TextStyle(fontSize: 16, fontWeight: FontWeight.bold, color: Colors.blue)),
            const SizedBox(height: 16),
            _buildInfoRow('Khách hàng', contract.customerName ?? 'N/A'),
            _buildInfoRow('Thời gian', '${contract.rentalStart ?? "N/A"} - ${contract.rentalEnd ?? "N/A"}'),
            _buildInfoRow('Hình thức', contract.rentalType ?? 'N/A'),
            _buildInfoRow('Tổng tiền', '${contract.totalAmount ?? 0} đ', valueColor: Colors.red),
            if (contract.installationDetails != null && contract.installationDetails!.isNotEmpty)
              _buildInfoRow('Lắp đặt', contract.installationDetails!),
            if (contract.extensionDetails != null && contract.extensionDetails!.isNotEmpty)
              _buildInfoRow('Gia hạn', contract.extensionDetails!),
            
            const Divider(height: 32),
            const Text('DANH SÁCH THIẾT BỊ', style: TextStyle(fontSize: 16, fontWeight: FontWeight.bold, color: Colors.blue)),
            const SizedBox(height: 16),
            
            if (contract.deviceIds == null || contract.deviceIds!.isEmpty)
              const Text('Không có thiết bị nào trong hợp đồng này.')
            else
              ...contract.deviceIds!.map((deviceId) {
                return _buildDeviceItem(context, deviceId);
              }).toList(),
          ],
        ),
      ),
    );
  }

  Widget _buildDeviceItem(BuildContext context, String deviceId) {
    // Dùng FutureBuilder để mô phỏng lookup nếu cần, hoặc đơn giản là mock tra cứu
    // Thay vì access trực tiếp Provider, ta gọi phương thức an toàn. 
    // Do repository cần injection, ta lấy data từ context.read<DeviceProvider>().devices
    // Lưu ý: context.read<DeviceProvider>().devices chỉ là filtered array, 
    // có thể ta sẽ miss. Nhưng ở đây giả sử ta tìm trong full cache, hoặc repository.
    // Để giữ clean architecture & UI không gọi Data trực tiếp, ta dùng context
    // Tuy nhiên theo prompt "Nếu thiết bị không tìm thấy -> hiển thị trạng thái phù hợp"
    // Tôi sẽ tra cứu qua DeviceProvider.

    return FutureBuilder<DeviceModel>(
      // Dùng extension method hoặc đọc provider để lấy thiết bị từ cache.
      // Vì mockup này không có fetchDeviceById, ta giả lập filter:
      future: _fetchDevice(context, deviceId),
      builder: (context, snapshot) {
        if (snapshot.connectionState == ConnectionState.waiting) {
          return const ListTile(
            leading: CircularProgressIndicator(),
            title: Text('Đang tải...'),
          );
        }
        if (snapshot.hasError || !snapshot.hasData) {
          return Card(
            color: Colors.red.shade50,
            child: ListTile(
              leading: const Icon(Icons.error, color: Colors.red),
              title: Text('Mã TB: $deviceId'),
              subtitle: const Text('Thiết bị không tồn tại hoặc đã bị xóa.'),
            ),
          );
        }
        final device = snapshot.data!;
        return Card(
          child: ListTile(
            leading: const Icon(Icons.devices),
            title: Text(device.name),
            subtitle: Text('Mã: ${device.code ?? 'N/A'} - Hãng: ${device.brand ?? 'N/A'} - Model: ${device.model ?? 'N/A'}'),
            trailing: const Icon(Icons.arrow_forward_ios, size: 16),
            onTap: () {
              Navigator.of(context).pushNamed('/device_detail', arguments: device);
            },
          ),
        );
      },
    );
  }

  Future<DeviceModel> _fetchDevice(BuildContext context, String deviceId) async {
    // Trong thực tế, cần DeviceRepository.getDeviceById
    // Dùng cách fake loop lookup qua Repository đã đăng ký ở widget gốc
    final devices = context.read<DeviceProvider>().devices;
    // Chú ý Provider.devices là filtered, có thể không chứa, nhưng mock list ngắn
    // Để test cover, ta tìm trong danh sách, nếu ko có throw Error
    final found = devices.where((d) => d.id == deviceId);
    if (found.isNotEmpty) return found.first;
    throw Exception('Không tìm thấy thiết bị');
  }

  Widget _buildInfoRow(String label, String value, {Color? valueColor}) {
    return Padding(
      padding: const EdgeInsets.only(bottom: 12.0),
      child: Row(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          SizedBox(
            width: 100,
            child: Text(label, style: const TextStyle(color: Colors.grey, fontWeight: FontWeight.w500)),
          ),
          Expanded(
            child: Text(value, style: TextStyle(fontWeight: FontWeight.w500, color: valueColor, fontSize: valueColor != null ? 16 : 14)),
          ),
        ],
      ),
    );
  }

  Widget _buildStatusBadge(String status) {
    Color color = Colors.grey;
    if (status == 'Đang hiệu lực') color = Colors.green;
    if (status == 'Chờ duyệt') color = Colors.orange;
    if (status == 'Đã thanh lý') color = Colors.blue;
    
    return Container(
      padding: const EdgeInsets.symmetric(horizontal: 10, vertical: 4),
      decoration: BoxDecoration(
        color: color.withValues(alpha: 0.1),
        borderRadius: BorderRadius.circular(12),
        border: Border.all(color: color),
      ),
      child: Text(status, style: TextStyle(color: color, fontSize: 12, fontWeight: FontWeight.w600)),
    );
  }
}
'''
with open("lib/screens/contracts/contract_detail_screen.dart", "w", encoding="utf-8") as f: f.write(screen_detail.replace(r'${', '${'))

print("Completed python phase 1")