"""Paper Parser 测试页面 — 上传 PDF 查看解析结果"""
import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

import streamlit as st
from src.parsers.pdf_parser import parse_pdf_from_bytes

st.set_page_config(page_title="Paper Parser 测试", layout="wide")
st.title("Paper Parser 测试页面")

uploaded = st.file_uploader("上传论文 PDF", type=["pdf"])

if uploaded:
    pdf_bytes = uploaded.read()
    paper = parse_pdf_from_bytes(pdf_bytes, uploaded.name)

    col1, col2 = st.columns(2)

    with col1:
        st.header("原始文档")
        st.markdown(f"**文件名:** {uploaded.name}")
        st.markdown(f"**大小:** {len(pdf_bytes) / 1024:.1f} KB")
        st.markdown(f"**页数:** {paper.metadata.pages}")
        st.divider()
        st.subheader("原始文本")
        st.text_area("raw_text", paper.raw_text, height=600, label_visibility="collapsed")

    with col2:
        st.header("解析结果")

        st.subheader("标题")
        st.write(paper.title)

        st.subheader("作者")
        st.write(", ".join(paper.authors) if paper.authors else "（未提取）")

        st.subheader("元数据")
        meta_cols = st.columns(3)
        meta_cols[0].metric("页数", paper.metadata.pages)
        meta_cols[1].metric("年份", paper.metadata.year or "未提取")
        meta_cols[2].metric("会议/期刊", paper.metadata.venue or "未提取")

        st.subheader("摘要")
        st.write(paper.abstract or "（未提取）")

        st.subheader(f"章节 ({len(paper.sections)})")
        for i, s in enumerate(paper.sections):
            with st.expander(f"[L{s.level}] {s.heading} ({len(s.content)} chars)"):
                st.write(s.content)

        st.subheader(f"参考文献 ({len(paper.references)})")
        for i, r in enumerate(paper.references):
            st.markdown(f"**[{i+1}]** {r.title}  \n年份: {r.year or '未提取'}")
