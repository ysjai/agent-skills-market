# Agent Skills Manager

<p align="center">
  <img src="https://img.shields.io/badge/Version-0.1.0-blue.svg" alt="Version">
  <img src="https://img.shields.io/badge/Python-3.10+-green.svg" alt="Python">
  <img src="https://img.shields.io/badge/Next.js-15+-blue.svg" alt="Next.js">
  <img src="https://img.shields.io/badge/License-MIT-yellow.svg" alt="License">
</p>

> Agent Skills Management Platform - Manage, Sync, and Share Custom Agent Skills

## Overview

Agent Skills Manager is a B/S architecture system that helps users manage, sync, and share custom Agent Skills. Supports both Claude Code and OpenCode platforms.

## Features

- **Web Interface** - Create, edit, and version-manage Skills
- **Bidirectional Sync** - Web and local automatic synchronization
- **Multi-file Skills** - Supports SKILL.md + templates/ + examples/ directory structure
- **Version History** - Git-like version control with rollback capability
- **User System** - Email registration/login with JWT authentication
- **Local Daemon** - Auto-discovery of projects and file watching
- **Symbolic Links** - Automatic linking to project directories
- **Open Source & Self-hosted** - Fully open source with private deployment support

## Tech Stack

### Backend

- **Python**: 3.10+
- **FastAPI**: 0.129.0+ (Web framework)
- **SQLAlchemy**: 2.0+ (ORM)
- **PostgreSQL**: 16+ (Database)
- **Alembic**: (Database migrations)
- **JWT**: (Authentication)

### Frontend

- **Next.js**: 15+ (App Router)
- **React**: 19+
- **TypeScript**: 5.7+
- **Tailwind CSS**: 4.0+

### Local Daemon

- **Python**: 3.10+
- **WebSocket**: (Real-time sync)
- **watchdog**: (File monitoring)

## Quick Start

### Prerequisites

- Python 3.10+
- Node.js 18+
- PostgreSQL 16+ (or Docker)
- Docker (optional)

### 1. Clone the Project

```bash
git clone https://github.com/your-repo/agent-skills-manager.git
cd agent-skills-manager
```

### 2. Start PostgreSQL

```bash
# Using Docker
docker compose up -d postgres

# Or configure PostgreSQL manually
```

### 3. Backend Setup

```bash
cd backend

# Install dependencies using uv (推荐)
uv sync

# Or create venv manually
python -m venv .venv
source .venv/bin/activate  # Linux/Mac
# .venv\Scripts\activate  # Windows
uv sync

# Configure environment variables
cp .env.example .env
# Edit .env to set database credentials

# Create database (if not exists)
docker exec -it agent_skills_db psql -U postgres -c "CREATE DATABASE agent_skills"
# Or: psql -U postgres -c "CREATE DATABASE agent_skills"

# Run migrations
alembic downgrade base
alembic upgrade head

# Start the server (SECRET_KEY auto-generated in dev)
uvicorn src.main:app --reload --host 0.0.0.0 --port 8000
```

Once the backend starts, access:

- API: http://localhost:8000
- API Docs: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc

### 4. Frontend Setup

```bash
cd frontend

# Install dependencies
npm install

# Start development server
npm run dev
```

Once the frontend starts, access: http://localhost:3000

### 5. Verification

```bash
# Test health check
curl http://localhost:8000/health

# Test registration
curl -X POST http://localhost:8000/api/auth/register \
  -H "Content-Type: application/json" \
  -d '{"email": "test@example.com", "username": "testuser", "password": "password123"}'

# Test login
curl -X POST http://localhost:8000/api/auth/login \
  -H "Content-Type: application/json" \
  -d '{"email": "test@example.com", "password": "password123"}'
```

## Project Structure

```
agent-skills-manager/
├── backend/                     # FastAPI Backend (DDD Architecture)
│   ├── src/
│   │   ├── api/                # API Layer (routers, dependencies, schemas)
│   │   │   ├── dependencies/   # FastAPI dependency injection
│   │   │   ├── routers/        # API route handlers
│   │   │   ├── schemas/        # Pydantic DTOs (Request/Response)
│   │   │   └── exception_handlers.py
│   │   ├── application/        # Application Layer (handlers)
│   │   │   └── handlers/       # Use case handlers
│   │   ├── domain/             # Domain Layer (core business logic)
│   │   │   ├── aggregates/     # Aggregate roots (Skill, User, Tree, etc.)
│   │   │   ├── entities/       # Domain entities
│   │   │   ├── value_objects/  # Value objects (Slug, Email, etc.)
│   │   │   ├── repositories/   # Repository interfaces (abstract)
│   │   │   └── exceptions.py   # Domain exceptions
│   │   ├── infra/              # Infrastructure Layer
│   │   │   └── persistence/    # ORM models and repository implementations
│   │   ├── core/               # Configuration
│   │   └── main.py            # Application entry point
│   ├── alembic/                # Database migrations
│   ├── tests/                  # Test files
│   ├── pyproject.toml          # Project configuration
│   ├── uv.lock                 # uv lock file
│   └── project_conventions.md  # DDD Architecture guide
│
├── frontend/                   # Next.js Frontend
│   ├── app/                   # App Router pages
│   ├── components/            # React components
│   ├── lib/                   # Utility functions
│   └── types/                 # TypeScript types
│
├── daemon/                     # Local daemon (TODO)
│
├── docker-compose.yml          # Docker configuration
├── AGENT.md                    # Agent operations guide
└── README.md                   # This file
```

## Architecture Overview

This project follows **Domain-Driven Design (DDD) Four-Layer Architecture**:

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

### Key Patterns

- **Value Objects**: Immutable objects validated at construction (e.g., Slug, Email)
- **Aggregate Roots**: Domain entities that encapsulate business logic (e.g., Skill, User)
- **Repositories**: Abstract data access interfaces with SQLAlchemy implementations
- **Handlers**: Stateless use case functions in the Application layer
- **Dependency Injection**: Repositories injected via FastAPI Depends

For detailed architecture documentation, see [backend/project_conventions.md](backend/project_conventions.md).

## API Documentation

### Authentication

| Method | Path | Description | Request DTO | Response DTO |
|--------|------|-------------|-------------|--------------|
| POST | /api/auth/register | User registration | RegisterUserReq | RegisterUserResp |
| POST | /api/auth/login | User login | LoginReq | LoginResp |
| POST | /api/auth/refresh | Refresh access token | - (Header: Bearer) | LoginResp |
| GET | /api/auth/me | Get current user | - | GetUserResp |
| POST | /api/auth/logout | User logout | - | Message |

### Skills

| Method | Path | Description | Request DTO | Response DTO |
|--------|------|-------------|-------------|--------------|
| GET | /api/skills | List user skills | Query: skip, limit | ListSkillsResp |
| POST | /api/skills | Create skill | CreateSkillReq | CreateSkillResp |
| POST | /api/skills/import | Import skill | ImportSkillReq | CreateSkillResp |
| GET | /api/skills/{id} | Get skill details | - | GetSkillResp |
| PUT | /api/skills/{id} | Update skill | UpdateSkillReq | UpdateSkillResp |
| DELETE | /api/skills/{id} | Delete skill | - | - |

### Trees

| Method | Path | Description | Request DTO | Response DTO |
|--------|------|-------------|-------------|--------------|
| POST | /api/trees | Create tree | CreateTreeReq | CreateTreeResp |
| GET | /api/trees/{id} | Get tree | - | GetTreeResp |
| POST | /api/trees/{id}/files | Add file to tree | AddTreeFileReq | AddTreeFileResp |
| DELETE | /api/trees/{id}/files | Delete file from tree | DeleteTreeFileReq | CreateTreeResp |
| PUT | /api/trees/{id}/files/rename | Rename file | RenameTreeFileReq | CreateTreeResp |
| PUT | /api/trees/{id}/files/move | Move file | MoveTreeFileReq | CreateTreeResp |

### Blobs

| Method | Path | Description | Request DTO | Response DTO |
|--------|------|-------------|-------------|--------------|
| POST | /api/blobs | Upload blob | Multipart file | UploadBlobResp |
| GET | /api/blobs/{id} | Download blob | - | Binary content |

### Projects

| Method | Path | Description | Request DTO | Response DTO |
|--------|------|-------------|-------------|--------------|
| GET | /api/projects | List user projects | Query: skip, limit | ListProjectsResp |
| POST | /api/projects | Create project | CreateProjectReq | CreateProjectResp |
| GET | /api/projects/{id} | Get project details | - | GetProjectResp |
| PUT | /api/projects/{id} | Update project | UpdateProjectReq | UpdateProjectResp |
| DELETE | /api/projects/{id} | Delete project | - | - |

### Health

| Method | Path | Description | Response |
|--------|------|-------------|----------|
| GET | /health | Health check | {"status": "ok", "version": "1.0.0"} |

Full API documentation available at: http://localhost:8000/docs

## Environment Variables

### Backend (.env)

```bash
# Database
DATABASE_URL=postgresql+asyncpg://user:password@localhost:5432/dbname
POSTGRES_HOST=localhost
POSTGRES_PORT=5432
POSTGRES_USER=user
POSTGRES_PASSWORD=password
POSTGRES_DB=dbname

# JWT (auto-generated in dev, required in production)
# SECRET_KEY=your-generated-secret-key-here
```

## Development

### Code Formatting

```bash
# Backend - using ruff
cd backend
ruff check .
ruff format .

# Frontend - using ESLint
cd frontend
npm run lint
```

### Security Scanning

```bash
# Run full security scan
./scripts/security-check.sh

# Scan Python dependencies
cd backend
safety check

# Scan Node.js dependencies
cd frontend
npm audit --audit-level=high
```

### Testing

```bash
# Backend
cd backend
pytest

# Frontend
cd frontend
npm run test
```

## License

MIT License - See LICENSE file for details

## Contributing

Issues and Pull Requests are welcome!

---

<p align="center">Made with by Agent Skills Team</p>
