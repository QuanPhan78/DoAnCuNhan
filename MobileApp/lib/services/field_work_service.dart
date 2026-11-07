import 'package:http/http.dart' as http;
import '../widgets/photo_field.dart';
import 'api_session.dart';
import 'customer_contract_service.dart';

class FieldWorkService {
  static Future<Map<String, dynamic>> handovers(String contractId) async => Map<String, dynamic>.from(
    CustomerContractService.decode(await ApiSession.get(CustomerContractService.url('/contracts/$contractId/handovers'))));

  static Future<void> handover(String contractId, int kind, String accessories, String condition,
      String notes, List<PickedPhoto> photos, String? signature) async {
    final request = http.MultipartRequest('POST', CustomerContractService.url('/contracts/$contractId/handovers'))
      ..fields.addAll({'kind': '$kind', 'accessories': accessories, 'condition': condition, 'notes': notes,
        'signatureData': signature ?? ''})
      ..files.addAll(photos.map((p) => http.MultipartFile.fromBytes('photos', p.bytes, filename: p.uploadName)));
    CustomerContractService.decode(await ApiSession.send(request));
  }

  static Future<void> evidence(String ticketId, PickedPhoto photo, String notes) async {
    final request = http.MultipartRequest('POST', CustomerContractService.url('/maintenance/$ticketId/evidence'))
      ..fields['notes'] = notes
      ..files.add(http.MultipartFile.fromBytes('image', photo.bytes, filename: photo.uploadName));
    CustomerContractService.decode(await ApiSession.send(request));
  }
}
