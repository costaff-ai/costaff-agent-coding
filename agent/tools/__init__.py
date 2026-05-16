"""Native function tools for the coding agent.

Only the 4 shared manager-core tools live here — they reach the
costaff-core HTTP shim via httpx (no MCP client, keeps coding off a 2nd
MCP session, keeps DB/notifiers/tokens centralised). Coding's OWN tools
(run_python_code, mkdir, ...) are served by its MCP server and reached
via a single McpToolset over SSE (see agent/mcp_toolsets/).
"""
from .costaff_api import load_costaff_api_tools

__all__ = ["load_costaff_api_tools"]
