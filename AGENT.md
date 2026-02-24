# Agent 工作指南

## 重要规则
始终中文跟用户交流！

---

## 后端开发规范（必读）

当执行后端开发任务时，**必须**参考 [`backend/project_conventions.md`](./backend/project_conventions.md) 中的规范。

### 核心原则

1. **DDD 分层架构** - 代码组织为四层：
   - `api/` - FastAPI 路由、DTOs
   - `application/` - 命令、处理器、编排
   - `domain/` - 领域对象（实体、值对象、仓库接口）⭐核心
   - `infra/` - SQLAlchemy 实现、外部服务

2. **依赖方向** - 只能向内依赖：
   ```
   api → application → domain ← infra
   ```

3. **充血领域模型** - 业务逻辑封装在领域对象中：
   ```python
   # 正确 - 领域对象有行为
   skill.rename("New Name")  # 内部更新 slug 和版本
   
   # 错误 - 贫血模型
   skill.name = "New Name"  # 直接修改，无业务逻辑
   ```

4. **值对象** - 封装验证逻辑：
   ```python
   slug = Slug("my-skill")  # 自动验证格式
   email = Email("user@example.com")  # 自动验证邮箱格式
   ```

5. **异常处理** - 使用全局异常处理器：
   ```python
   # 正确 - 路由层只需抛出领域异常
   @router.post("/skills")
   async def create_skill(...):
       skill = await handle_create_skill(...)  # 抛出 DomainError 子类
       return skill
   # 全局处理器会自动转换为 HTTP 响应
   # 无需在路由中写 try-catch！
   ```

6. **禁止事项**：
   - 禁止领域层（`domain/`）导入 SQLAlchemy 或 FastAPI
   - 禁止在路由中写业务逻辑
   - 禁止贫血模型（只 getter/setter 的类）
   - 禁止在路由中手动捕获异常并转换（使用全局处理器）

### 快速检查清单

创建新功能时，确保：
- [ ] 领域对象封装了业务行为（不只是数据）
- [ ] 值对象在构造时验证数据
- [ ] 依赖方向正确（domain 不依赖 infra）
- [ ] 仓库接口在 domain/，实现在 infra/
- [ ] ORM 模型（PO）包含 `to_domain()` 和 `from_domain()` 映射方法
- [ ] 业务逻辑在领域层，不在路由或处理器中
- [ ] 应用层使用函数式风格（`handle_create_skill()`）而非 Handler 类
- [ ] Repository 通过 `app/api/dependencies/repositories.py` 的 Depends 函数注入

### 规范文档分层

后端规范采用**渐进式披露**设计，按需加载：

**第一层 - 核心速查（462行，LLM友好）**：
→ [`backend/project_conventions.md`](./backend/project_conventions.md)
- 包含：11章核心规则、极简示例、快速检查清单
- **默认加载这个文件即可**

**第二层 - 代码模板（按需引用）**：
→ `backend/docs/templates/*.py`
- `value_object_slug.py` - 值对象模板
- `aggregate_skill.py` - 聚合根模板
- `repository_skill.py` - Repository模板
- `handler_create_skill.py` - Handler函数模板
- `dto_create_skill.py` - DTO模板
- **需要完整代码示例时引用对应模板**

**第三层 - 深度教程（复杂场景）**：
→ [`backend/docs/architecture/ddd-guide.md`](./backend/docs/architecture/ddd-guide.md)
- 详细说明、设计原理、完整示例
- **需要深入理解某个概念时使用**

### 使用建议

```
快速开发 → 只加载 project_conventions.md
需要模板 → project_conventions.md + 对应 template
复杂问题 → project_conventions.md + ddd-guide.md 相关章节
```

---

## 项目概述

**Agent Skills Manager** - B/S 架构的 Agent Skills 管理平台，支持 Web 管理、本地同步、版本历史。

**技术栈**: Python 3.10+ / FastAPI 0.129+ / SQLAlchemy 2.0+ / PostgreSQL 16+ / Next.js 15 / React 19 / TypeScript / Tailwind CSS 4.0

---

## 项目结构

```
backend/
├── app/
│   ├── api/          # API 路由注册 (api/v1/)
│   ├── core/         # 配置 (config.py)
│   ├── crud/         # 数据库 CRUD 操作
│   ├── db/           # 数据库会话、基类
│   ├── dependencies/ # FastAPI 依赖 (auth.py)
│   ├── models/       # SQLAlchemy 模型
│   ├── routers/      # 路由处理 (auth.py, skills.py, ...)
│   ├── schemas/      # Pydantic schemas
│   └── main.py       # FastAPI 入口
├── alembic/          # 数据库迁移

frontend/
├── app/              # Next.js App Router
│   ├── page.tsx      # 首页
│   ├── login/        # 登录
│   ├── register/     # 注册
│   └── skills/       # Skills CRUD 页面
├── components/       # React 组件 (ui/, FileTree, ...)
├── lib/              # 工具 (api.ts, auth.ts, utils.ts)
└── types/            # TypeScript 类型
```

---

## 数据模型

| 表名     | 说明                                  |
| -------- | ------------------------------------- |
| users    | 用户 (email, username, password_hash) |
| skills   | Skills (user_id, name, slug, tree_id) |
| trees    | 目录树结构 (data: JSONB)              |
| blobs      | 文件内容 (content_hash, content, reference_count) |
| file_versions | 文件版本历史 (skill_id, file_path, blob_id) |
| projects | 项目 (user_id, name, path, platform)  |

**主键**: UUID | **认证**: JWT (access 30min, refresh 7天) | **密码**: bcrypt

---

## 开发规范

### Python

- async/await 异步编程
- Pydantic v2 数据验证
- SQLAlchemy 2.0 异步 ORM
- 代码风格: ruff (line-length: 100)
- 类型提示: 必须

### TypeScript / React

- App Router (Next.js 15)
- Tailwind CSS 4.0
- 组件风格: shadcn/ui 模式
- 类型提示: 必须

### Git 提交

`feat:` `fix:` `chore:` `docs:` `refactor:` `test:`

---

## 运行与构建

### 启动服务

```bash
# 后端 (开发)
cd backend && uvicorn app.main:app --reload --port 8000
# API 文档: http://localhost:8000/docs

# 前端 (开发)
cd frontend && npm run dev

# 生产构建
cd frontend && npm run build && npm start
```

### 代码检查

```bash
# Backend
cd backend && ruff check . && ruff format .

# Frontend
cd frontend && npm run lint
```

---

## 测试规范与策略

### 测试框架

| 端 | 框架 | 命令 |
|---|------|------|
| Backend | pytest + pytest-asyncio | `cd backend && pytest` |
| Frontend | bun test | `cd frontend && bun test` |

### 测试文件组织

```
backend/tests/
├── integration/
│   ├── api/           # API 端点测试
│   └── journey/       # 端到端场景测试
├── unit/              # 单元测试
├── factories/         # 测试工厂
└── conftest.py       # fixtures (db, user, auth client)

frontend/lib/__tests__/
├── *.test.ts          # 工具函数测试
```

### 测试策略

- **Backend**: 
  - API 测试: 使用 `httpx.AsyncClient` 模拟请求
  - Fixtures: `db_session`, `test_user`, `auth_client`, `client`
  - 场景测试: journey 测试覆盖完整用户流程
- **Frontend**:
  - 工具函数测试: Mock fetch/localStorage
  - 使用 `@testing-library/jest-dom`

### 测试保证方式

1. **CI 强制**: 提交前必须通过 `pytest` 和 `bun test`
2. **LSP 校验**: 代码变更后运行 `lsp_diagnostics`
3. **类型检查**: 后端 mypy，前端 TypeScript 编译

---

## 添加新功能

### 添加新模型
1. `backend/app/models/` 创建模型
2. `backend/app/schemas/` 创建 schema
3. `backend/app/crud/` 创建 CRUD
4. `backend/app/routers/` 添加路由
5. `alembic revision --autogenerate -m "desc"` + `alembic upgrade head`

### 添加 API 端点
1. `backend/app/routers/` 创建路由
2. 使用 `Depends(get_current_user)` 保护认证接口
3. `backend/app/api/__init__.py` 注册路由

### 数据库迁移

**规范**: 按表分开，一个表一个迁移文件，无物理外键（外键关系在代码层维护）

**命名**: `<timestamp>__<描述>.py` (如 `20260214081000__create_users.py`)

**Revision ID**: 简洁版本号 (如 `v1_users`, `v2_blobs`)

**示例** (参考现有迁移文件 `backend/alembic/versions/`):
```python
# 20260214081000__create_users.py
revision: str = "v1_users"
down_revision: Union[str, None] = None  # 首个迁移无前置

# 20260214081010__create_blobs.py  
revision: str = "v2_blobs"
down_revision: Union[str, None] = "v1_users"

def upgrade() -> None:
    op.create_table("blobs", ...)  # 无 FOREIGN KEY

def downgrade() -> None:
    op.drop_table("blobs")
```

**执行**:
```bash
alembic upgrade head   # 执行全部
alembic history         # 查看历史
alembic downgrade -1   # 回滚一个
```

---

## API 认证

所有需认证的接口: `Authorization: Bearer <access_token>`

Token 过期时: `POST /api/auth/refresh` + Header: `Authorization: Bearer <refresh_token>`

API 文档: http://localhost:8000/docs

---

## 环境变量 (backend/.env)

```bash
DATABASE_URL=postgresql+asyncpg://user:pass@localhost:5432/db
SECRET_KEY=your-secret-key-min-32-chars
```
