# DDD 分层架构项目规范

本文档为 Agent Skills Manager 后端项目的 DDD 开发速查手册，涵盖分层架构、值对象、聚合根、仓库模式等核心规范。

详细教程见: [backend/docs/architecture/ddd-guide.md](./docs/architecture/ddd-guide.md)

---

## 第一章 项目概述

### 1.1 技术栈

| 组件     | 版本要求         |
| -------- | ---------------- |
| Web 框架 | FastAPI 0.129.0+ |
| ORM      | SQLAlchemy 2.0+  |
| 数据库   | PostgreSQL 16+   |
| Python   | 3.10+            |

### 1.2 四层架构

```
┌─────────────────────────────────────────────┐
│                  API 层                       │
│         (routers, dependencies)             │
│              ↓ 依赖                           │
├─────────────────────────────────────────────┤
│                应用层                         │
│           (handlers, commands)               │
│              ↓ 依赖                           │
├─────────────────────────────────────────────┤
│                 领域层                        │
│      (entities, value_objects, repositories) │
│              ↑ 依赖                            │
├─────────────────────────────────────────────┤
│                 基础设施层                    │
│        (persistence, external_services)     │
└─────────────────────────────────────────────┘
```

---

## 第二章 DDD 分层架构

### 2.1 目录结构

```
backend/app/
├── api/                      # API 层
│   ├── dependencies/         # 依赖注入
│   └── routers/              # 路由
├── application/              # 应用层
│   └── handlers/             # Handler 函数
├── domain/                   # 领域层（核心）
│   ├── entities/             # 实体与聚合根
│   ├── value_objects/        # 值对象
│   ├── repositories/         # 仓库接口
│   └── exceptions.py         # 领域异常
└── infra/                    # 基础设施层
    └── persistence/
        ├── models/           # ORM 模型
        └── repositories/     # 仓库实现
```

### 2.2 禁止事项清单

| 禁止项                       | 说明                     |
| ---------------------------- | ------------------------ |
| 禁止 domain/ 导入 SQLAlchemy | 领域层与 ORM 解耦        |
| 禁止 domain/ 导入 FastAPI    | 领域层与 Web 框架解耦    |
| 禁止贫血模型                 | 实体必须封装业务行为     |
| 禁止路由层写业务逻辑         | 路由只负责请求解析       |
| 禁止路由中手动捕获异常       | 使用全局异常处理器       |
| 禁止应用层直接操作数据库     | 必须通过 Repository 接口 |

### 2.3 Migration 脚本命名规范

Migration 文件命名格式：

```
YYYYMMDDHHMMSS__description.py
```

**格式说明：**

- `YYYYMMDDHHMMSS`: 时间戳（UTC），精确到秒
- `__`: 双下划线分隔符
- `description`: 描述性名称，使用小写字母和下划线

**示例：**

- `20260214081010__create_blobs.py`
- `20260214081015__create_trees.py`

**生成命令：**

```bash
alembic revision --autogenerate -m "create_blobs"
```

---

## 第三章 值对象

### 3.1 设计原则

1. **构造时验证，失败即抛异常**
2. **不可变，无 setter**（使用 `frozen=True` dataclass）
3. **基于值相等，非引用相等**（实现 `__eq__` 和 `__hash__`）

### 3.2 Slug 值对象示例

```python
from dataclasses import dataclass
import re

@dataclass(frozen=True)
class Slug:
    value: str
  
    _VALID_PATTERN = re.compile(r'^[a-z0-9]+(?:-[a-z0-9]+)*$')
    _MAX_LENGTH = 100
  
    def __post_init__(self):
        object.__setattr__(self, 'value', self._validate(self.value))
  
    @classmethod
    def _validate(cls, value):
        if not value:
            raise ValueError("Slug cannot be empty")
        if len(value) > cls._MAX_LENGTH:
            raise ValueError(f"Slug cannot exceed {cls._MAX_LENGTH} characters")
        return value.lower()
```

完整模板: [docs/templates/value_object_slug.py](./docs/templates/value_object_slug.py)

---

## 第四章 聚合根

### 4.1 充血模型原则

1. **封装业务规则** - 业务逻辑封装在领域模型中
2. **通过方法暴露行为** - 状态修改必须通过公开方法
3. **保持数据一致性** - 聚合根负责维护聚合内部的一致性

### 4.2 Skill 聚合根示例

```python
from dataclasses import dataclass
import uuid
from datetime import datetime

@dataclass
class Skill:
    id: uuid.UUID
    user_id: uuid.UUID
    name: str
    version: int
    created_at: datetime
    updated_at: datetime
  
    @classmethod
    def create(cls, user_id, name):
        now = datetime.utcnow()
        return cls(
            id=uuid.uuid4(),
            user_id=user_id,
            name=name.strip(),
            version=1,
            created_at=now,
            updated_at=now,
        )
  
    def update(self, name):
        self.name = name.strip()
        self.version += 1
        self.updated_at = datetime.utcnow()
```

完整模板: [docs/templates/aggregate_skill.py](./docs/templates/aggregate_skill.py)

---

## 第五章 仓库模式

### 5.1 接口定义（领域层）

```python
from abc import ABC, abstractmethod
import uuid

class SkillRepository(ABC):
    @abstractmethod
    async def get_by_id(self, skill_id: uuid.UUID): pass
  
    @abstractmethod
    async def save(self, skill): pass
```

### 5.2 ORM 映射方法

```python
# _to_domain: ORM 模型 -> 领域对象
def _to_domain(self, model):
    return Skill(
        id=model.id,
        name=model.name,
        version=model.version,
    )

# _to_model: 领域对象 -> ORM 模型
def _to_model(self, skill):
    return SkillModel(
        id=skill.id,
        name=skill.name,
        version=skill.version,
    )
```

完整模板: [docs/templates/repository_skill.py](./docs/templates/repository_skill.py)

---

## 第六章 应用层

### 6.1 Repository 依赖注入

```python
from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.session import get_db
from app.domain.repositories.skill_repository import SkillRepository
from app.infra.persistence.repositories.sql_skill_repository import SqlSkillRepository

async def get_skill_repo(db: AsyncSession = Depends(get_db)) -> SkillRepository:
    return SqlSkillRepository(db)
```

### 6.2 Handler 函数示例

```python
async def handle_create_skill(
    user_id: uuid.UUID,
    name: str,
    skill_repo: SkillRepository,
):
    # 构造值对象
    slug = Slug.from_name(name)
  
    # 领域验证
    existing = await skill_repo.get_by_slug(slug, user_id)
    if existing:
        raise SkillAlreadyExistsError()
  
    # 创建聚合根并持久化
    skill = Skill.create(user_id=user_id, name=name)
    await skill_repo.save(skill)
    return skill
```

完整模板: [docs/templates/handler_create_skill.py](./docs/templates/handler_create_skill.py)

### 6.3 核心原则

- **无状态** - Handler 函数无共享状态
- **模块+函数** - 不使用类，每个用例一个 Handler 函数
- **显式依赖** - 所有依赖通过参数传入

---

## 第七章 DTO 规范

### 7.1 命名规则

| 场景     | 命名格式                    | 示例                   |
| -------- | --------------------------- | ---------------------- |
| 创建请求 | `{Action}{Resource}Req`   | `CreateSkillReq`     |
| 创建响应 | `{Action}{Resource}Resp`  | `CreateSkillResp`    |
| 列表项   | `List{Resources}ItemResp` | `ListSkillsItemResp` |

### 7.2 极简示例

```python
from pydantic import BaseModel, Field

class CreateSkillReq(BaseModel):
    name: str = Field(..., min_length=1, max_length=200)
    description: str | None = Field(None, max_length=2000)
```

完整模板: [docs/templates/dto_create_skill.py](./docs/templates/dto_create_skill.py)

---

## 第八章 异常处理

### 8.1 DomainError 基类

```python
class DomainError(Exception):
    code: str = "DOMAIN_ERROR"
    message: str = "Domain error occurred"
    category: str = "BUSINESS"
  
    def __init__(self, message: str | None = None):
        self.message = message or self.message
        super().__init__(self.message)
```

### 8.2 CATEGORY_STATUS_MAP

```python
CATEGORY_STATUS_MAP = {
    "NOT_FOUND": 404,
    "CONFLICT": 409,
    "VALIDATION": 422,
    "UNAUTHORIZED": 401,
    "FORBIDDEN": 403,
    "BUSINESS": 400,
}
```

### 8.3 Code 命名规范

采用 `{类别}_{资源}_{操作}_{具体错误}` 格式:

| 场景          | Code                               |
| ------------- | ---------------------------------- |
| 创建冲突      | `DOMAIN_SKILL_CREATE_CONFLICT`   |
| 更新不存在    | `DOMAIN_SKILL_UPDATE_NOT_FOUND`  |
| Slug 格式错误 | `VALIDATION_SLUG_INVALID_FORMAT` |

---

## 第九章 事务管理

### 9.1 核心原则

**使用 `get_db()` 管理事务**。一个请求 = 一个事务。

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

### 9.2 Repository 实现

Repository 只负责数据操作，不控制事务。

```python
class SqlSkillRepository(SkillRepository):
    def __init__(self, db: AsyncSession):  # 由 get_db 注入
        self._db = db
  
    async def save(self, skill: Skill) -> None:
        # 只 add，不 commit（由 get_db 自动处理）
        self._db.add(SkillModel.from_domain(skill))
```

### 9.3 在 Handler 中使用

```python
async def handle_create_skill(
    user_id: UUID,
    name: str,
    skill_repo: SkillRepository,  # 事务由 get_db 管理
) -> Skill:
    slug = Slug.from_name(name)
  
    # 检查重复
    if await skill_repo.get_by_slug(slug):
        raise SkillAlreadyExistsError()
  
    # 创建并保存
    skill = Skill.create(user_id, name)
    await skill_repo.save(skill)
    return skill  # 请求结束时自动 commit
```

---

## 第十章 测试规范

### 10.1 目录结构

```
tests/
├── conftest.py              # 全局 fixtures
├── factories/               # 测试工厂
├── integration/
│   ├── api/                 # API 端点测试（类风格）
│   └── journey/             # 用户旅程测试
└── unit/                    # 少量单元测试
```

### 10.2 测试类型

| 类型         | 用途         | 示例                               |
| ------------ | ------------ | ---------------------------------- |
| API 测试     | 验证端点行为 | `test_create_skill_returns_201`  |
| Journey 测试 | 验证完整流程 | `test_create_and_retrieve_skill` |

### 10.3 核心 Fixtures

- `db_session` - 测试数据库会话
- `test_user` - 测试用户
- `auth_client` - 带认证的 HTTP 客户端

---

## 第十一章 编码规范

### 11.1 注释规范（严格）

**核心原则：除了 API Doc，尽可能避免注释。代码本身揭示意图。**

#### ❌ 禁止的注释

```python
# 错误的：解释"what"（做了什么）
def create_skill(request: CreateSkillReq) -> CreateSkillResp:
    """创建 skill"""  # ❌ 删除！方法名已说明
    ...

# 错误的：解释显而易见的代码
count = 0  # 初始化计数器 ❌ 删除！

# 错误的：类/方法的描述性 docstring（除非是 API Doc）
class User:
    """User 聚合根 - 充血领域模型"""  # ❌ 删除！类名已说明
  
    def verify_email(self) -> None:
        """验证用户邮箱"""  # ❌ 删除！方法名已说明
        ...

# 错误的：行内注释解释变量
user_id: UUID  # 用户 ID ❌ 删除！变量名已说明
```

#### ✅ 允许的注释

```python
# ✅ API Doc（用于生成 OpenAPI/Swagger 文档）
@router.post("/skills")
async def create_skill(request: CreateSkillReq) -> CreateSkillResp:
    """创建新的 Skill
  
    Args:
        request: Skill 创建请求
      
    Returns:
        创建成功的 Skill 信息
      
    Raises:
        SkillAlreadyExistsError: 当 slug 已存在时
    """
    ...

# ✅ 解释"why"（为什么这样做）
# 使用悲观锁防止并发创建相同 slug
async with transaction_lock():
    skill = await repo.get_by_slug(slug, for_update=True)

# ✅ TODO/FIXME（但应尽快解决）
# TODO: 添加邮件通知功能
await notification_service.send_email(user.email, "Skill created")

# ✅ 复杂的算法或业务规则
# 根据 Git 的 three-way merge 算法解决冲突
def resolve_conflict(base: str, ours: str, theirs: str) -> str:
    ...
```

#### 自解释代码的命名规范

| 场景     | ❌ 差的命名      | ✅ 好的命名                 |
| -------- | ---------------- | --------------------------- |
| 布尔判断 | `check_user()` | `is_authenticated()`      |
| 获取数据 | `get_data()`   | `fetch_active_skills()`   |
| 验证方法 | `validate()`   | `is_valid_email_format()` |
| 转换方法 | `convert()`    | `to_domain_model()`       |
| 列表过滤 | `filter()`     | `get_public_skills()`     |

**检查清单：**

- [ ] 删除所有解释"what"的 docstring 和注释
- [ ] 确保类/方法名能揭示意图
- [ ] 仅保留 API Doc、解释"why"的注释、TODO/FIXME

### 11.2 命名速查表

**文件命名:**

| 类型     | 示例                        |
| -------- | --------------------------- |
| 值对象   | `slug.py`                 |
| 聚合根   | `skill.py`                |
| 仓库接口 | `skill_repository.py`     |
| 仓库实现 | `sql_skill_repository.py` |
| ORM 模型 | `skill_model.py`          |
| Handler  | `create_skill_handler.py` |

**类命名:**

| 类型     | 规则              | 示例                   |
| -------- | ----------------- | ---------------------- |
| 值对象   | 大驼峰            | `Slug`               |
| 聚合根   | 大驼峰            | `Skill`              |
| 仓库接口 | 大驼峰+Repository | `SkillRepository`    |
| 仓库实现 | Sql前缀           | `SqlSkillRepository` |
| ORM 模型 | 大驼峰+Model      | `SkillModel`         |
| 异常     | 大驼峰+Error      | `SkillNotFoundError` |

**函数命名:**

| 类型       | 规则               | 示例                    |
| ---------- | ------------------ | ----------------------- |
| Handler    | handle_前缀        | `handle_create_skill` |
| Repository | get_/save_/delete_ | `get_by_id`, `save` |
| 布尔方法   | is_/has_/can_      | `is_authenticated`    |

### 11.3 快速检查清单

- [ ] domain/ 不导入 SQLAlchemy
- [ ] domain/ 不导入 FastAPI
- [ ] 实体包含业务方法，不只是数据
- [ ] 仓库接口在 domain/，实现在 infra/
- [ ] Handler 使用函数式风格
- [ ] Repository 通过 Depends 注入
- [ ] DTO 命名符合规范
- [ ] 异常继承 DomainError
- [ ] 使用全局异常处理器

---

## 第十二章 测试规范

### 12.1 测试方法命名规范

测试方法必须使用以下命名格式：

```
should_xxxx_when_xxxx_given_xxxx
```

- **should_xxx**: 期望的结果（result）
- **when_xxx**: 执行的功能行为（action）
- **given_xxx**: 场景的前提条件（context）

**示例：**

- `should_return_201_when_create_skill_given_valid_input`
- `should_raise_not_found_error_when_get_skill_given_nonexistent_id`
- `should_share_blob_when_import_same_content_given_two_skills`

### 12.2 禁止事项

- 禁止在测试方法中添加描述性docstring（代码应该自解释）
- 禁止旧的 `test_xxx` 命名格式

---

## 附录：模板索引

| 模板       | 路径                                                                            |
| ---------- | ------------------------------------------------------------------------------- |
| 值对象     | [docs/templates/value_object_slug.py](./docs/templates/value_object_slug.py)       |
| 聚合根     | [docs/templates/aggregate_skill.py](./docs/templates/aggregate_skill.py)           |
| Repository | [docs/templates/repository_skill.py](./docs/templates/repository_skill.py)         |
| Handler    | [docs/templates/handler_create_skill.py](./docs/templates/handler_create_skill.py) |
| DTO        | [docs/templates/dto_create_skill.py](./docs/templates/dto_create_skill.py)         |

详细说明见: [docs/architecture/ddd-guide.md](./docs/architecture/ddd-guide.md)
