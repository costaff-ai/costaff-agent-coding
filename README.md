# CoStaff Coding Agent

[![Python Version](https://img.shields.io/badge/python-3.10%2B-blue.svg)](https://www.python.org/)
[![Google ADK](https://img.shields.io/badge/Google%20ADK-latest-orange.svg)](https://github.com/google/adk-python)
[![MCP](https://img.shields.io/badge/MCP-enabled-green.svg)](https://modelcontextprotocol.io/)
[![Docker](https://img.shields.io/badge/docker-supported-blue.svg)](https://www.docker.com/)
[![A2A Protocol](https://img.shields.io/badge/A2A-protocol-violet.svg)](https://github.com/google/A2A)
[![costaff.agent.json](https://img.shields.io/badge/costaff-compatible-blue.svg)](https://github.com/costaff-ai/costaff)

[繁體中文](./README_zhtw.md) | **English**

**CoStaff Coding Agent** is a sandboxed code execution agent built on **Google ADK** and the **A2A protocol**. It specialises in writing and running Python code to solve computation, data processing, and logic problems — returning results and file paths to the orchestrating agent.

Designed as a first-party external agent for the [CoStaff](https://github.com/costaff-ai/costaff) platform, it can also run standalone or integrate with any A2A-compatible system.

---

## Table of Contents

- [How It Works](#how-it-works)
- [Features](#features)
- [Architecture](#architecture)
- [Getting Started](#getting-started)
- [Environment Variables](#environment-variables)
- [Git Tools](#git-tools)
- [MCP Extensions](#mcp-extensions)
- [costaff.agent.json](#costaffagentjson)
- [Output Format](#output-format)
- [License](#license)

---

## How It Works

```
CoStaff Agent
     │
     │  A2A Protocol (/.well-known/agent-card.json)
     ▼
Coding Agent  ──►  MCP Coding Server  ──►  Sandboxed Python Runtime
                        │
                        └──►  /app/data/coding_workspace/
```

1. The CoStaff Agent delegates computation tasks via **A2A protocol**
2. The Coding Agent writes Python code and executes it through the **MCP Coding Server**
3. Results (`.json`, `.csv`, `.txt`, `.py`) are saved to the shared `/app/data/coding_workspace/` volume
4. File paths are returned to the calling agent for downstream use (e.g. by `costaff-agent-viz-report`)

---

## Features

- **Sandboxed Python execution** via dedicated MCP server — code runs in isolation
- **A2A-compatible** — exposes `/.well-known/agent-card.json` health endpoint
- **Dynamic MCP support** — additional MCP servers can be assigned at runtime from the CoStaff dashboard without redeployment
- **Multi-model support** — works with Google Gemini natively or any LiteLLM-compatible provider
- **Shared volume integration** — output files accessible to other agents in the same ecosystem
- **costaff.agent.json manifest** — declares capabilities, env requirements, and MCP configurability for CoStaff platform discovery

---

## Architecture

```
costaff-agent-coding/
├── agent/                    # ADK agent definition
│   ├── agent.py              # LlmAgent with dynamic MCP loading
│   ├── utils/
│   │   └── instructions.py   # System prompt
│   └── requirements.txt
├── mcp/                      # MCP Coding Server
│   ├── server.py             # FastMCP server exposing code execution tools
│   └── requirements.txt
├── docker-compose.yaml       # Standalone deployment
└── costaff.agent.json       # CoStaff platform manifest
```

---

## Getting Started

### Prerequisites

- Docker and Docker Compose
- Google Gemini API Key **or** LiteLLM-compatible provider

### Standalone

```bash
# Clone
git clone https://github.com/costaff-ai/costaff-agent-coding.git
cd costaff-agent-coding

# Configure
cp agent/.env.example agent/.env
# Edit agent/.env with your API key

# Start
docker compose up -d --build
```

The agent will be available at `http://localhost:8081`.

### Via CoStaff Platform

Deploy directly from the CoStaff CLI:

```bash
cst agent deploy --local /path/to/costaff-agent-coding
```

CoStaff will read `costaff.agent.json`, build and start the containers, register the agent, and wire it into the ecosystem automatically.

---

## Environment Variables

| Variable | Required | Default | Description |
|----------|----------|---------|-------------|
| `GOOGLE_API_KEY` | ✅ | — | Google Gemini API key |
| `CODING_AGENT_MODEL` | ❌ | `gemini-2.5-flash` | Model name for Gemini provider |
| `COSTAFF_AGENT_MODEL_PROVIDER` | ❌ | `gemini` | `gemini` or `litellm` |
| `LITELLM_MODEL_NAME` | ❌ | — | Model name for LiteLLM provider |
| `LITELLM_API_BASE` | ❌ | — | LiteLLM API base URL |
| `LITELLM_API_KEY` | ❌ | — | LiteLLM API key |
| `MCP_CODING_URL` | ❌ | `http://costaff-mcp-coding:8082/mcp` | Internal MCP Coding Server URL |
| `CODING_WORKSPACE_DIR` | ❌ | `/app/data/coding_workspace` | Shared output directory |
| `CODING_AGENT_MCP_URLS` | ❌ | — | JSON dict of extra MCP servers (set via CoStaff dashboard) |
| `GIT_TOKEN` | ❌ | — | Personal Access Token for git push/pull over HTTPS |
| `GIT_AUTHOR_NAME` | ❌ | `Coding Agent` | Commit author name |
| `GIT_AUTHOR_EMAIL` | ❌ | `agent@costaff.ai` | Commit author email |

---

## Git Tools

The MCP Coding Server includes a built-in `git.py` tool module that exposes version-control operations to the agent.

### Available tools

| Tool | Description |
|------|-------------|
| `git_init` | Initialise a new repository in the workspace |
| `git_status` | Show working-tree status |
| `git_add` | Stage files for commit |
| `git_commit` | Commit staged changes |
| `git_log` | Show recent commit history |
| `git_diff` | Show unstaged or staged diff |
| `git_branch` | List local branches |
| `git_checkout` | Switch to or create a branch |
| `git_clone` | Clone a remote repository into the workspace |
| `git_push` | Push commits to remote (**requires `GIT_TOKEN`**) |
| `git_pull` | Pull changes from remote (**requires `GIT_TOKEN`**) |

### Configuration

**Step 1 — Generate a Personal Access Token**

- **GitHub**: Settings → Developer settings → Personal access tokens → Fine-grained tokens
  - Required scopes: `Contents: Read and Write`, `Metadata: Read`
- **GitLab**: User settings → Access Tokens → `write_repository` scope

**Step 2 — Add to `.env`**

```env
# Git credentials
GIT_TOKEN=ghp_xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx
GIT_AUTHOR_NAME=My Agent
GIT_AUTHOR_EMAIL=agent@mycompany.com
```

**Step 3 — Rebuild the MCP container**

```bash
docker compose up -d --build costaff-mcp-coding
```

### How push/pull works

The token is injected into the HTTPS remote URL at call time (`https://<token>@github.com/...`) and removed immediately after the operation completes, so it is never persisted to the repository config.

> **SSH remotes**: SSH clones and push/pull work without `GIT_TOKEN` if you mount your SSH key into the container:
> ```yaml
> # In compose-fragment.yaml or docker-compose.yaml
> volumes:
>   - ~/.ssh:/root/.ssh:ro
> ```

### Example agent conversation

```
# Clone a project into the workspace
"幫我 clone https://github.com/myorg/ledger-app 到 workspace"

# Write code, then commit
"建立 src/transactions.py，實作 CRUD，然後 commit，訊息寫 'feat: add transaction CRUD'"

# Push to GitHub
"把剛才的 commit push 到 origin main"
```

---

## MCP Extensions

The Coding Agent always connects to its own **MCP Coding Server** for sandboxed execution.

Additional MCPs (e.g. databases, search APIs, internal tools) can be assigned dynamically from the **CoStaff dashboard** under `Agents → costaff-agent-coding → MCP Extensions → Apply & Restart` — no redeployment needed.

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

## costaff.agent.json

This manifest file declares the agent's identity and capabilities to the CoStaff platform:

```json
{
  "name": "costaff-agent-coding",
  "version": "1.0.0",
  "description": "Writes and executes code to solve computation, data processing, or logic problems. Returns execution results and generated file paths.",
  "a2a_service": "agent-coding",
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

> The agent does **not** generate charts, HTML reports, or PDFs. Visual output is handled by [`costaff-agent-viz-report`](https://github.com/costaff-ai/costaff-agent-viz-report).

---

## License

Distributed under the MIT License. See `LICENSE` for details.
