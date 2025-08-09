import re, unicodedata
from typing import List

SAFE_BULLET = "•"

def normalize_text(txt: str) -> str:
    if not txt:
        return ""
    txt = unicodedata.normalize("NFKC", txt)
    # unify bullets & whitespace
    txt = txt.replace("\u2022", SAFE_BULLET).replace("*", SAFE_BULLET)
    txt = re.sub(r"\s+", " ", txt).strip()
    return txt

def tokenize(txt: str) -> List[str]:
    txt = txt.lower()
    # simple tokenization
    tokens = re.findall(r"[a-z0-9+.#-]+", txt)
    return tokens

ACTION_VERBS = [
    "led","built","automated","designed","implemented","optimized","launched","improved","delivered",
    "migrated","developed","analyzed","reduced","increased","collaborated","owned","drove"
]
