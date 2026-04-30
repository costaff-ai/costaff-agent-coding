import logging
import os

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

from google.adk.agents import LlmAgent

from instruction import build_instruction
from mcp_toolsets import load_all_mcp_toolsets
from models import selected_model
from skills import load_all_skills

# Tools = MCP toolsets + Skill toolset
tools = list(load_all_mcp_toolsets())
tools.append(load_all_skills())

# Instruction (placeholders resolved here)
instruction = build_instruction()

# Description references the workspace dir for clarity in the agent card.
_workspace_dir = os.getenv("WORKSPACE_DIR", "/app/data/costaff-agent-coding")

coding_agent = LlmAgent(
    name="coding_agent",
    model=selected_model,
    description=(
        f"A senior software engineer agent that writes and executes code inside a secure "
        f"sandboxed workspace ({_workspace_dir}). "
        "Capable of: end-to-end Python project development; installing packages; running scripts; "
        "testing and linting; producing output files (.py, .json, .csv, .txt, etc.). "
        "For tasks requiring charts or PDF reports, saves structured results (.json/.csv) "
        "so the viz-report agent can generate the final report."
    ),
    instruction=instruction,
    tools=tools,
    sub_agents=[],
    # Leaf agent: A2A response auto-returns control to the manager.
    # Both flags + empty sub_agents → ADK uses SingleFlow and omits the
    # transfer-to-agent system prompt, preventing Gemini from hallucinating
    # `transfer_to_agent` calls that would crash the run.
    disallow_transfer_to_parent=True,
    disallow_transfer_to_peers=True,
)
