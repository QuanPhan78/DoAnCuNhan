import 'package:flutter/services.dart';
import 'package:intl/intl.dart';
import 'package:pdf/pdf.dart';
import 'package:pdf/widgets.dart' as pw;
import '../models/contract_model.dart';

class ContractPdfGenerator {
  static String signatureLabel(bool? signed) => switch (signed) {
    true => 'Đã ký',
    false => 'Chưa ký',
    null => 'Chưa xác định',
  };

  static Future<Uint8List> generateContractPdf(ContractModel contract) async {
    final pdf = pw.Document();

    // Nạp Font chữ Times New Roman hỗ trợ 100% tiếng Việt Unicode
    final fontData = await rootBundle.load('assets/fonts/times.ttf');
    final ttfRegular = pw.Font.ttf(fontData);

    final fontBoldData = await rootBundle.load('assets/fonts/timesbd.ttf');
    final ttfBold = pw.Font.ttf(fontBoldData);

    final currencyFormat = NumberFormat('#,###', 'vi_VN');

    final totalFormatted = currencyFormat.format(contract.totalAmount ?? 0);
    final depositFormatted = currencyFormat.format(contract.depositAmount ?? 0);

    final deviceList = (contract.deviceIds != null && contract.deviceIds!.isNotEmpty)
        ? contract.deviceIds!
        : ['Thiết bị điện tử tiêu chuẩn'];

    pdf.addPage(
      pw.Page(
        pageFormat: PdfPageFormat.a4,
        margin: const pw.EdgeInsets.symmetric(horizontal: 24, vertical: 20),
        theme: pw.ThemeData.withFont(
          base: ttfRegular,
          bold: ttfBold,
        ),
        build: (pw.Context context) {
          return pw.Column(
            crossAxisAlignment: pw.CrossAxisAlignment.start,
            mainAxisAlignment: pw.MainAxisAlignment.spaceBetween,
            children: [
              // 1. Quốc hiệu Tiêu ngữ & Tiêu đề hợp đồng
              pw.Column(
                crossAxisAlignment: pw.CrossAxisAlignment.center,
                children: [
                  pw.Text(
                    'CỘNG HOÀ XÃ HỘI CHỦ NGHĨA VIỆT NAM',
                    style: pw.TextStyle(font: ttfBold, fontSize: 12),
                  ),
                  pw.SizedBox(height: 2),
                  pw.Text(
                    'Độc lập - Tự do - Hạnh phúc',
                    style: pw.TextStyle(
                      font: ttfBold,
                      fontSize: 11,
                      decoration: pw.TextDecoration.underline,
                    ),
                  ),
                  pw.SizedBox(height: 6),
                  pw.Align(
                    alignment: pw.Alignment.centerRight,
                    child: pw.Text(
                      'BẢN XEM TRƯỚC',
                      style: pw.TextStyle(font: ttfRegular, fontSize: 9.5, fontStyle: pw.FontStyle.italic),
                    ),
                  ),
                  pw.SizedBox(height: 8),
                  pw.Text(
                    'HỢP ĐỒNG THUÊ THIẾT BỊ',
                    style: pw.TextStyle(font: ttfBold, fontSize: 15),
                  ),
                  pw.SizedBox(height: 2),
                  pw.Text(
                    'Số: ${contract.contractCode ?? "HD-${contract.id}"}/HĐTTB-ABCRENTAL',
                    style: pw.TextStyle(font: ttfBold, fontSize: 10.5),
                  ),
                  pw.SizedBox(height: 8),
                ],
              ),

              // 2. Căn cứ pháp lý
              pw.Text(
                '- Căn cứ Bộ luật Dân sự số 91/2015/QH13 ngày 24/11/2015 của Quốc hội;\n'
                '- Căn cứ Luật Thương mại số 36/2005/QH11 ngày 14/6/2005 của Quốc hội;\n'
                '- Căn cứ vào thỏa thuận và nhu cầu thực tế của hai bên.',
                style: pw.TextStyle(font: ttfRegular, fontSize: 9.5, fontStyle: pw.FontStyle.italic),
              ),
              pw.SizedBox(height: 8),

              // 3. Thông tin Hai bên (Bên A & Bên B)
              pw.Row(
                crossAxisAlignment: pw.CrossAxisAlignment.start,
                children: [
                  pw.Expanded(
                    child: pw.Column(
                      crossAxisAlignment: pw.CrossAxisAlignment.start,
                      children: [
                        pw.Text('BÊN A (BÊN THUÊ):', style: pw.TextStyle(font: ttfBold, fontSize: 10.5)),
                        pw.SizedBox(height: 3),
                        pw.Text('• Ông/Bà: ${contract.customerName ?? "Khách hàng"}', style: const pw.TextStyle(fontSize: 9.5)),
                        pw.SizedBox(height: 2),
                        pw.Text('• SĐT: ${contract.customerPhone ?? "Chưa cập nhật"}', style: const pw.TextStyle(fontSize: 9.5)),
                        pw.SizedBox(height: 2),
                        pw.Text('• Nơi nhận: ${contract.note ?? "Tại quầy giao dịch ABC Rental"}', style: const pw.TextStyle(fontSize: 9.5)),
                      ],
                    ),
                  ),
                  pw.SizedBox(width: 14),
                  pw.Expanded(
                    child: pw.Column(
                      crossAxisAlignment: pw.CrossAxisAlignment.start,
                      children: [
                        pw.Text('BÊN B (BÊN CHO THUÊ): ABC RENTAL', style: pw.TextStyle(font: ttfBold, fontSize: 10.5)),
                        pw.SizedBox(height: 3),
                        pw.Text('• Đại diện: Bộ phận Quản lý & Kinh Doanh', style: const pw.TextStyle(fontSize: 9.5)),
                        pw.SizedBox(height: 2),
                        pw.Text('• Địa chỉ: 123 Đường ABC, Quận X, TP.HCM', style: const pw.TextStyle(fontSize: 9.5)),
                        pw.SizedBox(height: 2),
                        pw.Text('• Hotline: 1900 1234  |  support@abcrental.vn', style: const pw.TextStyle(fontSize: 9.5)),
                      ],
                    ),
                  ),
                ],
              ),
              pw.SizedBox(height: 8),

              // 4. Điều 1: Danh sách thiết bị
              pw.Text('ĐIỀU 1: DANH MỤC VÀ CẤU HÌNH THIẾT BỊ CHO THUÊ', style: pw.TextStyle(font: ttfBold, fontSize: 10.5)),
              pw.SizedBox(height: 4),
              pw.Table(
                border: pw.TableBorder.all(color: PdfColors.black, width: 0.5),
                children: [
                  pw.TableRow(
                    decoration: const pw.BoxDecoration(color: PdfColors.grey200),
                    children: [
                      _buildCell('STT', isHeader: true, align: pw.TextAlign.center),
                      _buildCell('Tên Thiết Bị / Cấu hình & Số Serial', isHeader: true),
                      _buildCell('Thời hạn thuê', isHeader: true, align: pw.TextAlign.center),
                      _buildCell('Thành tiền', isHeader: true, align: pw.TextAlign.right),
                    ],
                  ),
                  ...deviceList.asMap().entries.map((entry) {
                    final idx = entry.key + 1;
                    final dev = entry.value;
                    return pw.TableRow(
                      children: [
                        _buildCell('$idx', align: pw.TextAlign.center),
                        _buildCell(dev),
                        _buildCell('${contract.rentalStart ?? ""} - ${contract.rentalEnd ?? ""}', align: pw.TextAlign.center),
                        _buildCell('$totalFormatted đ', align: pw.TextAlign.right),
                      ],
                    );
                  }),
                ],
              ),
              pw.SizedBox(height: 4),
              pw.Align(
                alignment: pw.Alignment.centerRight,
                child: pw.Text(
                  'Tổng giá trị hợp đồng: $totalFormatted VNĐ',
                  style: pw.TextStyle(font: ttfBold, fontSize: 11),
                ),
              ),
              pw.SizedBox(height: 6),

              // 5. Điều 2: Phương thức thanh toán & đặt cọc
              pw.Text('ĐIỀU 2: PHƯƠNG THỨC THANH TOÁN & ĐẶT CỌC', style: pw.TextStyle(font: ttfBold, fontSize: 10.5)),
              pw.SizedBox(height: 2),
              pw.Text(
                '1. Tiền đặt cọc: Bên A thanh toán cho Bên B số tiền cọc là: $depositFormatted VNĐ ngay khi ký hợp đồng và nhận bàn giao.\n'
                '2. Thanh toán: Tiền mặt hoặc chuyển khoản qua ngân hàng / cổng thanh toán tích hợp trên ứng dụng.\n'
                '3. Hoàn cọc: Bên B hoàn trả 100% tiền đặt cọc cho Bên A sau khi thu hồi thiết bị đầy đủ phụ kiện và nguyên vẹn.',
                style: const pw.TextStyle(fontSize: 9.5),
              ),
              pw.SizedBox(height: 6),

              // 6. Điều 3: Thời hạn & Địa điểm
              pw.Text('ĐIỀU 3: THỜI HẠN VÀ ĐỊA ĐIỂM BÀN GIAO THIẾT BỊ', style: pw.TextStyle(font: ttfBold, fontSize: 10.5)),
              pw.SizedBox(height: 2),
              pw.Text(
                '• Thời gian bắt đầu: ${contract.rentalStart ?? "Chưa xác định"}  |  Thời gian kết thúc: ${contract.rentalEnd ?? "Chưa xác định"}\n'
                '• Địa điểm giao nhận: ${contract.note ?? "Tại quầy giao dịch ABC Rental"}',
                style: const pw.TextStyle(fontSize: 9.5),
              ),
              pw.SizedBox(height: 6),

              // 7. Điều 4: Trách nhiệm mỗi bên
              pw.Text('ĐIỀU 4: TRÁCH NHIỆM CỦA MỖI BÊN', style: pw.TextStyle(font: ttfBold, fontSize: 10.5)),
              pw.SizedBox(height: 2),
              pw.Text(
                '• Trách nhiệm Bên A: Bảo quản thiết bị trong suốt quá trình thuê; không tự ý tháo dỡ, thay thế linh kiện máy; chịu trách nhiệm bồi thường nếu làm mất mát hoặc hư hỏng do bất cẩn; hoàn trả thiết bị đúng thời hạn đã cam kết.\n'
                '• Trách nhiệm Bên B: Bàn giao thiết bị đúng chủng loại, cấu hình và hoạt động tốt; hỗ trợ kỹ thuật và đổi máy thay thế nếu phát sinh lỗi kỹ thuật từ nhà sản xuất; hoàn cọc đầy đủ cho Bên A khi kết thúc hợp đồng.',
                style: const pw.TextStyle(fontSize: 9.5),
              ),
              pw.SizedBox(height: 6),

              // 8. Điều 5: Điều khoản chung
              pw.Text('ĐIỀU 5: ĐIỀU KHOẢN CHUNG & HIỆU LỰC HỢP ĐỒNG', style: pw.TextStyle(font: ttfBold, fontSize: 10.5)),
              pw.SizedBox(height: 2),
              pw.Text(
                'Hai bên thực hiện các điều khoản đã thỏa thuận trong hồ sơ hợp đồng.',
                style: const pw.TextStyle(fontSize: 9.5),
              ),
              pw.SizedBox(height: 10),

              // 9. Trạng thái chữ ký của hai bên
              pw.Row(
                mainAxisAlignment: pw.MainAxisAlignment.spaceBetween,
                crossAxisAlignment: pw.CrossAxisAlignment.start,
                children: [
                  pw.Container(
                    width: 240,
                    child: pw.Column(
                      crossAxisAlignment: pw.CrossAxisAlignment.center,
                      children: [
                        pw.Text('ĐẠI DIỆN BÊN A (BÊN THUÊ)', style: pw.TextStyle(font: ttfBold, fontSize: 10.5)),
                        pw.SizedBox(height: 2),
                        pw.SizedBox(height: 8),
                        pw.Text(signatureLabel(contract.customerSigned), style: pw.TextStyle(font: ttfBold, fontSize: 9)),
                        pw.SizedBox(height: 4),
                        pw.Text(contract.customerName ?? "Khách hàng", style: pw.TextStyle(font: ttfBold, fontSize: 10)),
                      ],
                    ),
                  ),
                  pw.Container(
                    width: 240,
                    child: pw.Column(
                      crossAxisAlignment: pw.CrossAxisAlignment.center,
                      children: [
                        pw.Text('ĐẠI DIỆN BÊN B (ABC RENTAL)', style: pw.TextStyle(font: ttfBold, fontSize: 10.5)),
                        pw.SizedBox(height: 2),
                        pw.SizedBox(height: 8),
                        pw.Text(signatureLabel(contract.staffSigned), style: pw.TextStyle(font: ttfBold, fontSize: 9)),
                        pw.SizedBox(height: 4),
                        pw.Text('Đại diện Hệ thống ABC Rental', style: pw.TextStyle(font: ttfBold, fontSize: 10)),
                      ],
                    ),
                  ),
                ],
              ),
            ],
          );
        },
      ),
    );

    return pdf.save();
  }

  static pw.Widget _buildCell(
    String text, {
    bool isHeader = false,
    pw.TextAlign align = pw.TextAlign.left,
  }) {
    return pw.Padding(
      padding: const pw.EdgeInsets.symmetric(horizontal: 6, vertical: 5),
      child: pw.Text(
        text,
        textAlign: align,
        style: pw.TextStyle(
          fontSize: isHeader ? 10 : 9.5,
          fontWeight: isHeader ? pw.FontWeight.bold : pw.FontWeight.normal,
        ),
      ),
    );
  }
}
