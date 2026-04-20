"""
Reading tools — read files fully or partially, inspect code structure, and search.
"""
import ast
import re
from pathlib import Path

from _shared import _safe_path, _workspace


def read_file(path: str) -> str:
    """
    Read an entire file and return its content with line numbers.
    Equivalent to `cat -n`. Use read_lines() for large files when you only need a section.
    path: relative path within workspace.
    """
    try:
        target = _safe_path(path)
        if not target.exists():
            return f"[ERROR]: '{path}' does not exist."
        if target.is_dir():
            return f"[ERROR]: '{path}' is a directory. Use ls() or tree() to inspect it."
        content = target.read_text(encoding="utf-8")
        lines = content.splitlines()
        numbered = "\n".join(f"{i+1:4d} │ {line}" for i, line in enumerate(lines))
        return f"── {path} ({len(lines)} lines) ──\n{numbered}"
    except ValueError as e:
        return f"[ERROR]: {e}"
    except Exception as e:
        return f"[ERROR]: {e}"


def read_lines(path: str, start: int, end: int) -> str:
    """
    Read a specific line range from a file (1-indexed, inclusive).
    Useful for inspecting a section of a large file without loading the whole thing.
    path: relative path within workspace.
    start: first line to read (1-indexed).
    end: last line to read (1-indexed, inclusive).
    """
    try:
        target = _safe_path(path)
        if not target.exists():
            return f"[ERROR]: '{path}' does not exist."
        lines = target.read_text(encoding="utf-8").splitlines()
        total = len(lines)
        s = max(1, start) - 1
        e = min(total, end)
        if s >= total:
            return f"[ERROR]: start={start} is beyond file length ({total} lines)."
        selected = lines[s:e]
        numbered = "\n".join(f"{i+s+1:4d} │ {line}" for i, line in enumerate(selected))
        return f"── {path} (lines {s+1}–{e} of {total}) ──\n{numbered}"
    except ValueError as e:
        return f"[ERROR]: {e}"
    except Exception as e:
        return f"[ERROR]: {e}"


def head(path: str, n: int = 30) -> str:
    """
    Read the first N lines of a file (default: 30).
    path: relative path within workspace.
    n: number of lines to show.
    """
    try:
        target = _safe_path(path)
        if not target.exists():
            return f"[ERROR]: '{path}' does not exist."
        lines = target.read_text(encoding="utf-8").splitlines()
        selected = lines[:n]
        numbered = "\n".join(f"{i+1:4d} │ {line}" for i, line in enumerate(selected))
        suffix = f" (showing first {n} of {len(lines)})" if len(lines) > n else ""
        return f"── {path}{suffix} ──\n{numbered}"
    except ValueError as e:
        return f"[ERROR]: {e}"
    except Exception as e:
        return f"[ERROR]: {e}"


def tail(path: str, n: int = 30) -> str:
    """
    Read the last N lines of a file (default: 30). Useful for reading logs.
    path: relative path within workspace.
    n: number of lines to show.
    """
    try:
        target = _safe_path(path)
        if not target.exists():
            return f"[ERROR]: '{path}' does not exist."
        lines = target.read_text(encoding="utf-8").splitlines()
        start_idx = max(0, len(lines) - n)
        selected = lines[start_idx:]
        numbered = "\n".join(f"{start_idx+i+1:4d} │ {line}" for i, line in enumerate(selected))
        suffix = f" (showing last {n} of {len(lines)})" if len(lines) > n else ""
        return f"── {path}{suffix} ──\n{numbered}"
    except ValueError as e:
        return f"[ERROR]: {e}"
    except Exception as e:
        return f"[ERROR]: {e}"


def outline(path: str) -> str:
    """
    Show the structure of a Python file: classes, functions, and methods with line numbers.
    Does NOT read the full content — use this first to understand a file before diving in.
    path: relative path to a .py file within workspace.
    """
    try:
        target = _safe_path(path)
        if not target.exists():
            return f"[ERROR]: '{path}' does not exist."
        if target.suffix != ".py":
            return f"[ERROR]: outline() only works with .py files (got '{path}')."

        source = target.read_text(encoding="utf-8")
        try:
            tree = ast.parse(source)
        except SyntaxError as e:
            return f"[ERROR]: Syntax error in '{path}': {e}"

        lines_raw = source.splitlines()
        total = len(lines_raw)
        results = []

        for node in ast.walk(tree):
            if isinstance(node, ast.ClassDef):
                # Collect methods under this class
                methods = [
                    n for n in ast.walk(node)
                    if isinstance(n, (ast.FunctionDef, ast.AsyncFunctionDef))
                    and n.col_offset > 0
                ]
                results.append((node.lineno, f"class {node.name}:"))
                for m in sorted(methods, key=lambda x: x.lineno):
                    decorator = ""
                    if m.decorator_list:
                        d = m.decorator_list[0]
                        decorator = f"@{ast.unparse(d)} "
                    async_prefix = "async " if isinstance(m, ast.AsyncFunctionDef) else ""
                    results.append((m.lineno, f"    {decorator}{async_prefix}def {m.name}()"))

            elif isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
                # Top-level functions only (col_offset == 0)
                if node.col_offset == 0:
                    decorator = ""
                    if node.decorator_list:
                        d = node.decorator_list[0]
                        decorator = f"@{ast.unparse(d)} "
                    async_prefix = "async " if isinstance(node, ast.AsyncFunctionDef) else ""
                    results.append((node.lineno, f"{decorator}{async_prefix}def {node.name}()"))

        if not results:
            return f"── {path} ({total} lines) — no classes or functions found ──"

        seen = set()
        unique = []
        for lineno, label in sorted(results):
            key = (lineno, label)
            if key not in seen:
                seen.add(key)
                unique.append((lineno, label))

        numbered = "\n".join(f"  L{lineno:4d}  {label}" for lineno, label in unique)
        return f"── {path} ({total} lines) ──\n{numbered}"
    except ValueError as e:
        return f"[ERROR]: {e}"
    except Exception as e:
        return f"[ERROR]: {e}"


def grep(pattern: str, path: str = "", recursive: bool = True, context: int = 2) -> str:
    """
    Search for a regex pattern across files in the workspace.
    Returns matching lines with surrounding context (like grep -n -C).
    pattern: regex pattern to search for.
    path: file or directory to search (default: entire workspace).
    recursive: search subdirectories (default: True).
    context: number of lines to show before/after each match (default: 2).
    """
    try:
        root = _safe_path(path) if path else _workspace()
        if not root.exists():
            return f"[ERROR]: '{path}' does not exist."

        try:
            regex = re.compile(pattern)
        except re.error as e:
            return f"[ERROR]: Invalid regex pattern: {e}"

        files = (
            [root] if root.is_file()
            else list(root.rglob("*") if recursive else root.glob("*"))
        )
        text_files = [f for f in files if f.is_file()]

        results = []
        for filepath in sorted(text_files):
            try:
                lines = filepath.read_text(encoding="utf-8", errors="replace").splitlines()
            except Exception:
                continue

            matches = [i for i, line in enumerate(lines) if regex.search(line)]
            if not matches:
                continue

            rel = filepath.relative_to(_workspace())
            results.append(f"\n── {rel} ──")

            shown: set[int] = set()
            for mi in matches:
                start = max(0, mi - context)
                end = min(len(lines), mi + context + 1)
                for i in range(start, end):
                    if i in shown:
                        continue
                    shown.add(i)
                    marker = "►" if i == mi else " "
                    results.append(f"  {marker} L{i+1:4d} │ {lines[i]}")
                if mi != matches[-1]:
                    next_start = max(0, matches[matches.index(mi)+1] - context)
                    if next_start > end:
                        results.append("       ···")

        if not results:
            return f"No matches found for pattern: {pattern!r}"
        total_files = sum(1 for r in results if r.startswith("\n──"))
        header = f"Found matches in {total_files} file(s) for pattern: {pattern!r}"
        return header + "\n".join(results)
    except ValueError as e:
        return f"[ERROR]: {e}"
    except Exception as e:
        return f"[ERROR]: {e}"


def find_files(pattern: str, path: str = "") -> str:
    """
    Find files matching a glob pattern in the workspace.
    pattern: glob pattern (e.g. '**/*.py', 'tests/test_*.py', '*.json').
    path: directory to search from (default: workspace root).
    """
    try:
        root = _safe_path(path) if path else _workspace()
        if not root.exists():
            return f"[ERROR]: '{path}' does not exist."

        matches = sorted(root.glob(pattern))
        if not matches:
            return f"No files found matching: {pattern!r}"

        lines = []
        for m in matches:
            rel = m.relative_to(_workspace())
            kind = "DIR " if m.is_dir() else "FILE"
            lines.append(f"[{kind}]  {rel}")
        return f"Found {len(matches)} match(es) for '{pattern}':\n" + "\n".join(lines)
    except ValueError as e:
        return f"[ERROR]: {e}"
    except Exception as e:
        return f"[ERROR]: {e}"
