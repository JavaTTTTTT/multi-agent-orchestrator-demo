# Multi-Agent Paper Analyzer

面向科研人员的多智能体论文解析系统。上传论文，自动解析、摘要、方法论分析，支持多轮追问。

## 技术栈

Python + LangChain + LangGraph + FAISS

## 项目文档

- [需求分析](docs/requirements.md) — 目标用户、核心功能、使用场景
- [架构设计](docs/architecture.md) — Agent 架构、数据流、状态管理
- [Agent 详细设计](docs/agents.md) — 各 Agent 职责、输入输出、Prompt 策略
- [技术选型](docs/tech-stack.md) — 框架对比与选型理由
- [开发进度](docs/progress.md) — 当前开发阶段与任务追踪

## 目录结构

```
src/
  agents/        # 各 Agent 实现
  graph/         # LangGraph 工作流定义
  parsers/       # PDF 解析
  prompts/       # Prompt 模板
  models/        # 数据模型
tests/           # 测试
docs/            # 项目文档
```
