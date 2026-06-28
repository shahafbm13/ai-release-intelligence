# AI Release Intelligence Platform

Turn CI failure signals into evidence-backed classifications and explainable release-risk assessments.

## Status

**Phase B — Milestone 6 complete.** Portfolio-ready: eval suite, CI, runbooks, case study.

Live progress: [docs/delivery/05-milestone-status.md](docs/delivery/05-milestone-status.md)

**New contributor?** [CONTRIBUTING.md](CONTRIBUTING.md) · [docs/HANDOFF.md](docs/HANDOFF.md)

## Documentation

| Area | Location |
|------|----------|
| Product | [docs/product/](docs/product/) |
| Architecture | [docs/architecture/](docs/architecture/) |
| Delivery | [docs/delivery/](docs/delivery/) |
| Progress & handoff | [05-milestone-status.md](docs/delivery/05-milestone-status.md), [HANDOFF.md](docs/HANDOFF.md) |
| Portfolio | [case study](docs/portfolio/case-study.md), [demo script](docs/portfolio/demo-script.md) |
| Runbooks | [docs/runbooks/](docs/runbooks/) |
| ADRs | [docs/architecture/decisions/](docs/architecture/decisions/) |

## Technology stack

- Python 3.12+, FastAPI, SQLAlchemy 2, Alembic, Celery, PostgreSQL, Redis
- JWT authentication, modular monolith + worker

## Local setup

### Prerequisites

- Python 3.12+
- Docker Desktop (for PostgreSQL and Redis)

### Quick start

```bash
cp .env.example .env
docker compose up -d postgres redis
pip install -e ".[dev]"
alembic -c migrations/alembic.ini upgrade head
python -m api.seed
uvicorn api.main:app --reload --host 0.0.0.0 --port 8000
```

In a second terminal:

```bash
celery -A worker.celery_app worker --loglevel=info
```

Dashboard (third terminal):

```bash
cd apps/web && npm install && npm run dev
```

Open http://localhost:3000 (API at http://localhost:8000/docs).

### Demo credentials (after seed)

| Email | Password | Role |
|-------|----------|------|
| analyst@demo.example.com | demo-pass-1 | analyst |
| viewer@demo.example.com | demo-pass-2 | viewer |
| admin@demo.example.com | demo-pass-3 | admin |

### API endpoints (M1–M4)

| Method | Path | Auth |
|--------|------|------|
| GET | `/health` | No |
| GET | `/ready` | No |
| POST | `/api/v1/auth/login` | No |
| GET | `/api/v1/auth/me` | Bearer JWT |
| GET | `/api/v1/organizations/me` | Bearer JWT |
| GET | `/api/v1/repositories` | Bearer JWT |
| POST | `/api/v1/repositories` | Bearer JWT (analyst/admin) |
| POST | `/api/v1/webhooks/github` | HMAC (`X-Hub-Signature-256`) |
| GET | `/api/v1/ci-runs` | Bearer JWT |
| GET | `/api/v1/ci-runs/{id}` | Bearer JWT |
| GET | `/api/v1/ci-runs/{id}/assessment` | Bearer JWT |
| GET | `/api/v1/failures` | Bearer JWT (`ci_run_id` query) |
| GET | `/api/v1/failures/{id}` | Bearer JWT |
| GET | `/api/v1/failures/{id}/similar` | Bearer JWT |
| POST | `/api/v1/failures/{id}/feedback` | Bearer JWT (analyst/admin) |
| GET | `/api/v1/metrics/summary` | Bearer JWT |
| POST | `/api/v1/admin/seed/replay` | Bearer JWT (admin) |

OpenAPI docs: http://localhost:8000/docs

### Testing

Requires Docker (PostgreSQL + Redis running):

```bash
pytest tests/ -v
make eval              # AI eval suite (10 cases)
make eval-report       # writes reports/eval-report.md
```

Tests skip gracefully if PostgreSQL is unavailable.

### Makefile shortcuts

```bash
make install
make dev-up
make migrate
make seed
make test
```

## MVP summary

- **Primary user:** QA Automation Engineer
- **Cost target:** $0 (free APIs + free hosting tiers)

## Key decisions

- Modular monolith + worker (not microservices)
- Deterministic release-risk engine (not LLM) — M4 done
- Free-first LLM chain (Groq → Gemini → rules) — M3
