# Password Audit Tool – Architecture

## Components
- **GUI (Tkinter):** tabs, inputs, tables, actions.
- **Hashing & Metrics:** SHA‑1 function, entropy estimator, heuristic rating.
- **Database Layer (LeakDB):** SQLite wrapper for schema, upserts, stats, VACUUM.
- **Worker Threads:** Import and bulk audit run in the background; UI remains responsive.

## Data Flow (Simplified)
1. **Import:** TXT → read line → `SHA1(UTF‑8)` → `INSERT ... ON CONFLICT DO UPDATE count = count + 1`  
2. **Single Check:** user input → `SHA1(pw)` → DB lookup → result + metrics  
3. **Bulk Audit:** TXT → per line `SHA1` + DB lookup → table → CSV export

## Database Schema
```sql
CREATE TABLE IF NOT EXISTS leaks (
  sha1  TEXT PRIMARY KEY,
  count INTEGER NOT NULL
);

CREATE TABLE IF NOT EXISTS meta (
  key   TEXT PRIMARY KEY,
  value TEXT NOT NULL
);
```
- `leaks.sha1`: uppercase hex (`[0-9A-F]`) of `hashlib.sha1(UTF‑8).hexdigest().upper()`  
- `leaks.count`: occurrence count across all imports  
- `meta.last_import`: ISO‑8601 UTC timestamp

## Threading
- **Import:** batched, transactional, PRAGMA-optimized (WAL/MEMORY).  
- **Bulk:** chunked UI updates to avoid Treeview overload.

## Design Constraints
- Strictly **offline** (zero telemetry).  
- **No** disk storage of checked plaintext passwords.  
- **Light UI only** (no Dark Mode).
