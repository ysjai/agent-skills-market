# Agent Skills Manager - Backend

FastAPI-based backend service implementing Domain-Driven Design (DDD) architecture.

## Overview

This backend service provides RESTful APIs for the Agent Skills Manager platform, handling:

- User authentication and authorization (JWT-based)
- Skill management (create, update, delete, import)
- Project management
- Tree and blob storage for file versioning
- Health monitoring

## Architecture

### Four-Layer DDD Architecture

```
┌─────────────────────────────────────────────┐
│                  API Layer                    │
│         (routers, dependencies)             │
│              ↓ Depends on                     │
├─────────────────────────────────────────────┤
│              Application Layer                │
│           (handlers, commands)               │
│              ↓ Depends on                     │
├─────────────────────────────────────────────┤
│               Domain Layer                    │
│      (entities, value_objects, repositories) │
│              ↑ Implemented by                 │
├─────────────────────────────────────────────┤
│             Infrastructure Layer              │
│        (persistence, external_services)     │
└─────────────────────────────────────────────┘
```

### Project Structure

```
backend/
├── src/                      # Source code
│   ├── api/                  # API Layer
│   │   ├── dependencies/     # FastAPI dependency injection
│   │   │   ├── auth.py      # get_current_user dependency
│   │   │   └── repositories.py # Repository DI functions
│   │   ├── routers/          # API route handlers
│   │   │   ├── auth.py      # Auth endpoints
│   │   │   ├── blobs.py     # Blob storage endpoints
│   │   │   ├── health.py    # Health check
│   │   │   ├── skills.py    # Skill endpoints
│   │   │   ├── trees.py     # Tree structure endpoints
│   │   │   ├── categories.py
│   │   │   ├── prompts.py
│   │   │   ├── sharing.py
│   │   │   └── market.py
│   │   ├── schemas/          # Pydantic DTOs
│   │   │   ├── blob.py
│   │   │   ├── skill.py
│   │   │   ├── tree.py
│   │   │   └── user.py
│   │   ├── exception_handlers.py
│   │   └── __init__.py
│   │
│   ├── application/          # Application Layer
│   │   └── handlers/         # Use case handlers
│   │       ├── skill_handlers/
│   │       ├── tree_handlers/
│   │       ├── auth_handlers/
│   │       └── ...
│   │
│   ├── domain/               # Domain Layer (Core)
│   │   ├── aggregates/      # Aggregate roots
│   │   │   ├── skill.py
│   │   │   ├── tree.py
│   │   │   ├── user.py
│   │   │   └── ...
│   │   ├── entities/        # Domain entities
│   │   ├── value_objects/   # Value objects
│   │   │   ├── email.py
│   │   │   ├── path.py
│   │   │   └── slug.py
│   │   ├── repositories/    # Repository interfaces (abstract)
│   │   └── exceptions.py    # Domain exceptions
│   │
│   ├── infra/               # Infrastructure Layer
│   │   └── persistence/     # Data persistence
│   │       ├── models/      # SQLAlchemy ORM models
│   │       └── repositories/ # Repository implementations
│   │
│   ├── core/                # Configuration
│   │   ├── config.py
│   │   ├── auth.py
│   │   └── logging.py
│   │
│   ├── crud/                # CRUD operations
│   ├── models/              # Database models
│   ├── main.py              # Application entry point
│   └── auth.py              # Authentication utilities
│
├── alembic/                  # Database migrations
├── tests/                    # Test files
├── pyproject.toml            # Project configuration
├── uv.lock                   # uv lock file
└── README.md                  # This file
```

### Key Patterns

**Value Objects**: Immutable, validated at construction
- `Slug` - URL-friendly identifiers
- `Email` - Validated email addresses
- `Path` - File system paths

**Aggregate Roots**: Business logic encapsulation
- `Skill` - Skill management with versioning
- `User` - User account management
- `Tree` - File tree structures
- `Project` - Project associations

**Repositories**: Data access abstraction
- Interfaces in `domain/repositories/`
- SQLAlchemy implementations in `infra/persistence/repositories/`
- Injected via FastAPI Depends

**Handlers**: Stateless use case functions
- One handler per use case
- Receive repositories as parameters
- Return domain objects (not DTOs)

## Quick Start

### Prerequisites

- Python 3.10+
- PostgreSQL 16+ (or use Docker)

### 1. Setup Environment

```bash
cd backend

# Install dependencies using uv (推荐)
uv sync

# Or create venv manually and install
python -m venv .venv
source .venv/bin/activate  # Linux/Mac
# .venv\Scripts\activate  # Windows
uv sync

# Configure environment
cp .env.example .env
# Edit .env with your database credentials
```

### 2. Database Setup

```bash
# Create database (if PostgreSQL is running)
# Option A: Using Docker
docker exec -it agent_skills_db psql -U postgres -c "CREATE DATABASE agent_skills"

# Option B: Using psql directly
# psql -U postgres -c "CREATE DATABASE agent_skills"

# Run migrations
alembic downgrade base
alembic upgrade head
```

### 3. Start Server

```bash
# Development (auto-reload)
uvicorn src.main:app --reload --host 0.0.0.0 --port 8000

# Production
uvicorn src.main:app --host 0.0.0.0 --port 8000
```

Access:
- API: http://localhost:8000
- API Docs: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc

### Alternative: Using Docker Compose

```bash
# From project root
docker compose up -d postgres backend
```

## API Endpoints

### Authentication (/api/auth)

| Method | Path | Description | Auth Required |
|--------|------|-------------|---------------|
| POST | /register | User registration | No |
| POST | /login | User login | No |
| POST | /refresh | Refresh access token | Yes (Bearer) |
| GET | /me | Get current user | Yes |
| POST | /logout | User logout | Yes |

**DTOs**:
- `RegisterUserReq` / `RegisterUserResp`
- `LoginReq` / `LoginResp`
- `GetUserResp`

### Skills (/api/skills)

| Method | Path | Description | Auth Required |
|--------|------|-------------|---------------|
| GET | / | List user skills | Yes |
| POST | / | Create skill | Yes |
| POST | /import | Import skill | Yes |
| GET | /{id} | Get skill details | Yes |
| PUT | /{id} | Update skill | Yes |
| DELETE | /{id} | Delete skill | Yes |

**DTOs**:
- `CreateSkillReq` / `CreateSkillResp`
- `UpdateSkillReq` / `UpdateSkillResp`
- `GetSkillResp`
- `ListSkillsItemResp`

### Trees (/api/trees)

| Method | Path | Description | Auth Required |
|--------|------|-------------|---------------|
| POST | / | Create tree | Yes |
| GET | /{id} | Get tree | Yes |
| POST | /{id}/files | Add file to tree | Yes |
| DELETE | /{id}/files | Delete file from tree | Yes |
| PUT | /{id}/files/rename | Rename file | Yes |
| PUT | /{id}/files/move | Move file | Yes |

**DTOs**:
- `CreateTreeReq` / `CreateTreeResp`
- `AddTreeFileReq` / `AddTreeFileResp`
- `GetTreeResp`
- `DeleteTreeFileReq`
- `RenameTreeFileReq`
- `MoveTreeFileReq`

### Blobs (/api/blobs)

| Method | Path | Description | Auth Required |
|--------|------|-------------|---------------|
| POST | / | Upload blob | Yes |
| GET | /{id} | Download blob | Yes |

**DTOs**:
- `UploadBlobResp`

### Projects (/api/projects)

| Method | Path | Description | Auth Required |
|--------|------|-------------|---------------|
| GET | / | List user projects | Yes |
| POST | / | Create project | Yes |
| GET | /{id} | Get project details | Yes |
| PUT | /{id} | Update project | Yes |
| DELETE | /{id} | Delete project | Yes |

**DTOs**:
- `CreateProjectReq` / `CreateProjectResp`
- `UpdateProjectReq` / `UpdateProjectResp`
- `GetProjectResp`
- `ListProjectsItemResp`

### Health

| Method | Path | Description |
|--------|------|-------------|
| GET | /health | Health check |

**Response**: `{"status": "ok", "version": "1.0.0"}`

## Development

### Code Style

```bash
# Check code
ruff check .

# Format code
ruff format .
```

### Testing

```bash
# Run all tests
pytest

# Run with coverage
pytest --cov=app
```

### Database Migrations

```bash
# Create new migration
alembic revision --autogenerate -m "description"

# Upgrade to latest
alembic upgrade head

# Downgrade
alembic downgrade -1
```

## Architecture Documentation

For detailed DDD architecture guidelines, coding conventions, and patterns, see:

- [project_conventions.md](./project_conventions.md) - Architecture overview and conventions
- [docs/architecture/ddd-guide.md](./docs/architecture/ddd-guide.md) - Comprehensive DDD tutorial

## Environment Variables

```bash
# Database
DATABASE_URL=postgresql+asyncpg://user:password@localhost:5432/dbname
POSTGRES_HOST=localhost
POSTGRES_PORT=5432
POSTGRES_USER=user
POSTGRES_PASSWORD=password
POSTGRES_DB=dbname

# JWT (auto-generated in development, required in production)
SECRET_KEY=your-secret-key (min 32 characters)

# Environment
ENVIRONMENT=development  # or production
```
