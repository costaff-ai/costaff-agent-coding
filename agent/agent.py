import os
import sys
import json
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from google.adk.agents import LlmAgent
from google.adk.tools.mcp_tool import McpToolset
from google.adk.tools.mcp_tool.mcp_session_manager import StreamableHTTPServerParams
from utils.instructions import AGENT_INSTRUCTION

WORKSPACE_DIR = os.getenv("WORKSPACE_DIR", "/app/data/costaff-agent-coding")

def get_connection_params(entry):
    if isinstance(entry, str):
        url, headers = entry, None
    else:
        url     = entry.get("url", "")
        headers = entry.get("headers") or None
    if not url:
        raise ValueError("MCP entry has no URL")
    return StreamableHTTPServerParams(url=url, headers=headers or {})

# Own MCP — always connected
mcp_token = os.getenv("MCP_SECRET_KEY", "REDACTED")
MCP_CODING_URL = os.getenv("MCP_CODING_URL", "http://costaff-mcp-coding:8082/mcp")

mcp_params = StreamableHTTPServerParams(
    url=MCP_CODING_URL, 
    headers={"Authorization": f"Bearer {mcp_token}"}
)

tools = [McpToolset(connection_params=mcp_params)]
logger.info(f"Coding MCP URL: {MCP_CODING_URL}")

# Additional MCPs configured via CoStaff dashboard (CODING_AGENT_MCP_URLS)
raw_extra = os.getenv("CODING_AGENT_MCP_URLS", "")
if raw_extra:
    try:
        extra_config = json.loads(raw_extra)
        for mcp_name, entry in extra_config.items():
            if isinstance(entry, dict) and not entry.get("enabled", True):
                logger.info(f"Skipping disabled extra MCP: {mcp_name}")
                continue
            try:
                tools.append(McpToolset(connection_params=get_connection_params(entry)))
                logger.info(f"Added extra MCP: {mcp_name}")
            except Exception as e:
                logger.error(f"Failed to load extra MCP '{mcp_name}': {e}")
    except json.JSONDecodeError:
        logger.error("CODING_AGENT_MCP_URLS is not valid JSON, skipping extra MCPs")

model_provider = (os.getenv("CODING_AGENT_MODEL_PROVIDER") or os.getenv("COSTAFF_AGENT_MODEL_PROVIDER") or "gemini").lower()
model_name = os.getenv("CODING_AGENT_MODEL", "gemini-2.5-flash")

if model_provider == "litellm":
    from google.adk.models.lite_llm import LiteLlm
    selected_model = LiteLlm(
        model=os.getenv("LITELLM_MODEL_NAME"),
        api_base=os.getenv("LITELLM_API_BASE"),
        api_key=os.getenv("LITELLM_API_KEY"),
    )
    logger.info("Coding Agent using LiteLLM model provider")
else:
    selected_model = model_name
    logger.info(f"Coding Agent using model: {selected_model}")

preferred_lang = os.getenv("COSTAFF_PREFERRED_LANGUAGE", "Traditional Chinese (繁體中文)")
shared_dir = os.getenv("COSTAFF_SHARED_DIR_CODING", "/app/data/shared/costaff-agent-coding")
instruction = (
    AGENT_INSTRUCTION
    .replace("{WORKSPACE_DIR}", WORKSPACE_DIR)
    .replace("{COSTAFF_SHARED_DIR_CODING}", shared_dir)
    .replace("{user_id}", "shared")
    .replace("{PREFERRED_LANGUAGE}", preferred_lang)
)

coding_agent = LlmAgent(
    name="coding_agent",
    model=selected_model,
    description=(
        f"A senior software engineer agent that writes and executes code inside a secure "
        f"sandboxed workspace ({WORKSPACE_DIR}). "
        "Capable of: end-to-end Python project development; installing packages; running scripts; "
        "testing and linting; producing output files (.py, .json, .csv, .txt, etc.). "
        "For tasks requiring charts or PDF reports, saves structured results (.json/.csv) "
        "so the viz-report agent can generate the final report."
    ),
    instruction=instruction,
    tools=tools,
    sub_agents=[],
)
