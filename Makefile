.PHONY: help install-backend install-ml install-frontend data train eval export test test-backend test-ml test-frontend run-backend run-frontend smoke-test lint format up down clean

VENV = .venv
PYTHON = $(VENV)/bin/python
PIP = $(VENV)/bin/pip

help:
	@echo "Available commands:"
	@echo "  make run-backend       - Start the FastAPI backend server (http://localhost:8000)"
	@echo "  make run-frontend      - Start the Vite React development frontend (http://localhost:5173)"
	@echo "  make smoke-test        - Run the End-to-End in-process smoke test (8 stages)"
	@echo "  make test              - Run all test suites (backend, ml, frontend)"
	@echo "  make test-backend      - Run backend pytest with coverage"
	@echo "  make test-frontend     - Run frontend vitest suite"
	@echo "  make up                - Start full stack via Docker Compose"
	@echo "  make down              - Stop Docker Compose services"

install-backend:
	$(PIP) install -r backend/requirements.txt

install-ml:
	$(PIP) install -r ml/requirements.txt

install-frontend:
	cd frontend && npm install

data:
	$(PYTHON) ml/src/download_data.py
	$(PYTHON) ml/src/prepare_splits.py

train:
	$(PYTHON) ml/src/train.py --config ml/configs/train_config.yaml

eval:
	$(PYTHON) ml/src/evaluate.py --config ml/configs/train_config.yaml

export:
	$(PYTHON) ml/src/export_onnx.py
	$(PYTHON) ml/src/quantize.py
	$(PYTHON) ml/src/benchmark.py

test: test-backend test-ml test-frontend

run-backend:
	PYTHONPATH=. $(PYTHON) -m uvicorn backend.app.main:app --host 0.0.0.0 --port 8000 --reload

run-frontend:
	cd frontend && npm run dev

smoke-test:
	PYTHONPATH=. $(PYTHON) scripts/e2e_smoke_test.py

test-backend:
	PYTHONPATH=. $(PYTHON) -m pytest backend/tests --cov=backend/app --cov-report=term-missing

test-ml:
	$(PYTHON) -m pytest ml/tests

test-frontend:
	cd frontend && npm run test

lint:
	$(PYTHON) -m ruff check backend ml
	cd frontend && npm run lint

format:
	$(PYTHON) -m ruff format backend ml
	cd frontend && npm run format

up:
	docker compose up --build -d

down:
	docker compose down

clean:
	find . -type d -name "__pycache__" -exec rm -rf {} +
	find . -type d -name ".pytest_cache" -exec rm -rf {} +
	find . -type f -name "*.pyc" -delete
	rm -rf .coverage htmlcov/ frontend/dist/
