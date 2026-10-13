.PHONY: backend-dev frontend-dev test test-backend test-frontend lint lint-backend lint-frontend typecheck verify seed

BACKEND_DIR := backend
FRONTEND_DIR := frontend
PYTHON := $(BACKEND_DIR)/.venv/bin/python
PIP := $(BACKEND_DIR)/.venv/bin/pip

backend-dev:
	cd $(BACKEND_DIR) && .venv/bin/uvicorn app.main:app --reload --host 0.0.0.0 --port 8000

frontend-dev:
	cd $(FRONTEND_DIR) && npm run dev

test: test-backend test-frontend

test-backend:
	cd $(BACKEND_DIR) && .venv/bin/pytest -q

test-frontend:
	cd $(FRONTEND_DIR) && npm run test

lint: lint-backend lint-frontend

lint-backend:
	cd $(BACKEND_DIR) && .venv/bin/ruff check app tests

lint-frontend:
	cd $(FRONTEND_DIR) && npm run lint

typecheck:
	cd $(FRONTEND_DIR) && npm run typecheck

verify: lint-backend test-backend lint-frontend typecheck test-frontend

seed:
	cd $(BACKEND_DIR) && .venv/bin/python scripts/seed.py
