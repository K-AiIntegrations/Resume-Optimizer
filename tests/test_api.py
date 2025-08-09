import json
from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)

def test_health():
    r = client.get("/healthz")
    assert r.status_code == 200
    assert r.json()["ok"] is True

def test_parse_jd_text():
    r = client.post("/parse/jd", data={"text":"Looking for Python and SQL experience"})
    assert r.status_code == 200
    jd = r.json()["job_description"]
    assert "Python" in jd["entities"]["required_skills"] or "python" in [s.lower() for s in jd["entities"]["required_skills"]]

def test_align_and_optimize_roundtrip():
    resume = {"pii": {"name":"Test User","email":"test@example.com"}, "summary":"Data engineer", "raw_text": "I built ETL in Python and SQL for Snowflake."}
    jd = {"entities": {"required_skills":["Python","SQL","Snowflake"]}, "raw_text":"We need Python, SQL, Snowflake."}
    r = client.post("/align", json={"resume": resume, "job_description": jd})
    assert r.status_code == 200
    cov = r.json()["coverage"]
    assert cov["required"] >= 0.66

    r2 = client.post("/optimize", json={"resume": resume, "job_description": jd})
    assert r2.status_code == 200
    assert "tailored_resume" in r2.json()
