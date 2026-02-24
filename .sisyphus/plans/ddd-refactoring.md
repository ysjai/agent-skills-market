# Agent Skills Manager - DDD 分层架构重构计划

## TL;DR

> **目标**: 将现有 FastAPI 后端从贫血模型重构为充血领域模型的 DDD 分层架构
>
> **范围**: 全面重构，覆盖所有模块（User, Skill, Tree, Blob, Project）
>
> **时间**: 无压力，采用渐进式重构策略
>
> **复杂度**: 简化版 DDD（无领域事件/CQRS），重点实现充血领域模型
>
> **前置任务**: Wave 0 - 必须先创建 `backend/project_conventions.md` 规范文档并更新 `AGENT.md`

**核心改进**:

- 从贫血模型 → 充血领域模型
- 业务逻辑集中到领域层
- 值对象封装验证逻辑（Slug, Path, Email）
- 清晰的四层架构边界

**预期收益**:

- 业务逻辑内聚，修改只需改一处
- 领域层可独立测试（无外部依赖）
- 代码即文档，结构反映业务

---

## 前置要求 ⚠️

### Wave 0 必须先完成

在开始 Wave 1 及后续任务之前，**必须先完成 Wave 0**:

1. **创建 `backend/project_conventions.md`** - DDD 项目架构规范文档

   - 详细说明四层架构规范
   - 值对象、聚合根、仓库模式设计规范
   - 命名规范、导入规范、异常处理规范
   - 每个规范附带代码示例
2. **更新 `AGENT.md`** - 在开发指南中引用规范

   - 在显眼位置添加后端开发规范提示
   - 添加指向 `backend/project_conventions.md` 的链接
   - 列出核心原则和禁止事项

**为什么必须先完成 Wave 0？**

- 确保所有后续开发遵循统一标准
- 避免不同开发者理解不一致
- 提供可执行的代码检查清单
- 作为代码审查的基准

---

## Context

### 当前架构状态

**技术栈**: FastAPI 0.129.0 + SQLAlchemy 2.0 + PostgreSQL 16

**当前目录结构**:

```
backend/app/
├── api/              # API路由组装
├── core/             # 配置、认证、日志
├── crud/             # CRUD操作 (Repository层)
├── db/               # 数据库连接、Base类
├── models/           # SQLAlchemy 模型 (贫血)
├── routers/          # FastAPI 路由 (Controller层)
├── schemas/          # Pydantic 验证模型 (DTO)
├── services/         # 业务逻辑服务层
└── main.py           # 应用入口
```

**当前问题**:

1. **贫血领域模型**: Models 只是数据容器，业务逻辑散落在 services/ 和 crud/
2. **业务规则分散**: Slug 验证在 skill_service.py，Path 验证在 trees.py 路由
3. **基础设施耦合**: skill_service.py 直接操作 db.flush()，与数据库事务混合
4. **缺少值对象**: Slug, Path, Email 用原始字符串传递，验证逻辑重复

### 目标架构

```
backend/app/
├── api/                    # 接口层 (Interface Layer)
│   ├── routers/           # FastAPI 路由
│   ├── routers/           # FastAPI 路由
│   ├── schemas/           # Pydantic DTOs
│   ├── dependencies/      # FastAPI 依赖注入
│   └── exception_handlers.py  # 全局异常处理器
├── application/           # 应用层 (Application Layer) - 新增
│   ├── commands/          # 命令对象
│   ├── handlers/          # 命令处理器
│   └── # 注意：应用层不定义异常（使用 domain/exceptions.py）
├── domain/                # 领域层 (Domain Layer) - 核心
│   ├── aggregates/        # 聚合根 (Skill, User, Tree)
│   ├── entities/          # 实体
│   ├── value_objects/     # 值对象 (Slug, Path, Email)
│   ├── repositories/      # 仓库接口（仅接口）
│   ├── services/          # 领域服务
│   ├── exceptions.py      # 领域异常基类（唯一异常基类）
│   └── factories.py       # 领域工厂
├── infra/                 # 基础设施层 (Infrastructure Layer)
│   ├── persistence/       # SQLAlchemy 实现
│   │   ├── models/        # ORM 模型（包含领域模型到PO的映射方法）
│   │   └── repositories/  # 仓库实现
│   ├── auth/              # JWT 实现
│   └── config/            # 配置
└── shared/                # 共享内核
    └── types.py           # 类型定义
```

### 依赖关系规则

```
依赖方向（从上到下）：

┌─────────────────────────────────────────────┐
│  api/ (接口层)                                │
│  - FastAPI 路由、请求/响应 DTOs               │
└──────────────┬──────────────────────────────┘
               │ 依赖
               ▼
┌─────────────────────────────────────────────┐
│  application/ (应用层)                        │
│  - 命令对象、处理器、用例编排                  │
└──────────────┬──────────────────────────────┘
               │ 依赖
               ▼
┌─────────────────────────────────────────────┐
│  domain/ (领域层)                             │
│  - 实体、值对象、仓库接口(抽象)、领域服务      │
│  - ⚠️ 禁止依赖任何框架（FastAPI/SQLAlchemy）  │
└──────────────┬──────────────────────────────┘
               │ 依赖倒置（通过接口）
               ▼
┌─────────────────────────────────────────────┐
│  infra/ (基础设施层)                          │
│  - 仓库实现、ORM 模型、外部服务客户端          │
│  - 依赖 domain/ (实现接口)                    │
│  - 依赖 application/ (事件发布等)             │
└─────────────────────────────────────────────┘
```

**关键规则**:

- `domain/` 不依赖任何其他层（纯 Python）
- `application/` 可以依赖 `domain/`
- `api/` 可以依赖 `application/` 和 `domain/`
- `infra/` 通过**依赖倒置**依赖 `domain/`（实现 domain 的接口）
- `infra/` 也可以依赖 `application/`（如事件发布器实现）

---

## Work Objectives

### 核心目标

构建充血领域模型，让业务逻辑高度内聚，消除贫血模型，实现清晰的 DDD 分层架构。

### 具体目标

1. **值对象体系**: 创建 Slug, Path, Email 等值对象，封装验证逻辑
2. **充血实体**: 将 Skill, User, Tree 重构为富领域对象
3. **聚合根**: 明确聚合边界，通过聚合根访问内部对象
4. **仓库接口**: 定义抽象仓库接口，与基础设施解耦
5. **分层边界**: 严格执行依赖向内原则

### 定义完成标准

- [ ] 所有领域对象都有业务行为方法
- [ ] 业务规则不再散落在路由或服务层
- [ ] 值对象封装所有格式验证
- [ ] 仓库接口定义清晰
- [ ] 所有测试通过

### 必须实现

- 值对象系统
- 充血领域模型
- 四层架构
- 仓库模式

### 必须不实现（Guardrails）

- 领域事件系统（过于复杂，本次不需要）
- CQRS 模式（过于复杂，本次不需要）
- 事件溯源（过于复杂，本次不需要）
- 微服务拆分（超出本次范围）

---

## Verification Strategy

### 测试策略

- **基础设施**: 已存在 pytest
- **策略**: 测试后补（Tests-after）
- **框架**: pytest
- **测试类型**:
  1. **API 端点功能测试** - 测试单个 API 端点的功能正确性
  2. **User Journey 测试** - 测试一组连贯的 API 调用构成的业务流程

**不编写**:

- ❌ 单元测试（只针对领域对象的细粒度测试）
- ❌ 仓库层集成测试（测试 SQLAlchemy 实现）

**测试重点**:

```
API 端点测试示例:
  POST /api/skills       - 测试创建 skill 的各种场景
  GET /api/skills/{id}   - 测试获取 skill 的返回格式
  PUT /api/skills/{id}   - 测试更新 skill 的权限检查
  
User Journey 测试示例:
  [注册 → 登录 → 创建 Skill → 添加文件 → 下载 Skill]
  [创建 Skill → 更新名称 → 检查版本 → 删除 Skill]
  [批量上传文件 → 重命名目录 → 下载 Zip]
```

### QA 策略

每个任务包含 Agent-Executed QA Scenarios，验证通过 Bash（curl）或 pytest（API 测试）执行。

---

## Execution Strategy

### 重构策略：渐进式模块重构

不一次性重写全部代码，而是逐个模块迁移，使用适配器模式过渡。

**迁移顺序**:
0. **Wave 0**: 项目规范建立（前置任务）⭐

- 创建 `backend/project_conventions.md` DDD 架构规范
- 更新 `AGENT.md` 引用项目规范

1. **Wave 1**: 基础设施（目录结构、工具类）
2. **Wave 2**: 值对象（Slug, Path, Email）- 可并行
3. **Wave 3**: Skill 领域模型重构 - 核心模块
4. **Wave 4**: User 领域模型重构
5. **Wave 5**: Tree 领域模型重构
6. **Wave 6**: Blob & Project 领域模型重构
7. **Wave 7**: API 层适配
8. **Wave 8**: 清理旧代码
9. **Wave FINAL**: 文档创建

**重要执行规则 ⚠️**：
每个 Wave 执行完成后，**必须暂停并等待用户验收确认**：

1. 完成当前 Wave 的所有任务
2. 运行该 Wave 的 Final Verification Wave（4 个审查代理并行执行）
3. **暂停执行**，提示用户进行测试验收
4. **等待用户明确指令**：用户必须回复"继续"或"下一步"才能进入下一个 Wave
5. 如果用户发现问题，根据反馈修复后再继续

这样可以确保每个阶段的质量，避免问题累积到后期难以修复。

### 依赖关系

```
Wave 0 (前置任务) ⭐ 必须先完成
├── 创建 backend/project_conventions.md 规范文档
└── 更新 AGENT.md 引用规范

Wave 1 (基础设施) - 依赖 Wave 0
├── 创建目录结构
├── 创建基础异常类
└── 创建类型定义

Wave 2 (值对象 - 并行)
├── Slug 值对象
├── Path 值对象
└── Email 值对象

Wave 3 (Skill - 依赖 Wave 1, Wave 2)
├── Skill 领域工厂
├── Skill 聚合根
├── Skill 仓库接口
└── Skill 基础设施实现

Wave 4 (User - 依赖 Wave 1, Wave 2)
├── User 领域工厂
├── User 聚合根
├── User 仓库接口
└── User 基础设施实现

Wave 5 (Tree - 依赖 Wave 1, Wave 2)
├── Tree 领域工厂
├── Tree 聚合根
├── Tree 仓库接口
└── Tree 基础设施实现

Wave 6 (Blob & Project - 依赖 Wave 1, Wave 2)
├── Blob 值对象
├── Project 领域模型
└── 仓库实现

Wave 7 (API 适配 - 依赖 Wave 3-6)
├── 创建 DTO (Req/Resp)
├── 实现命令处理器（函数式风格）
└── 适配新领域模型

Wave 8 (清理 - 激进式)
├── 删除旧 services/
├── 删除旧 crud/
├── 删除旧 models/
└── 迁移 routers

Wave FINAL (文档)
├── DDD 培训文档
├── 架构文档
└── API 文档
```

---

## 前置任务：项目规范建立 (Wave 0)

在开始 DDD 重构之前，必须先建立项目架构规范，确保所有后续工作遵循统一标准。

---

## TODOs

### Wave 0: 项目规范建立（前置任务）

- [x] 0.1 创建 backend/project_conventions.md 项目架构规范（精简版）

  **What to do**:

  - 创建 `backend/project_conventions.md` 文件（控制在 400-600 行）
  - 文件定位为**速查手册（Reference）**，不是教程
  - 只包含**必须遵守的规则**和**可直接复制的代码模板**
  - 详细教程和解释放到 `docs/architecture/` 目录

  **必须包含的章节**（精简为 11 个核心章节）：

  1. **项目概述与核心原则**（简要）

     - 项目技术栈说明
     - DDD 核心原则一句话总结
     - 架构图（文字描述）
  2. **DDD 分层架构规范**（核心速查）

     - 四层架构图和依赖方向
     - 每层一句话职责说明
     - 目录结构速查表
     - 禁止事项清单
  3. **值对象设计规范**（代码模板）

     - Slug 值对象完整代码模板（可直接复制）
     - 值对象设计原则（3 条）
  4. **聚合根设计规范**（代码模板）

     - Skill 聚合根代码模板（包含 2-3 个领域方法）
     - 充血模型原则（3 条）
  5. **仓库模式规范**（代码模板）

     - SkillRepository 接口模板
     - SqlSkillRepository 实现模板
     - SkillModel 映射方法模板
    6. **应用层规范**（代码模板）

       **Repository 依赖注入**（FastAPI Depends）:

       ```python
       # app/api/dependencies/repositories.py
       from fastapi import Depends
       from sqlalchemy.ext.asyncio import AsyncSession

       from app.db.session import get_db
       from app.domain.repositories.skill_repository import SkillRepository
       from app.infra.persistence.repositories.sql_skill_repository import SqlSkillRepository


       async def get_skill_repo(
           db: AsyncSession = Depends(get_db)
       ) -> SkillRepository:
           """注入 SkillRepository"""
           return SqlSkillRepository(db)
       ```

       **Handler 函数模板**:

       ```python
       # app/application/handlers/create_skill_handler.py
       async def handle_create_skill(
           user_id: UUID,
           name: str,
           description: str | None,
           skill_repo: SkillRepository,  # 通过参数接收注入的 Repository
       ) -> Skill:
           """创建 Skill（纯函数，无状态）"""
           slug = Slug.from_name(name)
           
           existing = await skill_repo.get_by_slug(slug)
           if existing:
               raise SkillAlreadyExistsError()
           
           skill = Skill.create(user_id, name, description)
           await skill_repo.save(skill)
           return skill
       ```

       **在路由中使用**:

       ```python
       # app/api/routers/skills.py
       from app.api.dependencies.repositories import get_skill_repo

       @router.post("/skills", response_model=CreateSkillResp)
       async def create_skill(
           request: CreateSkillReq,
           skill_repo: SkillRepository = Depends(get_skill_repo),  # 自动注入
           current_user: User = Depends(get_current_user),
       ) -> CreateSkillResp:
           skill = await handle_create_skill(
               user_id=current_user.id,
               name=request.name,
               description=request.description,
               skill_repo=skill_repo,  # 传入已注入的 Repository
           )
           return CreateSkillResp.from_domain(skill)
       ```

       **核心原则**：
       - 应用层无状态，使用模块+函数而非类
       - Repository 通过 FastAPI Depends 在 API 层注入
       - Application 层通过参数接收 Repository（纯函数，易于测试）
  7. **DTO 设计规范**（命名速查表 + 代码模板）

     - 命名规则速查表
     - CreateSkillReq/Resp 模板
     - ListSkillsItemResp 模板
     - ❌ 不要包含"为什么每个 use case 要有独立 DTO"的详细解释
  8. **异常处理规范（简化版）**

     **核心原则**：

     - **业务异常只有一个基类**：`DomainError`（在 `domain/` 层定义）
     - **HTTP 状态码由 API 层决定**：业务层不感知 HTTP 传输细节
     - **统一响应格式**：生产/开发环境一致，只返回 `code` 和 `message`

     **异常层次结构**（单一基类，扁平化设计）：

     ```
     DomainError (app/domain/exceptions.py)
     ├── 类别分类（category 属性）
     │   ├── "NOT_FOUND"      → 404 资源不存在
     │   ├── "CONFLICT"       → 409 资源冲突（重复、已存在）
     │   ├── "VALIDATION"     → 422 格式验证失败
     │   ├── "UNAUTHORIZED"   → 401 未认证
     │   ├── "FORBIDDEN"      → 403 无权限
     │   └── "BUSINESS"       → 400 业务规则违反
     └── 具体异常子类
         ├── SkillNotFoundError(category="NOT_FOUND")
         ├── SkillAlreadyExistsError(category="CONFLICT")
         ├── InvalidSlugError(category="VALIDATION")
         └── ... (其他领域异常)
     ```

     **DomainError 基类设计**（纯业务，无 HTTP 信息）：

     ```python
     # app/domain/exceptions.py
     class DomainError(Exception):
         """领域错误基类 - 业务层专用，完全不知道 HTTP 的存在"""
         code: str = "DOMAIN_ERROR"           # i18n key
         message: str = "Domain error occurred"  # 人类可读的消息
         category: str = "BUSINESS"           # 业务分类（API层映射到HTTP状态码）

         def __init__(self, message: str | None = None):
             self.message = message or self.message
             super().__init__(self.message)

     # 具体领域异常示例
     class SkillAlreadyExistsError(DomainError):
         code = "SKILL_ALREADY_EXISTS"
         message = "Skill already exists"  # 通用描述，不含具体数据
         category = "CONFLICT"

     class ResourceNotFoundError(DomainError):
         code = "RESOURCE_NOT_FOUND"
         message = "Resource not found"
         category = "NOT_FOUND"

     class ValidationError(DomainError):
         code = "VALIDATION_ERROR"
         message = "Validation failed"
         category = "VALIDATION"

     class UnauthorizedError(DomainError):
         code = "UNAUTHORIZED"
         message = "Authentication required"
         category = "UNAUTHORIZED"
     ```

     **Code 命名规范**（用于 i18n）：

     ```
     格式: {DOMAIN|VALIDATION}_{RESOURCE}_{ACTION}_{RESULT}

     DOMAIN_SKILL_CREATE_CONFLICT         # 创建冲突
     DOMAIN_SKILL_UPDATE_NOT_FOUND        # 更新时找不到
     DOMAIN_SKILL_DELETE_HAS_CHILDREN     # 删除时有子节点
     DOMAIN_USER_AUTH_INVALID_CREDENTIALS # 认证失败
     DOMAIN_USER_REGISTER_EMAIL_EXISTS    # 邮箱已存在
     VALIDATION_SLUG_INVALID_FORMAT       # Slug 格式错误
     VALIDATION_PATH_TRAVERSAL_DETECTED   # 路径遍历攻击
     VALIDATION_EMAIL_MALFORMED           # 邮箱格式错误
     ```

     **全局异常处理器设计**（API 层负责 HTTP 状态码映射）：

     ```python
     # app/api/exception_handlers.py
     from fastapi import FastAPI, Request, status
     from fastapi.responses import JSONResponse
     from app.domain.exceptions import DomainError
     import logging

     logger = logging.getLogger(__name__)

     # 业务分类 → HTTP 状态码映射（API 层的职责）
     CATEGORY_STATUS_MAP = {
         "NOT_FOUND": status.HTTP_404_NOT_FOUND,          # 404
         "CONFLICT": status.HTTP_409_CONFLICT,            # 409
         "VALIDATION": status.HTTP_422_UNPROCESSABLE_ENTITY,  # 422
         "UNAUTHORIZED": status.HTTP_401_UNAUTHORIZED,    # 401
         "FORBIDDEN": status.HTTP_403_FORBIDDEN,          # 403
         "BUSINESS": status.HTTP_400_BAD_REQUEST,         # 400
     }

     def register_exception_handlers(app: FastAPI):
         """注册全局异常处理器"""

         @app.exception_handler(DomainError)
         async def handle_domain_error(request: Request, exc: DomainError):
             """处理领域错误 - API 层决定 HTTP 状态码"""
             status_code = CATEGORY_STATUS_MAP.get(exc.category, status.HTTP_400_BAD_REQUEST)

             # 统一格式：所有环境一致
             return JSONResponse(
                 status_code=status_code,
                 content={
                     "code": exc.code,      # 前端 i18n key
                     "message": exc.message  # 人类可读的消息
                 }
             )

         @app.exception_handler(Exception)
         async def handle_generic_exception(request: Request, exc: Exception):
             """处理未捕获的技术异常 → 500"""
             logger.exception("Unhandled exception")

             return JSONResponse(
                 status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                 content={
                     "code": "INTERNAL_SERVER_ERROR",
                     "message": "Internal server error"
                 }
             )
     ```

     在 `app/main.py` 中注册：

     ```python
     from app.api.exception_handlers import register_exception_handlers

     app = FastAPI()
     register_exception_handlers(app)
     ```

     **分层职责总结**：

     | 层级             | 职责                         | 属性                                |
     | ---------------- | ---------------------------- | ----------------------------------- |
     | **Domain** | 定义"发生了什么"（业务语义） | `code`, `message`, `category` |
     | **API**    | 决定"怎么回应"（HTTP 映射）  | 将 `category` 映射到 HTTP status  |

     **路由层无需 try-catch**：


     ```python
     # ✅ 正确 - 全局处理器会自动处理
     @router.post("/skills")
     async def create_skill(
         request: CreateSkillReq, 
         handler: CreateSkillHandler
     ) -> CreateSkillResp:
         skill = await handler.handle(request)  # 可能抛出 SkillAlreadyExistsError
         return CreateSkillResp.from_domain(skill)

     # ❌ 不需要这样写
     @router.post("/skills")
     async def create_skill(...):
         try:
             skill = await handler.handle(command)
         except SkillAlreadyExistsError as e:
             raise HTTPException(status_code=409, detail=str(e))  # 冗余！全局处理器会做
     ```

     **异常响应格式**：

     ```json
     {
       "code": "SKILL_ALREADY_EXISTS",
       "message": "Skill already exists"
     }
     ```

     **完整使用示例**：

     ```python
     # app/domain/value_objects/slug.py
     from app.domain.exceptions import ValidationError

     class Slug:
         def __init__(self, value: str):
             if not self._is_valid(value):
                 raise ValidationError("Invalid slug format")
             self._value = value.lower().strip()

      # app/application/handlers/create_skill_handler.py
      async def handle_create_skill(
          user_id: UUID,
          name: str,
          description: str | None,
          skill_repo: SkillRepository,
      ) -> Skill:
          """创建 Skill 的命令处理器（函数式风格）"""
          slug = Slug.from_name(name)
          
          # 检查重复
          existing = await skill_repo.get_by_slug(slug)
          if existing:
              raise SkillAlreadyExistsError()

          # 创建领域对象
          skill = Skill.create(user_id, name, description)
          await skill_repo.save(skill)
          return skill

      # app/api/routers/skills.py
      from app.api.dependencies.repositories import get_skill_repo

      @router.post("/skills", response_model=CreateSkillResp)
      async def create_skill(
          request: CreateSkillReq,
          skill_repo: SkillRepository = Depends(get_skill_repo),  # 自动注入
          current_user: User = Depends(get_current_user),
      ) -> CreateSkillResp:
          # 执行业务逻辑（可能抛出 DomainError 子类）
          skill = await handle_create_skill(
              user_id=current_user.id,
              name=request.name,
              description=request.description,
              skill_repo=skill_repo,  # 传入已注入的 Repository
          )

          # 返回响应
          return CreateSkillResp.from_domain(skill)
      ```
    9. **事务管理规范**

      **核心原则**：使用现有的 `get_db()` 管理事务，一个请求 = 一个事务。

      **事务边界定义**：

      ```python
      # app/db/session.py
      async def get_db() -> AsyncGenerator[AsyncSession, None]:
          async with AsyncSessionLocal() as session:
              try:
                  yield session
                  await session.commit()      # 请求成功自动提交
              except Exception:
                  await session.rollback()    # 异常自动回滚
                  raise
              finally:
                  await session.close()
      ```

      **Repository 层**：

      ```python
      class SqlSkillRepository(SkillRepository):
          def __init__(self, db: AsyncSession):  # 由 get_db 注入
              self._db = db
          
          async def save(self, skill: Skill) -> None:
              # 只 add，不 commit（由 get_db 自动处理）
              self._db.add(SkillModel.from_domain(skill))
      ```

      **Handler 中使用**：

      ```python
      async def handle_create_skill(
          user_id: UUID,
          name: str,
          skill_repo: SkillRepository,  # 事务由 get_db 管理
      ) -> Skill:
          """创建 Skill（事务由 get_db 自动管理）"""
          slug = Slug.from_name(name)
          
          # 检查重复
          if await skill_repo.get_by_slug(slug):
              raise SkillAlreadyExistsError()

          # 创建并保存
          skill = Skill.create(user_id, name)
          await skill_repo.save(skill)
          return skill  # 请求结束时自动 commit
      ```

      **并发控制策略**：

      1. **乐观锁**（推荐用于大多数场景）：
         - 领域对象包含 `version` 字段
         - 更新时检查 version 是否匹配
         - 不匹配则抛出 `ConcurrentModificationError`

      2. **数据库唯一约束**（防止重复创建）：
         - Slug 字段在数据库层设置唯一约束
         - 应用层先 SELECT 检查，再 INSERT
         - 数据库约束作为最终防线

      3. **悲观锁**（仅用于高频冲突场景）：
         - `SELECT FOR UPDATE` 锁定行
         - 在 Handler 中显式使用

      **禁止事项**：

      - ❌ 不要在仓库实现中调用 `db.commit()` 或 `db.rollback()`
      - ❌ 不要在领域层中管理事务
      - ❌ 不要在路由层中管理事务
      - ✅ 事务由 `get_db()` 统一管理（简单场景）
      - ✅ 只有复杂场景（多次 commit）才需要显式事务控制

   10. **测试规范（结合现有实践）**

      **测试类型**

     ```
     tests/
     ├── conftest.py                    # 全局 fixtures
     ├── integration/
     │   ├── api/                       # API 端点测试
     │   │   ├── test_skills_api.py
     │   │   ├── test_trees_api.py
     │   │   └── test_blobs_api.py
     │   └── journey/                   # User Journey 测试
     │       ├── test_journey_creation.py
     │       ├── test_journey_deletion.py
     │       └── test_journey_*.py
     └── unit/                          # 单元测试（少量）
     ```

     **1. API 端点测试** - `tests/integration/api/`

     - 按资源分组，使用 class 组织
     - 测试单个端点的功能正确性和边界情况

     ```python
     # tests/integration/api/test_skills_api.py
     import pytest
     from httpx import AsyncClient

     class TestCreateSkill:
         @pytest.mark.asyncio
         async def test_create_skill_success(self, auth_client: AsyncClient):
             response = await auth_client.post(
                 "/api/skills",
                 json={"name": "my-skill", "slug": "my-skill", "description": "A test skill"}
             )
             assert response.status_code == 201
             data = response.json()
             assert data["name"] == "my-skill"
             assert data["slug"] == "my-skill"
             assert "id" in data

         @pytest.mark.asyncio
         async def test_create_skill_duplicate_slug(self, auth_client: AsyncClient):
             # 测试重复 slug 返回 409
             pass

     class TestGetSkill:
         @pytest.mark.asyncio
         async def test_get_skill_success(self, auth_client: AsyncClient, test_skill):
             response = await auth_client.get(f"/api/skills/{test_skill.id}")
             assert response.status_code == 200
     ```

     **2. User Journey 测试** - `tests/integration/journey/`

     - 测试完整业务流程（多个 API 调用组合）
     - 使用专门的 journey_client fixture

     ```python
     # tests/integration/journey/test_journey_creation.py
     class TestJourneyCreation:
         """完整技能创建流程测试"""

         @pytest.mark.asyncio
         async def test_complete_skill_creation_flow(self, journey_client: AsyncClient):
             # 1. 创建技能
             response = await journey_client.post("/api/skills", json={...})
             skill_id = response.json()["id"]

             # 2. 上传文件
             response = await journey_client.post("/api/blobs", files={...})
             blob_id = response.json()["id"]

             # 3. 添加文件到树
             response = await journey_client.post(
                 f"/api/skills/{skill_id}/files",
                 json={"blob_id": blob_id, "path": "README.md"}
             )

             # 4. 验证
             response = await journey_client.get(f"/api/skills/{skill_id}")
             assert len(response.json()["files"]) == 1
     ```

     **不编写**：

     - ❌ 领域对象单元测试（领域逻辑通过 Journey 测试覆盖）
     - ❌ 仓库层集成测试（通过 API 测试间接覆盖）

     **核心 Fixtures**（在 `tests/conftest.py` 维护）：

     ```python
     @pytest_asyncio.fixture
     async def db_session(db_engine) -> AsyncGenerator[AsyncSession, None]:
         """数据库会话"""
         ...

     @pytest_asyncio.fixture
     async def test_user(db_session: AsyncSession) -> User:
         """测试用户"""
         ...

     @pytest_asyncio.fixture
     async def auth_client(test_user) -> AsyncClient:
         """已认证的 HTTP 客户端"""
         ...

     @pytest_asyncio.fixture
     async def test_skill(db_session, test_user) -> Skill:
         """测试技能数据"""
         ...

     @pytest_asyncio.fixture
     async def journey_client(db_session, journey_user) -> AsyncClient:
         """Journey 测试专用客户端（带认证）"""
         ...
     ```

     **运行测试**：

     ```bash
     # 全部测试
     pytest

     # 仅 API 测试
     pytest tests/integration/api/

     # 仅 Journey 测试
     pytest tests/integration/journey/

     # 特定测试
     pytest tests/integration/api/test_skills_api.py::TestCreateSkill::test_create_skill_success

     # 带覆盖率
     pytest --cov=app --cov-report=html
      ```
   11. **代码注释与自解释代码规范**

      **核心原则**：除了 API Doc（OpenAPI 文档字符串），**尽可能避免注释**，通过**代码本身揭示意图**。

      **为什么避免注释？**

      - 注释会过时（代码修改后注释常常忘记更新）
      - 好的代码应该是自解释的
      - 命名应该承担文档的责任

      **❌ 避免的注释**：

      ```python
      # ❌ 错误的注释：解释"what"（做了什么）
      # 创建 skill
      def create_skill(request: CreateSkillReq) -> CreateSkillResp:
          ...

      # ❌ 错误的注释：解释显而易见的代码
      # 初始化计数器
      count = 0

      # ❌ 错误的注释：解释变量类型（应该通过命名体现）
      # 用户 ID
      user_id: UUID

      # ❌ 错误的注释：解释业务逻辑（应该在领域方法名中体现）
      # 检查 skill 是否存在
      if await repo.get_by_slug(slug):
          raise SkillAlreadyExistsError(slug)
      ```

      **✅ 通过代码揭示意图**：

      ```python
      # ✅ 好的命名揭示意图
      @router.post("/skills")
      async def create_skill(request: CreateSkillReq) -> CreateSkillResp:
          """API Doc 是必要的（用于生成 OpenAPI 文档）"""
          if await repo.exists_by_slug(request.slug):
              raise SkillAlreadyExistsError(request.slug)

      # ✅ 通过方法名而非注释解释
      class Skill:
          def publish(self) -> None:
              """公开 skill（这是 API Doc，有必要）"""
              self._is_public = True
              self._published_at = datetime.utcnow()

          def is_published(self) -> bool:
              """检查是否已公开（API Doc）"""
              return self._is_public

      # ✅ 通过变量命名揭示意图
      already_exists = await repo.exists_by_slug(new_slug)
      if already_exists:
          raise SkillAlreadyExistsError(new_slug)

      # ✅ 通过提取方法揭示意图
      def calculate_discounted_price(self, discount_rate: float) -> Money:
          if self._is_eligible_for_discount(discount_rate):
              return self._apply_discount(discount_rate)
          return self._original_price

      def _is_eligible_for_discount(self, rate: float) -> bool:
          return rate > 0 and self._original_price.amount > 0
      ```

      **何时允许注释**：

      ```python
      # ✅ 允许：API Doc（用于生成 OpenAPI/Swagger 文档）
      @router.post("/skills")
      async def create_skill(request: CreateSkillReq) -> CreateSkillResp:
          """创建新的 Skill

          Args:
              request: Skill 创建请求，包含名称和描述

          Returns:
              创建成功的 Skill 信息

          Raises:
              SkillAlreadyExistsError: 当 slug 已存在时
          """
          ...

      # ✅ 允许：解释"why"（为什么这样做，而非做什么）
      # 使用悲观锁防止并发创建相同 slug 的 skill
      async with transaction_lock():
          skill = await repo.get_by_slug(slug, for_update=True)

      # ✅ 允许：标记 TODO/FIXME（但应该尽快解决）
      # TODO: 添加邮件通知功能
      await notification_service.send_email(user.email, "Skill created")

      # ✅ 允许：解释复杂的算法或业务规则
      # 根据 Git 的 three-way merge 算法解决冲突
      def resolve_conflict(base: str, ours: str, theirs: str) -> str:
          ...

      # ✅ 允许：空实现/占位符的说明
      def migrate_v1_to_v2(self) -> None:
          """v1 到 v2 的数据迁移（将在下一个版本实现）"""
          pass
      ```

      **命名规范（代码自解释的关键）**：

      | 场景     | ❌ 差的命名        | ✅ 好的命名                        |
      | -------- | ------------------ | ---------------------------------- |
      | 布尔判断 | `check_user()`   | `is_authenticated()`             |
      | 获取数据 | `get_data()`     | `fetch_active_skills()`          |
      | 验证方法 | `validate()`     | `is_valid_email_format()`        |
      | 转换方法 | `convert()`      | `to_domain_model()`              |
      | 列表过滤 | `filter()`       | `get_public_skills()`            |
      | 临时变量 | `temp`, `data` | `pending_skills`, `user_input` |

      **代码审查检查项**：


      - [ ] 删除所有解释"what"的注释
      - [ ] 检查命名是否能揭示意图
      - [ ] 提取复杂逻辑到命名良好的方法
       - [ ] 保留 API Doc（用于 OpenAPI）
       - [ ] 保留解释"why"的注释（如果必要）
   12. **命名与导入规范**（速查表）

       - 文件命名速查表
       - 类命名速查表
       - 依赖方向规则
   13. **快速检查清单**（Checklist）

       - 创建新功能时的检查步骤（5-7项）

  **文档定位说明**：

  - `backend/project_conventions.md` 是**速查手册**，不是教程
  - 详细解释和"为什么"放到 `docs/architecture/` 目录
  - 控制文件长度在 400-600 行

  **Must NOT do**:

  - ❌ 不要包含详细的理论解释（如"为什么要有 DDD"）
  - ❌ 不要包含大段的教程式文字
  - ❌ 不要使文件超过 600 行
  - ✅ 必须包含可直接复制的代码模板
  - ✅ 必须包含速查表和检查清单
  - ✅ 必须具体到本项目（不是通用 DDD）
  - ✅ 不要涉及前端规范，只关注后端

  **Recommended Agent Profile**:

  - **Category**: `writing`
  - **Skills**: []
  - Reason: 需要编写精简的技术文档和代码示例

  **Parallelization**:

  - **Can Run In Parallel**: NO
  - **Blocks**: Wave 1 及所有后续任务
  - **Blocked By**: None

   **Acceptance Criteria**:

   - [ ] `backend/project_conventions.md` 文件存在且可读
   - [ ] 包含 11 个核心章节（精简版）
  - [ ] 每个章节包含代码示例（可直接复制使用）
  - [ ] 文件长度 400-600 行（精简目标）
  - [ ] 包含快速检查清单

  **QA Scenarios**:

  ```
  Scenario: 规范文件创建完成
    Tool: Bash
    Steps:
      1. ls backend/project_conventions.md
      2. wc -l backend/project_conventions.md  # 检查行数（目标 400-600 行）
      3. grep -n "DDD 分层架构" backend/project_conventions.md
      4. grep -n "代码示例" backend/project_conventions.md
      5. head -100 backend/project_conventions.md
    Expected Result: 文件存在、精简、包含核心章节
    Evidence: .sisyphus/evidence/task-0-1-rules-file.txt
  ```

  **Commit**: YES

  - Message: `docs: add backend project architecture rules (project_conventions.md)`
  - Files: `backend/project_conventions.md`, `docs/architecture/` (详细文档目录)
- [x] 0.2 更新 AGENT.md 引用项目规范

  **What to do**:

  - 读取现有的 `AGENT.md` 文件（位于项目根目录）
  - 在文件的 `## 重要规则` 章节后面添加新的章节：

    ```markdown
    ## ⚠️ 后端开发规范（必读）

    当执行后端开发任务时，**必须**参考 [`backend/project_conventions.md`](../backend/project_conventions.md) 中的规范。

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
    # ✅ 正确 - 领域对象有行为
    skill.rename("New Name")  # 内部更新 slug 和版本

    # ❌ 错误 - 贫血模型
    skill.name = "New Name"  # 直接修改，无业务逻辑
    ```

    4. **值对象** - 封装验证逻辑：

       ```python
       slug = Slug("my-skill")  # 自动验证格式
       email = Email("user@example.com")  # 自动验证邮箱格式
       ```
    5. **异常处理** - 使用全局异常处理器：

        ```python
        # ✅ 正确 - 路由层只需抛出领域异常（函数式 Handler）
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

    ```

    ```
  - 在 `## 添加新功能` 章节后面添加详细指南：

    ```markdown
    ### 后端开发详细指南

    详细规范请参考 [`backend/project_conventions.md`](../backend/project_conventions.md)，包括：

    - 值对象设计（Slug, Path, Email）
    - 聚合根设计（Skill, User, Tree）
    - 仓库模式（Repository Pattern）
    - 应用层命令和处理器
    - 异常处理规范
    - 测试规范

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
    ```

  **References**:

  - File: `AGENT.md`（位于项目根目录，现有 217 行）

  **Must NOT do**:

  - 不要删除 AGENT.md 中现有的任何内容
  - 不要修改现有的项目结构说明（保持现有目录描述）
  - 不要删除现有的数据模型表格
  - 新增内容应该作为补充章节添加
  - 不要修改前端相关的说明（如果有）

  **Recommended Agent Profile**:

  - **Category**: `writing`
  - **Skills**: []

  **Parallelization**:

  - **Can Run In Parallel**: NO（与 0.1 串行）
  - **Blocks**: Wave 1 及所有后续任务
  - **Blocked By**: 0.1（需要知道 project_conventions.md 的位置）

  **Acceptance Criteria**:

  - [ ] AGENT.md 包含后端开发规范提示
  - [ ] AGENT.md 包含指向 project_conventions.md 的链接
  - [ ] 提示位于显眼位置（文件顶部或专门的章节）
  - [ ] 保留了 AGENT.md 的原有内容

  **QA Scenarios**:

  ```
  Scenario: AGENT.md 正确更新
    Tool: Bash
    Steps:
      1. grep -n "backend/project_conventions.md" AGENT.md
      2. grep -n "DDD" AGENT.md | head -5
      3. grep -n "重要.*后端" AGENT.md
      4. head -50 AGENT.md
    Expected Result: 包含规范引用和链接
    Evidence: .sisyphus/evidence/task-0-2-agent-updated.txt
  ```

  **Commit**: YES (group with 0.1)

  - Message: `docs: update AGENT.md to reference backend project rules`
  - Files: `AGENT.md`

### Wave 1: 基础设施搭建

- [x] 1.1 创建 DDD 分层目录结构

  **What to do**:

  - 创建 `backend/app/domain/` 目录及子目录
  - 创建 `backend/app/application/` 目录及子目录
  - 创建 `backend/app/infra/` 目录及子目录
  - 创建 `backend/app/shared/` 目录

  **Must NOT do**:

  - 不要删除或修改现有代码
  - 不要创建具体实现，只创建目录结构

  **Recommended Agent Profile**:

  - **Category**: `quick`
  - **Skills**: []
  - Reason: 纯目录创建任务，无需特殊技能

  **Parallelization**:

  - **Can Run In Parallel**: YES
  - **Parallel Group**: Wave 1
  - **Blocks**: 所有后续任务
  - **Blocked By**: None

  **Acceptance Criteria**:

  - [ ] `ls backend/app/domain/` 显示 aggregates/, entities/, value_objects/, repositories/, services/, exceptions.py, factories.py
  - [ ] `ls backend/app/application/` 显示 commands/, handlers/
  - [ ] `ls backend/app/api/` 显示 routers/, schemas/, dependencies/, exception_handlers.py
  - [ ] `ls backend/app/infra/` 显示 persistence/, auth/, config/
  - [ ] `ls backend/app/infra/persistence/` 显示 models/, repositories/

  **QA Scenarios**:

  ```
  Scenario: 目录结构正确创建
    Tool: Bash
    Steps:
      1. ls backend/app/domain/aggregates/
      2. ls backend/app/domain/value_objects/
      3. ls backend/app/application/commands/
      4. ls backend/app/infra/persistence/models/
    Expected Result: 所有目录存在且无错误
    Evidence: .sisyphus/evidence/task-1-1-directories-created.txt
  ```

  **Commit**: YES

  - Message: `chore(architecture): create DDD layered directory structure`
  - Files: `backend/app/domain/*`, `backend/app/application/*`, `backend/app/infra/*`, `backend/app/shared/*`
- [x] 1.2 创建基础异常体系

  **What to do**:

  - 创建 `backend/app/domain/exceptions.py` 领域异常基类
    - 定义 `DomainError` 基类（code, message, category, context）
    - 预定义常用异常子类：
      - `ValidationError(category="VALIDATION")`
      - `ResourceNotFoundError(category="NOT_FOUND")`
      - `ResourceConflictError(category="CONFLICT")`
      - `UnauthorizedError(category="UNAUTHORIZED")`
      - `ForbiddenError(category="FORBIDDEN")`
  - 创建 `backend/app/api/exception_handlers.py` 全局异常处理器
    - 实现 `CATEGORY_STATUS_MAP`（业务分类 → HTTP 状态码映射）
    - 实现 `handle_domain_error` 处理器
    - 实现 `handle_generic_exception` 处理器

  **Must NOT do**:

  - 不要创建 `SharedException` 或 `ApplicationException`（单一基类设计）
  - 不要在领域异常中包含 `status_code`（这是 API 层的职责）
  - 不要创建具体的业务异常（如 `SkillNotFoundError`），那些在每个模块中创建

  **Recommended Agent Profile**:

  - **Category**: `quick`
  - **Skills**: []
  - Reason: 简单类定义任务

  **Parallelization**:

  - **Can Run In Parallel**: YES (与 1.1 并行)
  - **Parallel Group**: Wave 1
  - **Blocks**: 所有后续任务
  - **Blocked By**: None

  **Acceptance Criteria**:

  - [ ] `DomainError` 基类可正确导入
  - [ ] 包含属性：code, message, category（简化版，无 context）
  - [ ] 预定义异常子类可正确导入和使用
  - [ ] 全局异常处理器文件创建（空文件或基础结构）
  - [ ] `CATEGORY_STATUS_MAP` 定义包含所有业务分类

  **QA Scenarios**:

  ```
  Scenario: 异常类可正确导入和使用
    Tool: Bash (python REPL)
    Steps:
      1. cd backend && python -c "from app.domain.exceptions import DomainError; print('OK')"
      2. python -c "from app.domain.exceptions import ValidationError; raise ValidationError('Invalid slug format')"
      3. python -c "from app.domain.exceptions import SkillAlreadyExistsError; e = SkillAlreadyExistsError(); print(e.code, e.category)"
    Expected Result: 
      - DomainError 导入成功
      - ValidationError 可抛出，接受 message 参数
      - SkillAlreadyExistsError 的 code 为 'SKILL_ALREADY_EXISTS'，category 为 'CONFLICT'
    Evidence: .sisyphus/evidence/task-1-2-exceptions.png

  Scenario: 全局异常处理器文件存在
    Tool: Bash
    Steps:
      1. ls backend/app/api/exception_handlers.py
      2. grep -q "CATEGORY_STATUS_MAP" backend/app/api/exception_handlers.py
    Expected Result: 
      - 文件存在
      - 包含 CATEGORY_STATUS_MAP 定义
    Evidence: .sisyphus/evidence/task-1-2-handler.txt
  ```

  **Commit**: YES (group with 1.1)
- [x] 1.3 创建类型定义和常量

  **What to do**:

  - 创建 `backend/app/shared/types.py` 类型别名
  - 定义 `UserId`, `SkillId`, `TreeId`, `BlobId` 等类型别名
  - 创建 `backend/app/shared/constants.py` 常量定义

  **Must NOT do**:

  - 不要创建运行时逻辑，只定义类型和常量

  **Recommended Agent Profile**:

  - **Category**: `quick`
  - **Skills**: []

  **Parallelization**:

  - **Can Run In Parallel**: YES (与 1.1, 1.2 并行)
  - **Parallel Group**: Wave 1
  - **Blocks**: Wave 2
  - **Blocked By**: None

  **Acceptance Criteria**:

  - [ ] 类型别名定义清晰
  - [ ] 可以使用类型检查器验证

  **QA Scenarios**:

  ```
  Scenario: 类型别名可正确使用
    Tool: Bash (python + mypy)
    Steps:
      1. 创建测试文件使用类型别名
      2. 运行 mypy 检查类型
    Expected Result: mypy 无错误
    Evidence: .sisyphus/evidence/task-1-3-types.txt
  ```

  **Commit**: YES (group with 1.1)

### Wave 2: 值对象 (并行)

- [x] 2.1 实现 Slug 值对象

  **What to do**:

  - 创建 `backend/app/domain/value_objects/slug.py`
  - 实现不可变的 Slug 值对象
  - 封装验证逻辑：正则 `^[a-z0-9]+(-[a-z0-9]+)*$`
  - 提供工厂方法 `from_name()` 将名称转换为 slug
  - 实现 `__str__`, `__eq__`, `__hash__`

  **References**:

  - Pattern: 当前 slug 验证在 `backend/app/services/skill_service.py` line 51-55
  - Pattern: 当前 slug 验证在 `backend/app/routers/skills.py` line 42
  - Docs: `docs/architecture/ddd-basics.md` 值对象章节

  **Must NOT do**:

  - 不要在值对象中访问数据库
  - 不要创建可变方法

  **Recommended Agent Profile**:

  - **Category**: `quick`
  - **Skills**: []
  - Reason: 纯领域逻辑，无外部依赖

  **Parallelization**:

  - **Can Run In Parallel**: YES (与 2.2, 2.3 并行)
  - **Parallel Group**: Wave 2
  - **Blocks**: Wave 3-6 (所有需要 slug 的模块)
  - **Blocked By**: Wave 1

  **Acceptance Criteria**:

  - [ ] Slug 创建时自动验证格式
  - [ ] 无效 slug 抛出 ValueError
  - [ ] `from_name("My Skill")` 返回 Slug("my-skill")
  - [ ] 两个相同值的 Slug 相等
  - [ ] 不可变性：无法修改 value 属性

  **QA Scenarios**:

  ```
  Scenario: Slug 值对象正确验证
    Tool: Bash (python)
    Steps:
      1. from app.domain.value_objects.slug import Slug
      2. slug = Slug("my-skill")
      3. str(slug) == "my-skill"
      4. Slug("Invalid Slug!") 应该抛出 ValueError
      5. Slug.from_name("My Skill").value == "my-skill"
    Expected Result: 验证通过，错误情况正确抛出异常
    Evidence: .sisyphus/evidence/task-2-1-slug.py

  Scenario: Slug 不可变性
    Tool: Bash (python)
    Steps:
      1. slug = Slug("test")
      2. 尝试修改 slug.value = "other"
    Expected Result: AttributeError 或类似的不可变错误
    Evidence: .sisyphus/evidence/task-2-1-slug-immutable.txt
  ```

  **Commit**: YES

  - Message: `feat(domain): add Slug value object with validation`
  - Files: `backend/app/domain/value_objects/slug.py`
- [x] 2.2 实现 Path 值对象

  **What to do**:

  - 创建 `backend/app/domain/value_objects/path.py`
  - 实现 Path 值对象封装文件路径
  - 封装验证：防止路径遍历（`..`, `~`）
  - 提供方法：`is_directory()`, `is_file()`, `extension()`, `parent()`
  - 实现规范化：`normalize()` 处理路径分隔符

  **References**:

  - Pattern: 当前 path 验证在 `backend/app/routers/trees.py` line 44-67
  - Pattern: 当前 has_extension 在 `backend/app/routers/trees.py` line 70-82

  **Must NOT do**:

  - 不要进行文件系统 I/O
  - 不要访问数据库

  **Recommended Agent Profile**:

  - **Category**: `quick`
  - **Skills**: []

  **Parallelization**:

  - **Can Run In Parallel**: YES (与 2.1, 2.3 并行)
  - **Parallel Group**: Wave 2
  - **Blocks**: Wave 5 (Tree 模块)
  - **Blocked By**: Wave 1

  **Acceptance Criteria**:

  - [ ] Path("test/file.md").is_file() == True
  - [ ] Path("test/dir/").is_directory() == True
  - [ ] Path("../etc/passwd") 抛出 ValueError（路径遍历）
  - [ ] Path("test/../file.md").normalize() == Path("file.md")

  **QA Scenarios**:

  ```
  Scenario: Path 正确验证和规范化
    Tool: Bash (python)
    Steps:
      1. from app.domain.value_objects.path import Path
      2. Path("SKILL.md").extension() == ".md"
      3. Path("templates/code.py").parent() == Path("templates")
      4. Path("../secret") 抛出 ValueError
    Expected Result: 所有验证和转换正确
    Evidence: .sisyphus/evidence/task-2-2-path.py
  ```

  **Commit**: YES

  - Message: `feat(domain): add Path value object with traversal protection`
  - Files: `backend/app/domain/value_objects/path.py`
- [x] 2.3 实现 Email 值对象

  **What to do**:

  - 创建 `backend/app/domain/value_objects/email.py`
  - 实现 Email 值对象
  - 封装验证：使用标准 email 验证规则
  - 提供方法：`domain()`, `is_valid_format()`

  **References**:

  - Pattern: User 模型中的 email 字段在 `backend/app/models/user.py`

  **Must NOT do**:

  - 不要发送验证邮件
  - 不要检查邮箱是否已注册（这是应用层逻辑）

  **Recommended Agent Profile**:

  - **Category**: `quick`
  - **Skills**: []

  **Parallelization**:

  - **Can Run In Parallel**: YES (与 2.1, 2.2 并行)
  - **Parallel Group**: Wave 2
  - **Blocks**: Wave 4 (User 模块)
  - **Blocked By**: Wave 1

  **Acceptance Criteria**:

  - [ ] Email("user@example.com") 创建成功
  - [ ] Email("invalid") 抛出 ValueError
  - [ ] Email("USER@EXAMPLE.COM").value == "user@example.com"（规范化）

  **QA Scenarios**:

  ```
  Scenario: Email 正确验证和规范化
    Tool: Bash (python)
    Steps:
      1. from app.domain.value_objects.email import Email
      2. email = Email("Test@Example.COM")
      3. email.value == "test@example.com"
      4. email.domain() == "example.com"
      5. Email("not-an-email") 抛出 ValueError
    Expected Result: 验证和规范化正确
    Evidence: .sisyphus/evidence/task-2-3-email.py
  ```

  **Commit**: YES

  - Message: `feat(domain): add Email value object with validation`
  - Files: `backend/app/domain/value_objects/email.py`

### Wave 3: Skill 领域模型重构

- [x] 3.1 定义 Skill 仓库接口

  **What to do**:

  - 创建 `backend/app/domain/repositories/skill_repository.py`
  - 定义抽象类 `SkillRepository`
  - 方法：`get_by_id()`, `get_by_slug()`, `find_by_user()`, `save()`, `delete()`
  - 接口只依赖领域对象，不依赖 SQLAlchemy

  **References**:

  - Pattern: 当前 CRUD 模式在 `backend/app/crud/skill.py`
  - Pattern: 当前 base CRUD 在 `backend/app/crud/base.py`

  **Must NOT do**:

  - 不要实现具体逻辑，只定义接口
  - 不要导入 SQLAlchemy

  **Recommended Agent Profile**:

  - **Category**: `quick`
  - **Skills**: []
  - Reason: 纯接口定义

  **Parallelization**:

  - **Can Run In Parallel**: NO
  - **Blocks**: 3.3 (实现), Wave 7 (应用层)
  - **Blocked By**: Wave 2

  **Acceptance Criteria**:

  - [ ] 接口继承自 ABC
  - [ ] 所有方法使用 @abstractmethod 装饰
  - [ ] 参数和返回类型使用领域对象
  - [ ] 无 SQLAlchemy 依赖

  **QA Scenarios**:

  ```
  Scenario: 仓库接口正确定义
    Tool: Bash (python)
    Steps:
      1. from app.domain.repositories.skill_repository import SkillRepository
      2. 检查抽象方法存在
      3. 尝试实例化应抛出 TypeError
    Expected Result: 接口正确定义，无法直接实例化
    Evidence: .sisyphus/evidence/task-3-1-repository-interface.py
  ```

  **Commit**: YES

  - Message: `feat(domain): add SkillRepository interface`
  - Files: `backend/app/domain/repositories/skill_repository.py`
- [x] 3.2 实现 Skill 聚合根

  **What to do**:

  - 创建 `backend/app/domain/aggregates/skill.py`
  - 实现 `Skill` 类作为聚合根
  - 属性：`id`, `user_id`, `name`, `slug` (Slug VO), `description`, `tree_id`, `version`, `is_public`
  - 领域行为方法：
    - `rename(new_name: str)` - 重命名并更新 slug
    - `update_description(desc: str)` - 更新描述
    - `attach_tree(tree_id: UUID)` - 关联 tree
    - `publish()` - 公开 skill
    - `unpublish()` - 取消公开
    - `increment_version()` - 递增版本号
  - 使用工厂方法 `create()` 作为构造入口
  - 所有业务规则在方法内部验证

  **References**:

  - Pattern: 当前 Skill 模型在 `backend/app/models/skill.py` (贫血模型)
  - Pattern: 当前业务逻辑在 `backend/app/services/skill_service.py`
  - Docs: `docs/architecture/ddd-basics.md` 聚合根章节

  **Must NOT do**:

  - 不要直接暴露内部属性供外部修改
  - 不要依赖 SQLAlchemy
  - 不要访问数据库

  **Recommended Agent Profile**:

  - **Category**: `unspecified-high`
  - **Skills**: []
  - Reason: 需要设计良好的领域模型，包含业务规则验证

  **Parallelization**:

  - **Can Run In Parallel**: NO
  - **Blocks**: 3.3, 3.4
  - **Blocked By**: 3.1, Wave 2

  **Acceptance Criteria**:

  - [ ] `Skill.create(name="My Skill", ...)` 自动创建 slug
  - [ ] `skill.rename("New Name")` 同时更新 slug
  - [ ] `skill.publish()` 设置 is_public = True
  - [ ] 无法直接修改 `skill.slug = xxx` (使用属性或封装)
  - [ ] 版本号在修改时自动递增
  - [ ] 所有变更都通过领域方法完成

  **QA Scenarios**:

  ```
  Scenario: Skill 聚合根业务行为
    Tool: Bash (python)
    Steps:
      1. from app.domain.aggregates.skill import Skill
      2. from app.domain.value_objects.slug import Slug
      3. skill = Skill.create(user_id=uuid, name="My Skill", description="Desc")
      4. assert str(skill.slug) == "my-skill"
      5. old_version = skill.version
      6. skill.rename("Updated Skill")
      7. assert str(skill.slug) == "updated-skill"
      8. assert skill.version == old_version + 1
      9. skill.publish()
      10. assert skill.is_public == True
    Expected Result: 所有领域行为正确执行
    Evidence: .sisyphus/evidence/task-3-2-skill-aggregate.py
  ```

  **Commit**: YES

  - Message: `feat(domain): add Skill aggregate root with domain behaviors`
  - Files: `backend/app/domain/aggregates/skill.py`
- [x] 3.3 实现 SQLAlchemy Skill 仓库

  **What to do**:

  - 创建 `backend/app/infra/persistence/models/skill_model.py` - ORM 模型，包含：
    - SQLAlchemy 模型定义（表结构）
    - `to_domain()` 方法 - 将 ORM 模型转换为领域对象
    - `from_domain(domain_skill)` 类方法 - 从领域对象创建 ORM 模型
  - 创建 `backend/app/infra/persistence/repositories/sql_skill_repository.py` - 仓库实现
  - 实现 `SkillRepository` 接口的所有方法
  - 处理领域对象和 ORM 模型之间的转换（通过模型中的方法）

  **映射逻辑放在 ORM 模型中的示例**：

  ```python
  # backend/app/infra/persistence/models/skill_model.py
  class SkillModel(Base):
      __tablename__ = "skills"

      id = Column(UUID, primary_key=True)
      name = Column(String(255))
      slug = Column(String(255))
      # ... 其他字段

      def to_domain(self) -> Skill:
          """转换为领域对象"""
          return Skill(
              id=self.id,
              name=self.name,
              slug=Slug(self.slug),  # 值对象转换
              # ...
          )

      @classmethod
      def from_domain(cls, skill: Skill) -> "SkillModel":
          """从领域对象创建 ORM 模型"""
          return cls(
              id=skill.id,
              name=skill.name,
              slug=str(skill.slug),  # 值对象转字符串
              # ...
          )
  ```

  **References**:

  - Pattern: 当前 ORM 模型在 `backend/app/models/skill.py`
  - Pattern: 当前 CRUD 在 `backend/app/crud/skill.py`

  **Must NOT do**:

  - 不要在仓库中实现业务逻辑
  - 不要让仓库直接暴露 ORM 模型
  - 不要在单独的 mapper 文件中处理映射（映射逻辑应在 PO 模型中）

  **Recommended Agent Profile**:

  - **Category**: `unspecified-high`
  - **Skills**: []
  - Reason: 需要处理 ORM 模型和领域模型的转换逻辑

  **Parallelization**:

  - **Can Run In Parallel**: NO
  - **Blocks**: Wave 7 (应用层)
  - **Blocked By**: 3.1, 3.2

  **Acceptance Criteria**:

  - [ ] `await repo.get_by_id(id)` 返回 Skill 领域对象
  - [ ] `await repo.save(skill)` 保存领域对象到数据库
  - [ ] 读写数据一致
  - [ ] 处理 Slug 值对象的序列化/反序列化
  - [ ] ORM 模型包含 `to_domain()` 和 `from_domain()` 方法

  **QA Scenarios**:

  ```
  Scenario: 仓库正确持久化 Skill
    Tool: Bash (python + pytest)
    Steps:
      1. 使用测试数据库
      2. skill = Skill.create(...)
      3. await repo.save(skill)
      4. loaded = await repo.get_by_id(skill.id)
      5. assert loaded.slug == skill.slug
      6. 检查 SkillModel.to_domain() 方法存在
      7. 检查 SkillModel.from_domain() 方法存在
    Expected Result: 保存和加载一致，映射方法存在
    Evidence: .sisyphus/evidence/task-3-3-repository-test.log
  ```

  **Commit**: YES

  - Message: `feat(infra): implement SQLSkillRepository with domain mapping`
  - Files: `backend/app/infra/persistence/models/skill_model.py`, `backend/app/infra/persistence/repositories/sql_skill_repository.py`

### Wave 4-6: 其他领域模型

- [ ] 4.1-4.3 User 领域模型 (并行，参考 Skill 模式)

  - 定义 UserRepository 接口
  - 实现 User 聚合根（含认证）
  - 实现 SqlUserRepository
- [ ] 5.1-5.3 Tree 领域模型 (并行，参考 Skill 模式)

  - 定义 TreeRepository 接口
  - 实现 Tree 聚合根（含文件操作）
  - 实现 SqlTreeRepository
- [ ] 6.1-6.3 Blob & Project 领域模型 (并行)

  - Blob 值对象
  - Project 聚合根
  - 对应仓库实现

### Wave 7: 应用层

- [ ] 7.1 创建 DTO 和命令对象

  - **Request DTO**（在 `app/api/schemas/`）：
    - CreateSkillReq, CreateSkillResp
    - UpdateSkillReq, UpdateSkillResp
    - GetSkillResp
    - ListSkillsItemResp
    - RegisterUserReq, LoginReq, etc.
  - **说明**：Command 对象直接使用 Req DTO（如 CreateSkillReq）
- [ ] 7.2 实现命令处理器（函数式风格）

  - `create_skill_handler.py`: `handle_create_skill()`
  - `update_skill_handler.py`: `handle_update_skill()`
  - 编排领域对象完成用例
  - 使用仓库保存
  - **风格**：应用层无状态，使用函数而非类
- [ ] 7.3 创建 Repository 依赖注入

  **文件**: `app/api/dependencies/repositories.py`

  ```python
  from fastapi import Depends
  from sqlalchemy.ext.asyncio import AsyncSession

  from app.db.session import get_db
  from app.domain.repositories.skill_repository import SkillRepository
  from app.domain.repositories.user_repository import UserRepository
  from app.infra.persistence.repositories.sql_skill_repository import SqlSkillRepository
  from app.infra.persistence.repositories.sql_user_repository import SqlUserRepository


  async def get_skill_repo(
      db: AsyncSession = Depends(get_db)
  ) -> SkillRepository:
      """注入 SkillRepository"""
      return SqlSkillRepository(db)


  async def get_user_repo(
      db: AsyncSession = Depends(get_db)
  ) -> UserRepository:
      """注入 UserRepository"""
      return SqlUserRepository(db)
  ```

  **在路由中使用**:

  ```python
  from app.api.dependencies.repositories import get_skill_repo

  @router.post("/skills")
  async def create_skill(
      request: CreateSkillReq,
      skill_repo: SkillRepository = Depends(get_skill_repo),  # 自动注入
      current_user: User = Depends(get_current_user),
  ) -> CreateSkillResp:
      # 直接调用 Application 层函数，无需手动组装 Repository
      skill = await handle_create_skill(
          user_id=current_user.id,
          name=request.name,
          skill_repo=skill_repo,  # 传入已注入的 Repository
      )
      return CreateSkillResp.from_domain(skill)
  ```

  **依赖注入链**:

  ```
  API Router
    ├─▶ Depends(get_skill_repo)
    │     └─▶ Depends(get_db) → AsyncSession
    │     └─▶ SqlSkillRepository(db)
    └─▶ handle_create_skill(..., skill_repo)
            └─▶ 纯函数，使用 Repository 接口
  ```

### Wave 8: API 层适配与旧代码清理

**策略说明**：由于项目处于本地开发阶段，采用**激进式清理策略**——确认新代码工作正常后直接删除旧代码，无需渐进式废弃。

- [ ] 8.1 重构技能管理路由

  - 使用新 handler
  - 移除旧 services 依赖
- [ ] 8.2 重构用户认证路由
- [ ] 8.3 重构 Tree 管理路由
- [ ] 8.4 重构其他路由
- [ ] 8.5 删除旧代码（激进式清理）

  - 删除 services/
  - 删除 crud/
  - 删除 models/
  - ⚠️ **注意**：此操作不可逆，确保已通过所有测试后再执行

### Wave FINAL: 文档

- [ ] F.1 创建 DDD 培训文档 (docs/architecture/)
- [ ] F.2 创建架构决策记录 (docs/adr/)
- [ ] F.3 更新 API 文档和 README

---

## Final Verification Wave

> **⚠️ 重要：每 Wave 执行后的暂停点**
>
> 完成当前 Wave 的 Final Verification 后，**必须暂停执行**，等待用户验收确认。

### 每个 Wave 结束后的标准流程：

1. **自动执行** Final Verification Wave（4 个审查代理并行）：

   - [ ] FV1. 计划合规审计 - 检查所有 Must Have 是否实现
   - [ ] FV2. 代码质量审查 - ruff, pytest
   - [ ] FV3. 端到端 QA - 所有 API 正常工作
   - [ ] FV4. 范围合规检查 - 验证 DDD 原则正确应用
2. **生成验收报告**：

   - 显示当前 Wave 完成的所有任务
   - 列出所有变更的文件
   - 展示测试通过率
   - 标记任何警告或需要注意的问题
3. **暂停执行并等待用户**：

   ```
   🎉 Wave X 执行完成！

   【完成情况】
   - 完成任务: N/N
   - 代码质量: PASS/FAIL
   - 测试通过率: X%

   【主要变更】
   - 新增文件: ...
   - 修改文件: ...

   【验收建议】
   - 请测试 API: ...
   - 请检查文件: ...

   💡 请输入"继续"或"下一步"以进入 Wave X+1
   💡 如有问题，请描述具体问题，我将修复后再继续
   ```
4. **等待用户指令**：

   - ✅ **"继续" / "下一步"** → 进入下一个 Wave
   - ✅ **具体问题描述** → 修复问题 → 重新验收 → 继续
   - ✅ **"查看详情"** → 显示详细报告 → 等待进一步指令

---

## Commit Strategy

| After Task | Commit Message                                                   |
| ---------- | ---------------------------------------------------------------- |
| Wave 0     | `docs: add backend project rules and update AGENT.md`          |
| Wave 1     | `chore(architecture): create DDD layered directory structure`  |
| Wave 2     | `feat(domain): add value objects (Slug, Path, Email)`          |
| Wave 3     | `feat(domain): implement Skill aggregate and repository`       |
| Wave 4-6   | `feat(domain): implement User, Tree, Blob, Project aggregates` |
| Wave 7     | `feat(application): add command objects and handlers`          |
| Wave 8     | `refactor(api): adapt routers to new DDD architecture`         |
| Wave FINAL | `docs: add DDD architecture documentation`                     |

---

## Success Criteria

### 验证命令

```bash
# 1. 代码质量
cd backend && ruff check . && ruff format --check .

# 2. 测试
pytest tests/ -v

# 3. 应用启动
python -c "from app.main import app; print('OK')"

# 4. 架构验证
ls app/domain/aggregates/
ls app/domain/value_objects/
ls app/application/commands/
ls app/infra/persistence/

# 5. 端到端测试
# 启动应用后测试所有 API
```

### 最终检查清单

#### Wave 0 前置任务检查

- [ ] `backend/project_conventions.md` 已创建（≥500 行）
- [ ] `AGENT.md` 已更新，包含后端开发规范提示
- [ ] `AGENT.md` 包含指向 `backend/project_conventions.md` 的链接
- [ ] 规范文档包含所有 14 个章节的详细说明

#### 重构完成检查

- [ ] 所有 Must Have 已实现
- [ ] 所有 Must NOT Have 已避免
- [ ] 旧代码已清理 (services/, crud/, models/)
- [ ] 所有测试通过
- [ ] ORM 模型（PO）包含 `to_domain()` 和 `from_domain()` 方法
- [ ] 文档完整 (docs/architecture/, docs/adr/)
- [ ] 代码质量通过 (ruff, pytest)

---

## 总结

### 预期收益

1. **业务逻辑内聚**: 修改业务规则只需改一处
2. **更好的测试性**: 领域层无外部依赖，可独立测试
3. **代码即文档**: 结构直接反映业务概念
4. **可维护性**: 清晰的边界，易于理解

### 关键设计决策

1. **简化版 DDD**: 无领域事件、CQRS，聚焦充血模型
2. **渐进式重构**: 逐个模块迁移，使用适配器过渡
3. **仓库模式**: 接口在领域层，实现在基础设施层
4. **值对象**: 封装验证逻辑（Slug, Path, Email）
5. **事务管理**: 应用层（Handler）通过 Unit of Work 管理事务边界
6. **应用层函数式风格**: 无状态，使用函数而非类（`handle_create_skill()`）
7. **Repository 依赖注入**: API 层使用 FastAPI Depends 注入，`app/api/dependencies/repositories.py`
8. **激进式清理**: Wave 8 直接删除旧代码（适合本地开发阶段）

### 学习路径

1. 阅读 docs/architecture/ddd-basics.md
2. 理解值对象和聚合根概念
3. 学习分层架构依赖规则
4. 实践重构指南
