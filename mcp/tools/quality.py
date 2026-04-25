"""
Code quality tools — lint and format Python files.
Requires ruff and black to be installed in the container.
"""
import subprocess
from pathlib import Path

from _shared import _safe_path, _workspace, TIMEOUT_MEDIUM

# module docstring update handled separately


def lint_file(path: str) -> str:
    """
    Run ruff on a Python file or directory and return a list of issues.
    Call this after writing or patching code to catch problems before running.
    path: relative path to a .py file or directory within workspace.
    """
    try:
        target = _safe_path(path)
        if not target.exists():
            return f"[ERROR]: '{path}' does not exist."

        result = subprocess.run(
            ["ruff", "check", str(target), "--output-format=text"],
            capture_output=True,
            text=True,
            timeout=TIMEOUT_MEDIUM,
            cwd=str(_workspace()),
        )

        output = result.stdout.strip()
        stderr = result.stderr.strip()

        if result.returncode == 0:
            return f"✓ No lint issues found in '{path}'."

        if not output and stderr:
            return f"[ERROR]: ruff failed: {stderr}"

        # Make paths relative for cleaner output
        output = output.replace(str(_workspace()) + "/", "")
        issue_count = len([l for l in output.splitlines() if l and not l.startswith("Found")])
        return f"── ruff: {issue_count} issue(s) in '{path}' ──\n{output}"
    except subprocess.TimeoutExpired:
        return f"[ERROR]: ruff timed out ({TIMEOUT_MEDIUM}s limit)."
    except FileNotFoundError:
        return "[ERROR]: ruff is not installed. Add 'ruff' to mcp/requirements.txt."
    except ValueError as e:
        return f"[ERROR]: {e}"
    except Exception as e:
        return f"[ERROR]: {e}"


def format_file(path: str) -> str:
    """
    Auto-format a Python file using black and show what changed.
    Safe to run at any time — black only reformats style, never changes logic.
    path: relative path to a .py file within workspace.
    """
    try:
        target = _safe_path(path)
        if not target.exists():
            return f"[ERROR]: '{path}' does not exist."
        if target.is_dir():
            return f"[ERROR]: '{path}' is a directory. Pass a specific .py file."

        # Read original for diff
        original = target.read_text(encoding="utf-8")

        result = subprocess.run(
            ["black", str(target), "--quiet"],
            capture_output=True,
            text=True,
            timeout=TIMEOUT_MEDIUM,
            cwd=str(_workspace()),
        )

        if result.returncode not in (0, 1):
            return f"[ERROR]: black failed: {result.stderr.strip()}"

        updated = target.read_text(encoding="utf-8")
        if original == updated:
            return f"✓ '{path}' is already formatted (no changes)."

        # Build a simple line-diff summary
        orig_lines = original.splitlines()
        new_lines = updated.splitlines()
        changed = sum(1 for a, b in zip(orig_lines, new_lines) if a != b)
        added = max(0, len(new_lines) - len(orig_lines))
        removed = max(0, len(orig_lines) - len(new_lines))

        summary_parts = [f"~{changed} line(s) reformatted"]
        if added:
            summary_parts.append(f"+{added} line(s) added")
        if removed:
            summary_parts.append(f"-{removed} line(s) removed")

        return f"✓ Formatted '{path}': {', '.join(summary_parts)}."
    except subprocess.TimeoutExpired:
        return f"[ERROR]: black timed out ({TIMEOUT_MEDIUM}s limit)."
    except FileNotFoundError:
        return "[ERROR]: black is not installed. Add 'black' to mcp/requirements.txt."
    except ValueError as e:
        return f"[ERROR]: {e}"
    except Exception as e:
        return f"[ERROR]: {e}"


def type_check(path: str = "") -> str:
    """
    Run mypy type checking on a Python file or directory.
    Requires mypy: pip_install('mypy').
    path: relative path to a .py file or directory (default: workspace root).
    """
    try:
        target = _safe_path(path) if path else _workspace()
        if not target.exists():
            return f"[ERROR]: '{path}' does not exist."

        result = subprocess.run(
            ["python3", "-m", "mypy", str(target), "--no-error-summary"],
            capture_output=True,
            text=True,
            timeout=TIMEOUT_MEDIUM,
            cwd=str(_workspace()),
        )

        output = result.stdout.strip()
        stderr = result.stderr.strip()

        if result.returncode == 0:
            return f"✓ No type errors in '{path or 'workspace'}'."

        if not output and stderr:
            return f"[ERROR]: mypy failed: {stderr}"

        output = output.replace(str(_workspace()) + "/", "")
        error_count = sum(1 for line in output.splitlines() if ": error:" in line)
        return f"── mypy: {error_count} error(s) ──\n{output}"
    except subprocess.TimeoutExpired:
        return f"[ERROR]: mypy timed out ({TIMEOUT_MEDIUM}s limit)."
    except FileNotFoundError:
        return "[ERROR]: mypy is not installed. Run pip_install('mypy') first."
    except ValueError as e:
        return f"[ERROR]: {e}"
    except Exception as e:
        return f"[ERROR]: {e}"
