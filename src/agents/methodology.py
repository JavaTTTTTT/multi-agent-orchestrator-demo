from __future__ import annotations

import json

from langchain_core.messages import HumanMessage, SystemMessage

from src.llm import get_llm
from src.models.schema import (
    ExperimentDetail,
    GraphState,
    MethodDetail,
    MethodologyResult,
    ReviewDetail,
)
from src.prompts.methodology_prompts import (
    METHODOLOGY_SYSTEM_PROMPT,
    METHODOLOGY_USER_PROMPT,
)


def methodology_agent(state: GraphState) -> GraphState:
    paper = state.get("parsed_paper")
    if not paper:
        return {"error": "未找到解析后的论文数据"}

    sections_text = "\n\n".join(
        f"## {s.heading}\n{s.content}" for s in paper.sections if s.heading.lower() != "references"
    )
    if len(sections_text) > 8000:
        sections_text = sections_text[:8000] + "\n...(截断)"

    llm = get_llm()
    messages = [
        SystemMessage(content=METHODOLOGY_SYSTEM_PROMPT),
        HumanMessage(content=METHODOLOGY_USER_PROMPT.format(
            title=paper.title,
            abstract=paper.abstract,
            sections_text=sections_text,
        )),
    ]

    try:
        response = llm.invoke(messages)
        text = response.content.strip()
        text = text.removeprefix("```json").removesuffix("```").strip()
        data = json.loads(text)

        m = data.get("method", {})
        e = data.get("experiment", {})
        r = data.get("review", {})

        result = MethodologyResult(
            method=MethodDetail(
                name=m.get("name", ""),
                description=m.get("description", ""),
                key_components=m.get("key_components", []),
                novelty=m.get("novelty", ""),
            ),
            experiment=ExperimentDetail(
                datasets=e.get("datasets", []),
                baselines=e.get("baselines", []),
                metrics=e.get("metrics", []),
                main_results=e.get("main_results", ""),
            ),
            review=ReviewDetail(
                strengths=r.get("strengths", []),
                weaknesses=r.get("weaknesses", []),
                suggestions=r.get("suggestions", []),
            ),
        )
    except (json.JSONDecodeError, Exception) as ex:
        return {"error": f"方法论分析失败: {ex}"}

    return {"methodology": result}
