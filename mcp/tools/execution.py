"""
Execution tools — run Python code, shell commands, and tests.
Security: all executions are workspace-scoped; shell commands are filtered against
a block-list of dangerous patterns.
"""
import os
import re
import subprocess
import tempfile
import uuid
from pathlib import Path

from _shared import _packages_dir, _safe_path, _workspace

# ---------------------------------------------------------------------------
# Shell safety block-list
# Patterns that are unconditionally rejected in run_shell().
# ---------------------------------------------------------------------------
_BLOCKED = re.compile(
    r"rm\s+-[a-zA-Z]*r[a-zA-Z]*\s+/"      # rm -rf / (recursive delete at root)
    r"|rm\s+--[a-zA-Z-]*\s+/"              # rm --recursive /
    r"|\bsudo\b"                            # privilege escalation
    r"|\bsu\b"
    r"|\bwget\b|\bcurl\b"                   # network fetch (use pip_install instead)
    r"|\bdd\b"                              # disk destroyer
    r"|\bmkfs\b"                            # format disk
    r"|\bchmod\s+[0-7]*\s+/"               # chmod on system paths
    r"|\bchown\b"
    r"|\bsystemctl\b|\bservice\b"           # system services
    r"|\|\s*sh\b|\|\s*bash\b|\|\s*zsh\b"   # pipe to shell (code injection)
    r"|>\s*/dev/"                           # write to device
    r"|/etc/passwd|/etc/shadow"            # sensitive system files
    r"|\bfork\s*bomb\b|:\(\)\s*\{"         # fork bomb
    r"|\bkillall\b|\bpkill\b"              # process killing
    r"|\bnc\b|\bnetcat\b|\bnmap\b"         # network tools
    r"|\bpython.*-c.*import\s+os.*system"  # os.system via python -c
)


def _inject_path(code: str) -> str:
    """Prepend PACKAGES_DIR to sys.path so user-installed packages are available."""
    packages = str(_packages_dir())
    return (
        f"import sys as _sys\n"
        f"if {packages!r} not in _sys.path:\n"
        f"    _sys.path.insert(0, {packages!r})\n"
        f"{code}"
    )


def run_python_file(path: str, args: str = "") -> str:
    """
    Execute a Python file in the workspace and return its output.
    Installed packages (via pip_install) are available.
    path: relative path to a .py file within workspace.
    args: optional command-line arguments string (e.g. '--input data.csv').
    """
    try:
        target = _safe_path(path)
        if not target.exists():
            return f"[ERROR]: '{path}' does not exist."
        if target.suffix != ".py":
            return f"[ERROR]: '{path}' is not a Python file."

        packages = str(_packages_dir())
        cmd = ["python3", str(target)] + (args.split() if args else [])
        env = os.environ.copy()
        existing_path = env.get("PYTHONPATH", "")
        env["PYTHONPATH"] = f"{packages}:{existing_path}" if existing_path else packages

        result = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            timeout=120,
            cwd=str(_workspace()),
            env=env,
        )
        output = result.stdout
        if result.stderr:
            output += f"\n[STDERR]:\n{result.stderr}"
        if result.returncode != 0:
            output += f"\n[EXIT CODE]: {result.returncode}"
        return output or "(no output)"
    except subprocess.TimeoutExpired:
        return "[ERROR]: Execution timed out (120s limit)."
    except ValueError as e:
        return f"[ERROR]: {e}"
    except Exception as e:
        return f"[ERROR]: {e}"


def run_python_code(code: str) -> str:
    """
    Execute a Python code snippet and return its output.
    Use this for quick checks, calculations, or exploratory code.
    For larger scripts, use write_file() then run_python_file() so you get
    accurate line numbers in tracebacks.
    code: Python source code to execute.
    """
    tmp_path = None
    try:
        full_code = _inject_path(code)
        suffix = f"_snippet_{uuid.uuid4().hex[:8]}.py"
        tmp_path = Path(tempfile.gettempdir()) / f"coding_agent{suffix}"
        tmp_path.write_text(full_code, encoding="utf-8")

        packages = str(_packages_dir())
        env = os.environ.copy()
        existing_path = env.get("PYTHONPATH", "")
        env["PYTHONPATH"] = f"{packages}:{existing_path}" if existing_path else packages

        result = subprocess.run(
            ["python3", str(tmp_path)],
            capture_output=True,
            text=True,
            timeout=120,
            cwd=str(_workspace()),
            env=env,
        )
        output = result.stdout
        if result.stderr:
            # Strip the temp file path from tracebacks for cleaner output
            stderr_clean = result.stderr.replace(str(tmp_path), "<snippet>")
            # Adjust line numbers (subtract the injected header lines)
            header_lines = len(full_code.splitlines()) - len(code.splitlines())
            def fix_lineno(m: re.Match) -> str:
                n = int(m.group(1)) - header_lines
                return f'line {max(1, n)}'
            stderr_clean = re.sub(r'line (\d+)', fix_lineno, stderr_clean)
            output += f"\n[STDERR]:\n{stderr_clean}"
        if result.returncode != 0 and not result.stderr:
            output += f"\n[EXIT CODE]: {result.returncode}"
        return output or "(no output)"
    except subprocess.TimeoutExpired:
        return "[ERROR]: Execution timed out (120s limit)."
    except Exception as e:
        return f"[ERROR]: {e}"
    finally:
        if tmp_path and tmp_path.exists():
            tmp_path.unlink(missing_ok=True)


def run_shell(command: str) -> str:
    """
    Execute a shell command inside the workspace directory.
    Useful for: pytest, pip freeze, ls, python -m, ruff, black, git, etc.

    SECURITY: The following are blocked and will be rejected:
    - rm -rf /, sudo, su, wget, curl, dd, mkfs
    - Piping to sh/bash, writing to /dev/, accessing /etc/passwd
    - Any pattern that could escape the container or cause irreversible damage

    command: shell command string to execute.
    """
    if _BLOCKED.search(command):
        return (
            f"[BLOCKED]: Command rejected for security reasons.\n"
            f"Command: {command}\n"
            "If you need network access, use pip_install(). "
            "If you need file operations, use the filesystem tools."
        )
    try:
        packages = str(_packages_dir())
        env = os.environ.copy()
        existing_path = env.get("PYTHONPATH", "")
        env["PYTHONPATH"] = f"{packages}:{existing_path}" if existing_path else packages
        existing_pp = env.get("PATH", "")
        env["PATH"] = f"{packages}/bin:{existing_pp}" if existing_pp else f"{packages}/bin"

        result = subprocess.run(
            command,
            shell=True,
            capture_output=True,
            text=True,
            timeout=60,
            cwd=str(_workspace()),
            env=env,
        )
        output = result.stdout
        if result.stderr:
            output += f"\n[STDERR]:\n{result.stderr}"
        if result.returncode != 0:
            output += f"\n[EXIT CODE]: {result.returncode}"
        return output or "(no output)"
    except subprocess.TimeoutExpired:
        return "[ERROR]: Command timed out (60s limit)."
    except Exception as e:
        return f"[ERROR]: {e}"


def run_pytest(path: str = "", flags: str = "") -> str:
    """
    Run pytest on a file or directory and return a structured summary.
    path: test file or directory (default: workspace root, discovers all tests).
    flags: additional pytest flags (e.g. '-v', '-k test_login', '--tb=short').
    """
    try:
        if path:
            target = _safe_path(path)
            if not target.exists():
                return f"[ERROR]: '{path}' does not exist."
            test_target = str(target)
        else:
            test_target = str(_workspace())

        packages = str(_packages_dir())
        env = os.environ.copy()
        existing_path = env.get("PYTHONPATH", "")
        env["PYTHONPATH"] = f"{packages}:{existing_path}" if existing_path else packages

        cmd = ["python3", "-m", "pytest", test_target, "--tb=short", "-q"]
        if flags:
            cmd += flags.split()

        result = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            timeout=120,
            cwd=str(_workspace()),
            env=env,
        )
        output = result.stdout
        if result.stderr:
            output += f"\n[STDERR]:\n{result.stderr}"

        # Highlight pass/fail summary
        if "passed" in output or "failed" in output or "error" in output.lower():
            lines = output.splitlines()
            summary = [l for l in lines if re.search(r'\d+ (passed|failed|error)', l)]
            if summary:
                output += f"\n\n─── SUMMARY ───\n" + "\n".join(summary)

        return output or "(no output)"
    except subprocess.TimeoutExpired:
        return "[ERROR]: pytest timed out (120s limit)."
    except ValueError as e:
        return f"[ERROR]: {e}"
    except Exception as e:
        return f"[ERROR]: {e}"
