# 技术选型

## LLM 层

| 组件 | 选型 | 理由 |
|------|------|------|
| Provider | OpenAI | 通过 LangChain ChatOpenAI 调用，生态成熟 |
| 重型 Agent（Parser/Summary/Methodology/QA/Report） | gpt-4o | 质量优先，论文理解需要强推理能力 |
| 轻型 Agent（Intent/Orchestrator） | gpt-4o-mini | 意图识别和调度是简单任务，降成本 |
| Embedding | text-embedding-3-small | QA 检索用，性价比高 |

## Agent 编排层

| 组件 | 选型 | 理由 |
|------|------|------|
| 工作流引擎 | LangGraph | 原生支持状态图、条件分支、并行执行，适合多 Agent 调度 |
| LLM 框架 | LangChain | Prompt 模板、ChatModel 封装、文档加载器，与 LangGraph 无缝集成 |

## PDF 解析层

| 组件 | 选型 | 理由 |
|------|------|------|
| 主选 | PyMuPDF (fitz) | 速度快，支持布局信息提取，可通过字号/加粗识别章节层级 |
| 备选 | pdfplumber | 表格提取能力更强，必要时作为补充 |

## 向量检索层（QA Agent）

| 组件 | 选型 | 理由 |
|------|------|------|
| 向量数据库 | FAISS (faiss-cpu) | 本地运行，无需外部服务，单论文场景足够 |
| 文本切片 | LangChain RecursiveCharacterTextSplitter | 按语义边界切片，chunk_size=1000, overlap=200 |

## 前端层

| 组件 | 选型 | 理由 |
|------|------|------|
| Web UI | Streamlit | 快速出界面，内置文件上传、聊天组件、Markdown 渲染 |

## 配置管理

| 组件 | 选型 | 理由 |
|------|------|------|
| API Key 管理 | .env + python-dotenv | 简单直接，.gitignore 排除 |

## 依赖清单

```
langchain
langchain-openai
langgraph
streamlit
pymupdf
faiss-cpu
python-dotenv
```
