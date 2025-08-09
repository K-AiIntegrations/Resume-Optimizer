from typing import List, Dict, Any
from ..models import Resume, JobDescription, Alignment, EditItem
from ..utils.text import ACTION_VERBS, tokenize

def rewrite_bullets(resume: Resume, jd: JobDescription, alignment: Alignment) -> List[EditItem]:
    # MVP: take first 3 sentences from raw_text and prefix with strong verbs if present
    text = resume.raw_text or ""
    sentences = [s.strip() for s in text.split(".") if len(s.strip()) > 8][:3]
    edits: List[EditItem] = []
    for idx, s in enumerate(sentences):
        verb = ACTION_VERBS[idx % len(ACTION_VERBS)]
        new_text = verb.capitalize() + ": " + s
        edits.append(EditItem(type="rewrite", source_id=f"exp.1.b{idx+1}", new_text=new_text))
    return edits

def build_tailored_resume(resume: Resume, jd: JobDescription, alignment: Alignment) -> Resume:
    # MVP: return original resume with summary enriched by JD title/keywords that already exist in resume text
    existing_tokens = set(tokenize(resume.raw_text))
    jd_terms = (jd.entities.required_skills or []) + (jd.entities.preferred_skills or []) + (jd.entities.keywords or [])
    keep_terms = [t for t in jd_terms if t.lower() in existing_tokens]
    addendum = (" | ".join(keep_terms[:10])) if keep_terms else "Aligned to target role."
    new_summary = (resume.summary + " — " + addendum).strip(" —")
    resume.summary = new_summary
    return resume
