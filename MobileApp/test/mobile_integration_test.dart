import 'package:flutter_test/flutter_test.dart';
import 'package:quan_ly_cho_thue_thiet_bi/models/contract_model.dart';
import 'package:quan_ly_cho_thue_thiet_bi/models/rental_request_model.dart';
import 'package:quan_ly_cho_thue_thiet_bi/models/maintenance_model.dart';
import 'package:quan_ly_cho_thue_thiet_bi/models/device_model.dart';
import 'package:quan_ly_cho_thue_thiet_bi/models/rental_status.dart';

void main() {
  group('Mobile End-to-End Model & Data Contract Tests', () {
    test('ContractModel deserializes complete contract with item and timeline', () {
      final contractJson = {
        'id': '14',
        'contractCode': 'HD-0014',
        'customerName': 'Nguyễn Văn Khách',
        'customerPhone': '079200001234',
        'deviceName': 'Bộ PC Dell OptiPlex 7010',
        'deviceId': '1',
        'startDate': '2026-11-03T00:00:00',
        'endDate': '2026-12-03T00:00:00',
        'totalAmount': 3000000.0,
        'depositAmount': 1000000.0,
        'status': 'Chờ duyệt',
        'deliveryAddress': '140 Lê Trọng Tấn, Tân Phú, TP.HCM',
        'notes': 'Đơn thuê thử nghiệm từ Mobile E2E Runner'
      };

      final contract = ContractModel.fromJson(contractJson);
      expect(contract.id, equals('14'));
      expect(contract.contractCode, equals('HD-0014'));
      expect(contract.customerName, equals('Nguyễn Văn Khách'));
      expect(contract.totalAmount, equals(3000000.0));
      expect(contract.depositAmount, equals(1000000.0));
    });

    test('RentalRequestModel instantiates with multi-item structure and rentalType', () {
      final item = RentalRequestItem(
        deviceId: '1',
        deviceName: 'Bộ PC Dell OptiPlex 7010',
        quantity: 1,
        rentalPrice: 3000000.0,
        subtotal: 3000000.0,
      );

      final request = RentalRequestModel(
        id: 'REQ-001',
        customerId: '5',
        items: [item],
        rentalType: 'month',
        startDate: DateTime(2026, 11, 3),
        endDate: DateTime(2026, 12, 3),
        deliveryAddress: '140 Lê Trọng Tấn, Tân Phú',
        note: 'Giao giờ hành chính',
        estimatedAmount: 3000000.0,
        status: RentalStatus.pending,
        createdAt: DateTime.now(),
      );

      expect(request.customerId, equals('5'));
      expect(request.items.length, equals(1));
      expect(request.items.first.deviceId, equals('1'));
      expect(request.rentalType, equals('month'));
      expect(request.deliveryAddress, equals('140 Lê Trọng Tấn, Tân Phú'));
      expect(request.estimatedAmount, equals(3000000.0));
      expect(request.status, equals(RentalStatus.pending));
    });

    test('MaintenanceModel deserializes ticket payload from /api/maintenance', () {
      final ticketJson = {
        'id': '5',
        'contractId': '14',
        'deviceId': '1',
        'description': 'Máy khởi động bị màn hình xanh khi bật ứng dụng nặng',
        'status': 'Mới tiếp nhận',
        'createdAt': '2026-11-02T19:30:00'
      };

      final ticket = MaintenanceModel.fromJson(ticketJson);
      expect(ticket.id, equals('5'));
      expect(ticket.description, equals('Máy khởi động bị màn hình xanh khi bật ứng dụng nặng'));
      expect(ticket.status, equals('Mới tiếp nhận'));
      expect(ticket.contractId, equals('14'));
      expect(ticket.deviceId, equals('1'));
    });

    test('DeviceModel correctly parses API devices JSON with pricing and availability', () {
      final deviceJson = {
        'id': '1',
        'code': 'SP-0001',
        'name': 'Bộ PC Dell OptiPlex 7010',
        'type': 'Máy tính bàn',
        'brand': 'Chính hãng',
        'rentalStatus': 'Sẵn sàng',
        'rentalPrice': 150000.0,
        'specifications': 'Core i5-13500, 16GB RAM',
        'condition': 'Mới 99%',
        'description': 'Máy tính để bàn doanh nghiệp',
        'imageUrl': '/images/sanpham/may-tinh.png'
      };

      final device = DeviceModel.fromJson(deviceJson);
      expect(device.id, equals('1'));
      expect(device.name, equals('Bộ PC Dell OptiPlex 7010'));
      expect(device.rentalStatus, equals('Sẵn sàng'));
      expect(device.rentalPrice, equals(150000.0));
      expect(device.specifications, equals('Core i5-13500, 16GB RAM'));
      expect(device.condition, equals('Mới 99%'));
    });
  });
}
