-- SQLCMD entry point. Select a new, empty database explicitly with -d.
-- Run from the repository root:
-- sqlcmd -S localhost -E -C -b -d RentalSystemDB_V2 -i MobileApp/RentalSystemDB.sql
:r .\RentalSystem\Database\Sql\001_Baseline.sql
:r .\RentalSystem\Database\Sql\002_MaintenanceAssignments.sql

:r .\RentalSystem\Database\Sql\003_FirstContractPayment.sql
:r .\RentalSystem\Database\Sql\004_ContractSettlements.sql
