# Agent 详细设计

## 1. Intent Agent — 意图识别 + 路由

**职责：** 理解用户输入，识别意图和参数，交给 Orchestrator。

**意图类型：**
- `full_analysis` — 全量解析（上传 PDF / "帮我解析这篇论文"）
- `summary_only` — 仅摘要（"总结一下"）
- `methodology` — 方法聚焦（"用了什么方法"）
- `qa` — 追问（"attention 怎么改进的"）
- `unknown` — 无法识别，兜底提示

**输出：**
```python
{
    "intent": "full_analysis",
    "paper_source": "upload" | "url" | "already_parsed",
    "focus_area": None | "实验部分" | "损失函数",
    "language": "zh"
}
```

---

## 2. Orchestrator — 轻量调度

**职责：** 根据意图按依赖关系调度下游 Agent，管理共享状态。

**核心逻辑：**
- 维护 LangGraph State，传递各 Agent 输出
- 控制并行（Summary + Methodology 可并行）
- 异常处理：某 Agent 失败时降级输出

---

## 3. Paper Parser Agent — 结构化抽取

**职责：** PDF → 结构化数据。

**输出：**
```python
{
    "title": str,
    "authors": list[str],
    "abstract": str,
    "sections": [{"heading": str, "content": str, "level": int}],
    "references": [{"title": str, "authors": list, "year": str}],
    "raw_text": str,
    "metadata": {"year": str, "venue": str, "pages": int}
}
```

**技术：** PyMuPDF 提取文本 + 布局信息，标题字号/加粗识别章节，参考文献正则 + LLM 辅助。

---

## 4. Summary Agent — 多级摘要

**职责：** 生成多粒度摘要。

**输出：**
```python
{
    "one_line": str,         # 一句话总结（< 50字）
    "key_findings": list,    # 3-5 条核心发现
    "detailed_summary": str, # 结构化详细摘要
    "keywords": list         # 关键术语
}
```

**输入依赖：** parsed_paper

---

## 5. Methodology Agent — 方法 + 实验 + 简评

**职责：** 分析技术方法、实验设计，给出评价。

**输出：**
```python
{
    "method": {
        "name": str,
        "description": str,
        "key_components": list,
        "novelty": str
    },
    "experiment": {
        "datasets": list,
        "baselines": list,
        "metrics": list,
        "main_results": str
    },
    "review": {
        "strengths": list,
        "weaknesses": list,
        "suggestions": list
    }
}
```

**输入依赖：** parsed_paper

---

## 6. QA Agent — 交互 + 追问

**职责：** 基于论文内容回答自由提问，支持多轮对话。

**实现：**
- parsed_paper.raw_text → 切片 → 向量数据库（FAISS）
- 用户提问 → 检索相关片段 → LLM 生成回答
- 维护 chat_history 支持上下文追问

**输入依赖：** parsed_paper + chat_history

---

## 7. Report Synthesizer — 统一输出

**职责：** 组装各 Agent 输出为 Markdown 报告。

**输出模板：**
```markdown
# 论文解析报告：{title}
## 一句话总结
## 核心发现
## 详细摘要
## 方法论分析
### 技术方法
### 实验设计
## 评价与建议
### 优点
### 不足
### 改进方向
```

**输入依赖：** summary + methodology
