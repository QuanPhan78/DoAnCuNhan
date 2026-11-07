"""Serve only synthetic phone data with existing VNPay Sandbox user-secrets.

The provider host is pinned to Sandbox. ENTER stops the server and drops only
the random database created by this process. No production settings are edited.
"""
import json
import os
from pathlib import Path
import re
import shutil
import socket
from uuid import uuid4

import cutover
import verify_debt_status as fixture


def main():
    secrets_path = Path(os.environ['APPDATA']) / 'Microsoft/UserSecrets/RentalSystem-Development-8af7464e-d2f7-4f43-8481-3c979a4567f3/secrets.json'
    secrets = json.loads(secrets_path.read_text(encoding='utf-8-sig'))
    if not all(secrets.get(k) for k in ('Vnpay:TmnCode', 'Vnpay:HashSecret')):
        raise RuntimeError('Existing VNPay user-secrets are incomplete; no settings changed.')
    name = 'RentalSystemNativeCheck_' + uuid4().hex[:12]
    out = cutover.ROOT / 'outputs/native-phone-sandbox-20261107'
    out.mkdir(exist_ok=True)
    (out / 'wwwroot').mkdir(exist_ok=True)
    for directory in ('css', 'js', 'lib'):
        source = cutover.ROOT / 'RentalSystem/wwwroot' / directory
        if source.exists():
            shutil.copytree(source, out / 'wwwroot' / directory, dirs_exist_ok=True)
    with socket.socket() as listener:
        listener.bind(('127.0.0.1', 0))
        port = listener.getsockname()[1]
    web = fixture.web
    web.DB, web.PORT, web.BASE, web.OUT = name, port, f'http://127.0.0.1:{port}', out
    os.environ.update({
        'Database__EnableBackgroundJobs': 'false',
        'BankTransfer__AccountNumber': '0000000000', 'BankTransfer__AccountName': 'TEST FIXTURE',
        'Vnpay__TmnCode': secrets['Vnpay:TmnCode'],
        'Vnpay__HashSecret': secrets['Vnpay:HashSecret'],
        'Vnpay__BaseUrl': 'https://sandbox.vnpayment.vn/paymentv2/vpcpay.html',
        'Vnpay__ReturnUrl': 'http://127.0.0.1:5000/Payment/PaymentCallback',
    })
    process = log = None
    created = False
    try:
        cutover.sql(f'CREATE DATABASE [{name}];')
        created = True
        for script in ('001_Baseline.sql', '002_MaintenanceAssignments.sql',
                       '003_FirstContractPayment.sql', '004_ContractSettlements.sql'):
            cutover.sql_file(cutover.SQL / script, name)
        cutover.sql(fixture.FIXTURE, name)
        cutover.sql("""
          INSERT dbo.NguoiDungs(MaVaiTro,HoTen,SoDienThoai,Email,MatKhau,CCCD,DiaChi,TrangThai)
          VALUES(2,N'Native Camera Sandbox Test',N'0900000099',N'native@demo.invalid',N'Demo@123',N'000000000099',N'Test fixture',1);
          INSERT dbo.HopDongs(MaKhachHang,MaNhanVien,NgayBatDau,NgayKetThuc,TienDaCoc,TongTien,
            TrangThai,SoKyHan,ChuKyKhachHang,ChuKyNhanVien,TrangThaiThanhToan,GhiChu,TrangThaiHoanCoc,
            YeuCauGiaHan,SoNgayGiaHan,YeuCauHuy,TienTraThua,TienGiamTruBaoTri,TienCocBaoDamMay,TienThueTraTruoc,YeuCauThanhToanLanDau)
          SELECT 4,1,CONVERT(date,GETDATE()),DATEADD(day,7,CONVERT(date,GETDATE())),0,10000,
            1,1,N'',N'',0,v.note,0,0,NULL,0,0,0,0,0,0
          FROM (VALUES(N'SANDBOX SUCCESS'),(N'NATIVE PHOTO RECEIPT'),(N'SANDBOX CANCEL'))v(note);
          INSERT dbo.KyHanThanhToans(MaHopDong,SoKyHan,NgayDenHan,SoTienPhai,SoTienDaTra,TrangThai,
            GhiChu,TrangThaiXacNhan,PhiPhatTreHan,TienPhat,SoNgayTreHan,NhomTuoiNo)
          SELECT MaHopDong,1,DATEADD(day,1,CONVERT(date,GETDATE())),10000,0,0,N'SYNTHETIC SANDBOX ONLY',0,0,0,0,0
          FROM dbo.HopDongs WHERE MaKhachHang=4;
          """, name)
        process, log = web.start_server()
        client = web.Session()
        client.api_login('native@demo.invalid')
        rows = client.get_json('/api/debts')
        metadata = {'database': name, 'port': port, 'pid': process.pid,
                    'customer': 'native@demo.invalid', 'provider': 'sandbox.vnpayment.vn',
                    'contracts': [{k: r[k] for k in ('id', 'contractId', 'balance', 'canVnPay')} for r in rows]}
        (out / 'session.json').write_text(json.dumps(metadata, indent=2), encoding='utf-8')
        print('NATIVE_PHONE_READY ' + json.dumps(metadata), flush=True)
        input('Press ENTER after native phone testing to stop and remove this synthetic database.\n')
    finally:
        web.stop_server(process, log)
        if created:
            if not re.fullmatch(r'RentalSystemNativeCheck_[a-f0-9]{12}', name):
                raise RuntimeError('Unexpected fixture name; automatic cleanup refused.')
            cutover.sql(f'ALTER DATABASE [{name}] SET SINGLE_USER WITH ROLLBACK IMMEDIATE; DROP DATABASE [{name}];')
            print('Synthetic native-phone database removed.', flush=True)


if __name__ == '__main__':
    main()
