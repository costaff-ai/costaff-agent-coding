---
name: code_quality
description: "Review, lint, type-check, format, and measure test coverage of Python code. Use when asked to review code quality, fix type errors, improve test coverage, or before marking any task complete."
---

# Code Quality Skill

## Standard Pipeline
Run in this order — each step may surface issues to fix before moving to the next:

1. **`lint_file(path)`** — ruff: style, unused imports, naming conventions
2. **`type_check(path)`** — mypy: type annotation correctness
3. **`format_file(path)`** — black: auto-format (safe, never changes logic)
4. **`run_coverage(path, min_pct=80)`** — pytest-cov: show uncovered lines

## Interpreting and Fixing Results

### lint_file
| Code | Meaning | Fix |
|------|---------|-----|
| `E501` | Line too long | Break into multiple lines or shorten |
| `F401` | Unused import | Remove it |
| `F841` | Variable assigned but never used | Remove or use it |
| `RUF*` | Ruff-specific | Read the message and apply |

### type_check
- `Incompatible type` → wrong type passed; fix the caller or add a cast
- `Item "None" of "Optional[X]" has no attribute` → add guard: `if val is not None:`
- `Cannot find implementation` → add `py.typed` or install stubs: `pip_install("types-requests")`
- Not installed: `pip_install("mypy")`

### run_coverage
- `MISS` lines → write tests that exercise those code paths
- Coverage below threshold → add targeted tests; do not pad with trivial assertions
- Not installed: `pip_install("pytest-cov")`

## Pre-completion Checklist
Before reporting any task complete, all modified files must pass:
- [ ] `lint_file()` → 0 issues (or explicitly justified exceptions noted in report)
- [ ] `format_file()` → "already formatted" or changes applied
