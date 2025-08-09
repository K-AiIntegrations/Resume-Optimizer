from typing import Tuple, Dict, Any
from io import BytesIO
from pdfminer.high_level import extract_text as pdf_extract_text
from docx import Document
import requests

from ..models import Resume, JobDescription, JobEntities
from ..utils.text import normalize_text

def parse_txt_bytes(b: bytes) -> str:
    try:
        return normalize_text(b.decode("utf-8", errors="ignore"))
    except Exception:
        return normalize_text(b.decode("latin-1", errors="ignore"))

def parse_pdf_bytes(b: bytes) -> str:
    bio = BytesIO(b)
    text = pdf_extract_text(bio) or ""
    return normalize_text(text)

def parse_docx_bytes(b: bytes) -> str:
    bio = BytesIO(b)
    doc = Document(bio)
    parts = []
    for p in doc.paragraphs:
        parts.append(p.text)
    text = "\n".join(parts)
    return normalize_text(text)

def parse_unknown(filename: str, content: bytes) -> str:
    name = filename.lower()
    if name.endswith(".pdf"): return parse_pdf_bytes(content)
    if name.endswith(".docx"): return parse_docx_bytes(content)
    return parse_txt_bytes(content)

def parse_resume(filename: str, content: bytes) -> Resume:
    text = parse_unknown(filename, content)
    # Very naive section slicing – MVP; UI allows manual fixes
    lines = [l.strip() for l in text.split("\n") if l.strip()]
    summary = lines[0][:300] if lines else ""
    resume = Resume(
        pii={},
        summary=summary,
        experience=[],
        education=[],
        skills={"hard":[],"soft":[],"certifications":[],"languages":[]},
        projects=[],
        raw_text=text,
        source_meta={"filename": filename}
    )
    return resume

def fetch_url_text(url: str) -> str:
    try:
        r = requests.get(url, timeout=10)
        r.raise_for_status()
        return normalize_text(r.text)
    except Exception:
        return ""

def parse_jd(
    filename: str = "jd.txt",
    content: bytes = b"",    text_input: str = "",    url: str = "") -> JobDescription:
    if url:
        raw = fetch_url_text(url)
    elif content:
        raw = parse_unknown(filename, content)
    else:
        raw = normalize_text(text_input or "")

    # Naive extraction: split lines, gather likely skills/tools keywords by simple heuristics
    entities = JobEntities(
        required_skills=[],
        preferred_skills=[],
        responsibilities=[],
        tools=[],
        certifications=[],
        domains=[],
        keywords=[]
    )
    # Heuristic: collect words that look like tools/skills
    for token in set(raw.split()[:500]):
        if any(ch.isdigit() for ch in token):  # e.g., ISO27001, SOC2, etc.
            entities.keywords.append(token.strip(",.;:"))
        if token.lower() in {"python","sql","node.js","nodejs","aws","gcp","azure","docker","kubernetes","snowflake"}:
            entities.required_skills.append(token)

    jd = JobDescription(
        title="",
        company="",
        entities=entities,
        raw_text=raw,
        source_meta={"filename": filename or url}
    )
    return jd
