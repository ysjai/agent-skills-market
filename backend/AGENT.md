# Agent 工作指南

## 重要规则
始终中文跟用户交流！

---

## 后端开发规范（必读）

当执行后端开发任务时，**必须**参考 [`project_conventions.md`](./project_conventions.md) 中的规范。

### 核心原则

1. **DDD 分层架构** - 代码组织为四层：
   - `src/api/` - FastAPI 路由、DTOs
   - `src/application/` - 命令、处理器、编排
   - `src/domain/` - 领域对象（实体、值对象、仓库接口）⭐核心
   - `src/infra/` - SQLAlchemy 实现、外部服务

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
   - 禁止领域层（`src/domain/`）导入 SQLAlchemy 或 FastAPI
   - 禁止在路由中写业务逻辑
   - 禁止贫血模型（只 getter/setter 的类）
   - 禁止在路由中手动捕获异常并转换（使用全局处理器）

### 快速检查清单

创建新功能时，确保：
- [ ] 领域对象封装了业务行为（不只是数据）
- [ ] 值对象在构造时验证数据
- [ ] 依赖方向正确（domain 不依赖 infra）
- [ ] 仓库接口在 `src/domain/repositories/`，实现在 `src/infra/persistence/repositories/`
- [ ] ORM 模型（PO）包含 `to_domain()` 和 `from_domain()` 映射方法
- [ ] 业务逻辑在领域层，不在路由或处理器中
- [ ] 应用层使用函数式风格（`handle_create_skill()`）而非 Handler 类
- [ ] Repository 通过 `src/api/dependencies/repositories.py` 的 Depends 函数注入

### 规范文档分层

后端规范采用**渐进式披露**设计，按需加载：

**第一层 - 核心速查（462行，LLM友好）**：
→ [`project_conventions.md`](./project_conventions.md)
- 包含：11章核心规则、极简示例、快速检查清单
- **默认加载这个文件即可**

**第二层 - 代码模板（按需引用）**：
→ `docs/templates/*.py`
- `value_object_slug.py` - 值对象模板
- `aggregate_skill.py` - 聚合根模板
- `repository_skill.py` - Repository模板
- `handler_create_skill.py` - Handler函数模板
- `dto_create_skill.py` - DTO模板
- **需要完整代码示例时引用对应模板**

**第三层 - 深度教程（复杂场景）**：
→ [`docs/architecture/ddd-guide.md`](./docs/architecture/ddd-guide.md)
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

**Agent Skills Manager Backend** - FastAPI 后端服务，支持 Agent Skills 的创建、管理和版本控制。

**技术栈**: Python 3.10+ / FastAPI 0.129+ / SQLAlchemy 2.0+ / PostgreSQL 16+

---

## 项目结构

```
backend/
├── src/
│   ├── api/              # API 路由、DTOs、依赖注入
│   │   ├── routers/      # FastAPI 路由
│   │   ├── schemas/      # Pydantic DTOs
│   │   └── dependencies/ # FastAPI Depends
│   ├── application/      # 应用层（Handlers）
│   │   └── handlers/     # 命令处理器函数
│   ├── domain/           # 领域层（核心）
│   │   ├── aggregates/   # 聚合根
│   │   ├── entities/     # 实体
│   │   ├── value_objects/# 值对象
│   │   ├── repositories/ # 仓库接口（抽象）
│   │   └── exceptions.py # 领域异常
│   ├── infra/            # 基础设施层
│   │   └── persistence/  # 持久化实现
│   │       ├── models/   # ORM 模型
│   │       └── repositories/ # 仓库实现
│   ├── core/             # 配置、认证
│   ├── db/               # 数据库连接
│   └── main.py           # FastAPI 入口
├── tests/                # 测试
├── alembic/              # 数据库迁移
└── docs/                 # 文档
    ├── architecture/     # 架构文档
    └── templates/        # 代码模板
```

---

## 数据模型

| 表名          | 说明                                              |
|---------------|---------------------------------------------------|
| users         | 用户 (email, username, password_hash)             |
| skills        | Skills (user_id, name, slug, tree_id)             |
| trees         | 目录树结构 (data: JSONB)                          |
| blobs         | 文件内容 (content_hash, content, reference_count) |
| file_versions | 文件版本历史 (skill_id, file_path, blob_id)       |
| projects      | 项目 (user_id, name, path, platform)              |

**主键**: UUID | **认证**: JWT (access 30min, refresh 7天) | **密码**: bcrypt

---

## 开发规范

### Python

- async/await 异步编程
- Pydantic v2 数据验证
- SQLAlchemy 2.0 异步 ORM
- 代码风格: ruff (line-length: 100)
- 类型提示: 必须

### 测试

- 测试框架: pytest + pytest-asyncio
- API 测试: `tests/integration/api/`
- Journey 测试: `tests/integration/journey/`
- 运行: `pytest`

### 数据库迁移

```bash
# 创建迁移
alembic revision --autogenerate -m "description"

# 执行迁移
alembic upgrade head

# 回滚
alembic downgrade -1
```

---

## 快速启动

```bash
# 安装依赖
pip install -r requirements.txt

# 配置环境变量
cp .env.example .env
# 编辑 .env 设置数据库连接

# 运行迁移
alembic upgrade head

# 启动开发服务器
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

---

## 参考资料

- [项目规范](project_conventions.md) - DDD 架构规范（必读）
- [详细教程](docs/architecture/ddd-guide.md) - 深度架构说明
- [代码模板](docs/templates/) - 可直接复制的代码模板
