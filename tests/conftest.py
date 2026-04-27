"""
Test configuration for Coding MCP tools.

Sets WORKSPACE_DIR / SHARED_DIR env vars to temp directories before any tool
module is imported, so tools run without a live container environment.
"""
import atexit
import os
import shutil
import sys
import tempfile
from pathlib import Path

import pytest

# mcp/tools/ must be on sys.path so "from _shared import ..." works
MCP_TOOLS_DIR = Path(__file__).parent.parent / "mcp" / "tools"
sys.path.insert(0, str(MCP_TOOLS_DIR))

# Create temp dirs once for the whole test session (before any import of tools)
_TMP_BASE = Path(tempfile.mkdtemp(prefix="coding_mcp_test_"))
_WORKSPACE_DIR = _TMP_BASE / "workspace"
_SHARED_DIR = _TMP_BASE / "shared"
_MY_SHARED_DIR = _TMP_BASE / "shared" / "costaff-agent-coding"

_WORKSPACE_DIR.mkdir()
_SHARED_DIR.mkdir()
_MY_SHARED_DIR.mkdir()

# Patch env vars before any tool module reads them at import time
os.environ["WORKSPACE_DIR"] = str(_WORKSPACE_DIR)
os.environ["SHARED_DIR"] = str(_SHARED_DIR)
os.environ["COSTAFF_SHARED_DIR_CODING"] = str(_MY_SHARED_DIR)

atexit.register(shutil.rmtree, _TMP_BASE, True)


@pytest.fixture
def workspace(tmp_path_factory):
    """
    A fresh empty workspace sub-directory per test.
    Overrides WORKSPACE_DIR env var and patches _shared._workspace() for isolation.
    """
    ws = tmp_path_factory.mktemp("ws")
    old = os.environ.get("WORKSPACE_DIR")
    os.environ["WORKSPACE_DIR"] = str(ws)
    yield ws
    if old is None:
        del os.environ["WORKSPACE_DIR"]
    else:
        os.environ["WORKSPACE_DIR"] = old


@pytest.fixture
def shared_dir():
    """Shared workspace directory (maps to SHARED_DIR inside container)."""
    return _SHARED_DIR
