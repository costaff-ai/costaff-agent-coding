# CoStaff Coding Agent

[![Python Version](https://img.shields.io/badge/python-3.10%2B-blue.svg)](https://www.python.org/)
[![Google ADK](https://img.shields.io/badge/Google%20ADK-latest-orange.svg)](https://github.com/google/adk-python)
[![MCP](https://img.shields.io/badge/MCP-enabled-green.svg)](https://modelcontextprotocol.io/)
[![Docker](https://img.shields.io/badge/docker-supported-blue.svg)](https://www.docker.com/)
[![A2A Protocol](https://img.shields.io/badge/A2A-protocol-violet.svg)](https://github.com/google/A2A)
[![costaff.agent.json](https://img.shields.io/badge/costaff-compatible-blue.svg)](https://github.com/costaff-ai/costaff)

**繁體中文** | [English](./README.md)

**CoStaff Coding Agent** 是一個基於 **Google ADK** 和 **A2A 協議**構建的沙盒程式碼執行 Agent。專門負責撰寫並執行 Python 程式碼，解決計算、資料處理與邏輯問題，並將執行結果與產出的檔案路徑回傳給呼叫方 Agent。

作為 [CoStaff](https://github.com/costaff-ai/costaff) 平台的第一方外部 Agent，也可獨立運行或整合至任何支援 A2A 的系統。

---

## 目錄

- [運作原理](#運作原理)
- [功能特色](#功能特色)
- [專案架構](#專案架構)
- [快速開始](#快速開始)
- [環境變數](#環境變數)
- [Git 工具](#git-工具)
- [MCP 擴充](#mcp-擴充)
- [costaff.agent.json](#costaffagentjson)
- [輸出格式](#輸出格式)
- [授權](#授權)

---

## 運作原理

```
CoStaff Agent
     │
     │  A2A 協議 (/.well-known/agent.json)
     ▼
Coding Agent  ──►  MCP Coding Server  ──►  沙盒 Python 執行環境
                        │
                        └──►  /app/data/coding_workspace/
```

1. CoStaff Agent 透過 **A2A 協議**將計算任務委派給 Coding Agent
2. Coding Agent 撰寫 Python 程式碼，並透過 **MCP Coding Server** 在沙盒中執行
3. 結果（`.json`、`.csv`、`.txt`、`.py`）儲存於共享的 `/app/data/coding_workspace/` volume
4. 檔案路徑回傳給呼叫方，供下游 Agent 使用（如 `costaff-agent-viz-report`）

---

## 功能特色

- **沙盒 Python 執行** — 透過專用 MCP Server 隔離執行，確保安全性
- **A2A 相容** — 提供 `/.well-known/agent.json` 健康檢查端點
- **動態 MCP 支援** — 可透過 CoStaff Dashboard 在不重新部署的情況下動態新增 MCP Server
- **多模型支援** — 原生支援 Google Gemini，或任何 LiteLLM 相容的模型提供者
- **共享 Volume 整合** — 產出檔案可被同一生態系中的其他 Agent 存取
- **costaff.agent.json 宣告** — 聲明功能、環境變數需求與 MCP 可配置性，供 CoStaff 平台自動發現

---

## 專案架構

```
costaff-agent-coding/
├── agent/                    # ADK Agent 定義
│   ├── agent.py              # LlmAgent，含動態 MCP 載入邏輯
│   ├── utils/
│   │   └── instructions.py   # 系統提示詞
│   └── requirements.txt
├── mcp/                      # MCP Coding Server
│   ├── server.py             # FastMCP Server，提供程式碼執行工具
│   └── requirements.txt
├── docker-compose.yaml       # 獨立部署設定
└── costaff.agent.json       # CoStaff 平台宣告文件
```

---

## 快速開始

### 前置需求

- Docker 與 Docker Compose
- Google Gemini API Key **或** LiteLLM 相容的模型提供者

### 獨立運行

```bash
# 克隆
git clone https://github.com/costaff-ai/costaff-agent-coding.git
cd costaff-agent-coding

# 設定環境變數
cp agent/.env.example agent/.env
# 編輯 agent/.env，填入 API Key

# 啟動
docker compose up -d --build
```

Agent 將在 `http://localhost:8081` 提供服務。

### 透過 CoStaff 平台部署

直接從 CoStaff CLI 部署：

```bash
cst agent deploy --local /path/to/costaff-agent-coding
```

CoStaff 會讀取 `costaff.agent.json`，自動建立容器、註冊 Agent，並接入整個生態系。

---

## 環境變數

| 變數名稱 | 必填 | 預設值 | 說明 |
|---------|------|--------|------|
| `GOOGLE_API_KEY` | ✅ | — | Google Gemini API Key |
| `CODING_AGENT_MODEL` | ❌ | `gemini-2.5-flash` | Gemini 模型名稱 |
| `COSTAFF_AGENT_MODEL_PROVIDER` | ❌ | `gemini` | `gemini` 或 `litellm` |
| `LITELLM_MODEL_NAME` | ❌ | — | LiteLLM 模型名稱 |
| `LITELLM_API_BASE` | ❌ | — | LiteLLM API Base URL |
| `LITELLM_API_KEY` | ❌ | — | LiteLLM API Key |
| `MCP_CODING_URL` | ❌ | `http://mcp-coding:8082/sse` | 內部 MCP Coding Server URL |
| `CODING_WORKSPACE_DIR` | ❌ | `/app/data/coding_workspace` | 共享輸出目錄 |
| `CODING_AGENT_MCP_URLS` | ❌ | — | 額外 MCP Server 的 JSON 設定（由 CoStaff Dashboard 管理） |
| `GIT_TOKEN` | ❌ | — | HTTPS 推送/拉取用的 Personal Access Token |
| `GIT_AUTHOR_NAME` | ❌ | `Coding Agent` | Commit 作者名稱 |
| `GIT_AUTHOR_EMAIL` | ❌ | `agent@costaff.ai` | Commit 作者信箱 |

---

## Git 工具

MCP Coding Server 內建 `git.py` 工具模組，Agent 可直接呼叫版本控制操作。

### 可用工具

| 工具 | 說明 |
|------|------|
| `git_init` | 在 workspace 中初始化新 repository |
| `git_status` | 顯示工作目錄狀態 |
| `git_add` | 將檔案加入暫存區 |
| `git_commit` | 提交暫存的變更 |
| `git_log` | 顯示近期 commit 歷史 |
| `git_diff` | 顯示未暫存或已暫存的差異 |
| `git_branch` | 列出本地分支 |
| `git_checkout` | 切換或建立分支 |
| `git_clone` | 將遠端 repository clone 進 workspace |
| `git_push` | 推送 commit 到遠端（**需設定 `GIT_TOKEN`**） |
| `git_pull` | 從遠端拉取最新變更（**需設定 `GIT_TOKEN`**） |

### 設定步驟

**第一步 — 產生 Personal Access Token**

- **GitHub**：Settings → Developer settings → Personal access tokens → Fine-grained tokens
  - 必要權限：`Contents: Read and Write`、`Metadata: Read`
- **GitLab**：User settings → Access Tokens → 勾選 `write_repository`

**第二步 — 加入 `.env`**

```env
# Git 認證設定
GIT_TOKEN=ghp_xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx
GIT_AUTHOR_NAME=我的 Agent
GIT_AUTHOR_EMAIL=agent@mycompany.com
```

**第三步 — 重新 build MCP 容器**

```bash
docker compose up -d --build costaff-ext-coding-agent-mcp-coding
```

### Push/Pull 的運作方式

Token 僅在操作當下注入 HTTPS 遠端 URL（`https://<token>@github.com/...`），操作完成後立即還原，**不會**被寫入 repository 的 remote config。

> **SSH 遠端**：如果掛載了 SSH key，可不設定 `GIT_TOKEN` 直接使用 SSH clone/push/pull：
> ```yaml
> # 在 compose-fragment.yaml 或 docker-compose.yaml 中加入
> volumes:
>   - ~/.ssh:/root/.ssh:ro
> ```

### 對話範例

```
# 將專案 clone 進 workspace
"幫我 clone https://github.com/myorg/ledger-app 到 workspace"

# 寫好程式後 commit
"建立 src/transactions.py，實作 CRUD，然後 commit，訊息寫 'feat: add transaction CRUD'"

# 推送到 GitHub
"把剛才的 commit push 到 origin main"
```

---

## MCP 擴充

Coding Agent 預設連接自身的 **MCP Coding Server** 進行沙盒執行。

額外的 MCP（如資料庫、搜尋 API、內部工具）可從 **CoStaff Dashboard** 動態指派：`Agents → coding-agent → MCP Extensions → Apply & Restart`，無需重新部署。

額外 MCP 透過 `CODING_AGENT_MCP_URLS` 環境變數以 JSON dict 格式傳入：

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

此宣告文件向 CoStaff 平台聲明 Agent 的身份與能力：

```json
{
  "name": "coding-agent",
  "version": "1.0.0",
  "description": "寫程式並執行來解決需要計算、資料處理或程式邏輯的問題，回傳執行結果與產生的檔案路徑。",
  "a2a_service": "coding-agent",
  "port": 8081,
  "env_required": ["GOOGLE_API_KEY"],
  "mcp_configurable": true,
  "mcp_env_var": "CODING_AGENT_MCP_URLS"
}
```

---

## 輸出格式

Agent 輸出：
- **執行結果** — 數值、摘要、分析發現
- **檔案路徑** — `/app/data/coding_workspace/` 內的絕對路徑，供下游 Agent 使用

支援的輸出檔案類型：`.json`、`.csv`、`.txt`、`.py`

> 本 Agent **不負責**生成圖表、HTML 報告或 PDF。視覺化輸出由 [`costaff-agent-viz-report`](https://github.com/costaff-ai/costaff-agent-viz-report) 負責。

---

## 授權

本專案採用 MIT 授權條款。詳見 `LICENSE`。
