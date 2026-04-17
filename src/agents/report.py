from __future__ import annotations

from src.models.schema import GraphState


def report_synthesizer(state: GraphState) -> GraphState:
    paper = state.get("parsed_paper")
    summary = state.get("summary")
    methodology = state.get("methodology")

    if not paper:
        return {"error": "未找到解析后的论文数据"}

    lines = [f"# 论文解析报告：{paper.title}\n"]

    if paper.authors:
        lines.append(f"**作者:** {', '.join(paper.authors)}")
    if paper.metadata.year or paper.metadata.venue:
        meta_parts = []
        if paper.metadata.year:
            meta_parts.append(paper.metadata.year)
        if paper.metadata.venue:
            meta_parts.append(paper.metadata.venue)
        lines.append(f"**发表:** {' / '.join(meta_parts)}")
    lines.append("")

    if summary:
        lines.append("## 一句话总结")
        lines.append(f"{summary.one_line}\n")

        if summary.keywords:
            lines.append(f"**关键词:** {', '.join(summary.keywords)}\n")

        lines.append("## 核心发现")
        for finding in summary.key_findings:
            lines.append(f"- {finding}")
        lines.append("")

        lines.append("## 详细摘要")
        lines.append(f"{summary.detailed_summary}\n")

    if methodology:
        m = methodology.method
        e = methodology.experiment
        r = methodology.review

        lines.append("## 方法论分析")
        lines.append(f"### 技术方法：{m.name}")
        lines.append(f"{m.description}\n")
        if m.key_components:
            lines.append("**核心组件:**")
            for comp in m.key_components:
                lines.append(f"- {comp}")
            lines.append("")
        if m.novelty:
            lines.append(f"**创新点:** {m.novelty}\n")

        lines.append("### 实验设计")
        if e.datasets:
            lines.append(f"**数据集:** {', '.join(e.datasets)}")
        if e.baselines:
            lines.append(f"**对比方法:** {', '.join(e.baselines)}")
        if e.metrics:
            lines.append(f"**评估指标:** {', '.join(e.metrics)}")
        if e.main_results:
            lines.append(f"\n**主要结果:** {e.main_results}")
        lines.append("")

        lines.append("## 评价与建议")
        if r.strengths:
            lines.append("### 优点")
            for s in r.strengths:
                lines.append(f"- {s}")
            lines.append("")
        if r.weaknesses:
            lines.append("### 不足")
            for w in r.weaknesses:
                lines.append(f"- {w}")
            lines.append("")
        if r.suggestions:
            lines.append("### 改进方向")
            for sg in r.suggestions:
                lines.append(f"- {sg}")
            lines.append("")

    report = "\n".join(lines)
    return {"report": report}
