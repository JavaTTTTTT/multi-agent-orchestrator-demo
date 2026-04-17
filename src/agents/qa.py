from __future__ import annotations

from langchain_core.messages import HumanMessage, SystemMessage
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_community.vectorstores import FAISS

from src.config import settings
from src.llm import get_embeddings, get_llm
from src.models.schema import GraphState
from src.prompts.qa_prompts import QA_SYSTEM_PROMPT, QA_USER_PROMPT

_vector_store_cache: dict[str, FAISS] = {}


def _get_or_create_vector_store(paper_title: str, raw_text: str) -> FAISS:
    if paper_title in _vector_store_cache:
        return _vector_store_cache[paper_title]

    splitter = RecursiveCharacterTextSplitter(
        chunk_size=settings.CHUNK_SIZE,
        chunk_overlap=settings.CHUNK_OVERLAP,
    )
    chunks = splitter.split_text(raw_text)
    embeddings = get_embeddings()
    store = FAISS.from_texts(chunks, embeddings)
    _vector_store_cache[paper_title] = store
    return store


def qa_agent(state: GraphState) -> GraphState:
    paper = state.get("parsed_paper")
    question = state.get("user_input", "")
    chat_history = state.get("chat_history", [])

    if not paper:
        return {"error": "未找到解析后的论文数据，请先上传论文"}
    if not question:
        return {"error": "请输入问题"}

    store = _get_or_create_vector_store(paper.title, paper.raw_text)
    docs = store.similarity_search(question, k=4)
    context = "\n\n".join(doc.page_content for doc in docs)

    history_text = ""
    for msg in chat_history[-6:]:
        role = "用户" if msg.get("role") == "user" else "助手"
        history_text += f"{role}: {msg.get('content', '')}\n"

    llm = get_llm()
    messages = [
        SystemMessage(content=QA_SYSTEM_PROMPT),
        HumanMessage(content=QA_USER_PROMPT.format(
            title=paper.title,
            context=context,
            chat_history=history_text or "(无)",
            question=question,
        )),
    ]

    response = llm.invoke(messages)
    answer = response.content.strip()

    new_history = chat_history + [
        {"role": "user", "content": question},
        {"role": "assistant", "content": answer},
    ]

    return {"report": answer, "chat_history": new_history}
