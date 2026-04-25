"""
Shared utilities for all tool modules.
Functions here are prefixed with _ so they are NOT auto-registered as MCP tools.
"""
import os
from pathlib import Path

# ---------------------------------------------------------------------------
# Timeout constants (seconds)
# ---------------------------------------------------------------------------
TIMEOUT_SHORT = 30      # quick reads: pip list, version checks
TIMEOUT_MEDIUM = 60     # shell commands, git operations
TIMEOUT_LONG = 120      # python execution, pytest
TIMEOUT_INSTALL = 180   # pip install


def _workspace() -> Path:
    return Path(os.getenv("WORKSPACE_DIR", "/app/data/costaff-agent-coding"))


def _shared_dir() -> Path:
    return Path(os.getenv("SHARED_DIR", "/app/data/shared"))


def _my_shared_dir() -> Path:
    return Path(os.getenv("COSTAFF_SHARED_DIR_CODING", "/app/data/shared/costaff-agent-coding"))


def _packages_dir() -> Path:
    return _workspace() / "pip_packages"


def _build_env(include_bin: bool = False) -> dict:
    """Return os.environ copy with packages dir prepended to PYTHONPATH (and optionally PATH)."""
    packages = str(_packages_dir())
    env = os.environ.copy()
    existing = env.get("PYTHONPATH", "")
    env["PYTHONPATH"] = f"{packages}:{existing}" if existing else packages
    if include_bin:
        existing_path = env.get("PATH", "")
        env["PATH"] = f"{packages}/bin:{existing_path}" if existing_path else f"{packages}/bin"
    return env


def _safe_path(rel_or_abs: str) -> Path:
    """
    Resolve a path safely within the agent's private workspace or the shared workspace.
    Relative paths are resolved against _workspace().
    """
    workspace = _workspace().resolve()
    shared = _shared_dir().resolve()
    candidate = Path(rel_or_abs)
    if not candidate.is_absolute():
        candidate = workspace / candidate
    resolved = candidate.resolve()

    if not (resolved.is_relative_to(workspace) or resolved.is_relative_to(shared)):
        raise ValueError(
            f"Path '{rel_or_abs}' resolves outside the allowed areas ({workspace} or {shared})."
        )
    return resolved
