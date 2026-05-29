# Agent Skills Manager - 后端

基于 FastAPI 的后端服务，采用领域驱动设计 (DDD) 架构。

## 简介

本后端服务为 Agent Skills Manager 平台提供 RESTful API，包括：

- 用户认证和授权 (JWT)
- Skill 管理（创建、更新、删除、导入）
- 项目管理
- Tree 和 Blob 存储（文件版本控制）
- 健康监控

## 架构

### DDD 四层架构

```
┌─────────────────────────────────────────────┐
│                  API 层                       │
│            (routers, dependencies)           │
│                ↓ 依赖方向                      │
├─────────────────────────────────────────────┤
│                  应用层                        │
│               (handlers, commands)           │
│                ↓ 依赖方向                      │
├─────────────────────────────────────────────┤
│                  领域层                         │
│        (entities, value_objects, repositories)│
│                ↑ 实现方向                      │
├─────────────────────────────────────────────┤
│                 基础设施层                       │
│           (persistence, external_services)   │
└─────────────────────────────────────────────┘
```

### 项目结构

```
backend/
├── src/                      # 源代码
│   ├── api/                  # API 层
│   │   ├── dependencies/     # FastAPI 依赖注入
│   │   │   ├── auth.py      # get_current_user 依赖
│   │   │   └── repositories.py # 仓库 DI 函数
│   │   ├── routers/          # API 路由
│   │   │   ├── auth.py      # 认证端点
│   │   │   ├── blobs.py     # Blob 存储端点
│   │   │   ├── health.py    # 健康检查
│   │   │   ├── skills.py    # Skill 端点
│   │   │   ├── trees.py     # 树结构端点
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
│   ├── application/          # 应用层
│   │   └── handlers/         # 用例处理器
│   │       ├── skill_handlers/
│   │       ├── tree_handlers/
│   │       ├── auth_handlers/
│   │       └── ...
│   │
│   ├── domain/               # 领域层（核心）
│   │   ├── aggregates/      # 聚合根
│   │   │   ├── skill.py
│   │   │   ├── tree.py
│   │   │   ├── user.py
│   │   │   └── ...
│   │   ├── entities/        # 领域实体
│   │   ├── value_objects/   # 值对象
│   │   │   ├── email.py
│   │   │   ├── path.py
│   │   │   └── slug.py
│   │   ├── repositories/    # 仓库接口（抽象）
│   │   └── exceptions.py    # 领域异常
│   │
│   ├── infra/               # 基础设施层
│   │   └── persistence/     # 数据持久化
│   │       ├── models/      # SQLAlchemy ORM 模型
│   │       └── repositories/ # 仓库实现
│   │
│   ├── core/                # 配置
│   │   ├── config.py
│   │   ├── auth.py
│   │   └── logging.py
│   │
│   ├── crud/                # CRUD 操作
│   ├── models/              # 数据库模型
│   ├── main.py              # 应用入口
│   └── auth.py              # 认证工具
│
├── alembic/                  # 数据库迁移
├── tests/                    # 测试文件
├── pyproject.toml            # 项目配置
├── uv.lock                   # uv 锁文件
└── README.md                # 本文件
```

### 核心模式

**值对象**: 构造时验证的不可变对象
- `Slug` - URL 友好标识符
- `Email` - 邮箱地址验证
- `Path` - 文件系统路径

**聚合根**: 业务逻辑封装
- `Skill` - 带版本管理的 Skill
- `User` - 用户账户管理
- `Tree` - 文件树结构
- `Project` - 项目关联

**仓库**: 数据访问抽象
- 接口在 `domain/repositories/`
- SQLAlchemy 实现在 `infra/persistence/repositories/`
- 通过 FastAPI Depends 注入

**处理器**: 无状态用例函数
- 一个用例一个处理器
- 接收仓库作为参数
- 返回领域对象（非 DTO）

## 快速开始

### 推荐：从项目根目录使用 just

根目录 `justfile` 已经收口了后端常用命令：

```bash
# 在仓库根目录执行
just setup-backend
just db-upgrade
just run-backend

# 质量检查
just lint-backend
just typecheck-backend
just test-backend
```

如果需要同时带前端一起启动，使用根目录的 `just dev`。

### 前置要求

- Python 3.12+
- PostgreSQL 16+ (或使用 Docker)

### 1. 环境设置

```bash
cd backend

# 使用 uv 安装依赖（推荐，包含开发依赖）
uv sync --extra dev

# 手动创建虚拟环境
python -m venv .venv
source .venv/bin/activate  # Linux/Mac
# .venv\Scripts\activate  # Windows
uv sync --extra dev

# 在项目根目录配置环境变量
cd ..
cp .env.example .env
# 编辑 .env 设置数据库连接后再回到 backend
cd backend
```

### 2. 数据库设置

```bash
# 创建数据库（PostgreSQL 运行中）
# 方式 A: 使用 Docker
docker exec -it agent_skills_db psql -U postgres -c "CREATE DATABASE agent_skills"

# 方式 B: 直接使用 psql
# psql -U postgres -c "CREATE DATABASE agent_skills"

# 运行迁移
uv run --extra dev alembic downgrade base
uv run --extra dev alembic upgrade head
```

### 3. 启动服务

```bash
# 开发模式（自动重载）
uv run --extra dev uvicorn src.main:app --reload --host 0.0.0.0 --port 8000

# 生产模式
uv run uvicorn src.main:app --host 0.0.0.0 --port 8000
```

访问：
- API: http://localhost:8000
- API 文档: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc

### 方式二: 使用 Docker Compose

```bash
# 从项目根目录启动完整开发栈（gateway + postgres + backend + frontend）
docker compose up

# 如果已配置 DOCKER_DATABASE_URL，希望跳过本地 postgres
docker compose up gateway backend frontend
```

说明：
- 后端容器会自动执行 `alembic upgrade head`
- Docker 模式下默认通过 Nginx 网关访问 API，默认地址为 `http://localhost:8080/api`
- 完整 Docker 栈默认不会把 PostgreSQL 暴露到宿主机；如果本机要直连数据库，请在仓库根目录执行 `just postgres-up`
- 如果要把 Docker 中的后端改连云数据库，请在根目录 `.env` 中设置 `DOCKER_DATABASE_URL`

## API 端点

### 认证 (/api/auth)

| 方法   | 路径         | 描述           | 需要认证 |
|--------|-------------|----------------|---------|
| POST   | /register   | 用户注册       | 否      |
| POST   | /login      | 用户登录       | 否      |
| POST   | /refresh    | 刷新访问令牌   | 是 (Bearer) |
| GET    | /me         | 获取当前用户   | 是      |
| POST   | /logout     | 用户登出       | 是      |

**DTOs**:
- `RegisterUserReq` / `RegisterUserResp`
- `LoginReq` / `LoginResp`
- `GetUserResp`

### Skills (/api/skills)

| 方法   | 路径         | 描述           | 需要认证 |
|--------|-------------|----------------|---------|
| GET    | /           | 列出用户 Skills | 是      |
| POST   | /           | 创建 Skill     | 是      |
| POST   | /import     | 导入 Skill     | 是      |
| GET    | /{id}       | 获取详情       | 是      |
| PUT    | /{id}       | 更新 Skill     | 是      |
| DELETE | /{id}       | 删除 Skill     | 是      |

**DTOs**:
- `CreateSkillReq` / `CreateSkillResp`
- `UpdateSkillReq` / `UpdateSkillResp`
- `GetSkillResp`
- `ListSkillsItemResp`

### Trees (/api/trees)

| 方法   | 路径                  | 描述           | 需要认证 |
|--------|---------------------|----------------|---------|
| POST   | /                   | 创建树         | 是      |
| GET    | /{id}               | 获取树         | 是      |
| POST   | /{id}/files         | 添加文件       | 是      |
| DELETE | /{id}/files         | 删除文件       | 是      |
| PUT    | /{id}/files/rename  | 重命名文件     | 是      |
| PUT    | /{id}/files/move    | 移动文件       | 是      |

**DTOs**:
- `CreateTreeReq` / `CreateTreeResp`
- `AddTreeFileReq` / `AddTreeFileResp`
- `GetTreeResp`
- `DeleteTreeFileReq`
- `RenameTreeFileReq`
- `MoveTreeFileReq`

### Blobs (/api/blobs)

| 方法   | 路径          | 描述           | 需要认证 |
|--------|--------------|----------------|---------|
| POST   | /            | 上传 blob      | 是      |
| GET    | /{id}        | 下载 blob      | 是      |

**DTOs**:
- `UploadBlobResp`

### Projects (/api/projects)

| 方法   | 路径           | 描述           | 需要认证 |
|--------|--------------|----------------|---------|
| GET    | /            | 列出用户项目   | 是      |
| POST   | /            | 创建项目       | 是      |
| GET    | /{id}        | 获取项目详情   | 是      |
| PUT    | /{id}        | 更新项目       | 是      |
| DELETE | /{id}        | 删除项目       | 是      |

**DTOs**:
- `CreateProjectReq` / `CreateProjectResp`
- `UpdateProjectReq` / `UpdateProjectResp`
- `GetProjectResp`
- `ListProjectsItemResp`

### Health

| 方法   | 路径       | 描述       |
|--------|-----------|-----------|
| GET    | /health   | 健康检查   |

**响应**: `{"status": "ok", "version": "1.0.0"}`

## 开发

如果已经安装 `just`，优先在仓库根目录使用 `just lint-backend`、`just typecheck-backend`、`just test-backend` 和 `just db-*`。

### 代码风格

```bash
# 检查代码
uv run --extra dev ruff check .

# 格式化代码
uv run --extra dev ruff format .
```

### 测试

```bash
# 运行所有测试
uv run --extra dev pytest

# 带覆盖率
uv run --extra dev pytest --cov=src
```

### 数据库迁移

```bash
# 创建新迁移
uv run --extra dev alembic revision --autogenerate -m "description"

# 升级到最新
uv run --extra dev alembic upgrade head

# 回滚
uv run --extra dev alembic downgrade -1
```

## 架构文档

详细 DDD 架构规范、编码约定和模式，请查看：

- [project_conventions.md](./project_conventions.md) - 架构概览和规范
- [docs/architecture/ddd-guide.md](./docs/architecture/ddd-guide.md) - 完整 DDD 教程

## 环境变量

```bash
# 数据库
DATABASE_URL=postgresql+asyncpg://user:password@localhost:5432/dbname
POSTGRES_HOST=localhost
POSTGRES_PORT=5432
POSTGRES_USER=user
POSTGRES_PASSWORD=password
POSTGRES_DB=dbname

# JWT（开发环境自动生成，生产环境需设置）
SECRET_KEY=your-secret-key (最少 32 字符)

# 环境
ENVIRONMENT=development  # 或 production
```
