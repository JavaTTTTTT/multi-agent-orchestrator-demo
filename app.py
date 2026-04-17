"""Multi-Agent Paper Analyzer — Streamlit UI"""
import sys
import os
sys.path.insert(0, os.path.dirname(__file__))

import streamlit as st
from src.graph.workflow import run_graph
from src.models.schema import IntentType

st.set_page_config(page_title="论文解析助手", page_icon="📄", layout="wide")
st.title("📄 多智能体论文解析系统")

if "parsed_paper" not in st.session_state:
    st.session_state.parsed_paper = None
if "chat_history" not in st.session_state:
    st.session_state.chat_history = []
if "report" not in st.session_state:
    st.session_state.report = None

# --- 侧边栏：上传论文 ---
with st.sidebar:
    st.header("上传论文")
    uploaded = st.file_uploader("选择 PDF 文件", type=["pdf"])

    analysis_mode = st.radio("分析模式", [
        "全量解析",
        "仅摘要",
        "方法论分析",
    ])

    mode_map = {
        "全量解析": "",
        "仅摘要": "总结一下这篇论文",
        "方法论分析": "分析这篇论文的方法论",
    }

    if uploaded and st.button("开始分析", type="primary"):
        pdf_bytes = uploaded.read()
        user_input = mode_map[analysis_mode]

        state = {
            "user_input": user_input,
            "paper_bytes": pdf_bytes,
            "chat_history": [],
        }

        with st.spinner("正在分析论文..."):
            result = run_graph(state)

        if result.get("error"):
            st.error(f"分析失败: {result['error']}")
        else:
            st.session_state.parsed_paper = result.get("parsed_paper")
            st.session_state.report = result.get("report")
            st.session_state.chat_history = result.get("chat_history", [])
            st.success("分析完成！")
            st.rerun()

# --- 主区域 ---
if st.session_state.report:
    st.markdown(st.session_state.report)

    st.divider()
    st.subheader("💬 追问")

    for msg in st.session_state.chat_history:
        role = msg.get("role", "user")
        with st.chat_message(role):
            st.write(msg["content"])

    question = st.chat_input("输入你的问题...")
    if question:
        st.session_state.chat_history.append({"role": "user", "content": question})

        state = {
            "user_input": question,
            "parsed_paper": st.session_state.parsed_paper,
            "chat_history": st.session_state.chat_history,
        }

        with st.spinner("思考中..."):
            result = run_graph(state)

        if result.get("error"):
            st.error(result["error"])
        else:
            answer = result.get("report", "")
            st.session_state.chat_history = result.get("chat_history", st.session_state.chat_history)
            st.rerun()

elif not uploaded:
    st.info('👈 请在左侧上传 PDF 论文文件，然后点击"开始分析"')
