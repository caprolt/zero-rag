# Job Application Assistant — Implementation Plan

> Drop this file into your repo as `IMPLEMENTATION_PLAN.md`. It’s a build-first plan with tasks, commands, API specs, schemas, prompts, and acceptance criteria.

---

## 0) Goals & Non-Goals

**Goals**
- Ingest a job posting URL, extract a normalized Job Description (JD).
- Parse a base resume into structured JSON.
- Generate a tailored resume (DOCX + PDF) and a cover letter (DOCX + PDF).
- Provide a diff/preview UI for human-in-the-loop edits.

**Non-Goals (MVP)**
- Account creation & billing.
- Multi-language JD parsing (beyond English).
- Advanced ATS scoring and company intel.

---

## 1) Architecture

- **Frontend**: Next.js (App Router), Tailwind, shadcn/ui
- **API**: FastAPI (Python 3.11+)
- **Workers**: Celery (Redis broker)
- **Data**: Postgres (metadata), local MinIO/S3 (files)
- **Vector (optional, M3+)**: Qdrant/FAISS
- **Scraping**: Playwright + Readability fallback
- **LLM Provider**: pluggable (OpenAI/Ollama/HF via one interface)
- **PDF/DOCX**: `python-docx` + `weasyprint` (or `docx-template` + `wkhtmltopdf`)
- **Observability**: Sentry + basic logging; Prometheus later

---

## 2) Repo Layout

```
/app
  /frontend          # Next.js
  /api               # FastAPI
    /routers         # route handlers
    /schemas         # pydantic models
    /services        # scraping, parsing, matching, generation
    /workers         # celery tasks
    /templates       # Jinja2 templates (resume, cover letter)
    /prompts         # system + task prompts
    /db              # alembic migrations
    /utils           # common utilities (cache, logging)
  /infrastructure
    docker-compose.yml
    Dockerfile.api
    Dockerfile.frontend
    env.example
/docs
  IMPLEMENTATION_PLAN.md (this file)
```

---

## 3) Environment & Bootstrap

**Prereqs**
- Node 20+, Python 3.11+, Docker, Playwright dependencies

**Environment**
```bash
cp app/infrastructure/env.example .env
# Fill: DATABASE_URL, REDIS_URL, STORAGE_BUCKET, LLM_PROVIDER, LLM_API_KEY, FILE_BASE_URL, S3 creds (optional)
```

**Backend (dev)**
```bash
cd app/api
python -m venv .venv && source .venv/bin/activate
pip install -U pip
pip install -r requirements.txt
alembic upgrade head
uvicorn main:app --reload --port 8000
```

**Workers**
```bash
celery -A workers.celery_app worker -l info
```

**Frontend**
```bash
cd app/frontend
npm i
npm run dev
```

**Playwright setup**
```bash
npx playwright install
```

---

## 4) Database Schema (Postgres via Alembic)

Tables (core):
- `users(id, email, name, created_at)`
- `jobs(id, user_id, url, company, title, location, description_json, raw_html, normalized_text, skills, seniority, created_at)`
- `resumes(id, user_id, source_file_uri, parsed_json, created_at)`
- `tailoring_runs(id, user_id, job_id, resume_id, status, scores_json, plan_json, prompts_json, outputs_uri, created_at)`
- `documents(id, owner_id, kind, format, uri, version, created_at)`

Enum hints:
- `documents.kind ∈ {resume, cover_letter}`
- `documents.format ∈ {docx, pdf, md}`

---

## 5) Pydantic Schemas (API)

`schemas/job.py`
```python
class JobDescription(BaseModel):
    company: str | None = None
    title: str | None = None
    location: str | None = None
    employment_type: str | None = None
    seniority: str | None = None
    posted_date: str | None = None
    compensation: str | None = None
    responsibilities: list[str] = []
    requirements: list[str] = []
    nice_to_haves: list[str] = []
    tech_stack: list[str] = []
    keywords: list[str] = []
    about_company: str | None = None
```

`schemas/resume.py`
```python
class ResumeBullet(BaseModel):
    text: str
    action: str | None = None
    impact: str | None = None
    metric: str | None = None
    tech: list[str] = []

class ResumeSection(BaseModel):
    name: str
    bullets: list[ResumeBullet] = []

class ResumeDoc(BaseModel):
    header: dict[str, str] = {}  # name, email, links
    sections: list[ResumeSection] = []
    skills: list[str] = []
```

`schemas/tailor.py`
```python
class TailorRequest(BaseModel):
    job_id: str
    resume_id: str
    style_prefs: dict[str, Any] | None = None  # tone, length, etc.

class TailorPlan(BaseModel):
    keep: list[str] = []
    drop: list[str] = []
    rewrite: list[dict] = []  # {old, new, why}
    order: list[str] = []     # sections order
    header_tweaks: dict[str, str] = {}
```
