from typing import List, Optional, Literal, Dict, Any
from pydantic import BaseModel, Field, HttpUrl

class Bullet(BaseModel):
    id: str
    text: str
    tokens: List[str] = []
    evidence_spans: List[Dict[str, int]] = []

class ExperienceItem(BaseModel):
    id: str
    title: str = ""
    normalized_title: str = ""
    company: str = ""
    location: str = ""
    start_date: Optional[str] = None  # YYYY-MM
    end_date: Optional[str] = None    # YYYY-MM or null
    current: bool = False
    bullets: List[Bullet] = []
    skills: List[str] = []
    tools: List[str] = []
    domains: List[str] = []

class EducationItem(BaseModel):
    school: str = ""
    degree: str = ""
    start_date: Optional[str] = None
    end_date: Optional[str] = None

class Skills(BaseModel):
    hard: List[str] = []
    soft: List[str] = []
    certifications: List[str] = []
    languages: List[str] = []

class Resume(BaseModel):
    pii: Dict[str, Any] = {}
    summary: str = ""
    experience: List[ExperienceItem] = []
    education: List[EducationItem] = []
    skills: Skills = Skills()
    projects: List[Dict[str, Any]] = []
    raw_text: str = ""
    source_meta: Dict[str, Any] = {}

class JobEntities(BaseModel):
    required_skills: List[str] = []
    preferred_skills: List[str] = []
    responsibilities: List[str] = []
    tools: List[str] = []
    certifications: List[str] = []
    domains: List[str] = []
    keywords: List[str] = []

class JobDescription(BaseModel):
    title: str = ""
    company: str = ""
    entities: JobEntities = JobEntities()
    raw_text: str = ""
    source_meta: Dict[str, Any] = {}

class AlignmentItem(BaseModel):
    term: str
    evidence: List[str] = []
    strength: Literal["strong","medium","weak","missing"] = "missing"
    confidence: float = 0.0

class ResponsibilityCoverage(BaseModel):
    jd_item: str
    evidence_ids: List[str] = []
    coverage: float = 0.0

class Alignment(BaseModel):
    skills: List[AlignmentItem] = []
    tools: List[AlignmentItem] = []
    responsibilities: List[ResponsibilityCoverage] = []
    gaps: List[Dict[str, str]] = []

class EditItem(BaseModel):
    type: Literal["rewrite","reorder"]
    source_id: Optional[str] = None
    section: Optional[str] = None
    order: Optional[List[str]] = None
    new_text: Optional[str] = None

class Report(BaseModel):
    coverage: Dict[str, float] = {"required": 0.0, "preferred": 0.0}
    gaps: List[str] = []
    ats_checklist: List[Dict[str, Any]] = []
    changelog: List[Dict[str, Any]] = []
    readability: Dict[str, float] = {}

class Settings(BaseModel):
    seniority: Literal["junior","mid","senior","lead","exec"] = "mid"
    tone: Literal["concise","impactful","formal"] = "impactful"
    length_pages: Literal[1,2] = 1
    region: Literal["US","UK","EU"] = "US"
    industry: Optional[str] = None
    linkedin_url: Optional[HttpUrl] = None

class JobPackage(BaseModel):
    resume: Resume
    job_description: JobDescription
    alignment: Optional[Alignment] = None
    edits: List[EditItem] = []
    report: Optional[Report] = None
    settings: Settings = Settings()
