"""
Shared utilities for all tool modules.
Functions here are prefixed with _ so they are NOT auto-registered as MCP tools.
"""
import os
from pathlib import Path


def _workspace() -> Path:
    return Path(os.getenv("CODING_WORKSPACE_DIR", "/app/data/coding_workspace"))


def _packages_dir() -> Path:
    return _workspace().parent / "pip_packages"


def _safe_path(rel_or_abs: str) -> Path:
    """
    Resolve a path safely within the workspace.
    Raises ValueError if the resolved path escapes the workspace root.
    """
    workspace = _workspace().resolve()
    candidate = Path(rel_or_abs)
    if not candidate.is_absolute():
        candidate = workspace / candidate
    resolved = candidate.resolve()
    if not str(resolved).startswith(str(workspace)):
        raise ValueError(
            f"Path '{rel_or_abs}' resolves outside the workspace ({workspace}). "
            "Only paths within the workspace are allowed."
        )
    return resolved
