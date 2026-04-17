from __future__ import annotations

import json

from langchain_core.messages import HumanMessage, SystemMessage

from src.llm import get_llm
from src.models.schema import GraphState, PaperMetadata, ParsedPaper
from src.parsers.pdf_parser import parse_pdf, parse_pdf_from_bytes

METADATA_PROMPT = """你是学术论文元数据提取专家。根据以下论文的标题和前500字内容，提取元数据。

标题: {title}
内容: {content}

请以 JSON 格式返回，字段包括:
- year: 发表年份（字符串，如 "2024"，找不到则为空）
- venue: 发表会议或期刊名称（如 "NeurIPS 2024"，找不到则为空）
- authors: 作者列表（数组，如果给定的作者列表为空或不准确则修正）

仅返回 JSON，不��其他内容。"""


def paper_parser_agent(state: GraphState) -> GraphState:
    paper_path = state.get("paper_source_path", "")
    paper_bytes = state.get("paper_bytes")

    if not paper_path and not paper_bytes:
        return {"error": "未提供论文文件路径或数据"}

    try:
        if paper_bytes:
            parsed = parse_pdf_from_bytes(paper_bytes)
        else:
            parsed = parse_pdf(paper_path)
    except Exception as e:
        return {"error": f"PDF 解析失败: {e}"}

    parsed = _enrich_metadata(parsed)
    return {"parsed_paper": parsed}


def _enrich_metadata(paper: ParsedPaper) -> ParsedPaper:
    try:
        llm = get_llm()
        content_preview = paper.raw_text[:500] if paper.raw_text else paper.abstract
        messages = [
            SystemMessage(content="你是学术论文元数据提取专家，仅返回 JSON。"),
            HumanMessage(content=METADATA_PROMPT.format(
                title=paper.title,
                content=content_preview,
            )),
        ]
        response = llm.invoke(messages)
        text = response.content.strip()
        text = text.removeprefix("```json").removesuffix("```").strip()
        data = json.loads(text)

        paper.metadata.year = data.get("year", paper.metadata.year)
        paper.metadata.venue = data.get("venue", paper.metadata.venue)
        if data.get("authors") and not paper.authors:
            paper.authors = data["authors"]
    except Exception:
        pass
    return paper
