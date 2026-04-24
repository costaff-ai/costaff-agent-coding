"""
Shared utilities for all tool modules.
Functions here are prefixed with _ so they are NOT auto-registered as MCP tools.
"""
import os
from pathlib import Path


def _workspace() -> Path:
    return Path(os.getenv("WORKSPACE_DIR", "/app/data/costaff-agent-coding"))


def _shared_dir() -> Path:
    return Path(os.getenv("SHARED_DIR", "/app/data/shared"))


def _my_shared_dir() -> Path:
    return Path(os.getenv("COSTAFF_SHARED_DIR_CODING", "/app/data/shared/costaff-agent-coding"))


def _packages_dir() -> Path:
    return _workspace() / "pip_packages"


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

    if not (str(resolved).startswith(str(workspace)) or str(resolved).startswith(str(shared))):
        raise ValueError(
            f"Path '{rel_or_abs}' resolves outside the allowed areas ({workspace} or {shared})."
        )
    return resolved
