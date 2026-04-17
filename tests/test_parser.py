"""Paper Parser 功能测试 — 对比原始文档与解析结果"""
import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

import fitz
from src.parsers.pdf_parser import parse_pdf

SEPARATOR = "=" * 70
SUB_SEPARATOR = "-" * 50
TEST_PDF_PATH = "tests/test_paper.pdf"


def create_test_pdf(path: str):
    """生成一个模拟学术论文 PDF"""
    doc = fitz.open()

    page = doc.new_page()
    y = 72

    page.insert_text((72, y), "Attention Is All You Need", fontsize=20, fontname="helv")
    y += 40
    page.insert_text((72, y), "Ashish Vaswani, Noam Shazeer, Niki Parmar", fontsize=11, fontname="helv")
    y += 20
    page.insert_text((72, y), "Google Brain", fontsize=10, fontname="helv")
    y += 40
    page.insert_text((72, y), "Abstract", fontsize=14, fontname="helvetica-bold")
    y += 25
    abstract_text = (
        "The dominant sequence transduction models are based on complex recurrent or "
        "convolutional neural networks that include an encoder and a decoder. The best "
        "performing models also connect the encoder and decoder through an attention mechanism. "
        "We propose a new simple network architecture, the Transformer, based solely on "
        "attention mechanisms, dispensing with recurrence and convolutions entirely."
    )
    for i in range(0, len(abstract_text), 80):
        page.insert_text((72, y), abstract_text[i:i+80], fontsize=10, fontname="helv")
        y += 14
    y += 20
    page.insert_text((72, y), "1 Introduction", fontsize=14, fontname="helvetica-bold")
    y += 25
    intro = (
        "Recurrent neural networks, long short-term memory and gated recurrent neural networks "
        "in particular, have been firmly established as state of the art approaches in sequence "
        "modeling and transduction problems such as language modeling and machine translation."
    )
    for i in range(0, len(intro), 80):
        page.insert_text((72, y), intro[i:i+80], fontsize=10, fontname="helv")
        y += 14

    page2 = doc.new_page()
    y = 72
    page2.insert_text((72, y), "3 Method", fontsize=14, fontname="helvetica-bold")
    y += 25
    method = (
        "The Transformer follows an encoder-decoder structure using stacked self-attention "
        "and point-wise, fully connected layers for both the encoder and decoder."
    )
    for i in range(0, len(method), 80):
        page2.insert_text((72, y), method[i:i+80], fontsize=10, fontname="helv")
        y += 14
    y += 20
    page2.insert_text((72, y), "5 Experiments", fontsize=14, fontname="helvetica-bold")
    y += 25
    exp = (
        "We trained our models on the WMT 2014 English-German and English-French datasets. "
        "The Transformer achieves 28.4 BLEU on the English-to-German translation task, "
        "improving over the existing best results by over 2 BLEU."
    )
    for i in range(0, len(exp), 80):
        page2.insert_text((72, y), exp[i:i+80], fontsize=10, fontname="helv")
        y += 14
    y += 20
    page2.insert_text((72, y), "References", fontsize=14, fontname="helvetica-bold")
    y += 25
    refs = [
        "[1] Bahdanau, D., Cho, K., and Bengio, Y. Neural machine translation by jointly learning to align and translate. (2015)",
        "[2] Gehring, J., Auli, M., Grangier, D. Convolutional sequence to sequence learning. (2017)",
        "[3] Hochreiter, S. and Schmidhuber, J. Long short-term memory. Neural computation (1997)",
    ]
    for ref in refs:
        for i in range(0, len(ref), 85):
            page2.insert_text((72, y), ref[i:i+85], fontsize=9, fontname="helv")
            y += 13
        y += 5

    doc.save(path)
    doc.close()


def print_raw_pdf(path: str):
    """逐页打印 PDF 原始文本，展示 PyMuPDF 实际提取到的内容"""
    doc = fitz.open(path)
    print(SEPARATOR)
    print("【原始文档内容】")
    print(SEPARATOR)
    for i, page in enumerate(doc):
        print(f"\n--- 第 {i + 1} 页 ---\n")
        print(page.get_text())
    doc.close()


def print_parsed_result(paper):
    """打印完整的解析结果"""
    print(SEPARATOR)
    print("【解析结果】")
    print(SEPARATOR)

    print(f"\n[标题]")
    print(f"  {paper.title}")

    print(f"\n[作者]")
    for a in paper.authors:
        print(f"  - {a}")

    print(f"\n[元数据]")
    print(f"  页数: {paper.metadata.pages}")
    print(f"  年份: {paper.metadata.year or '(未提取)'}")
    print(f"  会议/期刊: {paper.metadata.venue or '(未提取)'}")

    print(f"\n[摘要]")
    print(f"  {paper.abstract}")

    print(f"\n[章节] 共 {len(paper.sections)} 个")
    print(SUB_SEPARATOR)
    for i, s in enumerate(paper.sections):
        print(f"\n  [{i + 1}] {s.heading}  (level={s.level}, {len(s.content)} chars)")
        preview = s.content[:200]
        if len(s.content) > 200:
            preview += "..."
        for line in preview.split("\n"):
            print(f"      {line}")

    print(f"\n[参考文献] 共 {len(paper.references)} 条")
    print(SUB_SEPARATOR)
    for i, r in enumerate(paper.references):
        print(f"  [{i + 1}] {r.title}")
        print(f"       年份: {r.year or '(未提取)'}  作者: {', '.join(r.authors) or '(未提取)'}")

    print(f"\n[原始文本] {len(paper.raw_text)} chars")


def print_comparison(paper):
    """对比关键字段：期望值 vs 实际值"""
    print("\n" + SEPARATOR)
    print("【对比检查】")
    print(SEPARATOR)

    checks = [
        ("标题", "Attention Is All You Need", paper.title),
        ("作者数", "3", str(len(paper.authors))),
        ("摘要非空", "True", str(bool(paper.abstract))),
        ("章节数", ">=3", str(len(paper.sections))),
        ("参考文献数", "3", str(len(paper.references))),
        ("页数", "2", str(paper.metadata.pages)),
        ("Ref[1]年份", "2015", paper.references[0].year if paper.references else ""),
        ("Ref[2]年份", "2017", paper.references[1].year if len(paper.references) > 1 else ""),
        ("Ref[3]年份", "1997", paper.references[2].year if len(paper.references) > 2 else ""),
    ]

    all_pass = True
    for name, expected, actual in checks:
        if expected.startswith(">="):
            ok = int(actual) >= int(expected[2:])
        else:
            ok = expected == actual
        status = "PASS" if ok else "FAIL"
        if not ok:
            all_pass = False
        print(f"  [{status}] {name}: 期望={expected}, 实际={actual}")

    print(f"\n{'所有检查通过' if all_pass else '存在失败项，请检查上方详情'}")
    return all_pass


def main():
    # create_test_pdf(TEST_PDF_PATH)
    # print(f"测试 PDF 已生成: {os.path.abspath(TEST_PDF_PATH)}")
    # print(f"(可用 PDF 阅读器打开查看原始文档)\n")

    # print_raw_pdf(TEST_PDF_PATH)

    print("\n")

    paper = parse_pdf(TEST_PDF_PATH)
    print_parsed_result(paper)

    print_comparison(paper)


if __name__ == "__main__":
    main()
