# Password Audit Tool – Configuration

The tool works **out-of-the-box**. Optionally, define **environment variables** to override defaults.

## Paths & Database
- **Default DB:** `leaks.db` in the **application directory** (next to `app.py` / the EXE).
- The application must have **write permissions** to the directory.

## Optional Environment Variables
| Variable | Description | Example | Default |
|---|---|---|---|
| `PAT_DB_PATH` | Absolute path to `leaks.db` (overrides default) | `C:\\data\\leaks.db` | App directory |
| `PAT_LANG_DEFAULT` | Default UI language `DE` or `EN` | `EN` | `DE` |
| `PAT_IMPORT_BATCH` | Import batch size | `10000` | `5000` |
| `PAT_UI_SCALE` | UI scaling factor (1.0 = 100%) | `1.25` | `1.0` |
| `PAT_DISABLE_PLAINTEXT_EXPORT` | `1` disables plaintext in CSV export | `1` | `0` |

> **Precedence:** Environment variables override built-in defaults.

## Priority (Configuration Sources)
1. **Environment variables** (if set)  
2. **Built-in defaults**

## Security
- No secrets/keys required.  
- Consider setting `PAT_DISABLE_PLAINTEXT_EXPORT=1` for stricter compliance.
