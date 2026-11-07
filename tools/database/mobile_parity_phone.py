"""Serve synthetic data for a USB phone test; ENTER stops server and removes only this fixture."""
import json
import os
from pathlib import Path
import shutil
import socket
from uuid import uuid4

import cutover
import verify_debt_status as fixture
import verify_mobile_customer_technician as parity


def main():
    web = fixture.web
    name = 'RentalSystemPhoneCheck_' + uuid4().hex[:12]
    out = cutover.ROOT / 'outputs/mobile-parity-20261107/phone'
    out.mkdir(exist_ok=True)
    (out / 'wwwroot').mkdir(exist_ok=True)
    for directory in ('css', 'js', 'lib'):
        source = cutover.ROOT / 'RentalSystem/wwwroot' / directory
        if source.exists():
            shutil.copytree(source, out / 'wwwroot' / directory, dirs_exist_ok=True)
    with socket.socket() as listener:
        listener.bind(('127.0.0.1', 0))
        port = listener.getsockname()[1]
    web.DB, web.PORT, web.BASE, web.OUT = name, port, f'http://127.0.0.1:{port}', out
    os.environ.update({'Database__EnableBackgroundJobs': 'false',
                       'BankTransfer__AccountNumber': '0000000000', 'BankTransfer__AccountName': 'TEST FIXTURE',
                       'Vnpay__TmnCode': '', 'Vnpay__HashSecret': uuid4().hex, 'Vnpay__ReturnUrl': ''})
    created = False
    process = log = None
    try:
        cutover.sql(f'CREATE DATABASE [{name}];')
        created = True
        for script in ('001_Baseline.sql', '002_MaintenanceAssignments.sql',
                       '003_FirstContractPayment.sql', '004_ContractSettlements.sql'):
            cutover.sql_file(cutover.SQL / script, name)
        cutover.sql(fixture.FIXTURE, name)
        process, log = web.start_server()
        parity.verify(name, '')
        metadata = {'database': name, 'port': port, 'pid': process.pid,
                    'customer': 'mobile@demo.invalid', 'technician': 'tech@demo.invalid'}
        (out / 'session.json').write_text(json.dumps(metadata, indent=2), encoding='utf-8')
        print('PHONE_READY ' + json.dumps(metadata), flush=True)
        input('Press ENTER after the phone test to stop and remove this synthetic database.\n')
    finally:
        web.stop_server(process, log)
        if created:
            cutover.sql(f'ALTER DATABASE [{name}] SET SINGLE_USER WITH ROLLBACK IMMEDIATE; DROP DATABASE [{name}];')
            print('Synthetic phone database removed.', flush=True)


if __name__ == '__main__':
    main()
