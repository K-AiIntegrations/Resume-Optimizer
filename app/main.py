import os, io, time
from fastapi import FastAPI, UploadFile, File, Form
from fastapi import HTTPException
from fastapi.responses import FileResponse, HTMLResponse
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel
from typing import Optional, Dict, Any

from .models import Resume, JobDescription, JobPackage, Settings, Alignment, Report
from .services.parser import parse_resume, parse_jd
from .services.alignment import compute_alignment, coverage_scores
from .services.ats import ats_check
from .services.optimizer import rewrite_bullets, build_tailored_resume
from .services.exporter import export_resume_files

APP_NAME = os.getenv("APP_NAME","resume-optimizer-api")
STORAGE_DIR = os.getenv("STORAGE_DIR","files")

app = FastAPI(title=APP_NAME, version="0.1.0-MVP")
app.mount("/files", StaticFiles(directory=STORAGE_DIR), name="files")


# Permissive CORS for testing (tighten in production)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)



class JDInput(BaseModel):
    text: Optional[str] = None
    url: Optional[str] = None

@app.get("/healthz")
def health():
    return {"ok": True, "service": APP_NAME}

@app.post("/parse/resume")
async def parse_resume_api(file: UploadFile = File(...)):
    content = await file.read()
    resume = parse_resume(file.filename, content)
    return {"resume": resume.model_dump()}

@app.post("/parse/jd")
async def parse_jd_api(file: Optional[UploadFile] = File(None), text: Optional[str] = Form(None), url: Optional[str] = Form(None)):
    content = await file.read() if file is not None else b""
    jd = parse_jd(filename=(file.filename if file else "jd.txt"), content=content, text_input=text or "", url=url or "")
    return {"job_description": jd.model_dump()}

@app.post("/align")
async def align_api(payload: Dict[str, Any]):
    try:
        resume = Resume(**payload.get("resume"))
        jd = JobDescription(**payload.get("job_description"))
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Invalid payload: {e}")
    alignment = compute_alignment(resume, jd)
    coverage = coverage_scores(alignment, jd)
    return {"alignment": alignment.model_dump(), "coverage": coverage}

@app.post("/ats/check")
async def ats_check_api(payload: Dict[str, Any]):
    resume = Resume(**payload.get("resume"))
    checklist = ats_check(resume)
    return {"ats_checklist": checklist}

@app.post("/optimize")
async def optimize_api(payload: Dict[str, Any]):
    resume = Resume(**payload.get("resume"))
    jd = JobDescription(**payload.get("job_description"))
    alignment = compute_alignment(resume, jd)
    edits = rewrite_bullets(resume, jd, alignment)
    tailored = build_tailored_resume(resume, jd, alignment)
    return {"edits": [e.model_dump() for e in edits], "tailored_resume": tailored.model_dump()}

@app.post("/export/resume")
async def export_resume_api(payload: Dict[str, Any]):
    resume = Resume(**payload.get("resume"))
    os.makedirs(STORAGE_DIR, exist_ok=True)
    docx_path, pdf_path = export_resume_files(resume, STORAGE_DIR)
    return {"docx_url": f"/files/{os.path.basename(docx_path)}", "pdf_url": f"/files/{os.path.basename(pdf_path)}"}

@app.post("/report")
async def report_api(payload: Dict[str, Any]):
    # Minimal HTML report
    from datetime import datetime
    resume = Resume(**payload.get("resume"))
    jd = JobDescription(**payload.get("job_description"))
    alignment = compute_alignment(resume, jd)
    coverage = coverage_scores(alignment, jd)
    os.makedirs(STORAGE_DIR, exist_ok=True)
    ts = int(time.time())
    html_path = os.path.join(STORAGE_DIR, f"report_{ts}.html")
    with open(html_path, "w", encoding="utf-8") as f:
        f.write(f"<html><head><meta charset='utf-8'><title>Alignment Report</title></head><body>")
        f.write("<h1>Alignment Report</h1>")
        f.write(f"<p>Generated: {datetime.utcnow().isoformat()}Z</p>")
        f.write(f"<h2>Coverage</h2><pre>{coverage}</pre>")
        f.write("<h2>Gaps</h2><ul>")
        for g in alignment.gaps:
            f.write(f"<li>{g['term']} – {g['reason']}</li>")
        f.write("</ul></body></html>")
    return {"html_url": f"/files/{os.path.basename(html_path)}"}

@app.post("/cover-letter")
async def cover_letter_api(payload: Dict[str, Any]):
    resume = Resume(**payload.get("resume"))
    jd = JobDescription(**payload.get("job_description"))
    # Minimal letter text
    letter = f"""Dear Hiring Manager,\n\nI am excited to apply for the {jd.title or 'target'} role. My background aligns with your needs, including: {', '.join(jd.entities.required_skills[:3])}.\n\nBest regards,\n{resume.pii.get('name','')}\n"""
    os.makedirs(STORAGE_DIR, exist_ok=True)
    path = os.path.join(STORAGE_DIR, "cover_letter.txt")
    with open(path, "w", encoding="utf-8") as f:
        f.write(letter)
    return {"txt_url": f"/files/{os.path.basename(path)}"}

@app.post("/profile/save")
async def profile_save_api(payload: Dict[str, Any]):
    os.makedirs(STORAGE_DIR, exist_ok=True)
    path = os.path.join(STORAGE_DIR, "profile.json")
    with open(path, "w", encoding="utf-8") as f:
        import json
        json.dump(payload, f, indent=2)
    return {"profile_url": f"/files/{os.path.basename(path)}"}
