"""
Reading tools — read files fully or partially, inspect code structure, and search.
"""
import ast
import difflib
import json
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


def grep(pattern: str, path: str = "", recursive: bool = True, context: int = 2, max_matches: int = 500) -> str:
    """
    Search for a regex pattern across files in the workspace.
    Returns matching lines with surrounding context (like grep -n -C).
    pattern: regex pattern to search for.
    path: file or directory to search (default: entire workspace).
    recursive: search subdirectories (default: True).
    context: number of lines to show before/after each match (default: 2).
    max_matches: maximum total match lines to return across all files (default: 500).
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
        total_match_lines = 0
        truncated = False
        for filepath in sorted(text_files):
            if truncated:
                break
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
                    total_match_lines += 1
                    if total_match_lines >= max_matches:
                        results.append(f"\n[TRUNCATED]: Reached {max_matches}-line limit. Narrow your search with a more specific pattern or path.")
                        truncated = True
                        break
                if truncated:
                    break
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


def query_json(path: str, expression: str = "") -> str:
    """
    Parse a JSON or YAML file and optionally extract a nested value.
    expression: dot-notation path like 'servers.0.host' or 'metadata.name'.
                Leave empty to pretty-print the entire file.
    path: relative path within workspace (.json, .yaml, or .yml).
    """
    try:
        target = _safe_path(path)
        if not target.exists():
            return f"[ERROR]: '{path}' does not exist."

        content = target.read_text(encoding="utf-8")
        if target.suffix in (".yaml", ".yml"):
            try:
                import yaml
                data = yaml.safe_load(content)
            except ImportError:
                return "[ERROR]: PyYAML not installed. Run pip_install('pyyaml') first."
        else:
            try:
                data = json.loads(content)
            except json.JSONDecodeError as e:
                return f"[ERROR]: JSON parse error: {e}"

        if expression:
            for part in expression.split("."):
                if isinstance(data, list):
                    try:
                        data = data[int(part)]
                    except (ValueError, IndexError) as exc:
                        return f"[ERROR]: Cannot index list with '{part}': {exc}"
                elif isinstance(data, dict):
                    if part not in data:
                        available = ", ".join(list(data.keys())[:10])
                        return f"[ERROR]: Key '{part}' not found. Available: {available}"
                    data = data[part]
                else:
                    return f"[ERROR]: Cannot traverse into {type(data).__name__} with key '{part}'."

        return json.dumps(data, indent=2, ensure_ascii=False)
    except ValueError as e:
        return f"[ERROR]: {e}"
    except Exception as e:
        return f"[ERROR]: {e}"


def diff_files(path_a: str, path_b: str) -> str:
    """
    Compare two files and show a unified diff.
    path_a: first file (relative to workspace).
    path_b: second file (relative to workspace).
    """
    try:
        a = _safe_path(path_a)
        b = _safe_path(path_b)
        if not a.exists():
            return f"[ERROR]: '{path_a}' does not exist."
        if not b.exists():
            return f"[ERROR]: '{path_b}' does not exist."
        try:
            lines_a = a.read_text(encoding="utf-8").splitlines(keepends=True)
            lines_b = b.read_text(encoding="utf-8").splitlines(keepends=True)
        except UnicodeDecodeError:
            return "[ERROR]: One or both files appear to be binary."

        diff = list(difflib.unified_diff(lines_a, lines_b, fromfile=path_a, tofile=path_b))
        if not diff:
            return f"Files '{path_a}' and '{path_b}' are identical."
        return f"── diff {path_a} → {path_b} ({len(diff)} lines) ──\n" + "".join(diff)
    except ValueError as e:
        return f"[ERROR]: {e}"
    except Exception as e:
        return f"[ERROR]: {e}"
