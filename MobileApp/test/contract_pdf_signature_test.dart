import 'package:flutter_test/flutter_test.dart';
import 'package:quan_ly_cho_thue_thiet_bi/models/contract_model.dart';
import 'package:quan_ly_cho_thue_thiet_bi/services/contract_pdf_generator.dart';

void main() {
  TestWidgetsFlutterBinding.ensureInitialized();

  test('PDF uses each signature flag separately and handles missing flags', () async {
    for (final (customer, staff, customerLabel, staffLabel) in [
      (false, false, 'Chưa ký', 'Chưa ký'),
      (true, false, 'Đã ký', 'Chưa ký'),
      (false, true, 'Chưa ký', 'Đã ký'),
      (true, true, 'Đã ký', 'Đã ký'),
      (null, null, 'Chưa xác định', 'Chưa xác định'),
    ]) {
      final contract = ContractModel.fromJson({
        'id': '1',
        'status': 'Đang hiệu lực',
        'customerSigned': customer,
        'staffSigned': staff,
      });

      expect(ContractPdfGenerator.signatureLabel(contract.customerSigned), customerLabel);
      expect(ContractPdfGenerator.signatureLabel(contract.staffSigned), staffLabel);
      final pdf = await ContractPdfGenerator.generateContractPdf(contract);
      expect(String.fromCharCodes(pdf.take(5)), '%PDF-');
    }
  });
}
