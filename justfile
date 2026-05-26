# justfile for agent-skills-market

set shell := ["bash", "-uc"]
set dotenv-load := true

BACKEND_DIR := "backend"
FRONTEND_DIR := "frontend"
BACKEND_APP := "src.main:app"
BACKEND_HOST := env_var_or_default("BACKEND_HOST", "127.0.0.1")
BACKEND_PORT := env_var_or_default("BACKEND_PORT", "8000")
FRONTEND_HOST := env_var_or_default("FRONTEND_HOST", "127.0.0.1")
FRONTEND_PORT := env_var_or_default("FRONTEND_PORT", "3000")
API_URL := env_var_or_default("NEXT_PUBLIC_API_URL", "http://127.0.0.1:8000/api")

# List all available commands.
default:
    @just --list

# ----------------- Guards -----------------

_check_uv:
    @if ! command -v uv >/dev/null; then \
        printf "Command 'uv' not found. Install it from https://docs.astral.sh/uv/\n"; \
        exit 1; \
    fi

_check_node:
    @if ! command -v npm >/dev/null; then \
        printf "Command 'npm' not found. Install Node.js >= 18 and npm.\n"; \
        exit 1; \
    fi

_check_bun:
    @if ! command -v bun >/dev/null; then \
        printf "Command 'bun' not found. Install Bun to run frontend tests.\n"; \
        exit 1; \
    fi

_check_docker:
    @if ! command -v docker >/dev/null; then \
        printf "Command 'docker' not found. Install Docker Desktop or Docker Engine.\n"; \
        exit 1; \
    fi

# ----------------- Setup -----------------

# setup: Bootstrap env file and install backend/frontend dependencies.
setup: setup-env setup-backend setup-frontend

# setup-env: Create root .env from .env.example when missing.
setup-env:
    @if [ ! -f .env ]; then \
        cp .env.example .env; \
        printf "Created .env from .env.example\n"; \
    else \
        printf ".env already exists; leaving it unchanged\n"; \
    fi

# setup-backend: Install backend dependencies with uv.
setup-backend: _check_uv
    @cd {{BACKEND_DIR}} && uv sync --extra dev

# setup-frontend: Install frontend dependencies.
setup-frontend: _check_node
    @cd {{FRONTEND_DIR}} && npm install

# ----------------- Run -----------------

# run-backend: Start FastAPI backend with hot reload.
run-backend: _check_uv
    @cd {{BACKEND_DIR}} && uv run --extra dev uvicorn {{BACKEND_APP}} --reload --host {{BACKEND_HOST}} --port {{BACKEND_PORT}}

# run-frontend: Start Next.js frontend.
run-frontend: _check_node
    @cd {{FRONTEND_DIR}} && NEXT_PUBLIC_API_URL={{API_URL}} npm run dev -- --hostname {{FRONTEND_HOST}} --port {{FRONTEND_PORT}}

# dev: Start backend and frontend together. Ctrl-C stops both.
dev: _check_uv _check_node
    @trap 'kill 0' INT TERM EXIT; \
        (cd {{BACKEND_DIR}} && uv run --extra dev uvicorn {{BACKEND_APP}} --reload --host {{BACKEND_HOST}} --port {{BACKEND_PORT}}) & \
        (cd {{FRONTEND_DIR}} && NEXT_PUBLIC_API_URL={{API_URL}} npm run dev -- --hostname {{FRONTEND_HOST}} --port {{FRONTEND_PORT}}) & \
        wait

# ----------------- Database -----------------

# postgres-up: Start the local PostgreSQL container.
postgres-up: _check_docker
    @docker compose up -d postgres

# postgres-down: Stop the local PostgreSQL container.
postgres-down: _check_docker
    @docker compose stop postgres

# postgres-logs: Follow PostgreSQL container logs.
postgres-logs: _check_docker
    @docker compose logs -f postgres

# db-migrate: Generate an Alembic migration from model changes.
db-migrate message: _check_uv
    @cd {{BACKEND_DIR}} && uv run alembic revision --autogenerate -m "{{message}}"

# db-upgrade: Apply all pending Alembic migrations.
db-upgrade: _check_uv
    @cd {{BACKEND_DIR}} && uv run alembic upgrade head

# db-downgrade: Roll back the last Alembic migration.
db-downgrade: _check_uv
    @cd {{BACKEND_DIR}} && uv run alembic downgrade -1

# db-reset: Reset the database schema to base revision.
db-reset: _check_uv
    @cd {{BACKEND_DIR}} && uv run alembic downgrade base

# db-history: Show Alembic migration history.
db-history: _check_uv
    @cd {{BACKEND_DIR}} && uv run alembic history --verbose

# db-current: Show current Alembic revision.
db-current: _check_uv
    @cd {{BACKEND_DIR}} && uv run alembic current

# ----------------- Quality -----------------

# lint-backend: Run backend Ruff checks.
lint-backend: _check_uv
    @cd {{BACKEND_DIR}} && uv run --extra dev ruff check .

# format-backend: Format backend code with Ruff.
format-backend: _check_uv
    @cd {{BACKEND_DIR}} && uv run --extra dev ruff format .

# typecheck-backend: Run backend mypy checks.
typecheck-backend: _check_uv
    @cd {{BACKEND_DIR}} && uv run --extra dev mypy src --ignore-missing-imports

# test-backend: Run backend pytest suite.
test-backend *ARGS: _check_uv
    @cd {{BACKEND_DIR}} && uv run --extra dev pytest -q {{ARGS}}

# test-backend-cov: Run backend pytest with coverage.
test-backend-cov *ARGS: _check_uv
    @cd {{BACKEND_DIR}} && uv run --extra dev pytest --cov=src {{ARGS}}

# lint-frontend: Run frontend ESLint checks.
lint-frontend: _check_node
    @cd {{FRONTEND_DIR}} && npm run lint

# typecheck-frontend: Run frontend TypeScript check.
typecheck-frontend: _check_node
    @cd {{FRONTEND_DIR}} && npm exec tsc -- --noEmit

# build-frontend: Build the frontend for production.
build-frontend: _check_node
    @cd {{FRONTEND_DIR}} && npm run build

# test-frontend: Run frontend Bun tests.
test-frontend *ARGS: _check_bun
    @cd {{FRONTEND_DIR}} && bun test {{ARGS}}

# lint: Run backend and frontend lint checks.
lint: lint-backend lint-frontend

# typecheck: Run backend and frontend type checks.
typecheck: typecheck-backend typecheck-frontend

# test: Run backend and frontend test suites.
test: test-backend test-frontend

# check: Run lint, typecheck, and tests.
check: lint typecheck test

# clean: Remove generated caches and build artifacts.
clean:
    @find {{BACKEND_DIR}} -type d -name "__pycache__" -prune -exec rm -rf {} +
    @find {{BACKEND_DIR}} -type f \( -name "*.pyc" -o -name "*.pyo" \) -delete
    @rm -rf {{BACKEND_DIR}}/.pytest_cache {{BACKEND_DIR}}/.ruff_cache {{BACKEND_DIR}}/.mypy_cache {{BACKEND_DIR}}/.coverage {{BACKEND_DIR}}/htmlcov {{BACKEND_DIR}}/coverage.xml {{FRONTEND_DIR}}/.next {{FRONTEND_DIR}}/coverage
