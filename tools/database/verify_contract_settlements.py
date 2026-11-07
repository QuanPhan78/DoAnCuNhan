"""Settlement regression tests on an owned disposable schema-004 database."""
from concurrent.futures import ThreadPoolExecutor
from urllib.error import HTTPError
import json
import cutover
import verify_debt_status as fixture

web=fixture.web
check=web.require

def verify(db,_secret):
    assert db.startswith('RentalSystemDebtCheck_')
    sql=lambda query:cutover.sql(query,db)
    admin=web.Session();admin.login('admin@demo.invalid')
    def new(deposit=500000,rent=1000000,paid=800000,state=4):
        cid=int(sql(f"""INSERT dbo.HopDongs(MaKhachHang,MaNhanVien,NgayBatDau,NgayKetThuc,TienDaCoc,TongTien,
        TrangThai,SoKyHan,ChuKyKhachHang,ChuKyNhanVien,TrangThaiThanhToan,GhiChu,TrangThaiHoanCoc,
        YeuCauGiaHan,YeuCauHuy,TienTraThua,TienGiamTruBaoTri,TienCocBaoDamMay,TienThueTraTruoc,YeuCauThanhToanLanDau)
        OUTPUT INSERTED.MaHopDong VALUES(2,1,CONVERT(date,GETDATE()),DATEADD(day,20,CONVERT(date,GETDATE())),{deposit},{rent},
        {state},1,N'fixture',N'fixture',2,N'Settlement test',0,0,0,0,0,9000000,0,1);"""))
        sql(f"""INSERT dbo.KyHanThanhToans(MaHopDong,SoKyHan,NgayDenHan,SoTienPhai,SoTienDaTra,TrangThai,GhiChu,TrangThaiXacNhan,PhiPhatTreHan,TienPhat,SoNgayTreHan,NhomTuoiNo)
        VALUES({cid},1,GETDATE(),{rent},{paid},0,N'Fixture',0,0,0,0,0);
        INSERT dbo.PhieuThus(MaHopDong,LoaiPhieu,SoTien,NgayGiaoDich,HinhThucThanhToan,GhiChu,DaHuy)
        VALUES({cid},1,{deposit},GETDATE(),1,N'Collected deposit',0),({cid},0,{paid},GETDATE(),1,N'Collected rent',0);""")
        return cid
    def preview(cid,kind=0,**extra):
        from urllib.parse import urlencode
        return admin.get_json('/Admin/HopDong/SettlementPreview?'+urlencode({'id':cid,'kind':kind,**extra}))
    def post(cid,token=None,session=admin,**extra):
        return session.form('/Admin/HopDong/UpdateStatus',{'id':cid,'status':2,'settlementToken':token if token is not None else preview(cid)['token'],**extra},f'/Admin/HopDong/Details/{cid}')
    def stats(cid):
        return sql(f"SELECT (SELECT COUNT(*) FROM dbo.ContractSettlements WHERE MaHopDong={cid}), (SELECT COUNT(*) FROM dbo.PhieuChis WHERE MaHopDong={cid}),TrangThai FROM dbo.HopDongs WHERE MaHopDong={cid};")
    cid=new()
    admin.form('/Admin/HopDong/HoanCoc',{'id':cid,'soTienHoan':600000},f'/Admin/HopDong/Details/{cid}')
    check(stats(cid)=='0|0|4','Legacy standalone refund cannot disburse 600000 against a 500000 deposit')
    q=preview(cid)
    check(q['depositReceived']==500000 and q['depositToRent']==200000 and q['refundDeposit']==300000,'Actual receipt controls deposit: 500000 less 200000 rent refunds 300000')
    post(cid,q['token'],soTienHoan=600000)
    check(stats(cid)=='1|1|2' and sql(f'SELECT SoTien FROM dbo.PhieuChis WHERE MaHopDong={cid};')=='300000.00','Server ignores client refund amount and writes one atomic settlement')
    post(cid,q['token']);admin.form('/Admin/HopDong/HoanCoc',{'id':cid,'soTienHoan':600000},f'/Admin/HopDong/Details/{cid}')
    check(stats(cid)=='1|1|2','Repeated finalization and legacy refund add no disbursement')
    check(preview(cid)['completed'] and preview(cid)['additionalDue']==0,'Completed preview remains readable')
    receipt=int(sql(f'SELECT TOP 1 MaPhieuThu FROM dbo.PhieuThus WHERE MaHopDong={cid} ORDER BY MaPhieuThu;'))
    admin.form('/Admin/HopDong/HuyPhieuThu',{'maPhieuThu':receipt,'lyDoHuy':'Post-settlement probe'},f'/Admin/HopDong/Details/{cid}')
    check(sql(f'SELECT DaHuy FROM dbo.PhieuThus WHERE MaPhieuThu={receipt};')=='0','Settled deposit receipt cannot be voided')
    before=sql(f'SELECT COUNT(*) FROM dbo.PhieuThus WHERE MaHopDong={cid};')
    admin.form('/Admin/HopDong/ThemTienCoc',{'maHopDong':cid,'soTienCoc':100000,'hinhThuc':1,'ghiChu':'Post-settlement probe'},f'/Admin/HopDong/Details/{cid}')
    check(sql(f'SELECT COUNT(*) FROM dbo.PhieuThus WHERE MaHopDong={cid};')==before,'Closed settlement cannot collect extra rental money')
    import hashlib,hmac
    from urllib.parse import urlencode
    period=int(sql(f'SELECT TOP 1 MaKyHan FROM dbo.KyHanThanhToans WHERE MaHopDong={cid};'))
    query=urlencode(sorted({'vnp_Amount':10000000,'vnp_ResponseCode':'00','vnp_TransactionNo':'late-settlement-fixture','vnp_TxnRef':f'{cid}_{period}'}.items()))
    signature=hmac.new(_secret.encode(),query.encode(),hashlib.sha512).hexdigest()
    response=admin.get_json('/Payment/VnPayIPN?'+query+'&vnp_SecureHash='+signature)
    check(response['rspCode']=='02' and sql(f'SELECT COUNT(*) FROM dbo.PhieuThus WHERE MaHopDong={cid};')==before,
          'Late VNPay callback cannot append receipts to a completed settlement')
    owner=web.Session();owner.login('customer@demo.invalid')
    check('/Cart/ContractDetail/' in owner.request(f'/Payment/CreatePaymentUrl?maHopDong={cid}&soTien=100000')[1],
          'Completed settlement cannot create a new VNPay checkout URL')

    damage=new(paid=1000000)
    sql(f"""INSERT dbo.PhieuBaoTris(MaHopDong,MaThietBi,MoTaLoi,NgayBaoLoi,GhiChuSuaChua,PhiDenBu,TrangThai,DaGhiNhanCongNo,DaNghiemThu,TamDungTinhTien,DaTruTien)
    VALUES({damage},1,N'Fixture damage',GETDATE(),N'Done',200000,5,1,1,0,0);""")
    post(damage)
    check(sql(f'SELECT CocCanTruBoiThuong,HoanCoc FROM dbo.ContractSettlements WHERE MaHopDong={damage};')=='200000.00|300000.00','Deposit offsets damages once and refunds the correct remainder')
    absent=new();post(absent,'')
    check(stats(absent)=='0|0|4','Missing preview confirmation cannot disburse money')

    zero=new(0,1000000,1000000);post(zero)
    check(stats(zero)=='1|0|2','Zero deposit settles without a refund receipt')
    full=new(500000,1000000,500000);post(full)
    check(stats(full)=='1|0|2' and sql(f'SELECT CocCanTruThue FROM dbo.ContractSettlements WHERE MaHopDong={full};')=='500000.00','Deposit fully offsets rent with no cash refund')
    short=new(100000,1000000,800000);post(short)
    check(stats(short)=='0|0|4' and preview(short)['additionalDue']==100000,'Insufficient credit stays pending with the correct additional collection')
    partial=new(500000,1000000,900000)
    sql(f"INSERT dbo.PhieuChis(MaHopDong,LoaiChi,SoTien,NgayChi,HinhThucChi,MaNhanVienChi,GhiChu) VALUES({partial},0,200000,GETDATE(),1,1,N'Previous deposit refund'); UPDATE dbo.HopDongs SET TienCocThucHoan=200000 WHERE MaHopDong={partial};")
    check(preview(partial)['refundDeposit']==200000,'Prior refund is deducted from the deposit before allocation')
    post(partial)
    check(sql(f'SELECT SUM(SoTien) FROM dbo.PhieuChis WHERE MaHopDong={partial} AND LoaiChi=0;')=='400000.00','Previous 200000 plus new 200000 refund does not double-use the deposit')
    void=new(0,1000000,1000000)
    sql(f'UPDATE dbo.PhieuThus SET SoTien=500000,DaHuy=1 WHERE MaHopDong={void} AND LoaiPhieu=1;')
    post(void)
    check(stats(void)=='1|0|2','Voided deposit receipt is never refundable, even when required deposit is larger')
    missing=new();sql(f'DELETE dbo.PhieuThus WHERE MaHopDong={missing} AND LoaiPhieu=1;')
    post(missing)
    check(stats(missing)=='0|0|4' and preview(missing)['error'],'Legacy deposit without receipt requires reconciliation')
    history=new(state=2);post(history)
    check(stats(history)=='0|0|2','Historical closed contract is not settled again or backfilled')
    stale=new();token=preview(stale)['token']
    sql(f'UPDATE dbo.PhieuThus SET SoTien=700000 WHERE MaHopDong={stale} AND LoaiPhieu=0;')
    post(stale,token)
    check(stats(stale)=='0|0|4','Stale preview cannot finalize after financial inputs change')
    post(stale)
    check(stats(stale)=='1|1|2','Refreshed preview can finalize the updated balance')

    race=new();token=preview(race)['token'];second=web.Session();second.login('admin@demo.invalid')
    with ThreadPoolExecutor(2) as pool:
        list(pool.map(lambda session:post(race,token,session=session),[admin,second]))
    check(stats(race)=='1|1|2','Concurrent SQL requests produce one settlement and one refund')
    rollback=new()
    sql("EXEC(N'CREATE TRIGGER dbo.TestSettlementRollback ON dbo.PhieuChis AFTER INSERT AS THROW 51999,N''Owned fixture rollback probe'',1;');")
    try:
        try:post(rollback)
        except HTTPError as error:check(error.code==500,'Injected disbursement failure reaches the transaction rollback path')
    finally:sql('DROP TRIGGER dbo.TestSettlementRollback;')
    check(stats(rollback)=='0|0|4' and sql(f'SELECT COUNT(*) FROM dbo.PhieuThus WHERE MaHopDong={rollback};')=='2','Failure rolls back ledger, offset receipt, disbursement and contract status')

    early=new(500000,2000000,2000000,state=1)
    today=sql('SELECT CONVERT(varchar(10),DATEADD(day,10,GETDATE()),23);')
    q=preview(early,1,returnDate=today,earlyFee=0)
    admin.form('/Admin/HopDong/TraMayTruocHan',{'id':early,'ngayTraThucTe':today,'phiPhatTraSom':0,'settlementToken':q['token']},f'/Admin/HopDong/Details/{early}')
    check(stats(early)=='1|2|2' and sql(f'SELECT SUM(CASE WHEN LoaiChi=0 THEN SoTien ELSE 0 END),SUM(CASE WHEN LoaiChi=1 THEN SoTien ELSE 0 END) FROM dbo.PhieuChis WHERE MaHopDong={early};')=='500000.00|1000000.00','Early return separates 500000 deposit refund from 1000000 unused rent refund')
    check(sql(f'SELECT TienCocThucHoan FROM dbo.HopDongs WHERE MaHopDong={early};')=='500000.00','Deposit refunded field excludes unused rent')
    cancel=new(500000,1000000,800000,state=0)
    sql(f"INSERT dbo.PhieuThus(MaHopDong,LoaiPhieu,SoTien,NgayGiaoDich,HinhThucThanhToan,GhiChu,DaHuy) VALUES({cancel},3,100000,GETDATE(),1,N'Excess',0);")
    admin.form('/Admin/HopDong/UpdateStatus',{'id':cancel,'status':3},f'/Admin/HopDong/Details/{cancel}')
    check(stats(cancel)=='1|3|3' and sql(f'SELECT HoanCoc,HoanThue,HoanThua FROM dbo.ContractSettlements WHERE MaHopDong={cancel};')=='500000.00|800000.00|100000.00','Cancellation refunds actual deposit, rent and excess separately')
    payload=admin.get_json('/Admin/Database/Backup?format=json')
    check(any(s['MaHopDong']==cancel for s in payload['ContractSettlements']),'JSON backup includes the settlement ledger')

if __name__=='__main__':
    fixture.check_flows=verify
    fixture.main()
