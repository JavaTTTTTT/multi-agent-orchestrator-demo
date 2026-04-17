# 架构设计

## Agent 架构总览（6 个 Agent）

```
User
  ↓
Intent Agent（意图识别 + 路由）
  ↓
Orchestrator（轻量调度）
  ├── Paper Parser Agent（结构化抽取）
  ├── Summary Agent（多级摘要）
  ├── Methodology Agent（方法 + 实验 + 简评）
  └── QA Agent（交互 + 追问）
  ↓
Report Synthesizer（统一输出）
```

## 数��流

```
PDF/URL
  → [Intent Agent] 意图识别
  → [Orchestrator] 调度决策
  → [Paper Parser] 结构化抽取
       ↓
  ┌────┴────┐
  ↓         ↓
[Summary] [Methodology]   ← 并行执行
  ↓         ↓
  └────┬────┘
       ↓
  [Report Synthesizer] → 最终报告输出
       ↓
  [QA Agent] ← 用户追问循环
```

## 路由策略

| 意图 | 调度链路 |
|------|----------|
| full_analysis | Parser → Summary + Methodology(并行) → Report |
| summary_only | Parser → Summary → Report |
| methodology | Parser → Methodology → Report |
| qa | 检查已解析 → QA Agent |

## LangGraph 状态定义

```python
class GraphState(TypedDict):
    intent: dict            # Intent Agent 输出
    parsed_paper: dict      # Paper Parser 输出
    summary: dict           # Summary Agent 输出
    methodology: dict       # Methodology Agent 输出
    report: str             # Report Synthesizer 输出
    chat_history: list      # QA 对话历史
```

## 后续迭代方向
- Figure & Table Agent：图表解读（依赖多模态模型）
- Comparison Agent：多论文对比分析
- Literature Link Agent：参考文献脉络梳理
