from __future__ import annotations

import re

import fitz

from src.models.schema import PaperMetadata, ParsedPaper, Reference, Section


def parse_pdf(file_path: str) -> ParsedPaper:
    doc = fitz.open(file_path)
    blocks = _extract_blocks(doc)
    raw_text = "\n".join(b["text"] for b in blocks)
    title = _extract_title(blocks)
    sections = _identify_sections(blocks, title)
    authors = _extract_authors(blocks, title)
    abstract = _extract_abstract(sections, raw_text)
    references = _extract_references(raw_text)
    metadata = PaperMetadata(pages=len(doc))
    doc.close()

    return ParsedPaper(
        title=title,
        authors=authors,
        abstract=abstract,
        sections=sections,
        references=references,
        raw_text=raw_text,
        metadata=metadata,
    )


def parse_pdf_from_bytes(data: bytes, filename: str = "paper.pdf") -> ParsedPaper:
    doc = fitz.open(stream=data, filetype="pdf")
    blocks = _extract_blocks(doc)
    raw_text = "\n".join(b["text"] for b in blocks)
    title = _extract_title(blocks)
    sections = _identify_sections(blocks, title)
    authors = _extract_authors(blocks, title)
    abstract = _extract_abstract(sections, raw_text)
    references = _extract_references(raw_text)
    metadata = PaperMetadata(pages=len(doc))
    doc.close()

    return ParsedPaper(
        title=title,
        authors=authors,
        abstract=abstract,
        sections=sections,
        references=references,
        raw_text=raw_text,
        metadata=metadata,
    )


def _extract_blocks(doc: fitz.Document) -> list[dict]:
    blocks = []
    for page in doc:
        page_dict = page.get_text("dict", flags=fitz.TEXT_PRESERVE_WHITESPACE)
        for block in page_dict.get("blocks", []):
            if block.get("type") != 0:
                continue
            for line in block.get("lines", []):
                text_parts = []
                max_size = 0.0
                is_bold = False
                for span in line.get("spans", []):
                    text_parts.append(span["text"])
                    if span["size"] > max_size:
                        max_size = span["size"]
                    if "bold" in span.get("font", "").lower():
                        is_bold = True
                text = "".join(text_parts).strip()
                if text:
                    blocks.append({
                        "text": text,
                        "size": max_size,
                        "bold": is_bold,
                    })
    return blocks


def _extract_title(blocks: list[dict]) -> str:
    if not blocks:
        return ""
    max_size = max(b["size"] for b in blocks[:20])
    title_parts = []
    for b in blocks[:20]:
        if abs(b["size"] - max_size) < 0.5:
            title_parts.append(b["text"])
        elif title_parts:
            break
    return " ".join(title_parts)


def _extract_authors(blocks: list[dict], title: str) -> list[str]:
    if not blocks or not title:
        return []
    title_end = 0
    for i, b in enumerate(blocks[:20]):
        if title.startswith(b["text"]):
            title_end = i + 1
            continue
        if title_end > 0:
            break
    author_candidates = []
    for b in blocks[title_end:title_end + 5]:
        text = b["text"].strip()
        if not text or _looks_like_heading(text):
            break
        if any(kw in text.lower() for kw in ["abstract", "introduction", "@", "university", "institute"]):
            if "@" in text or "university" in text.lower():
                continue
            break
        author_candidates.append(text)

    if not author_candidates:
        return []
    raw = " ".join(author_candidates)
    raw = re.sub(r"[0-9∗†‡§¶\*,]+", ",", raw)
    authors = [a.strip() for a in raw.split(",") if a.strip() and len(a.strip()) > 1]
    return authors


def _identify_sections(blocks: list[dict], title: str = "") -> list[Section]:
    if not blocks:
        return []
    body_sizes = [b["size"] for b in blocks]
    if not body_sizes:
        return []
    body_sizes.sort()
    body_size = body_sizes[len(body_sizes) // 2]

    sections: list[Section] = []
    current_heading = ""
    current_content: list[str] = []
    current_level = 1

    for b in blocks:
        if title and b["text"].strip() == title.strip():
            continue
        if _is_heading(b, body_size):
            if current_heading or current_content:
                sections.append(Section(
                    heading=current_heading,
                    content="\n".join(current_content).strip(),
                    level=current_level,
                ))
            current_heading = b["text"]
            current_content = []
            current_level = 1 if b["size"] - body_size > 2 else 2
        else:
            current_content.append(b["text"])

    if current_heading or current_content:
        sections.append(Section(
            heading=current_heading,
            content="\n".join(current_content).strip(),
            level=current_level,
        ))

    # 过滤掉空 heading 的前导 section（通常是标题和 Abstract 之间的作者信息）
    sections = [s for s in sections if s.heading or s.content.strip()]
    if sections and not sections[0].heading:
        sections = sections[1:]

    return sections
def _is_heading(block: dict, body_size: float) -> bool:
    text = block["text"].strip()
    if len(text) > 200 or len(text) < 2:
        return False
    if block["size"] > body_size + 1:
        return True
    if block["bold"] and block["size"] >= body_size and len(text) < 80:
        if _looks_like_heading(text):
            return True
    return False


def _looks_like_heading(text: str) -> bool:
    heading_patterns = [
        r"^\d+\.?\s+[A-Z]",
        r"^(Abstract|Introduction|Related Work|Method|Approach|Experiment|Result|Discussion|Conclusion|Reference|Acknowledgment)",
        r"^[A-Z][a-z]+ [A-Z][a-z]+$",
    ]
    return any(re.match(p, text, re.IGNORECASE) for p in heading_patterns)


def _extract_abstract(sections: list[Section], raw_text: str) -> str:
    for s in sections:
        if "abstract" in s.heading.lower():
            return s.content

    match = re.search(
        r"(?i)abstract[:\s\-—]*\n?(.*?)(?=\n\s*\n|\n\d+\.?\s*introduction)",
        raw_text,
        re.DOTALL,
    )
    if match:
        return match.group(1).strip()
    return ""


def _extract_references(raw_text: str) -> list[Reference]:
    ref_match = re.search(r"(?i)\breferences?\b\s*\n", raw_text)
    if not ref_match:
        return []
    ref_text = raw_text[ref_match.end():]
    ref_text = ref_text.replace("\n", " ")
    entries = re.split(r"(?=\[\d+\])", ref_text)
    references = []
    for entry in entries:
        entry = entry.strip()
        if len(entry) < 10:
            continue
        year_match = re.search(r"\(?((?:19|20)\s?\d\s?\d)\)?", entry)
        year = year_match.group(1).replace(" ", "") if year_match else ""
        title = entry[:100].strip()
        references.append(Reference(title=title, year=year))
        if len(references) >= 50:
            break
    return references
