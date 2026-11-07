"""Exercise customer/technician parity over HTTP against a disposable database only."""
from base64 import b64encode
from datetime import date, timedelta
import json
import os
from urllib.error import HTTPError
from urllib.request import Request
from uuid import uuid4

import cutover
import verify_debt_status as fixture
from verify_customer_maintenance import PNG

web = fixture.web
check = web.require


def upload(session, path, fields, files):
    boundary = uuid4().hex
    parts = [f'--{boundary}\r\nContent-Disposition: form-data; name="{k}"\r\n\r\n{v}\r\n'.encode()
             for k, v in fields.items()]
    for name, content in files:
        parts.append((f'--{boundary}\r\nContent-Disposition: form-data; name="{name}"; filename="fixture.png"\r\n'
                      'Content-Type: image/png\r\n\r\n').encode() + content + b'\r\n')
    parts.append(f'--{boundary}--\r\n'.encode())
    return json.loads(session.request(path, b''.join(parts), 'POST', f'multipart/form-data; boundary={boundary}')[0])


def denied(action, status, name):
    try:
        action()
    except HTTPError as error:
        check(error.code == status, f'{name}: HTTP {status} (got {error.code})')
    else:
        raise AssertionError(f'{name}: expected HTTP {status}')


def private_file(session, path):
    request = Request(web.BASE + path)
    if session.access_token:
        request.add_header('Authorization', 'Bearer ' + session.access_token)
    with session.opener.open(request, timeout=30) as response:
        return response.read(), response.url, response.headers


def verify(db, _secret):
    sql = lambda query: cutover.sql("SET QUOTED_IDENTIFIER ON;\n" + query, db)
    sql("""
        INSERT dbo.VaiTros(TenVaiTro) VALUES(N'KyThuat'),(N'KinhDoanh');
        INSERT dbo.NguoiDungs(MaVaiTro,HoTen,SoDienThoai,Email,MatKhau,CCCD,DiaChi,TrangThai)
        VALUES (2,N'Mobile Customer',N'0900000004',N'mobile@demo.invalid',N'Demo@123',N'000000000004',N'Fixture',1),
               (3,N'Assigned Technician',N'0900000005',N'tech@demo.invalid',N'Demo@123',N'000000000005',N'',1),
               (3,N'Other Technician',N'0900000006',N'othertech@demo.invalid',N'Demo@123',N'000000000006',N'',1),
               (4,N'Sales',N'0900000007',N'sales@demo.invalid',N'Demo@123',N'000000000007',N'',1);
        INSERT dbo.SanPhams(MaLoai,TenSanPham,CauHinh,MoTa,GiaThueNgay,TienCoc,HinhAnh)
        VALUES (1,N'Laptop',N'',N'',100000,300000,N''),(1,N'Monitor',N'',N'',50000,100000,N'');
        INSERT dbo.ThietBis(MaSanPham,SoSerial,TinhTrangMay,TrangThai)
        VALUES (2,N'MOBILE-LAP',N'',0),(3,N'MOBILE-MON',N'',0);
        """)
    app, other, tech, second, guest, admin, desktop, tech_web = (web.Session() for _ in range(8))
    for session, email in ((app, 'mobile'), (other, 'threshold'), (tech, 'tech'), (second, 'othertech')):
        session.api_login(email + '@demo.invalid')
    admin.login('admin@demo.invalid')
    desktop.login('mobile@demo.invalid')
    tech_web.login('tech@demo.invalid')
    today = date.fromisoformat(sql('SELECT CONVERT(varchar(10),GETDATE(),23);'))
    order = dict(startDate=today.isoformat(), endDate=(today + timedelta(days=14)).isoformat(),
                 deliveryAddress='Fixture address', items=[{'productId': 2, 'quantity': 1}, {'productId': 3, 'quantity': 1}])
    quote = app.send_json('/api/contracts/quote', order)
    check(quote['totalAmount'] == 2100000 and quote['depositAmount'] == 400000,
          'Server prices a two-device cart and computes its deposit')
    created = app.send_json('/api/contracts', dict(order, expectedTotal=quote['totalAmount']))
    cid = int(created['contractId'])
    check(app.get_json(f'/api/contracts/{cid}')['depositRequired'] == 400000,
          'Contract returns required deposit separately from money collected')
    detail = f'/Cart/ContractDetail/{cid}'
    admin_detail = f'/Admin/HopDong/Details/{cid}'
    signature = 'data:image/png;base64,' + b64encode(PNG).decode()
    denied(lambda: other.get_json(f'/api/contracts/{cid}/sign'), 404, 'Other customer cannot sign')
    denied(lambda: tech.get_json('/api/debts'), 403, 'Technician cannot access customer finance')
    denied(lambda: upload(app, f'/api/contracts/{cid}/sign', {'signatureData': signature}, [('front', PNG)]),
           400, 'Signing requires both identity sides')
    check(sql(f'SELECT COUNT(*) FROM dbo.KyHanThanhToans WHERE MaHopDong={cid};') == '0',
          'Rejected signing creates no installments')
    check(upload(app, f'/api/contracts/{cid}/sign', {'signatureData': signature, 'installments': 2},
                 [('front', PNG), ('back', PNG)])['success'], 'Customer signs directly on Mobile API')
    denied(lambda: upload(app, f'/api/contracts/{cid}/sign', {'signatureData': signature}, [('front', PNG), ('back', PNG)]),
           409, 'An already signed contract cannot be signed again')
    check(app.get_json(f'/api/contracts/{cid}')['customerSigned'], 'Signed status is read back from server')
    identity = sql(f'SELECT AnhCCCD_Truoc FROM dbo.HopDongs WHERE MaHopDong={cid};')
    denied(lambda: private_file(guest, identity), 401, 'Identity images require authentication')
    denied(lambda: private_file(other, identity), 404, 'Other customer cannot fetch identity image')
    denied(lambda: private_file(tech, identity), 403, 'Technician cannot fetch identity image')
    check(private_file(app, identity)[0] == PNG and private_file(desktop, identity)[0] == PNG,
          'API owner and Web owner both retrieve their protected identity image')
    debt = next(r for r in app.get_json('/api/debts') if r['contractId'] == cid and r['period'] == 1)
    kid = debt['id']
    check(debt['balance'] == 1450000 and debt['bank']['accountNumber'] == '0000000000' and
          debt['reference'] == f'HD{cid} LD' and not debt['canVnPay'],
          'First payment combines deposit and first rent period using configured bank details')
    check('0000000000' in desktop.request(detail)[0].decode(), 'Web and Mobile use the same bank configuration')
    before = sql(f'SELECT COUNT(*) FROM dbo.PhieuThus WHERE MaHopDong={cid};')
    upload(app, f'/api/debts/{kid}/receipt', {'reference': 'FIRST-PROOF'}, [('image', PNG)])
    check(sql(f'SELECT COUNT(*) FROM dbo.PhieuThus WHERE MaHopDong={cid};') == before and
          app.get_json('/api/debts')[0] is not None,
          'Submitting a proof does not create a receipt or claim money collected')
    denied(lambda: upload(app, f'/api/debts/{kid}/receipt', {'reference': 'DUPLICATE'}, [('image', PNG)]),
           409, 'A pending proof cannot be overwritten')
    denied(lambda: upload(other, f'/api/debts/{kid}/receipt', {'reference': 'OTHER'}, [('image', PNG)]),
           404, 'Receipt upload enforces installment ownership')
    admin.form('/Admin/HopDong/UpdateStatus', {'id': cid, 'status': 1}, admin_detail)
    check(sql(f'SELECT TrangThai FROM dbo.HopDongs WHERE MaHopDong={cid};') == '0',
          'Unsigned staff or unpaid first balance blocks handover')
    admin.form('/Admin/HopDong/AdminSign', {'id': cid, 'signatureData': signature}, admin_detail)
    admin.form('/Admin/HopDong/XacNhanThanhToanLanDau', {'id': cid, 'soTien': debt['balance'], 'maGiaoDich': 'CONFIRMED-FIRST'}, admin_detail)
    admin.form('/Admin/HopDong/UpdateStatus', {'id': cid, 'status': 1}, admin_detail)
    check(app.get_json(f'/api/contracts/{cid}')['statusCode'] == 1, 'Web confirmation and delivery synchronize to Mobile')
    denied(lambda: app.send_json(f'/api/contracts/{cid}/renew', {'days': 0}), 400, 'Zero-day renewal rejected')
    denied(lambda: app.send_json(f'/api/contracts/{cid}/renew', {'duration': '1 tháng'}), 400, 'Ambiguous legacy duration rejected')
    renewal = app.send_json(f'/api/contracts/{cid}/renew', {'days': 7, 'notes': 'More time'})
    check(renewal['days'] == 7 and sql(f'SELECT COUNT(*) FROM dbo.YeuCauGiaHans WHERE MaHopDong={cid} AND TrangThai=0;') == '1',
          'Mobile renewal appears in the actual Web approval queue')
    denied(lambda: app.send_json(f'/api/contracts/{cid}/renew', {'days': 7}), 409, 'Repeated pending renewal rejected')
    desktop.form('/Cart/YeuCauGiaHan', {'id': cid, 'soNgayGiaHan': 7, 'lyDo': 'Duplicate from Web'}, detail)
    check(len(app.get_json(f'/api/contracts/{cid}/renewals')) == 1, 'Web and Mobile share duplicate protection')
    admin.form('/Admin/HopDong/DuyetGiaHan', {'id': cid, 'chapNhan': 'true'}, admin_detail)
    check(app.get_json(f'/api/contracts/{cid}/renewals')[0]['statusCode'] == 1 and
          sql(f'SELECT COUNT(*) FROM dbo.KyHanThanhToans WHERE MaHopDong={cid};') == '3',
          'Approval extends the contract and adds exactly one installment')
    denied(lambda: tech.get_json(f'/api/contracts/{cid}/handovers'), 404, 'Unassigned technician cannot view handovers')
    sql(f"""INSERT dbo.PhanCongCongViecs(MaHopDong,MaNhanVien,MaNguoiGiao,TieuDe,NoiDung,NgayGiao,TrangThai,TuDongTuBaoTri)
            VALUES({cid},5,1,N'Lắp đặt',N'Fixture',GETDATE(),0,0);""")
    check(tech.get_json(f'/api/contracts/{cid}')['id'] == str(cid), 'Assigned delivery task grants scoped contract access')
    denied(lambda: second.get_json(f'/api/contracts/{cid}/handovers'), 404, 'Another technician remains denied')
    result = upload(tech, f'/api/contracts/{cid}/handovers', {'kind': 0, 'condition': 'Checked', 'accessories': 'Charger'}, [('photos', PNG)])
    records = tech.get_json(f'/api/contracts/{cid}/handovers')['records']
    record = next(r for r in records if r['id'] == result['id'])
    check(private_file(tech, record['photos'][0])[0] == PNG and private_file(app, record['photos'][0])[0] == PNG,
          'Technician records equipment evidence visible to customer')
    denied(lambda: private_file(second, record['photos'][0]), 404, 'Other technician cannot retrieve protected equipment image')
    tech_html = tech_web.request(admin_detail)[0].decode()
    check(identity not in tech_html and '000000000004' not in tech_html,
          'Technician Web detail omits identity images and number')
    count = sql(f'SELECT COUNT(*) FROM dbo.PhieuThus WHERE MaHopDong={cid};')
    desktop.form('/Cart/TatToanSom', {'maHopDong': cid}, detail)
    check(sql(f'SELECT COUNT(*) FROM dbo.PhieuThus WHERE MaHopDong={cid};') == count,
          'Customer cannot self-confirm collection through Web settlement shortcut')
    period = next(r for r in app.get_json('/api/debts') if r['contractId'] == cid and r['period'] == 2)
    denied(lambda: tech.send_json(f"/api/debts/{period['id']}/vnpay", {}), 403, 'Technician cannot create payment sessions')
    # A complete/duplicate approval produces only one financial receipt.
    upload(app, f"/api/debts/{period['id']}/receipt", {'reference': 'PERIOD-TWO'}, [('image', PNG)])
    for _ in range(2):
        admin.form('/Admin/HopDong/DuyetBienLai', {'maKyHan': period['id'], 'chapNhan': 'true'}, admin_detail)
    check(sql(f"SELECT COUNT(*) FROM dbo.PhieuThus WHERE MaGiaoDichNganHang=N'PERIOD-TWO';") == '1',
          'Repeated Web proof approval cannot double-book collected money')


if __name__ == '__main__':
    os.environ['BankTransfer__AccountNumber'] = '0000000000'
    os.environ['BankTransfer__AccountName'] = 'TEST FIXTURE'
    fixture.check_flows = verify
    fixture.main()
