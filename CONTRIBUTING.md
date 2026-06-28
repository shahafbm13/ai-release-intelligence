# Contributing

Thank you for contributing to the AI Release Intelligence Platform.

## Development setup

See [README.md](README.md) for prerequisites and quick start. You need Python 3.12+, Docker (Postgres + Redis), and optionally Node 20+ for the dashboard.

```bash
cp .env.example .env
docker compose up -d postgres redis
pip install -e ".[dev]"
alembic -c migrations/alembic.ini upgrade head
python -m api.seed
```

## Running tests

Requires Docker services running:

```bash
make test                    # full suite
pytest tests/unit -v         # unit only
pytest tests/integration -v  # integration (Postgres)
pytest tests/evals -v        # AI eval suite
pytest tests/e2e -v          # critical path E2E
python tests/evals/runner.py # generate eval report → reports/
```

## Code style

- **Python:** Ruff for lint and format (`make lint`)
- **Line length:** 100
- Match existing patterns in `packages/` and `apps/`
- Minimize scope — focused diffs preferred

## AI behavior changes

If you modify classification prompts, rule classifier, or pipeline:

1. Add or update cases in `tests/evals/data/v1/cases.json`
2. Run `python tests/evals/runner.py` and ensure pass rate ≥ 70%
3. Note eval impact in PR description

## Migrations

```bash
make migrate-new msg="describe change"
make migrate
```

Never edit applied migration files on shared branches.

## Documentation

- Backlog definitions: `docs/delivery/03-backlog.md`
- Status checkboxes: `docs/delivery/05-milestone-status.md` only
- Update `docs/HANDOFF.md` current focus when changing milestone scope

## Pull requests

CI runs lint, unit/contract/integration/e2e tests, eval suite, and Next.js build. No live API keys in CI.

## Questions

Start with [docs/HANDOFF.md](docs/HANDOFF.md) for orientation.
