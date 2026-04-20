# Mateclaw Coding Agent

[![Python Version](https://img.shields.io/badge/python-3.10%2B-blue.svg)](https://www.python.org/)
[![Google ADK](https://img.shields.io/badge/Google%20ADK-latest-orange.svg)](https://github.com/google/adk-python)
[![MCP](https://img.shields.io/badge/MCP-enabled-green.svg)](https://modelcontextprotocol.io/)
[![Docker](https://img.shields.io/badge/docker-supported-blue.svg)](https://www.docker.com/)
[![A2A Protocol](https://img.shields.io/badge/A2A-protocol-violet.svg)](https://github.com/google/A2A)
[![mateclaw.agent.json](https://img.shields.io/badge/mateclaw-compatible-blue.svg)](https://github.com/MateClawAI/mateclaw)

[繁體中文](./README_zhtw.md) | **English**

**Mateclaw Coding Agent** is a sandboxed code execution agent built on **Google ADK** and the **A2A protocol**. It specialises in writing and running Python code to solve computation, data processing, and logic problems — returning results and file paths to the orchestrating agent.

Designed as a first-party external agent for the [Mateclaw](https://github.com/MateClawAI/mateclaw) platform, it can also run standalone or integrate with any A2A-compatible system.

---

## Table of Contents

- [How It Works](#how-it-works)
- [Features](#features)
- [Architecture](#architecture)
- [Getting Started](#getting-started)
- [Environment Variables](#environment-variables)
- [MCP Extensions](#mcp-extensions)
- [mateclaw.agent.json](#mateclawagentjson)
- [Output Format](#output-format)
- [License](#license)

---

## How It Works

```
Mateclaw Agent
     │
     │  A2A Protocol (/.well-known/agent.json)
     ▼
Coding Agent  ──►  MCP Coding Server  ──►  Sandboxed Python Runtime
                        │
                        └──►  /app/data/coding_workspace/
```

1. The Mateclaw Agent delegates computation tasks via **A2A protocol**
2. The Coding Agent writes Python code and executes it through the **MCP Coding Server**
3. Results (`.json`, `.csv`, `.txt`, `.py`) are saved to the shared `/app/data/coding_workspace/` volume
4. File paths are returned to the calling agent for downstream use (e.g. by `mateclaw-viz-report-agent`)

---

## Features

- **Sandboxed Python execution** via dedicated MCP server — code runs in isolation
- **A2A-compatible** — exposes `/.well-known/agent.json` health endpoint
- **Dynamic MCP support** — additional MCP servers can be assigned at runtime from the Mateclaw dashboard without redeployment
- **Multi-model support** — works with Google Gemini natively or any LiteLLM-compatible provider
- **Shared volume integration** — output files accessible to other agents in the same ecosystem
- **mateclaw.agent.json manifest** — declares capabilities, env requirements, and MCP configurability for Mateclaw platform discovery

---

## Architecture

```
mateclaw-coding-agent/
├── agent/                    # ADK agent definition
│   ├── agent.py              # LlmAgent with dynamic MCP loading
│   ├── utils/
│   │   └── instructions.py   # System prompt
│   └── requirements.txt
├── mcp/                      # MCP Coding Server
│   ├── server.py             # FastMCP server exposing code execution tools
│   └── requirements.txt
├── docker-compose.yaml       # Standalone deployment
└── mateclaw.agent.json       # Mateclaw platform manifest
```

---

## Getting Started

### Prerequisites

- Docker and Docker Compose
- Google Gemini API Key **or** LiteLLM-compatible provider

### Standalone

```bash
# Clone
git clone https://github.com/MateClawAI/mateclaw-coding-agent.git
cd mateclaw-coding-agent

# Configure
cp agent/.env.example agent/.env
# Edit agent/.env with your API key

# Start
docker compose up -d --build
```

The agent will be available at `http://localhost:8081`.

### Via Mateclaw Platform

Deploy directly from the Mateclaw CLI:

```bash
mateclaw agent deploy --local /path/to/mateclaw-coding-agent
```

Mateclaw will read `mateclaw.agent.json`, build and start the containers, register the agent, and wire it into the ecosystem automatically.

---

## Environment Variables

| Variable | Required | Default | Description |
|----------|----------|---------|-------------|
| `GOOGLE_API_KEY` | ✅ | — | Google Gemini API key |
| `CODING_AGENT_MODEL` | ❌ | `gemini-2.5-flash` | Model name for Gemini provider |
| `MATECLAW_AGENT_MODEL_PROVIDER` | ❌ | `gemini` | `gemini` or `litellm` |
| `LITELLM_MODEL_NAME` | ❌ | — | Model name for LiteLLM provider |
| `LITELLM_API_BASE` | ❌ | — | LiteLLM API base URL |
| `LITELLM_API_KEY` | ❌ | — | LiteLLM API key |
| `MCP_CODING_URL` | ❌ | `http://mcp-coding:8082/sse` | Internal MCP Coding Server URL |
| `CODING_WORKSPACE_DIR` | ❌ | `/app/data/coding_workspace` | Shared output directory |
| `CODING_AGENT_MCP_URLS` | ❌ | — | JSON dict of extra MCP servers (set via Mateclaw dashboard) |

---

## MCP Extensions

The Coding Agent always connects to its own **MCP Coding Server** for sandboxed execution.

Additional MCPs (e.g. databases, search APIs, internal tools) can be assigned dynamically from the **Mateclaw dashboard** under `Agents → coding-agent → MCP Extensions → Apply & Restart` — no redeployment needed.

The extra MCPs are passed via the `CODING_AGENT_MCP_URLS` environment variable as a JSON dict:

```json
{
  "my-db-mcp": {
    "url": "https://my-db-mcp.internal/mcp",
    "transport": "streamable",
    "headers": { "Authorization": "Bearer ..." }
  }
}
```

---

## mateclaw.agent.json

This manifest file declares the agent's identity and capabilities to the Mateclaw platform:

```json
{
  "name": "coding-agent",
  "version": "1.0.0",
  "description": "Writes and executes code to solve computation, data processing, or logic problems. Returns execution results and generated file paths.",
  "a2a_service": "coding-agent",
  "port": 8081,
  "env_required": ["GOOGLE_API_KEY"],
  "mcp_configurable": true,
  "mcp_env_var": "CODING_AGENT_MCP_URLS"
}
```

---

## Output Format

The agent outputs:
- **Execution results** — numerical values, summaries, analysis findings
- **File paths** — absolute paths within `/app/data/coding_workspace/` for downstream agents

Supported output file types: `.json`, `.csv`, `.txt`, `.py`

> The agent does **not** generate charts, HTML reports, or PDFs. Visual output is handled by [`mateclaw-viz-report-agent`](https://github.com/MateClawAI/mateclaw-viz-report-agent).

---

## License

Distributed under the MIT License. See `LICENSE` for details.
