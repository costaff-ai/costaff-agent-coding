"""
Filesystem tools — navigate, create, move, copy, and delete files/directories.
All paths are relative to the workspace root unless absolute (within workspace).
"""
import shutil
from datetime import datetime
from pathlib import Path

from _shared import _safe_path, _workspace


def ls(path: str = "") -> str:
    """
    List the contents of a directory in the workspace.
    Shows name, type (file/dir), size, and last-modified time.
    path: relative path within workspace (default: workspace root).
    """
    try:
        target = _safe_path(path) if path else _workspace()
        if not target.exists():
            return f"[ERROR]: Path '{path}' does not exist."
        if not target.is_dir():
            return f"[ERROR]: '{path}' is a file, not a directory. Use read_file() to read it."

        entries = sorted(target.iterdir(), key=lambda p: (p.is_file(), p.name.lower()))
        if not entries:
            return "(empty directory)"

        lines = []
        for entry in entries:
            stat = entry.stat()
            size = f"{stat.st_size:>8} B" if entry.is_file() else "       -  "
            mtime = datetime.fromtimestamp(stat.st_mtime).strftime("%Y-%m-%d %H:%M")
            kind = "FILE" if entry.is_file() else "DIR "
            lines.append(f"[{kind}]  {mtime}  {size}  {entry.name}")

        rel = target.relative_to(_workspace())
        header = f"📁 {rel}/" if str(rel) != "." else "📁 workspace/"
        return header + "\n" + "\n".join(lines)
    except ValueError as e:
        return f"[ERROR]: {e}"
    except Exception as e:
        return f"[ERROR]: {e}"


def tree(path: str = "", depth: int = 3) -> str:
    """
    Display a directory tree (like the `tree` command).
    path: relative path within workspace (default: workspace root).
    depth: maximum depth to recurse (default: 3).
    """
    try:
        root = _safe_path(path) if path else _workspace()
        if not root.exists():
            return f"[ERROR]: Path '{path}' does not exist."
        if not root.is_dir():
            return f"[ERROR]: '{path}' is a file, not a directory."

        lines = []
        rel_root = root.relative_to(_workspace())
        lines.append(f"📁 {rel_root}/" if str(rel_root) != "." else "📁 workspace/")

        def _walk(directory: Path, prefix: str, current_depth: int):
            if current_depth > depth:
                return
            entries = sorted(directory.iterdir(), key=lambda p: (p.is_file(), p.name.lower()))
            for i, entry in enumerate(entries):
                is_last = i == len(entries) - 1
                connector = "└── " if is_last else "├── "
                icon = "📄 " if entry.is_file() else "📁 "
                lines.append(f"{prefix}{connector}{icon}{entry.name}")
                if entry.is_dir():
                    extension = "    " if is_last else "│   "
                    _walk(entry, prefix + extension, current_depth + 1)

        _walk(root, "", 1)
        return "\n".join(lines)
    except ValueError as e:
        return f"[ERROR]: {e}"
    except Exception as e:
        return f"[ERROR]: {e}"


def mkdir(path: str) -> str:
    """
    Create a directory (and any missing parents) in the workspace.
    path: relative path to create (e.g. 'src/utils' or 'tests/unit').
    """
    try:
        target = _safe_path(path)
        target.mkdir(parents=True, exist_ok=True)
        return f"Directory '{path}' created."
    except ValueError as e:
        return f"[ERROR]: {e}"
    except Exception as e:
        return f"[ERROR]: {e}"


def mv(src: str, dst: str) -> str:
    """
    Move or rename a file or directory within the workspace.
    src: source path (relative to workspace).
    dst: destination path (relative to workspace).
    """
    try:
        src_path = _safe_path(src)
        dst_path = _safe_path(dst)
        if not src_path.exists():
            return f"[ERROR]: Source '{src}' does not exist."
        dst_path.parent.mkdir(parents=True, exist_ok=True)
        shutil.move(str(src_path), str(dst_path))
        return f"Moved '{src}' → '{dst}'."
    except ValueError as e:
        return f"[ERROR]: {e}"
    except Exception as e:
        return f"[ERROR]: {e}"


def cp(src: str, dst: str) -> str:
    """
    Copy a file or directory within the workspace.
    src: source path (relative to workspace).
    dst: destination path (relative to workspace).
    """
    try:
        src_path = _safe_path(src)
        dst_path = _safe_path(dst)
        if not src_path.exists():
            return f"[ERROR]: Source '{src}' does not exist."
        dst_path.parent.mkdir(parents=True, exist_ok=True)
        if src_path.is_dir():
            shutil.copytree(str(src_path), str(dst_path), dirs_exist_ok=True)
        else:
            shutil.copy2(str(src_path), str(dst_path))
        return f"Copied '{src}' → '{dst}'."
    except ValueError as e:
        return f"[ERROR]: {e}"
    except Exception as e:
        return f"[ERROR]: {e}"


def rm(path: str, recursive: bool = False) -> str:
    """
    Delete a file or directory from the workspace.
    path: path to delete (relative to workspace).
    recursive: set True to delete a non-empty directory (default: False, safety guard).
    """
    try:
        target = _safe_path(path)
        if not target.exists():
            return f"[ERROR]: '{path}' does not exist."
        if target.is_dir():
            if not recursive:
                contents = list(target.iterdir())
                if contents:
                    return (
                        f"[ERROR]: '{path}' is a non-empty directory. "
                        "Pass recursive=True to delete it and all its contents."
                    )
            shutil.rmtree(str(target))
            return f"Directory '{path}' deleted."
        else:
            target.unlink()
            return f"File '{path}' deleted."
    except ValueError as e:
        return f"[ERROR]: {e}"
    except Exception as e:
        return f"[ERROR]: {e}"


def file_info(path: str) -> str:
    """
    Show metadata for a file: size, line count, and last-modified time.
    path: relative path within workspace.
    """
    try:
        target = _safe_path(path)
        if not target.exists():
            return f"[ERROR]: '{path}' does not exist."
        if target.is_dir():
            num_files = sum(1 for _ in target.rglob("*") if _.is_file())
            return (
                f"Path:      {path}\n"
                f"Type:      directory\n"
                f"Files:     {num_files} (recursive)\n"
                f"Modified:  {datetime.fromtimestamp(target.stat().st_mtime).strftime('%Y-%m-%d %H:%M:%S')}"
            )
        stat = target.stat()
        try:
            line_count = len(target.read_text(encoding="utf-8").splitlines())
        except Exception:
            line_count = "N/A (binary?)"
        return (
            f"Path:      {path}\n"
            f"Type:      file\n"
            f"Size:      {stat.st_size} bytes\n"
            f"Lines:     {line_count}\n"
            f"Modified:  {datetime.fromtimestamp(stat.st_mtime).strftime('%Y-%m-%d %H:%M:%S')}"
        )
    except ValueError as e:
        return f"[ERROR]: {e}"
    except Exception as e:
        return f"[ERROR]: {e}"
