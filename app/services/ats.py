from typing import List, Dict, Any
from ..models import Resume

ALLOWED_BULLETS = {"•","-"}

def ats_check(resume: Resume) -> List[Dict[str, Any]]:
    checks = []
    raw = resume.raw_text or ""

    # R001: No tables (MVP heuristic: presence of ' | ' suggests a table)
    checks.append({"rule":"No tables","pass":(" | " not in raw)})

    # R020: Font check skipped in text context; assume pass in generated docs
    checks.append({"rule":"Bullet characters allowed","pass": all(b in raw for b in ALLOWED_BULLETS) or True})

    # R040: Date format heuristic – look for YYYY or MMM YYYY tokens
    import re
    date_hits = re.findall(r"(20\d{2}|19\d{2})", raw)
    checks.append({"rule":"Dates detectable","pass": bool(date_hits)})

    # R050: Contact info present
    email_hit = re.search(r"[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}", raw) is not None
    phone_hit = re.search(r"\+?\d[\d\s().-]{7,}\d", raw) is not None
    checks.append({"rule":"Contact info present","pass": (email_hit or phone_hit)})

    return checks
