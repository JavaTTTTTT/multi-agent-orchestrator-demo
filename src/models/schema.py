from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum
from typing import TypedDict


class IntentType(str, Enum):
    FULL_ANALYSIS = "full_analysis"
    SUMMARY_ONLY = "summary_only"
    METHODOLOGY = "methodology"
    QA = "qa"
    UNKNOWN = "unknown"


@dataclass
class IntentResult:
    intent: IntentType
    paper_source: str  # "upload" | "url" | "already_parsed"
    focus_area: str | None = None
    language: str = "zh"


@dataclass
class Section:
    heading: str
    content: str
    level: int = 1


@dataclass
class Reference:
    title: str
    authors: list[str] = field(default_factory=list)
    year: str = ""


@dataclass
class PaperMetadata:
    year: str = ""
    venue: str = ""
    pages: int = 0


@dataclass
class ParsedPaper:
    title: str = ""
    authors: list[str] = field(default_factory=list)
    abstract: str = ""
    sections: list[Section] = field(default_factory=list)
    references: list[Reference] = field(default_factory=list)
    raw_text: str = ""
    metadata: PaperMetadata = field(default_factory=PaperMetadata)


@dataclass
class SummaryResult:
    one_line: str = ""
    key_findings: list[str] = field(default_factory=list)
    detailed_summary: str = ""
    keywords: list[str] = field(default_factory=list)


@dataclass
class MethodDetail:
    name: str = ""
    description: str = ""
    key_components: list[str] = field(default_factory=list)
    novelty: str = ""


@dataclass
class ExperimentDetail:
    datasets: list[str] = field(default_factory=list)
    baselines: list[str] = field(default_factory=list)
    metrics: list[str] = field(default_factory=list)
    main_results: str = ""


@dataclass
class ReviewDetail:
    strengths: list[str] = field(default_factory=list)
    weaknesses: list[str] = field(default_factory=list)
    suggestions: list[str] = field(default_factory=list)


@dataclass
class MethodologyResult:
    method: MethodDetail = field(default_factory=MethodDetail)
    experiment: ExperimentDetail = field(default_factory=ExperimentDetail)
    review: ReviewDetail = field(default_factory=ReviewDetail)


class GraphState(TypedDict, total=False):
    user_input: str
    intent: IntentResult
    paper_source_path: str
    paper_bytes: bytes
    parsed_paper: ParsedPaper
    summary: SummaryResult
    methodology: MethodologyResult
    report: str
    chat_history: list[dict]
    error: str
