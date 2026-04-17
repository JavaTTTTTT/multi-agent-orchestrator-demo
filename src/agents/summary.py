from __future__ import annotations

import json

from langchain_core.messages import HumanMessage, SystemMessage

from src.llm import get_llm
from src.models.schema import GraphState, SummaryResult
from src.prompts.summary_prompts import SUMMARY_SYSTEM_PROMPT, SUMMARY_USER_PROMPT


def summary_agent(state: GraphState) -> GraphState:
    paper = state.get("parsed_paper")
    if not paper:
        return {"error": "未找到解析后的论文数据"}

    sections_text = "\n\n".join(
        f"## {s.heading}\n{s.content}" for s in paper.sections if s.heading.lower() != "references"
    )
    # 截断避免超长
    if len(sections_text) > 8000:
        sections_text = sections_text[:8000] + "\n...(截断)"

    llm = get_llm()
    messages = [
        SystemMessage(content=SUMMARY_SYSTEM_PROMPT),
        HumanMessage(content=SUMMARY_USER_PROMPT.format(
            title=paper.title,
            authors=", ".join(paper.authors),
            abstract=paper.abstract,
            sections_text=sections_text,
        )),
    ]

    try:
        response = llm.invoke(messages)
        text = response.content.strip()
        text = text.removeprefix("```json").removesuffix("```").strip()
        data = json.loads(text)

        summary = SummaryResult(
            one_line=data.get("one_line", ""),
            key_findings=data.get("key_findings", []),
            detailed_summary=data.get("detailed_summary", ""),
            keywords=data.get("keywords", []),
        )
    except (json.JSONDecodeError, Exception) as e:
        return {"error": f"摘要生成失败: {e}"}

    return {"summary": summary}
