# Mateclaw Coding Agent

[![Python Version](https://img.shields.io/badge/python-3.10%2B-blue.svg)](https://www.python.org/)
[![Google ADK](https://img.shields.io/badge/Google%20ADK-latest-orange.svg)](https://github.com/google/adk-python)
[![MCP](https://img.shields.io/badge/MCP-enabled-green.svg)](https://modelcontextprotocol.io/)
[![Docker](https://img.shields.io/badge/docker-supported-blue.svg)](https://www.docker.com/)
[![A2A Protocol](https://img.shields.io/badge/A2A-protocol-violet.svg)](https://github.com/google/A2A)
[![mateclaw.agent.json](https://img.shields.io/badge/mateclaw-compatible-blue.svg)](https://github.com/MateClawAI/mateclaw)

**繁體中文** | [English](./README.md)

**Mateclaw Coding Agent** 是一個基於 **Google ADK** 和 **A2A 協議**構建的沙盒程式碼執行 Agent。專門負責撰寫並執行 Python 程式碼，解決計算、資料處理與邏輯問題，並將執行結果與產出的檔案路徑回傳給呼叫方 Agent。

作為 [Mateclaw](https://github.com/MateClawAI/mateclaw) 平台的第一方外部 Agent，也可獨立運行或整合至任何支援 A2A 的系統。

---

## 目錄

- [運作原理](#運作原理)
- [功能特色](#功能特色)
- [專案架構](#專案架構)
- [快速開始](#快速開始)
- [環境變數](#環境變數)
- [MCP 擴充](#mcp-擴充)
- [mateclaw.agent.json](#mateclawagentjson)
- [輸出格式](#輸出格式)
- [授權](#授權)

---

## 運作原理

```
Mateclaw Agent
     │
     │  A2A 協議 (/.well-known/agent.json)
     ▼
Coding Agent  ──►  MCP Coding Server  ──►  沙盒 Python 執行環境
                        │
                        └──►  /app/data/coding_workspace/
```

1. Mateclaw Agent 透過 **A2A 協議**將計算任務委派給 Coding Agent
2. Coding Agent 撰寫 Python 程式碼，並透過 **MCP Coding Server** 在沙盒中執行
3. 結果（`.json`、`.csv`、`.txt`、`.py`）儲存於共享的 `/app/data/coding_workspace/` volume
4. 檔案路徑回傳給呼叫方，供下游 Agent 使用（如 `mateclaw-viz-report-agent`）

---

## 功能特色

- **沙盒 Python 執行** — 透過專用 MCP Server 隔離執行，確保安全性
- **A2A 相容** — 提供 `/.well-known/agent.json` 健康檢查端點
- **動態 MCP 支援** — 可透過 Mateclaw Dashboard 在不重新部署的情況下動態新增 MCP Server
- **多模型支援** — 原生支援 Google Gemini，或任何 LiteLLM 相容的模型提供者
- **共享 Volume 整合** — 產出檔案可被同一生態系中的其他 Agent 存取
- **mateclaw.agent.json 宣告** — 聲明功能、環境變數需求與 MCP 可配置性，供 Mateclaw 平台自動發現

---

## 專案架構

```
mateclaw-coding-agent/
├── agent/                    # ADK Agent 定義
│   ├── agent.py              # LlmAgent，含動態 MCP 載入邏輯
│   ├── utils/
│   │   └── instructions.py   # 系統提示詞
│   └── requirements.txt
├── mcp/                      # MCP Coding Server
│   ├── server.py             # FastMCP Server，提供程式碼執行工具
│   └── requirements.txt
├── docker-compose.yaml       # 獨立部署設定
└── mateclaw.agent.json       # Mateclaw 平台宣告文件
```

---

## 快速開始

### 前置需求

- Docker 與 Docker Compose
- Google Gemini API Key **或** LiteLLM 相容的模型提供者

### 獨立運行

```bash
# 克隆
git clone https://github.com/MateClawAI/mateclaw-coding-agent.git
cd mateclaw-coding-agent

# 設定環境變數
cp agent/.env.example agent/.env
# 編輯 agent/.env，填入 API Key

# 啟動
docker compose up -d --build
```

Agent 將在 `http://localhost:8081` 提供服務。

### 透過 Mateclaw 平台部署

直接從 Mateclaw CLI 部署：

```bash
mateclaw agent deploy --local /path/to/mateclaw-coding-agent
```

Mateclaw 會讀取 `mateclaw.agent.json`，自動建立容器、註冊 Agent，並接入整個生態系。

---

## 環境變數

| 變數名稱 | 必填 | 預設值 | 說明 |
|---------|------|--------|------|
| `GOOGLE_API_KEY` | ✅ | — | Google Gemini API Key |
| `CODING_AGENT_MODEL` | ❌ | `gemini-2.5-flash` | Gemini 模型名稱 |
| `MATECLAW_AGENT_MODEL_PROVIDER` | ❌ | `gemini` | `gemini` 或 `litellm` |
| `LITELLM_MODEL_NAME` | ❌ | — | LiteLLM 模型名稱 |
| `LITELLM_API_BASE` | ❌ | — | LiteLLM API Base URL |
| `LITELLM_API_KEY` | ❌ | — | LiteLLM API Key |
| `MCP_CODING_URL` | ❌ | `http://mcp-coding:8082/sse` | 內部 MCP Coding Server URL |
| `CODING_WORKSPACE_DIR` | ❌ | `/app/data/coding_workspace` | 共享輸出目錄 |
| `CODING_AGENT_MCP_URLS` | ❌ | — | 額外 MCP Server 的 JSON 設定（由 Mateclaw Dashboard 管理） |

---

## MCP 擴充

Coding Agent 預設連接自身的 **MCP Coding Server** 進行沙盒執行。

額外的 MCP（如資料庫、搜尋 API、內部工具）可從 **Mateclaw Dashboard** 動態指派：`Agents → coding-agent → MCP Extensions → Apply & Restart`，無需重新部署。

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

## mateclaw.agent.json

此宣告文件向 Mateclaw 平台聲明 Agent 的身份與能力：

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

> 本 Agent **不負責**生成圖表、HTML 報告或 PDF。視覺化輸出由 [`mateclaw-viz-report-agent`](https://github.com/MateClawAI/mateclaw-viz-report-agent) 負責。

---

## 授權

本專案採用 MIT 授權條款。詳見 `LICENSE`。
