.PHONY: install dev-up dev-down migrate seed test lint eval eval-report

install:
	pip install -e ".[dev]"

dev-up:
	docker compose up -d postgres redis

dev-down:
	docker compose down

migrate:
	alembic -c migrations/alembic.ini upgrade head

migrate-new:
	alembic -c migrations/alembic.ini revision --autogenerate -m "$(msg)"

seed:
	python -m api.seed

test:
	pytest tests/ -v

eval:
	pytest tests/evals -v -m eval

eval-report:
	python tests/evals/runner.py

lint:
	ruff check packages apps tests
	ruff format --check packages apps tests

run-api:
	uvicorn api.main:app --reload --host 0.0.0.0 --port 8000

run-worker:
	celery -A worker.celery_app worker --loglevel=info

run-web:
	cd apps/web && npm run dev
