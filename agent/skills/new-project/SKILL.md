---
name: new-project
description: >
  Scaffold a complete Python project from scratch with the right layout for the task type
  (CLI/library, data analysis, API service, or single utility script). Use when the workspace
  is empty, the user asks to create / initialise / start a new project, or the task requires
  a clean project structure with no existing code to modify. Provides standard directory
  layouts, naming conventions, and the scaffold workflow. Skip the survey step and activate
  this skill immediately.
---

# New Project Skill

## When This Skill Applies
- Workspace is empty or contains no relevant existing code
- Task is to "create", "build", "scaffold", or "start" a new project

## Override: Skip the Standard Survey
When building from scratch, `tree()` will show an empty directory. Call it **once** to confirm, then jump straight to implementation — do not repeat `outline()` or `read_lines()` on a workspace with nothing in it.

---

## Standard Layouts by Task Type

Pick the layout matching the task before scaffolding. All layouts live under `{COSTAFF_SHARED_DIR_CODING}/<project-name>/`.

### Default Selection Rule

When the request mentions **「專案」 / project / build / scaffold / create / initialise**, default to the **Python project layout** (`src/` + `tests/` + `pyproject.toml`) and call `scaffold_project()` as Step 1. This is the right choice in any ambiguous case — under-scaffolding a real project is worse than over-scaffolding a small task.

Pick a non-default layout only when:
- **Data analysis** layout — task involves loading/analysing a dataset, producing charts or statistics.
- **API / web service** layout — task explicitly mentions FastAPI / Flask / endpoints / REST API / web service.
- **Single utility script** layout — user explicitly says **「單一檔」 / 「簡單腳本」 / one-off / quick script / throwaway**, or the task is genuinely a one-line computation. **Do not** pick this layout just because the task sounds small — when in doubt, choose the Python project layout instead.

### Python project / CLI / library
```
<project-name>/
  src/<package>/__init__.py
  src/<package>/main.py
  tests/test_main.py
  pyproject.toml
  README.md
```

### Data analysis / data science
```
<analysis-name>/
  data/        ← (OPTIONAL) raw input files (CSV, JSON, Parquet, etc.) — only when copying input files in
  src/         ← reusable modules (loaders, transforms, models)
  outputs/     ← ALL result files: charts (.png), processed data (.csv), results (.json)
  main.py      ← entry point / analysis script
```

**`data/` is optional — do not create it preemptively.** Only `mkdir()` `data/` when there are real raw input files to put in it. If the data source is in-memory (sklearn datasets, API responses, generated data, hardcoded values), **skip `data/` entirely** — leaving an empty directory is noise.

**CRITICAL**: result files (`.json`, `.csv`, `.png`, etc.) must always be saved under `outputs/` inside the project directory — **never at SHARED root**.

### API / web service
```
<service-name>/
  src/main.py    ← FastAPI / Flask app entry point
  src/models.py
  src/routes/
  tests/
  pyproject.toml
```

### Single utility script
```
<task-name>/
  script.py
  README.md
```

---

## Naming Conventions

| Item | Convention | Example |
|------|-----------|---------|
| Project / output directory | `kebab-case` | `sales-analysis/` |
| Python module / file | `snake_case.py` | `data_processor.py` |
| Output / report file | descriptive, no spaces | `monthly_report_2024_01.csv` |
| Test file | `test_<module>.py` | `test_data_processor.py` |
| Constant | `UPPER_SNAKE_CASE` | `MAX_RETRIES = 3` |

Never use spaces or special characters in file or directory names.

---

## Scaffold Workflow

### Step 1 — Scaffold First
For any structured Python project, always start with:

```
scaffold_project("project_name")
```

This generates the standard layout under `{COSTAFF_SHARED_DIR_CODING}/project_name/`:
```
project_name/
  src/project_name/__init__.py
  src/project_name/main.py
  tests/__init__.py
  tests/test_main.py
  pyproject.toml
  .gitignore
```

For data-analysis or API layouts, scaffold first then `mkdir()` the additional directories (`data/`, `outputs/`, `routes/`, etc.).

### Step 2 — Install Dependencies
Install all required packages immediately after scaffolding, before writing domain code:
```
pip_install("package1 package2 ...")
```

### Step 3 — Write Domain Code
Replace the scaffold placeholder `main.py` with actual implementation.
- Use `patch_file()` for edits, not `write_file()` rewrites
- Split by responsibility: one module per concern, never one giant file

### Step 4 — Verify
Run `run_pytest()` to confirm the base scaffold tests pass, then add domain tests.

---

## Output Path Reminder
All project files MUST live under `{COSTAFF_SHARED_DIR_CODING}`, not `{WORKSPACE_DIR}`.
