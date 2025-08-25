# Contributing Guide

## Process
1. Review or open an Issue.
2. Create a branch: `feature/short-desc` or `fix/short-desc`.
3. Implement, test, and document changes.
4. Open a Pull Request (use the template if provided).

## Commit Convention (Recommended: Conventional Commits)
Examples:
- `feat: add CSV export option without plaintext`
- `fix: handle latin-1 decoding in bulk audit`
- `docs: update installation guide`
- `refactor: simplify LeakDB vacuum`

## Code Style & Quality
- Python 3.11/3.12, standard library only.
- Avoid adding dependencies unless justified.
- UI text should support DE/EN.

## PR Checklist
- [ ] Runs on Windows (and optionally Linux/macOS)
- [ ] No regressions (smoke test: Import, Single, Bulk, Export)
- [ ] Docs/Changelog updated
