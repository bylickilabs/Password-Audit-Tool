# Changelog

All notable changes to this project will be documented in this file.  
Format based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/) and **Semantic Versioning**.

## [1.0.0] - 2025-08-24
### Added
- First stable release: leak import, single check, bulk audit, CSV export
- SQLite DB (`leaks(sha1,count)`, `meta(key,value)`), VACUUM/Optimize

### Fixed
- UTC timestamps (`datetime.now(timezone.utc)`)
- Language dictionary access (labels)