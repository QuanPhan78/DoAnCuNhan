"""Run the legacy console assertions using a fresh, explicitly marked SQL fixture."""
import os
import subprocess
from uuid import uuid4

import cutover
from verify_debt_status import FIXTURE


def main():
    name = 'RentalSystemCheck_' + uuid4().hex[:12]
    created = False
    try:
        cutover.sql(f'CREATE DATABASE [{name}];')
        created = True
        for script in ('001_Baseline.sql', '002_MaintenanceAssignments.sql',
                       '003_FirstContractPayment.sql', '004_ContractSettlements.sql'):
            cutover.sql_file(cutover.SQL / script, name)
        cutover.sql(FIXTURE, name)
        cutover.sql("EXEC sys.sp_addextendedproperty @name=N'RentalSystem.TestFixture',@value=1;", name)
        env = dict(os.environ, RENTALSYSTEM_VERIFY_CONNECTION=
                   f'Server=localhost;Database={name};Trusted_Connection=True;TrustServerCertificate=True;')
        result = subprocess.run(['dotnet', 'run', '--project', str(cutover.ROOT / 'ChallengerTests/ChallengerTests.csproj'),
                                 '--no-build'], cwd=cutover.ROOT, env=env, check=False)
        return result.returncode
    finally:
        if created:
            cutover.sql(f'ALTER DATABASE [{name}] SET SINGLE_USER WITH ROLLBACK IMMEDIATE; DROP DATABASE [{name}];')
            print('Isolated Challenger database removed.', flush=True)


if __name__ == '__main__':
    raise SystemExit(main())
