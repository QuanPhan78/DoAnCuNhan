import os
import json
import base64

# 1. Update pubspec.yaml
with open("pubspec.yaml", "r", encoding="utf-8") as f:
    pubspec = f.read()

if "assets:" not in pubspec:
    pubspec = pubspec.replace("uses-material-design: true", "uses-material-design: true\n  assets:\n    - assets/mock/\n    - assets/images/devices/")
    with open("pubspec.yaml", "w", encoding="utf-8") as f:
        f.write(pubspec)

# 2. Create directories
os.makedirs("assets/mock", exist_ok=True)
os.makedirs("assets/images/devices", exist_ok=True)
os.makedirs("lib/models", exist_ok=True)
os.makedirs("lib/datasources/device", exist_ok=True)
os.makedirs("lib/repositories", exist_ok=True)
os.makedirs("lib/providers", exist_ok=True)
os.makedirs("lib/widgets", exist_ok=True)

# 3. Create dummy 1x1 transparent PNG
png_base64 = "iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAQAAAC1HAwCAAAAC0lEQVR42mNkYAAAAAYAAjCB0C8AAAAASUVORK5CYII="
png_data = base64.b64decode(png_base64)

for device in ['laptop', 'pc', 'maytinh', 'mayin', 'maychieu', 'manhinh', 'banphim', 'chuot', 'webcam', 'router', 'switch', 'accesspoint', 'phukien']:
    with open(f"assets/images/devices/{device}.png", "wb") as f:
        f.write(png_data)

# 4. Create devices.json
mock_devices = [
    {
        "id": "1",
        "code": "DEV-001",
        "name": "Laptop Dell XPS 13",
        "type": "Laptop",
        "brand": "Dell",
        "model": "XPS 13 9310",
        "serialNumber": "SN-XPS-001",
        "specifications": "Core i7, 16GB RAM, 512GB SSD",
        "condition": "Mới 99%",
        "rentalStatus": "Sẵn sàng",
        "rentalPrice": 500000,
        "description": "Laptop mỏng nhẹ, phù hợp văn phòng.",
        "imageAsset": "assets/images/devices/laptop.png",
        "imageUrl": ""
    },
    {
        "id": "2",
        "code": "DEV-002",
        "name": "Màn hình Dell Ultrasharp",
        "type": "Màn hình",
        "brand": "Dell",
        "model": "U2422H",
        "serialNumber": "SN-DEL-002",
        "specifications": "24 inch, FHD, IPS",
        "condition": "Tốt",
        "rentalStatus": "Đang cho thuê",
        "rentalPrice": 100000,
        "description": "Màn hình chuẩn màu đồ họa.",
        "imageAsset": "assets/images/devices/manhinh.png",
        "imageUrl": ""
    },
    {
        "id": "3",
        "code": "DEV-003",
        "name": "Bàn phím cơ Keychron K8",
        "type": "Bàn phím",
        "brand": "Keychron",
        "model": "K8",
        "serialNumber": "SN-KEY-003",
        "specifications": "Brown Switch, RGB, Bluetooth",
        "condition": "Mới 100%",
        "rentalStatus": "Sẵn sàng",
        "rentalPrice": 50000,
        "description": "Bàn phím cơ không dây.",
        "imageAsset": "assets/images/devices/banphim.png",
        "imageUrl": ""
    },
    {
        "id": "4",
        "code": "DEV-004",
        "name": "Router Wifi 6 TP-Link",
        "type": "Router",
        "brand": "TP-Link",
        "model": "AX3000",
        "serialNumber": "SN-TPL-004",
        "specifications": "Wifi 6, Gigabit ports",
        "condition": "Đang bảo trì",
        "rentalStatus": "Bảo trì",
        "rentalPrice": 80000,
        "description": "Router wifi tốc độ cao.",
        "imageAsset": "assets/images/devices/router.png",
        "imageUrl": ""
    }
]

with open("assets/mock/devices.json", "w", encoding="utf-8") as f:
    json.dump(mock_devices, f, ensure_ascii=False, indent=2)

# 5. Create Dart files
dart_device_model = r'''class DeviceModel {
  final String id;
  final String? code;
  final String name;
  final String type;
  final String? brand;
  final String? model;
  final String? serialNumber;
  final String? specifications;
  final String? condition;
  final String? rentalStatus;
  final double? rentalPrice;
  final String? description;
  final String? imageAsset;
  final String? imageUrl;

  DeviceModel({
    required this.id,
    this.code,
    required this.name,
    required this.type,
    this.brand,
    this.model,
    this.serialNumber,
    this.specifications,
    this.condition,
    this.rentalStatus,
    this.rentalPrice,
    this.description,
    this.imageAsset,
    this.imageUrl,
  });

  factory DeviceModel.fromJson(Map<String, dynamic> json) {
    return DeviceModel(
      id: json['id'],
      code: json['code'],
      name: json['name'],
      type: json['type'],
      brand: json['brand'],
      model: json['model'],
      serialNumber: json['serialNumber'],
      specifications: json['specifications'],
      condition: json['condition'],
      rentalStatus: json['rentalStatus'],
      rentalPrice: (json['rentalPrice'] as num?)?.toDouble(),
      description: json['description'],
      imageAsset: json['imageAsset'],
      imageUrl: json['imageUrl'],
    );
  }
}
'''
with open("lib/models/device_model.dart", "w", encoding="utf-8") as f: f.write(dart_device_model)

dart_device_datasource = r'''import '../../models/device_model.dart';

abstract class DeviceDataSource {
  Future<List<DeviceModel>> getDevices();
  Future<DeviceModel> getDeviceById(String id);
}
'''
with open("lib/datasources/device/device_datasource.dart", "w", encoding="utf-8") as f: f.write(dart_device_datasource)

dart_local_device_datasource = r'''import 'dart:convert';
import 'package:flutter/services.dart';
import '../../models/device_model.dart';
import 'device_datasource.dart';

class LocalDeviceDataSource implements DeviceDataSource {
  @override
  Future<List<DeviceModel>> getDevices() async {
    await Future.delayed(const Duration(seconds: 1)); // Mô phỏng delay
    final String response = await rootBundle.loadString('assets/mock/devices.json');
    final List<dynamic> data = json.decode(response);
    return data.map((json) => DeviceModel.fromJson(json)).toList();
  }

  @override
  Future<DeviceModel> getDeviceById(String id) async {
    final devices = await getDevices();
    return devices.firstWhere((device) => device.id == id, orElse: () => throw Exception('Không tìm thấy thiết bị'));
  }
}
'''
with open("lib/datasources/device/local_device_datasource.dart", "w", encoding="utf-8") as f: f.write(dart_local_device_datasource)

dart_remote_device_datasource = r'''import '../../models/device_model.dart';
import 'device_datasource.dart';

class RemoteDeviceDataSource implements DeviceDataSource {
  @override
  Future<List<DeviceModel>> getDevices() async {
    throw UnimplementedError('API chưa có sẵn');
  }

  @override
  Future<DeviceModel> getDeviceById(String id) async {
    throw UnimplementedError('API chưa có sẵn');
  }
}
'''
with open("lib/datasources/device/remote_device_datasource.dart", "w", encoding="utf-8") as f: f.write(dart_remote_device_datasource)

dart_device_repository = r'''import '../models/device_model.dart';
import '../datasources/device/device_datasource.dart';

class DeviceRepository {
  final DeviceDataSource _dataSource;
  DeviceRepository(this._dataSource);

  Future<List<DeviceModel>> getAllDevices() {
    return _dataSource.getDevices();
  }

  Future<DeviceModel> getDeviceById(String id) {
    return _dataSource.getDeviceById(id);
  }
}
'''
with open("lib/repositories/device_repository.dart", "w", encoding="utf-8") as f: f.write(dart_device_repository)

dart_device_provider = r'''import 'package:flutter/material.dart';
import '../models/device_model.dart';
import '../repositories/device_repository.dart';

class DeviceProvider with ChangeNotifier {
  final DeviceRepository _repository;

  DeviceProvider(this._repository);

  List<DeviceModel> _allDevices = [];
  List<DeviceModel> _filteredDevices = [];
  
  bool _isLoading = false;
  String? _errorMessage;
  
  String _searchQuery = '';
  String? _selectedType;
  String? _selectedStatus;

  List<DeviceModel> get devices => _filteredDevices;
  bool get isLoading => _isLoading;
  String? get errorMessage => _errorMessage;

  List<String> get availableTypes => _allDevices.map((d) => d.type).toSet().toList();
  List<String> get availableStatuses => _allDevices.map((d) => d.rentalStatus ?? 'Khác').toSet().toList();

  String? get selectedType => _selectedType;
  String? get selectedStatus => _selectedStatus;
  String get searchQuery => _searchQuery;

  Future<void> fetchDevices() async {
    _isLoading = true;
    _errorMessage = null;
    notifyListeners();

    try {
      _allDevices = await _repository.getAllDevices();
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

  void setTypeFilter(String? type) {
    _selectedType = type;
    _applyFilters();
  }

  void setStatusFilter(String? status) {
    _selectedStatus = status;
    _applyFilters();
  }

  void _applyFilters() {
    _filteredDevices = _allDevices.where((device) {
      final matchesSearch = device.name.toLowerCase().contains(_searchQuery.toLowerCase()) || 
                            (device.code?.toLowerCase().contains(_searchQuery.toLowerCase()) ?? false);
      final matchesType = _selectedType == null || device.type == _selectedType;
      final matchesStatus = _selectedStatus == null || device.rentalStatus == _selectedStatus;
      
      return matchesSearch && matchesType && matchesStatus;
    }).toList();
    notifyListeners();
  }
}
'''
with open("lib/providers/device_provider.dart", "w", encoding="utf-8") as f: f.write(dart_device_provider)

dart_device_card = r'''import 'package:flutter/material.dart';
import '../models/device_model.dart';
import 'custom_image_widget.dart';

class DeviceCard extends StatelessWidget {
  final DeviceModel device;
  final VoidCallback onTap;

  const DeviceCard({super.key, required this.device, required this.onTap});

  @override
  Widget build(BuildContext context) {
    final hasImage = (device.imageUrl != null && device.imageUrl!.isNotEmpty) || 
                     (device.imageAsset != null && device.imageAsset!.isNotEmpty);
                     
    final imagePath = (device.imageUrl != null && device.imageUrl!.isNotEmpty) 
        ? device.imageUrl! 
        : (device.imageAsset ?? '');

    return Card(
      elevation: 2,
      margin: const EdgeInsets.symmetric(horizontal: 16, vertical: 8),
      shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(12)),
      child: InkWell(
        onTap: onTap,
        borderRadius: BorderRadius.circular(12),
        child: Padding(
          padding: const EdgeInsets.all(12),
          child: Row(
            crossAxisAlignment: CrossAxisAlignment.start,
            children: [
              ClipRRect(
                borderRadius: BorderRadius.circular(8),
                child: hasImage 
                    ? CustomImageWidget(imageUrl: imagePath, width: 80, height: 80, fit: BoxFit.cover)
                    : Container(width: 80, height: 80, color: Colors.grey[200], child: const Icon(Icons.devices)),
              ),
              const SizedBox(width: 16),
              Expanded(
                child: Column(
                  crossAxisAlignment: CrossAxisAlignment.start,
                  children: [
                    Text(device.name, style: const TextStyle(fontSize: 16, fontWeight: FontWeight.bold), maxLines: 2, overflow: TextOverflow.ellipsis),
                    const SizedBox(height: 4),
                    Text('Mã: ${device.code ?? "N/A"}', style: TextStyle(color: Colors.grey[600], fontSize: 13)),
                    const SizedBox(height: 4),
                    Row(
                      children: [
                        Container(
                          padding: const EdgeInsets.symmetric(horizontal: 8, vertical: 2),
                          decoration: BoxDecoration(
                            color: Colors.blue.withValues(alpha: 0.1),
                            borderRadius: BorderRadius.circular(12),
                          ),
                          child: Text(device.type, style: const TextStyle(color: Colors.blue, fontSize: 12)),
                        ),
                        const SizedBox(width: 8),
                        if (device.rentalStatus != null)
                          Container(
                            padding: const EdgeInsets.symmetric(horizontal: 8, vertical: 2),
                            decoration: BoxDecoration(
                              color: _getStatusColor(device.rentalStatus!).withValues(alpha: 0.1),
                              borderRadius: BorderRadius.circular(12),
                            ),
                            child: Text(device.rentalStatus!, style: TextStyle(color: _getStatusColor(device.rentalStatus!), fontSize: 12)),
                          ),
                      ],
                    ),
                    const SizedBox(height: 8),
                    Text(
                      device.rentalPrice != null ? '${device.rentalPrice} đ / ngày' : 'Liên hệ',
                      style: const TextStyle(color: Colors.red, fontWeight: FontWeight.bold),
                    ),
                  ],
                ),
              ),
            ],
          ),
        ),
      ),
    );
  }

  Color _getStatusColor(String status) {
    if (status == 'Sẵn sàng') return Colors.green;
    if (status == 'Đang cho thuê') return Colors.orange;
    if (status == 'Bảo trì') return Colors.red;
    return Colors.grey;
  }
}
'''
with open("lib/widgets/device_card.dart", "w", encoding="utf-8") as f: f.write(dart_device_card)

dart_devices_screen = r'''import 'package:flutter/material.dart';
import 'package:provider/provider.dart';
import '../../providers/device_provider.dart';
import '../../widgets/device_card.dart';

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
      children: [
        // Search bar
        Padding(
          padding: const EdgeInsets.all(16.0),
          child: TextField(
            controller: _searchController,
            decoration: InputDecoration(
              hintText: 'Tìm kiếm thiết bị...',
              prefixIcon: const Icon(Icons.search),
              border: OutlineInputBorder(borderRadius: BorderRadius.circular(12)),
              contentPadding: const EdgeInsets.symmetric(vertical: 0),
            ),
            onChanged: (value) => provider.search(value),
          ),
        ),
        
        // Filters
        SingleChildScrollView(
          scrollDirection: Axis.horizontal,
          padding: const EdgeInsets.symmetric(horizontal: 16),
          child: Row(
            children: [
              _buildFilterDropdown(
                hint: 'Loại',
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
                TextButton(
                  onPressed: () {
                    provider.setTypeFilter(null);
                    provider.setStatusFilter(null);
                  },
                  child: const Text('Xóa lọc'),
                )
            ],
          ),
        ),
        const SizedBox(height: 8),

        // List
        Expanded(
          child: provider.isLoading 
              ? const Center(child: CircularProgressIndicator())
              : provider.errorMessage != null
                  ? Center(child: Text('Lỗi: ${provider.errorMessage}'))
                  : provider.devices.isEmpty
                      ? const Center(child: Text('Không tìm thấy thiết bị phù hợp'))
                      : RefreshIndicator(
                          onRefresh: () => provider.fetchDevices(),
                          child: ListView.builder(
                            itemCount: provider.devices.length,
                            itemBuilder: (context, index) {
                              return DeviceCard(
                                device: provider.devices[index],
                                onTap: () {
                                  Navigator.of(context).pushNamed(
                                    '/device_detail', 
                                    arguments: provider.devices[index],
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
with open("lib/screens/devices/devices_screen.dart", "w", encoding="utf-8") as f: f.write(dart_devices_screen)

dart_device_detail = r'''import 'package:flutter/material.dart';
import '../../models/device_model.dart';
import '../../widgets/custom_image_widget.dart';

class DeviceDetailScreen extends StatelessWidget {
  final DeviceModel device;

  const DeviceDetailScreen({super.key, required this.device});

  @override
  Widget build(BuildContext context) {
    final imagePath = (device.imageUrl != null && device.imageUrl!.isNotEmpty) 
        ? device.imageUrl! 
        : (device.imageAsset ?? '');

    return Scaffold(
      appBar: AppBar(
        title: const Text('Chi tiết thiết bị'),
      ),
      body: SingleChildScrollView(
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.stretch,
          children: [
            if (imagePath.isNotEmpty)
              CustomImageWidget(imageUrl: imagePath, height: 250, fit: BoxFit.contain)
            else
              Container(height: 250, color: Colors.grey[200], child: const Icon(Icons.devices, size: 80)),
            
            Padding(
              padding: const EdgeInsets.all(16.0),
              child: Column(
                crossAxisAlignment: CrossAxisAlignment.start,
                children: [
                  Text(device.name, style: const TextStyle(fontSize: 24, fontWeight: FontWeight.bold)),
                  const SizedBox(height: 8),
                  Text(
                    device.rentalPrice != null ? '${device.rentalPrice} đ / ngày' : 'Liên hệ để biết giá',
                    style: const TextStyle(fontSize: 20, color: Colors.red, fontWeight: FontWeight.bold),
                  ),
                  const Divider(height: 32),
                  
                  _buildInfoRow('Mã thiết bị', device.code ?? 'N/A'),
                  _buildInfoRow('Loại', device.type),
                  _buildInfoRow('Thương hiệu', device.brand ?? 'N/A'),
                  _buildInfoRow('Model', device.model ?? 'N/A'),
                  _buildInfoRow('Tình trạng', device.condition ?? 'N/A'),
                  _buildInfoRow('Trạng thái', device.rentalStatus ?? 'N/A'),
                  _buildInfoRow('Số Serial', device.serialNumber ?? 'N/A'),
                  
                  const SizedBox(height: 16),
                  const Text('Thông số kỹ thuật', style: TextStyle(fontSize: 18, fontWeight: FontWeight.bold)),
                  const SizedBox(height: 8),
                  Text(device.specifications ?? 'Không có thông tin'),
                  
                  const SizedBox(height: 16),
                  const Text('Mô tả', style: TextStyle(fontSize: 18, fontWeight: FontWeight.bold)),
                  const SizedBox(height: 8),
                  Text(device.description ?? 'Không có mô tả'),
                ],
              ),
            ),
          ],
        ),
      ),
    );
  }

  Widget _buildInfoRow(String label, String value) {
    return Padding(
      padding: const EdgeInsets.only(bottom: 12.0),
      child: Row(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          SizedBox(
            width: 120,
            child: Text(label, style: const TextStyle(color: Colors.grey, fontWeight: FontWeight.w500)),
          ),
          Expanded(
            child: Text(value, style: const TextStyle(fontWeight: FontWeight.w500)),
          ),
        ],
      ),
    );
  }
}
'''
with open("lib/screens/devices/device_detail_screen.dart", "w", encoding="utf-8") as f: f.write(dart_device_detail)

print("Setup completed successfully.")