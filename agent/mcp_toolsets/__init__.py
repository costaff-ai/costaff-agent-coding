"""MCP toolset loader for the coding agent — own MCP only, transport env-selectable.

The agent connects to its OWN MCP server (costaff-mcp-coding) via a
SINGLE McpToolset. Transport is chosen by MCP_TRANSPORT:

  - "sse" (DEFAULT): empirically race-free under to_a2a()+ADK1.33 ONLY
    when there is exactly one McpToolset session. The streamable-http
    anyio CancelScope race (google/adk-python#4454) does NOT occur on
    SSE, but a 2nd concurrent SSE session reintroduces it (verified
    2026-05-16: coding hard-failed at 2 sessions — get_tools raced and
    its own tools `run_python_code`/`mkdir` vanished from the spec).
  - "streamable-http": the future standard; switch back here once ADK
    fixes #4454. Currently races under to_a2a — do not use in prod yet.

The 4 shared manager-core tools (send_message_now / add_task_comment /
move_to_shared / list_data_files) are NOT loaded here — they go via the
costaff-core HTTP shim (agent/tools/costaff_api.py). That keeps coding
off a 2nd MCP session and keeps DB/notifiers/tokens centralised in
costaff-mcp. The old CODING_AGENT_MCP_URLS extra-MCP loop is removed on
purpose: every extra entry was a 2nd+ concurrent session and the direct
cause of the race.
"""
import logging
import os
from typing import List

from google.adk.tools.mcp_tool import McpToolset
from google.adk.tools.mcp_tool.mcp_session_manager import (
    SseConnectionParams,
    StreamableHTTPServerParams,
)

logger = logging.getLogger(__name__)

_HOST = os.getenv("MCP_CODING_HOST", "costaff-mcp-coding:8082")


def load_all_mcp_toolsets() -> List[McpToolset]:
    """Return [own-MCP McpToolset] with transport selected by MCP_TRANSPORT."""
    transport = os.getenv("MCP_TRANSPORT", "streamable-http").strip().lower()
    mcp_token = os.getenv(
        "MCP_SECRET_KEY",
        "REDACTED",
    )
    headers = {"Authorization": f"Bearer {mcp_token}"} if mcp_token else {}

    if transport == "streamable-http":
        url = os.getenv("MCP_CODING_URL", f"http://{_HOST}/mcp")
        params = StreamableHTTPServerParams(url=url, headers=headers)
        logger.warning(
            f"Coding MCP transport=streamable-http ({url}) — races under "
            f"to_a2a (#4454). Only use after ADK fixes it."
        )
    else:  # default: sse
        url = os.getenv("MCP_CODING_SSE_URL", f"http://{_HOST}/sse")
        params = SseConnectionParams(url=url, headers=headers)
        logger.info(f"Coding MCP transport=sse ({url}) — race-free under to_a2a")

    return [McpToolset(connection_params=params)]
