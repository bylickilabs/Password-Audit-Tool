# Troubleshooting

## `AttributeError: datetime.UTC`
Use:
```python
from datetime import datetime, timezone
datetime.now(timezone.utc)
```

## `sqlite3.OperationalError: database is locked`
Close the app; avoid parallel access to `leaks.db`. Restart and run **VACUUM** afterwards if needed.

## `PermissionError` when writing `leaks.db`
Move the app to a user‑writeable folder (e.g., `%USERPROFILE%\Apps\PasswordAuditTool`).

## Tkinter not found (Linux/minimal distros)
Install the Tkinter package (e.g., Debian/Ubuntu: `sudo apt install python3-tk`).

## Wrong encoding during import
Save TXT files as UTF‑8 (recommended) or Latin‑1; the app ignores invalid bytes (`errors="ignore"`).
