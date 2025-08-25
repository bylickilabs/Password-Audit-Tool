# Password Audit Tool – Usage & Workflows

## Overview
The tool validates passwords **offline** against a local SQLite database that stores **SHA‑1 hashes only** (uppercase hex). No telemetry. Light UI only.

## Tabs & Functions

### 1) Leak DB
- **Import leak file (.txt):** one password per line; imported in batches (default 5,000/commit).
- **Cancel:** cleanly aborts an in-progress import.
- **Database status:** shows total entries and last import timestamp.
- **VACUUM/Optimize:** compacts and optimizes the SQLite database.

**Workflow:**  
1. Open **Leak DB** → start **Import**.  
2. After completion: review **Stats**, optionally run **VACUUM**.

### 2) Single Check
- Password field (Show/Hide) + **Check** button.
- Result: **LEAKED — found in database** or **Not found**.
- **Metrics:** length, character classes used, entropy (≈), heuristic rating (“Weak/Fair/Good/Strong”).

**Workflow:**  
1. Type a password → **Check**.  
2. Interpret result; replace if leaked.

### 3) Bulk Audit
- Choose a TXT file (one password per line) → **Run Audit**.
- Table columns: `Plaintext | SHA-1 | Leaked | Count`.
- **Export CSV:** by default **without plaintext** (`sha1, leaked, count`); plaintext export is optional.

**Workflow:**  
1. Select list → run audit.  
2. Review results → **Export** to CSV (prefer without plaintext).

## Language & UI
- Header provides **DE/EN** language toggle.
- **Light UI only** (no Dark Mode).

## Security Notes
- No telemetry, no storage of checked plaintext passwords.  
- CSV export excludes plaintext by default (compliance-first).  
- Only audit data you are authorized to assess.
