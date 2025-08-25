# Password Audit Tool – Design Decision

## ADR‑001 — SHA‑1 as Matching Format
- **Context:** Many leak lists ship as SHA‑1.  
- **Decision:** Use SHA‑1 purely for **matching**, not for cryptographic protection.  
- **Consequences:** Fast deterministic matching; collision risk acceptable for this audit use-case.

## ADR‑002 — Offline Model
- **Context:** Privacy, compliance, zero telemetry.  
- **Decision:** No online APIs; fully local processing.  
- **Consequences:** Maximum control; no third‑party dependencies.

## ADR‑003 — SQLite for Storage
- **Context:** ACID, portability, no external service.  
- **Decision:** SQLite with WAL/PRAGMAs to accelerate bulk imports.  
- **Consequences:** Robust, distributable, low maintenance.

## ADR‑004 — Tkinter GUI
- **Context:** Standard library, no external UI frameworks, broad OS support.  
- **Decision:** Tkinter (Windows/Linux/macOS) without third‑party UI libs.  
- **Consequences:** Minimal dependencies; stable UX.

## ADR‑005 — Light‑Only UI
- **Context:** Consistency & simplicity.  
- **Decision:** Remove Dark Mode; ship light theme only.  
- **Consequences:** Less styling complexity and fewer code paths to test.

## ADR‑006 — CSV Export Without Plaintext (Default)
- **Context:** Compliance & least exposure.  
- **Decision:** Default export excludes plaintext; optional plaintext export remains available.  
- **Consequences:** Reduced data handling risk in audits.
