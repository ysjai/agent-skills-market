.PHONY: help install lint format test test-cov clean migrate migrate-down migrate-reset run run-dev docker-up docker-down

help:
	@echo "Available commands:"
	@echo "  install       - Install Python dependencies"
	@echo "  lint          - Run ruff linter"
	@echo "  lint-fix      - Run ruff linter with auto-fix"
	@echo "  format        - Run ruff formatter"
	@echo "  format-check  - Check formatting without modifying files"
	@echo "  type-check    - Run mypy type checker"
	@echo "  test          - Run all tests"
	@echo "  test-cov      - Run tests with coverage report"
	@echo "  test-unit     - Run unit tests only"
	@echo "  test-integration - Run integration tests only"
	@echo "  test-journey  - Run journey tests only"
	@echo "  clean         - Remove Python cache files"
	@echo "  migrate       - Run database migrations (upgrade)"
	@echo "  migrate-down  - Downgrade database one revision"
	@echo "  migrate-reset - Reset database to base"
	@echo "  run           - Run production server"
	@echo "  run-dev       - Run development server with auto-reload"
	@echo "  docker-up     - Start Docker services"
	@echo "  docker-down   - Stop Docker services"

install:
	pip install -r requirements.txt
	pip install -e .

lint:
	ruff check .

lint-fix:
	ruff check --fix .

format:
	ruff format .

format-check:
	ruff format --check .

type-check:
	mypy src --ignore-missing-imports

test:
	pytest -v

test-cov:
	pytest --cov=src --cov-report=term --cov-report=html --cov-report=xml -v

test-unit:
	pytest tests/unit -v

test-integration:
	pytest tests/integration -v

test-journey:
	pytest tests/integration/journey -v

clean:
	find . -type d -name "__pycache__" -exec rm -rf {} +
	find . -type f -name "*.pyc" -delete
	find . -type f -name "*.pyo" -delete
	find . -type f -name ".coverage" -delete
	rm -rf .pytest_cache .mypy_cache .ruff_cache htmlcov

migrate:
	alembic upgrade head

migrate-down:
	alembic downgrade -1

migrate-reset:
	alembic downgrade base

migrate-create:
	@read -p "Migration message: " msg; \
	alembic revision --autogenerate -m "$$msg"

run:
	uvicorn src.main:app --host 0.0.0.0 --port 8000

run-dev:
	uvicorn src.main:app --reload --host 0.0.0.0 --port 8000

docker-up:
	docker-compose up -d

docker-down:
	docker-compose down

docker-logs:
	docker-compose logs -f
