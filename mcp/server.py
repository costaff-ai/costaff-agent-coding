import os
import sys
import inspect
import importlib
import pkgutil
import logging
from pathlib import Path

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("mcp-coding")

sys.path.insert(0, str(Path(__file__).parent))
sys.path.insert(0, str(Path(__file__).parent / "tools"))  # allow tools to import _shared

WORKSPACE = os.getenv("WORKSPACE_DIR", "/app/data/costaff-agent-coding")
PACKAGES_DIR = os.path.join(WORKSPACE, "pip_packages")
os.makedirs(WORKSPACE, exist_ok=True)
os.makedirs(PACKAGES_DIR, exist_ok=True)

from mcp.server.fastmcp import FastMCP
mcp = FastMCP("Coding", host="0.0.0.0", port=int(os.getenv("MCP_CODING_PORT", "8082")), stateless_http=True)


# ---------------------------------------------------------------------------
# Auto-discover and register all tools from the tools/ subdirectory.
#
# Tool categories:
#   filesystem.py  — ls, tree, mkdir, mv, cp, rm, file_info
#   reading.py     — read_file, read_lines, head, tail, outline, grep, find_files
#   writing.py     — write_file, append_file, patch_file, insert_after_line
#   execution.py   — run_python_file, run_python_code, run_shell, run_pytest
#   quality.py     — lint_file, format_file
#   environment.py — pip_install, pip_list, python_env_info
#
# To add tools: create a new .py file in tools/ with public functions.
# Functions starting with "_" are skipped (private helpers).
# ---------------------------------------------------------------------------

def _register_tools(mcp_instance):
    tools_pkg_dir = Path(__file__).parent / "tools"
    for _, module_name, _ in pkgutil.iter_modules([str(tools_pkg_dir)]):
        full_name = f"tools.{module_name}"
        try:
            module = importlib.import_module(full_name)
        except Exception as e:
            logger.error(f"Failed to import tool module '{full_name}': {e}")
            continue

        registered = 0
        for name, fn in inspect.getmembers(module, inspect.isfunction):
            if fn.__module__ != full_name:
                continue
            if name.startswith("_"):
                continue
            mcp_instance.tool()(fn)
            registered += 1

        logger.info(f"Registered {registered} tool(s) from tools/{module_name}.py")


_register_tools(mcp)


if __name__ == "__main__":
    # Transport env-selectable. Default SSE: race-free under to_a2a()+
    # ADK1.33 (streamable-http anyio CancelScope race #4454 does NOT
    # occur on SSE — verified 2026-05-16 on BA). MCP_TRANSPORT=
    # streamable-http to switch back once ADK fixes #4454.
    _t = os.getenv("MCP_TRANSPORT", "sse")
    logger.info(f"Starting Coding MCP server (transport={_t}, workspace={WORKSPACE})")
    mcp.run(transport=_t)
