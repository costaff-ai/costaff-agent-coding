import os
import sys
import json
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from google.adk.agents import LlmAgent
from google.adk.tools.mcp_tool import McpToolset
from google.adk.tools.mcp_tool.mcp_session_manager import SseServerParams, StreamableHTTPServerParams
from utils.instructions import AGENT_INSTRUCTION

WORKSPACE_DIR = os.getenv("CODING_WORKSPACE_DIR", "/app/data/coding_workspace")

def get_connection_params(entry):
    if isinstance(entry, str):
        url, headers, transport = entry, None, "sse" if "/sse" in entry else "streamable"
    else:
        url       = entry.get("url", "")
        headers   = entry.get("headers") or None
        transport = entry.get("transport", "streamable")
    if not url:
        raise ValueError("MCP entry has no URL")
    if transport == "sse" or "/sse" in url:
        return SseServerParams(url=url, headers=headers)
    return StreamableHTTPServerParams(url=url, headers=headers)

# Own MCP — always connected
MCP_CODING_URL = os.getenv("MCP_CODING_URL", "http://mcp-coding:8082/sse")
tools = [McpToolset(connection_params=SseServerParams(url=MCP_CODING_URL))]
logger.info(f"Coding MCP URL: {MCP_CODING_URL}")

# Additional MCPs configured via mateclaw dashboard (CODING_AGENT_MCP_URLS)
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

model_provider = os.getenv("MATECLAW_AGENT_MODEL_PROVIDER", "gemini").lower()
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

instruction = (
    AGENT_INSTRUCTION
    .replace("{WORKSPACE_DIR}", WORKSPACE_DIR)
    .replace("{user_id}", "shared")
)

coding_agent = LlmAgent(
    name="coding_agent",
    model=selected_model,
    description="寫程式並執行來解決需要計算、資料處理或程式邏輯的問題，回傳執行結果與產生的檔案路徑。",
    instruction=instruction,
    tools=tools,
)
