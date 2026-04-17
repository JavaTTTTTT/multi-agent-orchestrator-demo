from __future__ import annotations

import json

from langchain_core.messages import HumanMessage, SystemMessage

from src.llm import get_light_llm
from src.models.schema import GraphState, IntentResult, IntentType
from src.prompts.intent_prompts import INTENT_SYSTEM_PROMPT, INTENT_USER_PROMPT


def intent_agent(state: GraphState) -> GraphState:
    user_input = state.get("user_input", "")
    has_pdf = bool(state.get("paper_bytes") or state.get("paper_source_path"))
    has_parsed = bool(state.get("parsed_paper"))

    if not user_input and has_pdf:
        intent = IntentResult(
            intent=IntentType.FULL_ANALYSIS,
            paper_source="upload" if state.get("paper_bytes") else "url",
        )
        return {"intent": intent}

    llm = get_light_llm()
    messages = [
        SystemMessage(content=INTENT_SYSTEM_PROMPT),
        HumanMessage(content=INTENT_USER_PROMPT.format(
            user_input=user_input,
            has_pdf=has_pdf,
            has_parsed_paper=has_parsed,
        )),
    ]

    try:
        response = llm.invoke(messages)
        text = response.content.strip()
        text = text.removeprefix("```json").removesuffix("```").strip()
        data = json.loads(text)

        intent_type = IntentType(data.get("intent", "unknown"))
        intent = IntentResult(
            intent=intent_type,
            paper_source=data.get("paper_source", "none"),
            focus_area=data.get("focus_area"),
            language=data.get("language", "zh"),
        )
    except (json.JSONDecodeError, ValueError):
        intent = IntentResult(intent=IntentType.UNKNOWN, paper_source="none")

    return {"intent": intent}
