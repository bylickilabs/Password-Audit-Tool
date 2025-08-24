# Password Audit Tool

| ![Python](https://img.shields.io/badge/Python-3.11%2B-blue) | ![GUI](https://img.shields.io/badge/GUI-Tkinter-informational) | ![DB](https://img.shields.io/badge/DB-SQLite-success) | ![Offline](https://img.shields.io/badge/Mode-Offline-critical)|
|---|---|---|---|

|<img width="1280" height="640" alt="audit" src="https://github.com/user-attachments/assets/e141bcf1-2bcf-4e4e-b291-79ea045081fb" />|
|---|

**Offline. Secure. Fast.**  
> A local desktop app to verify passwords against your **own leak database** — **no cloud, no telemetry**.  
  - SQLite stores **SHA-1 hashes only**

---

## Table of Contents
- [Features](#features)
- [Architecture & Security Model](#architecture--security-model)
- [Requirements](#requirements)
- [Installation](#installation)
- [Quick Start](#quick-start)
- [Usage](#usage)
- [Performance Tips](#performance-tips)
- [Export & Data Handling](#export--data-handling)
- [Troubleshooting](#troubleshooting)
- [FAQ](#faq)
- [Legal & Ethics](#legal--ethics)
- [Changelog](#changelog)
- [License](#license)

---

## Features
- ✅ **Offline leak checks** against a local SQLite database (stores **SHA-1** only)  
- ✅ **Single Check** & **Bulk Audit** (TXT list; one password per line)  
- ✅ **Language toggle: DE/EN** (light UI only; no Dark Mode)  
- ✅ **Strength metrics**: length, character classes, **entropy** (≈), simple heuristic (“Weak/Fair/Good/Strong”)  
- ✅ **Leak DB management**: import large text lists, **Cancel**, **VACUUM/Optimize**, stats (entries, last import)  
- ✅ **CSV export** (plaintext **off** by default; optional)  
- ✅ **Resilient encodings** (UTF-8 / Latin-1 with `errors="ignore"`)  
- ✅ **Zero telemetry**, no plaintext persistence

---

## Architecture & Security Model
- **Storage**: SQLite (`leaks.db`) with table  
  `leaks (sha1 TEXT PRIMARY KEY, count INTEGER NOT NULL)`  
- **Import**: plaintext leak lists → per line **SHA-1** → upsert (`count++`)  
- **Verification**: compares **SHA-1(password)** to the DB; app does **not** persist checked plaintexts  
- **DB location**: created next to the script/executable (run from a writeable directory)  
- **Seed data**: minimal entries (e.g., `123456`, `password`, `qwerty`) included for immediate validation

---

## Requirements
- **Python**: 3.11 or 3.12 (validated on Windows 10/11)  
- **Dependencies**: Standard library only (Tkinter, sqlite3, hashlib, etc.)

---

## Installation
1. Place `app.py` (or `password_audit_tool.py`) in a **writeable** folder.  
2. (Optional) Create & activate a virtual environment.  
3. Launch:
   ```bash
   python app.py
   ```
   > On Windows you can also use `py app.py` or double-click if file associations allow.

---

## Quick Start
1. Open **Leak DB** → **Import leak file (.txt)** (one password per line).  
2. Use **Single Check** → type a password → get result + strength metrics.  
3. Use **Bulk Audit** → pick a TXT file → run → optional **CSV Export**.  
4. Switch **DE/EN** in the header as needed.

---

## Usage

### Tabs
**Leak DB**
- **Import**: processes large lists in batches (default 5,000/commit).  
- **Cancel**: cleanly aborts an in-progress import.  
- **Stats**: total entries & last import timestamp.  
- **VACUUM/Optimize**: compacts and optimizes the database.

**Single Check**
- Password field with Show/Hide and **Check** button.  
- Result: “LEAKED – found in database” or “Not found”.  
- Metrics: length, character classes used, entropy (≈), heuristic rating.

**Bulk Audit**
- Select a TXT list → run → the table shows `Plaintext | SHA-1 | Leaked | Count`.  
- **CSV Export**: by default exports `sha1, leaked, count`.  
  Enable plaintext export only if you must (compliance risk).

### Header Controls
- **Language**: DE/EN  
- **GitHub** button, **Info** dialog

---

## Performance Tips
- **Large imports**: WAL/Memory pragmas + transaction batching are used for throughput.  
- **Encoding**: UTF-8 recommended; Latin-1 and byte-error ignoring are supported.  
- **Hardware**: SSD + sufficient RAM accelerates upserts.  
- **Batching**: internal 5k batches; scales to millions of lines with stable memory.

---

## Export & Data Handling
- **DB file**: `leaks.db` is created in the app directory.  
- **CSV Export**: plaintext off by default; enable only if required.  
- **Backups**: for production, back up and/or version the DB file regularly.

---

## Troubleshooting
- **`AttributeError: datetime.UTC`**  
  Use:
  ```python
  from datetime import datetime, timezone
  datetime.now(timezone.utc)
  ```
- **`sqlite3.OperationalError: database is locked`**  
  Close the app and retry. Ensure no other process holds `leaks.db`. Run **VACUUM** afterwards.
- **No write permission**  
  Move the app to a user-writeable path (e.g., `%USERPROFILE%\Apps\PasswordAuditTool`).
- **Very large leak lists (GBs)**  
  Split into parts if needed; IO/CPU-bound task — SSD recommended.

---

## FAQ
**Does the app store plaintext passwords?**  
No. The DB stores **only SHA-1** and counts. Plaintext appears in the UI only and is **excluded** from exports by default.

**Why SHA-1?**  
This is a detection use-case (exact match against known leaked strings), not cryptographic protection. SHA-1 is a de-facto standard format for many leak lists.

**Can I import multiple files?**  
Yes. The importer is idempotent; duplicates increment the `count`.

**Does it support the Pwned Passwords API?**  
No. This tool is **strictly offline** — zero telemetry, zero cloud.

---

## Legal & Ethics
Use this tool **only** for legitimate audits and security hygiene on data/systems you’re **authorized** to assess.  
No liability for misuse.

---

## Changelog
- **v1.0.0**
  - Language label fixes; UTC timestamp fix
  - Stability/UX improvements

---

## License
© Thorsten Bylicki | © BYLICKILABS

[LICENSE](LICENSE)

