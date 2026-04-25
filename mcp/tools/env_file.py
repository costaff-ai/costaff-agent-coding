"""
Dotenv tools — read and write .env files within the workspace.
"""
import re

from _shared import _safe_path


def _parse_dotenv(text: str) -> dict[str, str]:
    result = {}
    for line in text.splitlines():
        stripped = line.strip()
        if not stripped or stripped.startswith("#") or "=" not in stripped:
            continue
        key, _, value = stripped.partition("=")
        key = key.strip()
        value = value.strip()
        if len(value) >= 2 and value[0] == value[-1] and value[0] in ('"', "'"):
            value = value[1:-1]
        result[key] = value
    return result


def dotenv_list(path: str = ".env") -> str:
    """
    Show all key=value pairs in a .env file.
    path: relative path to the .env file (default: '.env' in workspace root).
    """
    try:
        target = _safe_path(path)
        if not target.exists():
            return f"('{path}' does not exist)"
        pairs = _parse_dotenv(target.read_text(encoding="utf-8"))
        if not pairs:
            return f"('{path}' is empty)"
        lines = [f"  {k}={v}" for k, v in sorted(pairs.items())]
        return f"── {path} ({len(pairs)} key(s)) ──\n" + "\n".join(lines)
    except ValueError as e:
        return f"[ERROR]: {e}"
    except Exception as e:
        return f"[ERROR]: {e}"


def dotenv_get(key: str, path: str = ".env") -> str:
    """
    Read a single value from a .env file.
    key: the environment variable name.
    path: relative path to the .env file (default: '.env' in workspace root).
    """
    try:
        target = _safe_path(path)
        if not target.exists():
            return f"[ERROR]: '{path}' does not exist."
        pairs = _parse_dotenv(target.read_text(encoding="utf-8"))
        if key not in pairs:
            available = ", ".join(sorted(pairs.keys())[:10])
            return f"[ERROR]: '{key}' not found. Keys: {available}"
        return pairs[key]
    except ValueError as e:
        return f"[ERROR]: {e}"
    except Exception as e:
        return f"[ERROR]: {e}"


def dotenv_set(key: str, value: str, path: str = ".env") -> str:
    """
    Set or update a key=value pair in a .env file. Creates the file if it does not exist.
    key: environment variable name (must match [A-Za-z_][A-Za-z0-9_]*).
    value: the value to assign.
    path: relative path to the .env file (default: '.env' in workspace root).
    """
    if not re.match(r'^[A-Za-z_][A-Za-z0-9_]*$', key):
        return f"[ERROR]: Invalid env var name '{key}'. Must match [A-Za-z_][A-Za-z0-9_]*."
    try:
        target = _safe_path(path)
        target.parent.mkdir(parents=True, exist_ok=True)
        existing = target.read_text(encoding="utf-8") if target.exists() else ""
        lines = existing.splitlines(keepends=True)
        new_line = f"{key}={value}\n"

        updated = False
        new_lines = []
        for line in lines:
            if re.match(rf'^{re.escape(key)}\s*=', line):
                new_lines.append(new_line)
                updated = True
            else:
                new_lines.append(line)

        if not updated:
            if existing and not existing.endswith("\n"):
                new_lines.append("\n")
            new_lines.append(new_line)

        target.write_text("".join(new_lines), encoding="utf-8")
        return f"{'Updated' if updated else 'Added'} {key} in '{path}'."
    except ValueError as e:
        return f"[ERROR]: {e}"
    except Exception as e:
        return f"[ERROR]: {e}"


def dotenv_delete(key: str, path: str = ".env") -> str:
    """
    Remove a key from a .env file.
    key: the environment variable name to remove.
    path: relative path to the .env file (default: '.env' in workspace root).
    """
    try:
        target = _safe_path(path)
        if not target.exists():
            return f"[ERROR]: '{path}' does not exist."
        lines = target.read_text(encoding="utf-8").splitlines(keepends=True)
        new_lines = [line for line in lines if not re.match(rf'^{re.escape(key)}\s*=', line)]
        if len(new_lines) == len(lines):
            return f"[ERROR]: Key '{key}' not found in '{path}'."
        target.write_text("".join(new_lines), encoding="utf-8")
        return f"Removed '{key}' from '{path}'."
    except ValueError as e:
        return f"[ERROR]: {e}"
    except Exception as e:
        return f"[ERROR]: {e}"
