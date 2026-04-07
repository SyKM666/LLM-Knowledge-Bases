# KB Agent — 简易 LLM驱动的个人知识库

LLM 驱动的智能知识库管理系统。思想来自 [Andrej Karpathy](https://x.com/karpathy) 关于用 LLM 构建个人知识库的理念。支持多种 LLM 后端（Claude CLI / OpenAI / Anthropic API / Ollama 等），提供文档摄入、自动编译为结构化 Wiki 文章、语义搜索、自然语言问答，以及质量检查与自动修复。CLI 和 Web 两种使用方式。

## 功能概览

- **文档摄入** — 从文件或 URL 导入原始文档，支持 PDF 自动提取文本
- **智能编译** — 利用 Claude 将原始文档编译为结构化 Wiki 文章
- **关键词搜索** — 在知识库中快速检索相关文章
- **自然语言问答** — 基于 RAG 模式对知识库提问，可智能将回答整合进已有文章或创建新文章
- **自动索引** — 生成分类目录索引
- **质量检查 & 修复** — 检测断链、缺失分类、孤立文章等问题并自动修复

## 项目结构

```
├── kb_agent/            # Python 后端
│   ├── cli.py           # CLI 入口 (Click)
│   ├── core.py          # 核心逻辑：摄入、编译、查询、检查、修复
│   ├── llm.py           # LLM 多后端抽象层
│   └── web.py           # Flask REST API 服务
├── frontend/            # TypeScript 前端
│   ├── src/
│   │   ├── main.ts      # 应用入口
│   │   ├── api.ts       # REST 客户端
│   │   ├── state.ts     # 状态管理
│   │   ├── types.ts     # 类型定义
│   │   ├── styles.css   # 样式
│   │   └── components/  # UI 组件 (sidebar, content, modal)
│   ├── index.html
│   ├── package.json
│   └── vite.config.ts
├── data/                # 数据目录（可通过 KB_DATA_DIR 自定义）
│   ├── raw/             # 原始文档
│   ├── wiki/            # 编译后的 Wiki 文章
│   └── output/          # 导出目录
└── pyproject.toml       # Python 包配置
```

## 技术栈

| 层 | 技术 |
|---|------|
| 后端 | Python 3.10+, Flask, Click, Rich |
| 前端 | TypeScript, Vite, Marked |
| LLM | Claude CLI / OpenAI API / Anthropic API（可扩展） |

## 快速开始

### 前置条件

- Python >= 3.10
- Node.js (前端开发)
- LLM 后端（任选其一）：
  - [Claude CLI](https://docs.anthropic.com/en/docs/claude-code)（默认，零配置）
  - OpenAI API key / 兼容 API（Ollama、vLLM 等）
  - Anthropic API key

### 安装

```bash
# 安装 Python 后端
pip install -e .

# 如需 PDF 支持
pip install -e ".[pdf]"

# 如需使用 OpenAI 兼容 API
pip install -e ".[openai]"

# 如需使用 Anthropic API
pip install -e ".[anthropic]"

# 全部安装
pip install -e ".[all]"

# 安装前端依赖
cd frontend && npm install
```

### 启动 Web UI

```bash
# 终端 1：启动后端服务（默认端口 5002，可通过 KB_PORT 自定义）
kb-web
# 或指定端口：KB_PORT=8080 kb-web

# 终端 2：启动前端开发服务器 (端口 5173)
cd frontend
npm run dev
```

浏览器打开 `http://localhost:5173`。

### CLI 使用

```bash
# 摄入文档
kb ingest /path/to/document.md

# 编译原始文档为 Wiki 文章
kb compile
kb compile --force   # 强制重新编译

# 搜索
kb search "transformer attention"

# 问答（--save 会智能整合到已有文章或新建文章）
kb query "什么是 RAG？" --save

# 质量检查与修复
kb lint
kb fix

# 重建索引
kb index
```

## LLM 配置

通过环境变量切换 LLM 后端，默认使用 Claude CLI：

```bash
# Claude CLI（默认，无需配置）
kb query "什么是注意力机制？"

# OpenAI
export KB_LLM_PROVIDER=openai
export KB_LLM_MODEL=gpt-4o        # 可选，默认 gpt-4o
kb query "什么是注意力机制？"

# Anthropic API
export KB_LLM_PROVIDER=anthropic
export KB_LLM_MODEL=claude-sonnet-4-20250514
kb query "什么是注意力机制？"

# DeepSeek
export KB_LLM_PROVIDER=deepseek
export DEEPSEEK_API_KEY=sk-xxx
kb query "什么是注意力机制？"

# 通义千问 (Qwen)
export KB_LLM_PROVIDER=qwen
export DASHSCOPE_API_KEY=sk-xxx
kb query "什么是注意力机制？"

# 智谱 (GLM)
export KB_LLM_PROVIDER=zhipu
export ZHIPUAI_API_KEY=xxx
kb query "什么是注意力机制？"

# 月之暗面 (Moonshot/Kimi)
export KB_LLM_PROVIDER=moonshot
export MOONSHOT_API_KEY=sk-xxx
kb query "什么是注意力机制？"

# 豆包 (Doubao)
export KB_LLM_PROVIDER=doubao
export ARK_API_KEY=xxx
kb query "什么是注意力机制？"

# 硅基流动 (SiliconFlow)
export KB_LLM_PROVIDER=silicon
export SILICON_API_KEY=sk-xxx
kb query "什么是注意力机制？"

# Ollama / vLLM 等本地模型（OpenAI 兼容接口）
export KB_LLM_PROVIDER=openai
export KB_LLM_BASE_URL=http://localhost:11434/v1
export KB_LLM_MODEL=llama3
export KB_LLM_API_KEY=unused       # Ollama 不需要 key，但字段不能为空
kb query "什么是注意力机制？"
```

### 内置 Provider 一览

| Provider | 说明 | 默认模型 | API Key 环境变量 |
|----------|------|---------|-----------------|
| `claude-cli` | Claude CLI（默认） | — | — |
| `openai` | OpenAI / 兼容接口 | `gpt-4o` | `OPENAI_API_KEY` |
| `anthropic` | Anthropic API | `claude-sonnet-4-20250514` | `ANTHROPIC_API_KEY` |
| `deepseek` | 深度求索 | `deepseek-chat` | `DEEPSEEK_API_KEY` |
| `qwen` | 通义千问 | `qwen-plus` | `DASHSCOPE_API_KEY` |
| `zhipu` | 智谱 GLM | `glm-4-plus` | `ZHIPUAI_API_KEY` |
| `moonshot` | 月之暗面 Kimi | `moonshot-v1-auto` | `MOONSHOT_API_KEY` |
| `doubao` | 字节豆包 | `doubao-1.5-pro-32k-250115` | `ARK_API_KEY` |
| `silicon` | 硅基流动 | `deepseek-ai/DeepSeek-V3` | `SILICON_API_KEY` |

所有国产模型均走 OpenAI 兼容协议，只需 `pip install -e ".[openai]"` 即可。可通过 `KB_LLM_MODEL` 覆盖默认模型。

| 环境变量 | 说明 | 默认值 |
|---------|------|--------|
| `KB_LLM_PROVIDER` | 见上表 | `claude-cli` |
| `KB_LLM_MODEL` | 覆盖默认模型名称 | 按 provider 而定 |
| `KB_LLM_BASE_URL` | 自定义 API 地址（用于本地模型） | — |
| `KB_LLM_API_KEY` | 通用 API 密钥（优先级高于各 provider 专属变量） | — |

## 工作流程

1. **摄入** — 将文档导入 `data/raw/` 目录
2. **编译** — LLM 将原始文档转换为带标题、分类、内链的结构化 Wiki 文章，存入 `data/wiki/`
3. **索引** — 自动生成 `data/wiki/INDEX.md` 分类目录
4. **查询** — 关键词搜索或自然语言提问，LLM 基于检索到的文章生成回答
5. **维护** — Lint 检测问题，Fix 自动修复

## 许可证

MIT
