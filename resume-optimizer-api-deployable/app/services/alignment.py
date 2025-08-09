from typing import Dict, List, Tuple
from ..models import Resume, JobDescription, Alignment, AlignmentItem, ResponsibilityCoverage
from ..utils.text import tokenize

BANDS = [(0.75,"strong"),(0.55,"medium"),(0.35,"weak")]

def _band(score: float) -> str:
    for thr, name in BANDS:
        if score >= thr: return name
    return "missing"

def _score_term_in_text(term: str, text: str) -> float:
    # Simple lexical frequency-based score
    if not term: return 0.0
    tkns = tokenize(text)
    term_l = term.lower()
    hits = sum(1 for t in tkns if term_l in t)
    if not tkns: return 0.0
    return min(1.0, hits / max(3, len(tkns)/50))  # cap at 1.0

def compute_alignment(resume: Resume, jd: JobDescription) -> Alignment:
    text = resume.raw_text or ""
    req = jd.entities.required_skills or []
    pref = jd.entities.preferred_skills or []
    tools = jd.entities.tools or []

    skills_items: List[AlignmentItem] = []
    tools_items: List[AlignmentItem] = []

    all_terms = list(dict.fromkeys([*req, *pref]))
    for term in all_terms:
        s = _score_term_in_text(term, text)
        skills_items.append(AlignmentItem(term=term, evidence=[], strength=_band(s), confidence=float(f"{s:.2f}")))

    for t in dict.fromkeys(tools):
        s = _score_term_in_text(t, text)
        tools_items.append(AlignmentItem(term=t, evidence=[], strength=_band(s), confidence=float(f"{s:.2f}")))

    responsibilities: List[ResponsibilityCoverage] = []
    # MVP: match top 10 frequent words from JD responsibilities (if any were supplied)
    for r in (jd.entities.responsibilities or [])[:10]:
        s = _score_term_in_text(r, text)
        responsibilities.append(ResponsibilityCoverage(jd_item=r, evidence_ids=[], coverage=float(f"{s:.2f}")))

    gaps = []
    for term in all_terms:
        if _score_term_in_text(term, text) < 0.35:
            gaps.append({"term": term, "reason": "not found", "suggestion": "ApprovalRequired"})

    return Alignment(skills=skills_items, tools=tools_items, responsibilities=responsibilities, gaps=gaps)

def coverage_scores(alignment: Alignment, jd: JobDescription) -> Dict[str, float]:
    required = jd.entities.required_skills or []
    preferred = jd.entities.preferred_skills or []
    def cov(terms: List[str]) -> float:
        if not terms: return 1.0
        found = 0
        for t in terms:
            for it in alignment.skills:
                if it.term == t and it.strength in {"strong","medium"}:
                    found += 1
                    break
        return round(found / len(terms), 2)
    return {"required": cov(required), "preferred": cov(preferred)}
