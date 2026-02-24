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
backend/app/
├── api/                      # API Layer
│   ├── dependencies/         # FastAPI dependency injection
│   │   ├── auth.py          # get_current_user dependency
│   │   └── repositories.py  # Repository DI functions
│   ├── routers/              # API route handlers
│   │   ├── auth.py          # Auth endpoints
│   │   ├── blobs.py         # Blob storage endpoints
│   │   ├── health.py        # Health check
│   │   ├── projects.py      # Project endpoints
│   │   ├── skills.py        # Skill endpoints
│   │   └── trees.py         # Tree structure endpoints
│   └── schemas/              # Pydantic DTOs
│       ├── blob.py
│       ├── project.py
│       ├── skill.py
│       ├── tree.py
│       └── user.py
│
├── application/              # Application Layer
│   └── handlers/             # Use case handlers
│       ├── add_tree_file_handler.py
│       ├── create_blob_handler.py
│       ├── create_project_handler.py
│       ├── create_skill_handler.py
│       ├── create_tree_handler.py
│       ├── delete_skill_handler.py
│       ├── delete_tree_file_handler.py
│       ├── get_blob_handler.py
│       ├── get_current_user_handler.py
│       ├── get_project_handler.py
│       ├── get_skill_handler.py
│       ├── get_tree_handler.py
│       ├── handle_create_tree_file.py
│       ├── import_skill_handler.py
│       ├── list_skills_handler.py
│       ├── login_handler.py
│       ├── move_tree_file_handler.py
│       ├── refresh_token_handler.py
│       ├── register_user_handler.py
│       ├── rename_tree_file_handler.py
│       └── update_skill_handler.py
│
├── domain/                   # Domain Layer (Core)
│   ├── aggregates/           # Aggregate roots
│   │   ├── project.py
│   │   ├── skill.py
│   │   ├── tree.py
│   │   └── user.py
│   ├── entities/             # Domain entities
│   │   └── blob.py
│   ├── value_objects/        # Value objects
│   │   ├── email.py
│   │   ├── path.py
│   │   └── slug.py
│   ├── repositories/         # Repository interfaces (abstract)
│   │   ├── blob_repository.py
│   │   ├── project_repository.py
│   │   ├── skill_repository.py
│   │   ├── tree_repository.py
│   │   └── user_repository.py
│   └── exceptions.py         # Domain exceptions
│
├── infra/                    # Infrastructure Layer
│   └── persistence/          # Data persistence
│       ├── models/           # SQLAlchemy ORM models
│       │   ├── base.py
│       │   ├── blob_model.py
│       │   ├── project_model.py
│       │   ├── skill_model.py
│       │   ├── tree_model.py
│       │   └── user_model.py
│       └── repositories/     # Repository implementations
│           ├── sql_blob_repository.py
│           ├── sql_project_repository.py
│           ├── sql_skill_repository.py
│           ├── sql_tree_repository.py
│           └── sql_user_repository.py
│
├── core/                     # Configuration
│   └── config.py
│
└── main.py                   # Application entry point
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
- PostgreSQL 16+

### 1. Setup Environment

```bash
# Create virtual environment
python -m venv .venv
source .venv/bin/activate  # Linux/Mac
# .venv\Scripts\activate  # Windows

# Install dependencies
pip install -r requirements.txt

# Configure environment
cp .env.example .env
# Edit .env with your database credentials
```

### 2. Database Setup

```bash
# Run migrations
alembic downgrade base
alembic upgrade head
```

### 3. Start Server

```bash
# Development (auto-reload)
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000

# Production
uvicorn app.main:app --host 0.0.0.0 --port 8000
```

Access:
- API: http://localhost:8000
- API Docs: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc

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
SECRET_KEY=your-secret-key
ACCESS_TOKEN_EXPIRE_MINUTES=30
REFRESH_TOKEN_EXPIRE_DAYS=7
```
