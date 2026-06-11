# DC Legends WarehouseOS

Tagline: Built by Warehouse People

This rebuild keeps the existing QR Legends operational data and warehouse
workflows while making the new Control Center the primary management view.

## What changed

- Added the responsive DC Legends WarehouseOS application shell.
- Replaced the legacy main dashboard with an operations-first Control Center.
- Added live KPI, workload, exception, task-aging, and inventory-health views.
- Added `/control-center` and `/warehouse-os` aliases.
- Added `/api/warehouse-os/control-center`, backed by existing JSON data stores.
- Added a WarehouseOS role-permission model for future configurable RBAC.
- Preserved receiving, putaway, inventory, replenishment, cycle count, picking,
  shipping, labor, safety, reporting, QR, and administration routes.
- Added mobile workflow navigation and a large QR scanning action.
- Added placeholders for slotting, forecasting, inventory-risk, and labor AI.

## Run locally

```powershell
$env:PYTHONIOENCODING = "utf-8"
python main.py
```

Open `http://127.0.0.1:5000/main_dashboard?demo_login=qrlegends22@gmail.com`.

## Verification

- Python syntax compilation passed.
- WarehouseOS JavaScript syntax validation passed.
- Authenticated Flask route smoke tests passed for all core modules.
- Desktop and mobile browser rendering passed with no console errors.
