---
name: new-project
description: >
  Scaffold a complete Python project from scratch: src layout, pyproject.toml,
  tests directory, .gitignore, and README. Use when the workspace is empty, the user
  asks to create or initialise a new project, or the task requires a clean project
  structure with no existing code to modify. Skip the survey step and activate this
  skill immediately.
---

# New Project Skill

## When This Skill Applies
- Workspace is empty or contains no relevant existing code
- Task is to "create", "build", "scaffold", or "start" a new project

## Override: Skip the Standard Survey
When building from scratch, `tree()` will show an empty directory. Call it **once** to confirm, then jump straight to implementation — do not repeat `outline()` or `read_lines()` on a workspace with nothing in it.

## Step 1 — Scaffold First
For any structured Python project, always start with:

```
scaffold_project("project_name")
```

This generates the standard layout under `COSTAFF_SHARED_DIR_CODING/project_name/`:
```
project_name/
  src/project_name/__init__.py
  src/project_name/main.py
  tests/__init__.py
  tests/test_main.py
  pyproject.toml
  .gitignore
```

## Step 2 — Install Dependencies
Install all required packages immediately after scaffolding, before writing domain code:
```
pip_install("package1 package2 ...")
```

## Step 3 — Write Domain Code
Replace the scaffold placeholder `main.py` with actual implementation.
- Use `patch_file()` for edits, not `write_file()` rewrites
- Split by responsibility: one module per concern, never one giant file

## Step 4 — Verify
Run `run_pytest()` to confirm the base scaffold tests pass, then add domain tests.

## Output Path Reminder
All project files MUST live under `COSTAFF_SHARED_DIR_CODING`, not `WORKSPACE_DIR`.
