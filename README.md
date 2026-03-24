# Agent Skills Manager

<p align="center">
  <img src="https://img.shields.io/badge/Version-0.1.0-blue.svg" alt="Version">
  <img src="https://img.shields.io/badge/Python-3.10+-green.svg" alt="Python">
  <img src="https://img.shields.io/badge/Next.js-15+-blue.svg" alt="Next.js">
  <img src="https://img.shields.io/badge/License-MIT-yellow.svg" alt="License">
</p>

> Agent Skills 管理平台 - 管理、同步和分享自定义 Agent Skills

## 简介

Agent Skills Manager 是一个 B/S 架构系统，帮助用户管理、同步和分享自定义 Agent Skills。支持 Claude Code 和 OpenCode 平台。

## 功能特性

- **Web 界面** - 创建、编辑和版本管理 Skills
- **双向同步** - Web 与本地自动同步
- **多文件 Skills** - 支持 SKILL.md + templates/ + examples/ 目录结构
- **版本历史** - Git 风格的版本控制，支持回滚
- **用户系统** - 邮箱注册/登录，JWT 认证
- **本地 Daemon** - 自动发现项目和文件监控
- **符号链接** - 自动链接到项目目录
- **开源可自托管** - 完全开源，支持私有部署

## 技术栈

### 后端

- **Python**: 3.10+
- **FastAPI**: 0.129.0+ (Web 框架)
- **SQLAlchemy**: 2.0+ (ORM)
- **PostgreSQL**: 16+ (数据库)
- **Alembic**: (数据库迁移)
- **JWT**: (认证)

### 前端

- **Next.js**: 15+ (App Router)
- **React**: 19+
- **TypeScript**: 5.7+
- **Tailwind CSS**: 4.0+

### 本地 Daemon

- **Python**: 3.10+
- **WebSocket**: (实时同步)
- **watchdog**: (文件监控)

## 快速开始

### 前置要求

- Python 3.10+
- Node.js 18+
- PostgreSQL 16+ (或 Docker)
- Docker (可选)

### 1. 克隆项目

```bash
git clone https://github.com/ai-agent-ysj/agent-skills-market.git
cd agent-skills-market
```

### 2. 启动 PostgreSQL

```bash
# 使用 Docker
docker compose up -d postgres

# 或手动配置 PostgreSQL
```

### 3. 后端设置

```bash
cd backend

# 使用 uv 安装依赖（推荐）
uv sync

# 手动创建虚拟环境
python -m venv .venv
source .venv/bin/activate  # Linux/Mac
# .venv\Scripts\activate  # Windows
uv sync

# 配置环境变量
cp .env.example .env
# 编辑 .env 设置数据库连接

# 创建数据库（如果不存在）
docker exec -it agent_skills_db psql -U postgres -c "CREATE DATABASE agent_skills"
# 或: psql -U postgres -c "CREATE DATABASE agent_skills"

# 运行迁移
alembic downgrade base
alembic upgrade head

# 启动开发服务器（开发模式下 SECRET_KEY 自动生成）
uvicorn src.main:app --reload --host 0.0.0.0 --port 8000
```

后端启动后，访问：

- API: http://localhost:8000
- API 文档: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc

### 4. 前端设置

```bash
cd frontend

# 安装依赖
npm install

# 启动开发服务器
npm run dev
```

前端启动后，访问：http://localhost:3000

### 5. 验证

```bash
# 测试健康检查
curl http://localhost:8000/health

# 测试注册
curl -X POST http://localhost:8000/api/auth/register \
  -H "Content-Type: application/json" \
  -d '{"email": "test@example.com", "username": "testuser", "password": "password123"}'

# 测试登录
curl -X POST http://localhost:8000/api/auth/login \
  -H "Content-Type: application/json" \
  -d '{"email": "test@example.com", "password": "password123"}'
```

## 项目结构

```
agent-skills-market/
├── backend/                     # FastAPI 后端 (DDD 架构)
│   ├── src/
│   │   ├── api/                # API 层 (路由、依赖、schemas)
│   │   │   ├── dependencies/   # FastAPI 依赖注入
│   │   │   ├── routers/        # API 路由
│   │   │   ├── schemas/        # Pydantic DTOs
│   │   │   └── exception_handlers.py
│   │   ├── application/       # 应用层 (handlers)
│   │   │   └── handlers/       # 用例处理器
│   │   ├── domain/            # 领域层 (核心业务逻辑)
│   │   │   ├── aggregates/     # 聚合根 (Skill, User, Tree 等)
│   │   │   ├── entities/       # 实体
│   │   │   ├── value_objects/  # 值对象 (Slug, Email 等)
│   │   │   ├── repositories/   # 仓库接口 (抽象)
│   │   │   └── exceptions.py   # 领域异常
│   │   ├── infra/             # 基础设施层
│   │   │   └── persistence/   # ORM 模型和仓库实现
│   │   ├── core/              # 配置
│   │   └── main.py            # 应用入口
│   ├── alembic/               # 数据库迁移
│   ├── tests/                 # 测试文件
│   ├── pyproject.toml         # 项目配置
│   ├── uv.lock                # uv 锁文件
│   └── project_conventions.md # DDD 架构指南
│
├── frontend/                  # Next.js 前端
│   ├── app/                   # App Router 页面
│   ├── components/            # React 组件
│   ├── lib/                  # 工具函数
│   └── types/                # TypeScript 类型
│
├── daemon/                    # 本地 Daemon (TODO)
│
├── docker-compose.yml        # Docker 配置
├── AGENTS.md                 # Agent 工作指南
└── README.md                # 本文件
```

## 架构概览

本项目采用 **领域驱动设计 (DDD) 四层架构**：

```
┌─────────────────────────────────────────────┐
│                  API 层                      │
│            (routers, dependencies)          │
│                ↓ 依赖方向                      │
├─────────────────────────────────────────────┤
│                应用层                          │
│             (handlers, commands)              │
│                ↓ 依赖方向                      │
├─────────────────────────────────────────────┤
│                 领域层                         │
│       (entities, value_objects, repositories)│
│                ↑ 实现方向                      │
├─────────────────────────────────────────────┤
│               基础设施层                        │
│          (persistence, external_services)    │
└─────────────────────────────────────────────┘
```

### 核心模式

- **值对象**: 构造时验证的不可变对象 (如 Slug, Email)
- **聚合根**: 封装业务逻辑的领域实体 (如 Skill, User)
- **仓库**: 抽象数据访问接口，SQLAlchemy 实现
- **处理器**: 应用层中的无状态用例函数
- **依赖注入**: 通过 FastAPI Depends 注入仓库

详细架构文档请查看 [backend/project_conventions.md](backend/project_conventions.md)。

## API 文档

### 认证

| 方法   | 路径                  | 描述           | 请求 DTO        | 响应 DTO         |
|--------|----------------------|----------------|-----------------|------------------|
| POST   | /api/auth/register   | 用户注册       | RegisterUserReq | RegisterUserResp |
| POST   | /api/auth/login      | 用户登录       | LoginReq        | LoginResp        |
| POST   | /api/auth/refresh    | 刷新访问令牌   | - (Header)      | LoginResp        |
| GET    | /api/auth/me        | 获取当前用户   | -               | GetUserResp      |
| POST   | /api/auth/logout     | 用户登出       | -               | Message          |

### Skills

| 方法   | 路径                     | 描述         | 请求 DTO         | 响应 DTO         |
|--------|-------------------------|--------------|------------------|------------------|
| GET    | /api/skills             | 列出用户 Skills | Query: skip, limit | ListSkillsResp  |
| POST   | /api/skills             | 创建 Skill   | CreateSkillReq   | CreateSkillResp  |
| POST   | /api/skills/import      | 导入 Skill   | ImportSkillReq   | CreateSkillResp  |
| GET    | /api/skills/{id}        | 获取详情     | -                | GetSkillResp     |
| PUT    | /api/skills/{id}        | 更新 Skill   | UpdateSkillReq   | UpdateSkillResp  |
| DELETE | /api/skills/{id}        | 删除 Skill   | -                | -                |

### Trees

| 方法   | 路径                          | 描述         | 请求 DTO          | 响应 DTO         |
|--------|------------------------------|--------------|-------------------|------------------|
| POST   | /api/trees                   | 创建树       | CreateTreeReq     | CreateTreeResp   |
| GET    | /api/trees/{id}              | 获取树       | -                 | GetTreeResp      |
| POST   | /api/trees/{id}/files        | 添加文件     | AddTreeFileReq    | AddTreeFileResp  |
| DELETE | /api/trees/{id}/files        | 删除文件     | DeleteTreeFileReq | CreateTreeResp   |
| PUT    | /api/trees/{id}/files/rename | 重命名文件   | RenameTreeFileReq | CreateTreeResp   |
| PUT    | /api/trees/{id}/files/move   | 移动文件     | MoveTreeFileReq   | CreateTreeResp   |

### Blobs

| 方法   | 路径              | 描述       | 请求 DTO     | 响应 DTO       |
|--------|------------------|------------|--------------|----------------|
| POST   | /api/blobs       | 上传 blob  | Multipart    | UploadBlobResp |
| GET    | /api/blobs/{id}  | 下载 blob  | -            | 二进制内容      |

### Projects

| 方法   | 路径                   | 描述           | 请求 DTO           | 响应 DTO            |
|--------|----------------------|----------------|--------------------|---------------------|
| GET    | /api/projects        | 列出用户项目   | Query: skip, limit | ListProjectsResp    |
| POST   | /api/projects        | 创建项目       | CreateProjectReq   | CreateProjectResp   |
| GET    | /api/projects/{id}   | 获取项目详情   | -                  | GetProjectResp      |
| PUT    | /api/projects/{id}  | 更新项目       | UpdateProjectReq   | UpdateProjectResp   |
| DELETE | /api/projects/{id}   | 删除项目       | -                  | -                   |

### Health

| 方法   | 路径       | 描述       | 响应                        |
|--------|-----------|-----------|----------------------------|
| GET    | /health   | 健康检查   | {"status": "ok", "version": "1.0.0"} |

完整 API 文档：http://localhost:8000/docs

## 环境变量

### 后端 (.env)

```bash
# 数据库
DATABASE_URL=postgresql+asyncpg://user:password@localhost:5432/dbname
POSTGRES_HOST=localhost
POSTGRES_PORT=5432
POSTGRES_USER=user
POSTGRES_PASSWORD=password
POSTGRES_DB=dbname

# JWT（开发环境自动生成，生产环境需设置）
# SECRET_KEY=your-generated-secret-key-here
```

## 开发

### 代码格式化

```bash
# 后端 - 使用 ruff
cd backend
ruff check .
ruff format .

# 前端 - 使用 ESLint
cd frontend
npm run lint
```

### 安全扫描

```bash
# 运行完整安全扫描
./scripts/security-check.sh

# 扫描 Python 依赖
cd backend
safety check

# 扫描 Node.js 依赖
cd frontend
npm audit --audit-level=high
```

### 测试

```bash
# 后端
cd backend
pytest

# 前端
cd frontend
npm run test
```

## License

MIT License - 详见 LICENSE 文件

## 贡献

欢迎提交 Issues 和 Pull Requests！

---

<p align="center">Made with by Agent Skills Team</p>
