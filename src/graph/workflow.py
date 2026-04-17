from __future__ import annotations

from langgraph.graph import END, StateGraph

from src.agents.intent import intent_agent
from src.agents.methodology import methodology_agent
from src.agents.parser import paper_parser_agent
from src.agents.qa import qa_agent
from src.agents.report import report_synthesizer
from src.agents.summary import summary_agent
from src.models.schema import GraphState, IntentType


def _route_by_intent(state: GraphState) -> str:
    intent = state.get("intent")
    if not intent:
        return "end"

    match intent.intent:
        case IntentType.FULL_ANALYSIS | IntentType.SUMMARY_ONLY | IntentType.METHODOLOGY:
            return "parse"
        case IntentType.QA:
            return "qa" if state.get("parsed_paper") else "parse"
        case _:
            return "end"


def _route_after_parse(state: GraphState) -> str | list[str]:
    if state.get("error"):
        return "end"

    intent = state.get("intent")
    if not intent:
        return "end"

    match intent.intent:
        case IntentType.FULL_ANALYSIS:
            return ["summary", "methodology"]
        case IntentType.SUMMARY_ONLY:
            return "summary"
        case IntentType.METHODOLOGY:
            return "methodology"
        case IntentType.QA:
            return "qa"
        case _:
            return "end"


def build_graph() -> StateGraph:
    graph = StateGraph(GraphState)

    graph.add_node("intent", intent_agent)
    graph.add_node("parse", paper_parser_agent)
    graph.add_node("summary", summary_agent)
    graph.add_node("methodology", methodology_agent)
    graph.add_node("qa", qa_agent)
    graph.add_node("report", report_synthesizer)

    graph.set_entry_point("intent")

    graph.add_conditional_edges("intent", _route_by_intent, {
        "parse": "parse",
        "qa": "qa",
        "end": END,
    })

    graph.add_conditional_edges("parse", _route_after_parse, {
        "summary": "summary",
        "methodology": "methodology",
        "qa": "qa",
        "end": END,
    })

    graph.add_edge("summary", "report")
    graph.add_edge("methodology", "report")
    graph.add_edge("qa", END)
    graph.add_edge("report", END)

    return graph


def run_graph(state: GraphState) -> GraphState:
    graph = build_graph()
    app = graph.compile()
    result = app.invoke(state)
    return result
