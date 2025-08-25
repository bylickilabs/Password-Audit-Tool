# Password Audit Tool – Installation Guide

## System Requirements
- **OS:** Windows 10/11 (validated). Linux and macOS are supported if Tkinter is installed.
- **Python:** 3.11 or 3.12
- **Dependencies:** Standard library only (Tkinter, sqlite3, hashlib, csv, threading, etc.).
- **Write permissions:** The application directory **must be writeable** (for `leaks.db`).

## Setup (Windows PowerShell)
```powershell
# 1) Navigate to your working folder
cd C:\path\to\app

# 2) (Optional) Create a virtual environment
py -3.12 -m venv .venv
.\.venv\Scripts\Activate.ps1

# 3) Launch
py app.py
```

## Setup (Linux / macOS)
```bash
cd /path/to/app
python3 -m venv .venv
source .venv/bin/activate
python3 app.py
```

## Launch Options
- Double-click `app.py` (Windows, if file associations allow), or
- Launch via terminal: `python app.py` / `py app.py`


## Recommended Project Layout
```
app/
├─ app.py
├─ README.md
└─ (generated at runtime) leaks.db
```
