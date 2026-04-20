"""
Shared utilities for all tool modules.
Functions here are prefixed with _ so they are NOT auto-registered as MCP tools.
"""
import os
from pathlib import Path


def _workspace() -> Path:
    return Path(os.getenv("AGENT_CODING_WORKSPACE_DIR", "/app/data/agent-coding"))


def _workspace_root() -> Path:
    return Path(os.getenv("WORKSPACE_DIR", "/app/data"))


def _packages_dir() -> Path:
    return _workspace_root() / "pip_packages"


def _safe_path(rel_or_abs: str) -> Path:
    """
    Resolve a path safely within the workspace.
    Note: We allow access anywhere within WORKSPACE_DIR (/app/data) if needed,
    but the primary workspace is _workspace().
    For now, we stick to the restriction of _workspace() for safety, 
    but _workspace_root() is available for cross-agent tasks.
    """
    workspace = _workspace().resolve()
    candidate = Path(rel_or_abs)
    if not candidate.is_absolute():
        candidate = workspace / candidate
    resolved = candidate.resolve()
    
    # Check if it starts with the agent's workspace OR the global workspace root
    workspace_root = _workspace_root().resolve()
    if not (str(resolved).startswith(str(workspace)) or str(resolved).startswith(str(workspace_root))):
        raise ValueError(
            f"Path '{rel_or_abs}' resolves outside the allowed areas ({workspace} or {workspace_root})."
        )
    return resolved
