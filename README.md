# Resume Optimizer API (MVP)

A FastAPI service that ingests a resume and job description (JD), computes alignment, generates ATS‑safe tailored resume text, and exports DOCX/PDF. This scaffold implements the endpoints from your spec with simple, testable logic and file uploads.

## Quick Start (Local)

```bash
python -m venv .venv && source .venv/bin/activate  # Windows: .venv\Scripts\activate
pip install -r requirements.txt
uvicorn app.main:app --reload
```

Open http://127.0.0.1:8000/docs for Swagger UI.

## Docker

```bash
docker build -t resume-optimizer-api .
docker run -it --rm -p 8000:8000 -v $(pwd)/files:/app/files resume-optimizer-api
```

## Endpoints (MVP)

- `POST /parse/resume` – upload PDF/DOCX/TXT to parse -> `{resume}`
- `POST /parse/jd` – upload or paste JD (PDF/DOCX/TXT/URL/text) -> `{job_description}`
- `POST /align` – compute alignment & coverage -> `{alignment}`
- `POST /optimize` – produce factual-only edits & tailored text -> `{edits, tailored_resume}`
- `POST /ats/check` – ATS safety heuristics -> `{ats_checklist}`
- `POST /export/resume` – generate DOCX and PDF -> file URLs
- `POST /report` – alignment report (HTML + PDF) -> file URLs
- `POST /cover-letter` – optional cover letter -> file URLs
- `POST /profile/save` – persist settings/profile for reuse

All data is stored under `files/` by default (mount a volume in Docker for persistence).

> Note: This MVP uses simple keyword/semantic heuristics and does **not** fabricate content. Heavy NLP/LLM logic is stubbed behind service functions so you can swap in more advanced models later.

## One‑Click Deploy

### Render (recommended for simplicity)
1. Push this folder to a public GitHub repo.
2. Go to https://render.com/deploy and **New +** → **Blueprint**; select your repo (uses `render.yaml`).
3. Click **Deploy**. Once live, open `/docs` for Swagger.

### Railway
1. Push to GitHub.
2. Visit https://railway.app/new and select your repo (it reads `railway.json`).
3. Deploy → open the generated URL → `/docs`.

### Heroku
1. Push to GitHub and create a Heroku app.
2. In Heroku → **Deploy** tab → connect GitHub repo → enable auto-deploy (uses `Procfile`).
3. Set stack to container or Python; open app → `/docs`.

### Fly.io
```bash
flyctl launch --now --copy-config  # uses fly.toml and Dockerfile
```
