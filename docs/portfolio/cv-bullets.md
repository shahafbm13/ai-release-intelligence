# Portfolio Assets

## CV bullets (adapt to your resume)

- Built an **AI-assisted CI failure triage platform** (FastAPI, Celery, PostgreSQL, Next.js) that classifies test failures and produces **explainable release-risk assessments** on a **$0 free-tier stack**.
- Designed a **pluggable LLM provider chain** (Groq → Gemini → rules) with JSON schema validation, repair retries, and **10-case eval suite** for regression testing without live API keys in CI.
- Implemented **deterministic release-risk engine** with golden tests — separating probabilistic classification from auditable release recommendations (ADR-008).
- Delivered **idempotent webhook ingestion** with HMAC verification, org-isolated JWT auth, and **human-in-the-loop feedback** with immutable AI records.
- Shipped **Next.js analyst dashboard** (runs, failures, similar history, metrics) with Docker Compose local dev and Render/Neon deploy documentation.

## Interview stories (STAR prompts)

### 1. AI vs deterministic split

**Situation:** Release decisions need auditability; LLM classifications are useful but non-deterministic.  
**Task:** Design architecture that uses AI where appropriate without LLM-generated risk scores.  
**Action:** Classifications via LLM chain; release-risk via weighted code in `risk_engine.py`; eval suite tests each path independently.  
**Result:** Reviewers can inspect factor breakdown; golden tests lock risk behavior; portfolio demonstrates AI governance.

### 2. Free-tier reliability

**Situation:** No budget for paid APIs or hosting.  
**Task:** Keep platform runnable when Groq/Gemini unavailable.  
**Action:** Rule-based fallback always available; CI runs evals without API keys; deploy docs cover cold start.  
**Result:** Demo works offline; metrics track rules fallback rate as health signal.

### 3. Scope discipline

**Situation:** Many possible features (OAuth, pgvector, Slack, multi-org).  
**Task:** Ship portfolio-ready MVP in bounded milestones.  
**Action:** Phase A planning with explicit non-goals; M0–M6 delivery with backlog IDs and exit criteria.  
**Result:** End-to-end demo path complete; deferred items documented with rationale.

## Demo script

See [demo-script.md](./demo-script.md).

## Case study

See [case-study.md](./case-study.md).
