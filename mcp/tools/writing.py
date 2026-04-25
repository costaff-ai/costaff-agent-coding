"""
Writing tools — create, overwrite, append, patch, and insert into files.
"""
from pathlib import Path

from _shared import _safe_path


def write_file(path: str, content: str) -> str:
    """
    Create or fully overwrite a file in the workspace.
    Use this for new files. For modifications to existing files, prefer patch_file()
    to avoid accidentally overwriting other parts of the file.
    path: relative path within workspace (parent directories are created automatically).
    content: full file content to write.
    """
    try:
        target = _safe_path(path)
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_text(content, encoding="utf-8")
        line_count = len(content.splitlines())
        return f"Written '{path}' ({line_count} lines, {len(content)} bytes)."
    except ValueError as e:
        return f"[ERROR]: {e}"
    except Exception as e:
        return f"[ERROR]: {e}"


def append_file(path: str, content: str) -> str:
    """
    Append content to the end of an existing file.
    A newline is automatically added if the file does not already end with one.
    path: relative path within workspace.
    content: text to append.
    """
    try:
        target = _safe_path(path)
        if not target.exists():
            return f"[ERROR]: '{path}' does not exist. Use write_file() to create it first."
        existing = target.read_text(encoding="utf-8")
        if existing and not existing.endswith("\n"):
            content = "\n" + content
        target.write_text(existing + content, encoding="utf-8")
        added_lines = len(content.splitlines())
        return f"Appended {added_lines} line(s) to '{path}'."
    except ValueError as e:
        return f"[ERROR]: {e}"
    except Exception as e:
        return f"[ERROR]: {e}"


def patch_file(path: str, old_str: str, new_str: str) -> str:
    """
    Replace an exact string in a file with a new string (like a surgical edit).
    This is the preferred way to modify existing code — do NOT rewrite the whole file.

    Rules:
    - old_str must match EXACTLY once. If it matches zero or multiple times, the
      operation is rejected — make old_str more specific to uniquely identify the target.
    - Whitespace and indentation in old_str must match the file exactly.
    - To delete a block, pass new_str as an empty string "".

    path: relative path within workspace.
    old_str: the exact text to find and replace.
    new_str: the replacement text.
    """
    try:
        target = _safe_path(path)
        if not target.exists():
            return f"[ERROR]: '{path}' does not exist."

        original = target.read_text(encoding="utf-8")
        count = original.count(old_str)

        if count == 0:
            # Provide a helpful hint
            return (
                f"[ERROR]: old_str not found in '{path}'.\n"
                "Check for exact whitespace and indentation. "
                "Use read_lines() or grep() to locate the exact text."
            )
        if count > 1:
            return (
                f"[ERROR]: old_str matches {count} locations in '{path}'. "
                "Make old_str more specific (add surrounding lines) to target exactly one location."
            )

        updated = original.replace(old_str, new_str, 1)
        target.write_text(updated, encoding="utf-8")

        old_lines = len(old_str.splitlines())
        new_lines = len(new_str.splitlines()) if new_str else 0
        delta = new_lines - old_lines
        delta_str = f"+{delta}" if delta >= 0 else str(delta)
        return (
            f"Patched '{path}': replaced {old_lines}-line block with {new_lines} line(s) "
            f"({delta_str} lines net)."
        )
    except ValueError as e:
        return f"[ERROR]: {e}"
    except Exception as e:
        return f"[ERROR]: {e}"


def insert_after_line(path: str, line_number: int, text: str) -> str:
    """
    Insert one or more lines of text after a specific line number in a file.
    Useful for adding imports, inserting a function, or adding a block mid-file.
    path: relative path within workspace.
    line_number: the line after which to insert (1-indexed). Use 0 to insert at the top.
    text: the text to insert (may contain newlines for multi-line inserts).
    """
    try:
        target = _safe_path(path)
        if not target.exists():
            return f"[ERROR]: '{path}' does not exist."

        lines = target.read_text(encoding="utf-8").splitlines(keepends=True)
        total = len(lines)

        if line_number < 0 or line_number > total:
            return f"[ERROR]: line_number={line_number} is out of range (file has {total} lines)."

        insertion = text if text.endswith("\n") else text + "\n"
        lines.insert(line_number, insertion)

        target.write_text("".join(lines), encoding="utf-8")
        inserted_count = insertion.count("\n")
        return (
            f"Inserted {inserted_count} line(s) after line {line_number} in '{path}'. "
            f"File now has {total + inserted_count} lines."
        )
    except ValueError as e:
        return f"[ERROR]: {e}"
    except Exception as e:
        return f"[ERROR]: {e}"
