# DDD 分层架构详细教程

> **注意**: 本文档为详细教程（1656行），涵盖完整的 DDD 架构说明和代码示例。
> 
> 快速查阅请使用精简版: [backend/project_conventions.md](../../project_conventions.md)
> 
> 代码模板请查看: [backend/docs/templates/](../templates/)

本文档为 Agent Skills Manager 后端项目的 DDD 重构开发速查手册，涵盖分层架构、值对象、聚合根、仓库模式、应用层、DTO 设计、异常处理、事务管理、测试规范及代码注释规范。所有代码模板均基于 FastAPI 0.129.0 + SQLAlchemy 2.0 + PostgreSQL 16 技术栈，可直接复制使用。

---

## 第一章 项目概述与核心原则

### 1.1 技术栈

| 组件 | 版本要求 |
|------|----------|
| Web 框架 | FastAPI 0.129.0+ |
| ORM | SQLAlchemy 2.0+ |
| 数据库 | PostgreSQL 16+ |
| 迁移工具 | Alembic |
| 认证 | JWT (access 30min, refresh 7天) |
| 密码加密 | bcrypt |
| Python | 3.10+ |

### 1.2 DDD 核心原则

领域驱动设计的核心原则是将业务逻辑置于领域模型中，通过聚合根封装业务规则，通过值对象表示无标识的概念，通过仓库模式实现持久化。简言之，代码结构应反映业务结构，而非技术分层。

### 1.3 四层架构

本项目采用经典 DDD 四层架构，依赖方向如下：

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

各层职责如下：

| 层级 | 职责 |
|------|------|
| API 层 | 处理 HTTP 请求响应、依赖注入、认证授权 |
| 应用层 | 编排领域逻辑、协调多个聚合、事务边界 |
| 领域层 | 承载核心业务逻辑、领域模型、业务规则 |
| 基础设施层 | 数据库持久化、外部 API 调用、消息队列 |

---

## 第二章 DDD 分层架构规范

### 2.1 目录结构速查表

重构后的目标目录结构如下：

```
backend/src/
├── api/                      # API 层
│   ├── __init__.py
│   ├── dependencies/         # FastAPI 依赖注入
│   │   └── repositories.py   # Repository 注入
│   └── routers/              # 路由处理
│       └── skills.py
├── application/              # 应用层
│   ├── __init__.py
│   └── handlers/             # Handler 函数
│       ├── __init__.py
│       └── create_skill_handler.py
├── domain/                   # 领域层（核心）
│   ├── __init__.py
│   ├── entities/             # 实体与聚合根
│   │   ├── __init__.py
│   │   └── skill.py
│   ├── value_objects/        # 值对象
│   │   ├── __init__.py
│   │   └── slug.py
│   ├── repositories/        # 仓库接口（抽象）
│   │   ├── __init__.py
│   │   └── skill_repository.py
│   ├── exceptions.py        # 领域异常
│   └── services/            # 领域服务（可选）
├── infra/                    # 基础设施层
│   ├── __init__.py
│   └── persistence/
│       ├── __init__.py
│       ├── models/           # ORM 模型
│       │   ├── __init__.py
│       │   └── skill_model.py
│       └── repositories/     # 仓库实现
│           ├── __init__.py
│           └── sql_skill_repository.py
├── core/                     # 核心配置
│   ├── __init__.py
│   ├── config.py
│   └── auth.py
├── db/                       # 数据库会话
│   ├── __init__.py
│   └── session.py
└── main.py                   # FastAPI 入口
```

### 2.2 依赖方向规则

API 层依赖应用层，应用层依赖领域层，领域层不依赖任何外部层。基础设施层实现领域层定义的接口，但领域层不知道基础设施的存在。这是依赖倒置原则的核心应用。

### 2.3 禁止事项清单

以下行为严格禁止，违者将导致代码审查失败：

| 禁止项 | 说明 |
|--------|------|
| 禁止 domain/ 导入 SQLAlchemy | 领域层必须与 ORM 解耦 |
| 禁止 domain/ 导入 FastAPI | 领域层必须与 Web 框架解耦 |
| 禁止贫血模型 | 实体必须封装业务行为，不能只是数据容器 |
| 禁止路由层写业务逻辑 | 路由只负责请求解析和响应组装 |
| 禁止在路由中手动捕获异常 | 使用全局异常处理器统一处理 |
| 禁止应用层直接操作数据库 | 必须通过 Repository 接口 |

---

## 第三章 值对象设计规范

### 3.1 值对象定义

值对象是不可变的、基于值相等的领域概念。它没有唯一标识，通过其属性值来定义和区分。值对象用于表达领域中的度量性、描述性概念。

### 3.2 Slug 值对象完整模板

以下代码可直接复制到 `backend/src/domain/value_objects/slug.py`：

```python
from __future__ import annotations

import re
from dataclasses import dataclass


@dataclass(frozen=True)
class Slug:
    """Skill 的 URL 友好标识符值对象"""
    
    value: str
    
    # 类级别的正则表达式缓存，避免重复编译
    _VALID_PATTERN = re.compile(r'^[a-z0-9]+(?:-[a-z0-9]+)*$')
    _MAX_LENGTH = 100
    
    def __post_init__(self) -> None:
        # 构造时验证，失败即抛异常
        object.__setattr__(self, 'value', self._validate(self.value))
    
    @classmethod
    def _validate(cls, value: str) -> str:
        if not value:
            raise ValueError("Slug cannot be empty")
        if len(value) > cls._MAX_LENGTH:
            raise ValueError(f"Slug cannot exceed {cls._MAX_LENGTH} characters")
        if not cls._VALID_PATTERN.match(value):
            raise ValueError(
                "Slug must contain only lowercase letters, numbers, and hyphens"
            )
        return value.lower()
    
    @classmethod
    def from_name(cls, name: str) -> Slug:
        """从名称生成 Slug"""
        # 转换规则：空格转横线，去除特殊字符，小写化
        slug = name.lower().strip()
        slug = re.sub(r'[^a-z0-9\s-]', '', slug)
        slug = re.sub(r'[\s]+', '-', slug)
        slug = re.sub(r'-+', '-', slug).strip('-')
        return cls(slug)
    
    def __str__(self) -> str:
        return self.value
    
    def __eq__(self, other: object) -> bool:
        # 基于值相等，而非引用相等
        if not isinstance(other, Slug):
            return NotImplemented
        return self.value == other.value
    
    def __hash__(self) -> int:
        return hash(self.value)
```

### 3.3 值对象设计原则

值对象必须满足以下三条原则：

**原则一：构造时验证，失败即抛异常**

值对象的构造函数必须验证所有不变量。任何无效状态都应立即抛出异常，而不是创建无效对象。这确保了值对象在整个生命周期中始终保持有效。

**原则二：不可变，无 setter**

值对象创建后不可修改。使用 `frozen=True` 的 dataclass 可以防止属性被修改。任何修改操作都应返回新的值对象实例。

**原则三：基于值相等，非引用相等**

值对象使用 `__eq__` 和 `__hash__` 方法实现基于值的相等性比较。两个具有相同值的 Slug 实例被认为是相等的，这符合值对象的语义。

### 3.4 其他值对象示例

项目常用的值对象还包括：

| 值对象 | 用途 | 验证规则 |
|--------|------|----------|
| Email | 用户邮箱 | 符合 email 格式 |
| Password | 密码 | 最小长度 8 位 |
| FilePath | 文件路径 | 符合路径规范 |
| ContentHash | 内容哈希 | 固定长度哈希值 |

---

## 第四章 聚合根设计规范

### 4.1 聚合根定义

聚合根是领域模型的核心，是领域边界的代表。一个聚合由聚合根实体和一组相关实体、值对象组成。聚合根负责维护聚合内部的一致性，所有对聚合内部对象的访问都必须通过聚合根进行。

### 4.2 Skill 聚合根完整模板

以下代码可直接复制到 `backend/src/domain/entities/skill.py`：

```python
from __future__ import annotations

import uuid
from dataclasses import dataclass, field
from datetime import datetime
from typing import Optional

from src.domain.value_objects.slug import Slug


@dataclass
class Skill:
    """Skill 聚合根"""
    
    id: uuid.UUID
    user_id: uuid.UUID
    name: str
    slug: Slug
    description: Optional[str]
    tree_id: Optional[uuid.UUID]
    version: int
    created_at: datetime
    updated_at: datetime
    
    # 私有属性存储内部状态
    _is_deleted: bool = field(default=False, repr=False)
    
    def __post_init__(self) -> None:
        # 业务规则验证
        if not self.name or not self.name.strip():
            raise ValueError("Skill name cannot be empty")
        if len(self.name) > 200:
            raise ValueError("Skill name cannot exceed 200 characters")
    
    @classmethod
    def create(
        cls,
        user_id: uuid.UUID,
        name: str,
        description: Optional[str] = None,
        tree_id: Optional[uuid.UUID] = None,
    ) -> Skill:
        """工厂方法：创建新的 Skill"""
        now = datetime.utcnow()
        return cls(
            id=uuid.uuid4(),
            user_id=user_id,
            name=name.strip(),
            slug=Slug.from_name(name),
            description=description,
            tree_id=tree_id,
            version=1,
            created_at=now,
            updated_at=now,
        )
    
    def update(
        self,
        name: Optional[str] = None,
        description: Optional[str] = None,
    ) -> None:
        """领域方法：更新 Skill 信息"""
        if name is not None:
            if not name.strip():
                raise ValueError("Skill name cannot be empty")
            self.name = name.strip()
            self.slug = Slug.from_name(name)
        
        if description is not None:
            self.description = description
        
        self._increment_version()
        self.updated_at = datetime.utcnow()
    
    def assign_tree(self, tree_id: uuid.UUID) -> None:
        """领域方法：分配目录树"""
        if self.tree_id == tree_id:
            return
        self.tree_id = tree_id
        self._increment_version()
        self.updated_at = datetime.utcnow()
    
    def delete(self) -> None:
        """领域方法：软删除 Skill"""
        if self._is_deleted:
            raise ValueError("Skill is already deleted")
        self._is_deleted = True
        self._increment_version()
        self.updated_at = datetime.utcnow()
    
    def _increment_version(self) -> None:
        """递增版本号，用于乐观锁"""
        self.version += 1
    
    @property
    def is_deleted(self) -> bool:
        return self._is_deleted
```

### 4.3 充血模型原则

领域实体必须采用充血模型设计，遵循以下三条原则：

**原则一：封装业务规则**

业务规则应该封装在领域模型中，而不是散落在应用层或基础设施层。例如，Skill 的名称不能为空、Slug 自动从名称生成等规则都应该在 Skill 实体内部处理。

**原则二：通过方法暴露行为**

领域对象的状态修改必须通过公开的方法进行，而不是直接暴露属性给外部修改。所有状态变更都应经过领域方法的验证和处理。

**原则三：保持数据一致性**

聚合根负责维护聚合内部的数据一致性。任何对聚合内部对象的修改都应该通过聚合根进行，以确保业务不变量始终成立。

---

## 第五章 仓库模式规范

### 5.1 仓库接口定义

仓库接口定义在领域层，属于领域模型的一部分。接口只定义行为签名，不包含任何实现细节。实现放在基础设施层。

### 5.2 SkillRepository 接口模板

以下代码可直接复制到 `backend/src/domain/repositories/skill_repository.py`：

```python
from __future__ import annotations

import uuid
from abc import ABC, abstractmethod
from typing import Optional

from src.domain.entities.skill import Skill
from src.domain.value_objects.slug import Slug


class SkillRepository(ABC):
    """Skill 仓库接口（抽象基类）"""
    
    @abstractmethod
    async def get_by_id(self, skill_id: uuid.UUID) -> Optional[Skill]:
        """根据 ID 获取 Skill"""
        pass
    
    @abstractmethod
    async def get_by_slug(self, slug: Slug, user_id: uuid.UUID) -> Optional[Skill]:
        """根据 Slug 和用户 ID 获取 Skill"""
        pass
    
    @abstractmethod
    async def get_by_user(self, user_id: uuid.UUID) -> list[Skill]:
        """获取用户的所有 Skill"""
        pass
    
    @abstractmethod
    async def save(self, skill: Skill) -> None:
        """保存 Skill（创建或更新）"""
        pass
    
    @abstractmethod
    async def delete(self, skill_id: uuid.UUID) -> None:
        """删除 Skill"""
        pass
```

### 5.3 ORM 模型映射模板

以下代码可直接复制到 `backend/src/infra/persistence/models/skill_model.py`：

```python
from __future__ import annotations

import uuid
from datetime import datetime
from typing import Optional

from sqlalchemy import Boolean, Column, DateTime, Integer, String, Text
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column

from src.db.base import Base


class SkillModel(Base):
    """Skill ORM 模型"""
    
    __tablename__ = "skills"
    
    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True)
    user_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), nullable=False)
    name: Mapped[str] = mapped_column(String(200), nullable=False)
    slug: Mapped[str] = mapped_column(String(100), nullable=False, unique=True)
    description: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    tree_id: Mapped[Optional[uuid.UUID]] = mapped_column(UUID(as_uuid=True), nullable=True)
    version: Mapped[int] = mapped_column(Integer, default=1, nullable=False)
    is_deleted: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime, nullable=False)
    updated_at: Mapped[datetime] = mapped_column(DateTime, nullable=False)
    
    # 复合唯一索引：slug + user_id（软删除场景）
    __table_args__ = (
        # 具体索引定义由 alembic 迁移处理
    )
```

### 5.4 SqlSkillRepository 实现模板

以下代码可直接复制到 `backend/src/infra/persistence/repositories/sql_skill_repository.py`：

```python
from __future__ import annotations

import uuid
from typing import Optional

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from src.domain.entities.skill import Skill
from src.domain.repositories.skill_repository import SkillRepository
from src.domain.value_objects.slug import Slug
from src.infra.persistence.models.skill_model import SkillModel


class SqlSkillRepository(SkillRepository):
    """Skill 仓库 SQL 实现"""
    
    def __init__(self, db: AsyncSession) -> None:
        self._db = db
    
    async def get_by_id(self, skill_id: uuid.UUID) -> Optional[Skill]:
        result = await self._db.execute(
            select(SkillModel).where(
                SkillModel.id == skill_id,
                SkillModel.is_deleted == False,
            )
        )
        model = result.scalar_one_or_none()
        return self._to_domain(model) if model else None
    
    async def get_by_slug(
        self,
        slug: Slug,
        user_id: uuid.UUID,
    ) -> Optional[Skill]:
        result = await self._db.execute(
            select(SkillModel).where(
                SkillModel.slug == str(slug),
                SkillModel.user_id == user_id,
                SkillModel.is_deleted == False,
            )
        )
        model = result.scalar_one_or_none()
        return self._to_domain(model) if model else None
    
    async def get_by_user(self, user_id: uuid.UUID) -> list[Skill]:
        result = await self._db.execute(
            select(SkillModel).where(
                SkillModel.user_id == user_id,
                SkillModel.is_deleted == False,
            ).order_by(SkillModel.created_at.desc())
        )
        return [self._to_domain(m) for m in result.scalars().all()]
    
    async def save(self, skill: Skill) -> None:
        model = self._to_model(skill)
        self._db.add(model)
        await self._db.flush()
    
    async def delete(self, skill_id: uuid.UUID) -> None:
        result = await self._db.execute(
            select(SkillModel).where(SkillModel.id == skill_id)
        )
        model = result.scalar_one_or_none()
        if model:
            model.is_deleted = True
            await self._db.flush()
    
    def _to_domain(self, model: SkillModel) -> Skill:
        """ORM 模型转领域对象"""
        return Skill(
            id=model.id,
            user_id=model.user_id,
            name=model.name,
            slug=Slug(model.slug),
            description=model.description,
            tree_id=model.tree_id,
            version=model.version,
            created_at=model.created_at,
            updated_at=model.updated_at,
        )
    
    def _to_model(self, skill: Skill) -> SkillModel:
        """领域对象转 ORM 模型"""
        return SkillModel(
            id=skill.id,
            user_id=skill.user_id,
            name=skill.name,
            slug=str(skill.slug),
            description=skill.description,
            tree_id=skill.tree_id,
            version=skill.version,
            is_deleted=skill.is_deleted,
            created_at=skill.created_at,
            updated_at=skill.updated_at,
        )
```

---

## 第六章 应用层规范

### 6.1 应用层职责

应用层是领域层的客户，负责协调领域对象完成用例。它不包含业务逻辑，只是领域逻辑的编排者。应用层采用函数式风格，使用模块加函数而非类来组织代码。

### 6.2 Repository 依赖注入

以下代码可直接复制到 `backend/src/api/dependencies/repositories.py`：

```python
from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession

from src.db.session import get_db
from src.domain.repositories.skill_repository import SkillRepository
from src.infra.persistence.repositories.sql_skill_repository import SqlSkillRepository


async def get_skill_repo(
    db: AsyncSession = Depends(get_db),
) -> SkillRepository:
    """Skill Repository 依赖注入"""
    return SqlSkillRepository(db)
```

### 6.3 Handler 函数模板

以下代码可直接复制到 `backend/src/application/handlers/create_skill_handler.py`：

```python
from typing import Optional
import uuid

from src.domain.entities.skill import Skill
from src.domain.exceptions import SkillAlreadyExistsError
from src.domain.repositories.skill_repository import SkillRepository
from src.domain.value_objects.slug import Slug


async def handle_create_skill(
    user_id: uuid.UUID,
    name: str,
    description: Optional[str],
    skill_repo: SkillRepository,
) -> Skill:
    """创建 Skill 的 Handler"""
    # 1. 构造值对象
    slug = Slug.from_name(name)
    
    # 2. 领域验证：检查是否已存在
    existing = await skill_repo.get_by_slug(slug, user_id)
    if existing:
        raise SkillAlreadyExistsError(f"Skill with name '{name}' already exists")
    
    # 3. 创建聚合根
    skill = Skill.create(
        user_id=user_id,
        name=name,
        description=description,
    )
    
    # 4. 持久化
    await skill_repo.save(skill)
    
    # 5. 返回结果
    return skill
```

### 6.4 在路由中使用 Handler

以下代码展示了如何在路由中调用 Handler：

```python
# backend/src/api/routers/skills.py
from fastapi import APIRouter, Depends, status
from uuid import UUID

from src.api.dependencies.repositories import get_skill_repo
from src.application.handlers.create_skill_handler import handle_create_skill
from src.domain.repositories.skill_repository import SkillRepository
from src.schemas.skill import CreateSkillReq, CreateSkillResp
from src.dependencies.auth import get_current_user
from src.models.user import User


router = APIRouter(prefix="/skills", tags=["skills"])


@router.post(
    "",
    response_model=CreateSkillResp,
    status_code=status.HTTP_201_CREATED,
)
async def create_skill(
    request: CreateSkillReq,
    skill_repo: SkillRepository = Depends(get_skill_repo),
    current_user: User = Depends(get_current_user),
) -> CreateSkillResp:
    """创建新 Skill"""
    skill = await handle_create_skill(
        user_id=current_user.id,
        name=request.name,
        description=request.description,
        skill_repo=skill_repo,
    )
    return CreateSkillResp.from_domain(skill)
```

### 6.5 应用层核心原则

**原则一：应用层无状态**

应用层的 Handler 函数应该是无状态的。每次调用都应该是一个完整的事务，不应依赖于任何共享状态。

**原则二：使用模块加函数而非类**

应用层采用函数式编程风格，不使用类来组织代码。每个用例对应一个 Handler 函数，放在对应的模块文件中。

**原则三：依赖通过参数显式传入**

所有依赖都通过函数参数显式传入，不使用类属性或全局变量。这使得 Handler 函数易于测试。

---

## 第七章 DTO 设计规范

### 7.1 DTO 命名规则速查表

| 场景 | 命名格式 | 示例 |
|------|----------|------|
| 单个创建请求 | `{Action}{Resource}Req` | CreateSkillReq |
| 单个响应 | `{Action}{Resource}Resp` | CreateSkillResp |
| 获取单个请求 | `Get{Resource}Req` | GetSkillReq |
| 获取单个响应 | `Get{Resource}Resp` | GetSkillResp |
| 更新请求 | `Update{Resource}Req` | UpdateSkillReq |
| 列表项响应 | `List{Resources}ItemResp` | ListSkillsItemResp |
| 列表响应 | `list[List{Resources}ItemResp]` | list[ListSkillsItemResp] |

### 7.2 CreateSkillReq 模板

```python
from typing import Optional

from pydantic import BaseModel, Field


class CreateSkillReq(BaseModel):
    """创建 Skill 请求"""
    
    name: str = Field(..., min_length=1, max_length=200, description="Skill 名称")
    description: Optional[str] = Field(None, max_length=2000, description="Skill 描述")
```

### 7.3 CreateSkillResp 模板

```python
import uuid
from datetime import datetime
from typing import Optional

from pydantic import BaseModel, Field

from src.domain.entities.skill import Skill


class CreateSkillResp(BaseModel):
    """创建 Skill 响应"""
    
    id: uuid.UUID = Field(..., description="Skill ID")
    name: str = Field(..., description="Skill 名称")
    slug: str = Field(..., description="Skill Slug")
    description: Optional[str] = Field(None, description="Skill 描述")
    version: int = Field(..., description="版本号")
    created_at: datetime = Field(..., description="创建时间")
    updated_at: datetime = Field(..., description="更新时间")
    
    @classmethod
    def from_domain(cls, skill: Skill) -> CreateSkillResp:
        return cls(
            id=skill.id,
            name=skill.name,
            slug=str(skill.slug),
            description=skill.description,
            version=skill.version,
            created_at=skill.created_at,
            updated_at=skill.updated_at,
        )
```

### 7.4 ListSkillsItemResp 模板

```python
import uuid
from datetime import datetime
from typing import Optional

from pydantic import BaseModel, Field

from src.domain.entities.skill import Skill


class ListSkillsItemResp(BaseModel):
    """Skill 列表项响应"""
    
    id: uuid.UUID = Field(..., description="Skill ID")
    name: str = Field(..., description="Skill 名称")
    slug: str = Field(..., description="Skill Slug")
    description: Optional[str] = Field(None, description="Skill 描述")
    updated_at: datetime = Field(..., description="更新时间")
    
    @classmethod
    def from_domain(cls, skill: Skill) -> ListSkillsItemResp:
        return cls(
            id=skill.id,
            name=skill.name,
            slug=str(skill.slug),
            description=skill.description,
            updated_at=skill.updated_at,
        )
```

### 7.5 响应模型配置

在路由中配置响应模型时：

```python
@router.get("", response_model=list[ListSkillsItemResp])
async def list_skills(
    skill_repo: SkillRepository = Depends(get_skill_repo),
    current_user: User = Depends(get_current_user),
) -> list[ListSkillsItemResp]:
    skills = await skill_repo.get_by_user(current_user.id)
    return [ListSkillsItemResp.from_domain(s) for s in skills]
```

---

## 第八章 异常处理规范

### 8.1 核心原则

业务异常只有一个基类 DomainError。HTTP 状态码由 API 层根据异常类别决定，不在异常类中硬编码。统一响应格式为 `{code, message}`。

### 8.2 异常层次结构

```
DomainError (src/domain/exceptions.py)
├── 类别分类（category 属性）
│   ├── "NOT_FOUND"     → 404
│   ├── "CONFLICT"      → 409
│   ├── "VALIDATION"   → 422
│   ├── "UNAUTHORIZED" → 401
│   ├── "FORBIDDEN"    → 403
│   └── "BUSINESS"     → 400
└── 具体异常子类
```

### 8.3 DomainError 基类模板

以下代码可直接复制到 `backend/src/domain/exceptions.py`：

```python
from __future__ import annotations


class DomainError(Exception):
    """领域异常基类"""
    
    code: str = "DOMAIN_ERROR"
    message: str = "Domain error occurred"
    category: str = "BUSINESS"
    
    def __init__(self, message: str | None = None) -> None:
        self.message = message or self.message
        super().__init__(self.message)


class NotFoundError(DomainError):
    """资源不存在"""
    
    code: str = "NOT_FOUND"
    message: str = "Resource not found"
    category: str = "NOT_FOUND"


class ConflictError(DomainError):
    """资源冲突"""
    
    code: str = "CONFLICT"
    message: str = "Resource conflict"
    category: str = "CONFLICT"


class ValidationError(DomainError):
    """验证错误"""
    
    code: str = "VALIDATION"
    message: str = "Validation failed"
    category: str = "VALIDATION"


class UnauthorizedError(DomainError):
    """未授权"""
    
    code: str = "UNAUTHORIZED"
    message: str = "Unauthorized"
    category: str = "UNAUTHORIZED"


class ForbiddenError(DomainError):
    """禁止访问"""
    
    code: str = "FORBIDDEN"
    message: str = "Forbidden"
    category: str = "FORBIDDEN"


# 具体业务异常示例


class SkillAlreadyExistsError(ConflictError):
    """Skill 已存在"""
    
    code: str = "DOMAIN_SKILL_CREATE_CONFLICT"
    message: str = "Skill with this name already exists"


class SkillNotFoundError(NotFoundError):
    """Skill 不存在"""
    
    code: str = "DOMAIN_SKILL_NOT_FOUND"
    message: str = "Skill not found"


class InvalidSlugError(ValidationError):
    """Slug 格式无效"""
    
    code: str = "VALIDATION_SLUG_INVALID_FORMAT"
    message: str = "Invalid slug format"
```

### 8.4 Code 命名规范

异常 code 命名采用 `{类别}_{资源}_{操作}_{具体错误}` 格式：

| 场景 | Code 示例 |
|------|-----------|
| 创建冲突 | DOMAIN_SKILL_CREATE_CONFLICT |
| 更新不存在 | DOMAIN_SKILL_UPDATE_NOT_FOUND |
| 删除不存在 | DOMAIN_SKILL_DELETE_NOT_FOUND |
| Slug 格式错误 | VALIDATION_SLUG_INVALID_FORMAT |
| 名称为空 | VALIDATION_SKILL_NAME_EMPTY |

### 8.5 全局异常处理器

以下代码放置在 `backend/src/api/exceptions.py`：

```python
from fastapi import FastAPI, Request, status
from fastapi.responses import JSONResponse

from src.domain.exceptions import DomainError


CATEGORY_STATUS_MAP = {
    "NOT_FOUND": status.HTTP_404_NOT_FOUND,
    "CONFLICT": status.HTTP_409_CONFLICT,
    "VALIDATION": status.HTTP_422_UNPROCESSABLE_ENTITY,
    "UNAUTHORIZED": status.HTTP_401_UNAUTHORIZED,
    "FORBIDDEN": status.HTTP_403_FORBIDDEN,
    "BUSINESS": status.HTTP_400_BAD_REQUEST,
}


def setup_exception_handlers(app: FastAPI) -> None:
    """注册全局异常处理器"""
    
    @app.exception_handler(DomainError)
    async def handle_domain_error(request: Request, exc: DomainError):
        status_code = CATEGORY_STATUS_MAP.get(exc.category, status.HTTP_400_BAD_REQUEST)
        return JSONResponse(
            status_code=status_code,
            content={
                "code": exc.code,
                "message": exc.message,
            },
        )
```

在 `main.py` 中注册：

```python
from fastapi import FastAPI
from src.api.exceptions import setup_exception_handlers


def create_app() -> FastAPI:
    app = FastAPI(...)
    setup_exception_handlers(app)
    return app
```

### 8.6 路由层无需 try-catch

使用全局异常处理器后，路由层无需手动捕获异常：

```python
# 正确写法
@router.post("/skills", ...)
async def create_skill(...):
    skill = await handle_create_skill(...)  # 异常自动抛出
    return CreateSkillResp.from_domain(skill)


# 错误写法（禁止）
@router.post("/skills", ...)
async def create_skill(...):
    try:
        skill = await handle_create_skill(...)
        return CreateSkillResp.from_domain(skill)
    except SkillAlreadyExistsError as e:
        raise HTTPException(status_code=409, detail=str(e))
```

---

## 第九章 事务管理规范

### 9.1 核心原则

**使用现有的 `get_db()` 管理事务**。

现有的 `get_db()` 依赖已经提供了完善的事务管理：
- 每个请求一个事务
- 成功自动 commit
- 异常自动 rollback

### 9.2 现有实现

```python
# src/db/session.py
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

### 9.3 Repository 层

Repository 只负责数据操作，不控制事务：

```python
class SqlSkillRepository(SkillRepository):
    def __init__(self, db: AsyncSession):  # 由 get_db 注入
        self._db = db
    
    async def save(self, skill: Skill) -> None:
        # 只 add，不 commit（由 get_db 自动处理）
        self._db.add(SkillModel.from_domain(skill))
    
    async def get_by_id(self, id: SkillId) -> Skill | None:
        result = await self._db.execute(...)
        return result.scalar_one_or_none()
```

### 9.4 在 Handler 中使用

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

### 9.5 并发控制策略

**策略一：乐观锁（推荐）**

领域对象包含 version 字段，更新时检查版本号。

**策略二：数据库唯一约束**

对于唯一性约束（如 Slug），使用数据库唯一索引防止重复。

**策略三：悲观锁（仅高频冲突场景）**

仅在高频冲突的业务场景使用 `SELECT FOR UPDATE`。

### 9.6 何时需要显式事务控制

以下情况才需要显式事务管理：

| 场景 | 说明 | 示例 |
|------|------|------|
| 多次 commit | 一个请求需要分批提交 | 先保存草稿，再正式发布 |
| 后台任务 | 批处理任务 | 批量更新，每100条提交一次 |
| 分布式事务 | 涉及多个服务 |  saga 模式 |

**简单业务场景保持使用 `get_db()` 即可。**

### 9.7 禁止事项

| 禁止项 | 说明 | 正确做法 |
|--------|------|----------|
| 不要在仓库实现中调用 db.commit() | 事务由 get_db 管理 | Repository 只 add/update/delete |
| 不要在领域层管理事务 | 领域层不知道事务存在 | 通过 Repository 接口操作 |
| 不要在路由层管理事务 | 路由只负责请求响应 | 使用 `Depends(get_db)` |

---

## 第十章 测试规范

### 10.1 测试目录结构

```
backend/tests/
├── conftest.py                      # 全局 fixtures
├── factories/                       # 测试工厂
│   ├── __init__.py
│   └── skill_factory.py
├── integration/
│   ├── api/                         # API 端点测试（类风格）
│   │   ├── __init__.py
│   │   ├── test_skills_api.py
│   │   └── test_auth_api.py
│   └── journey/                     # 用户旅程测试
│       ├── __init__.py
│       ├── test_journey_creation.py
│       └── test_journey_deletion.py
└── unit/                            # 少量单元测试
    ├── __init__.py
    └── test_value_objects.py
```

### 10.2 核心 Fixtures

`conftest.py` 中定义以下核心 fixtures：

```python
import pytest
import pytest_asyncio
from httpx import AsyncClient, ASGITransport
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine, async_sessionmaker

from src.main import create_app
from src.db.base import Base
from src.db.session import get_db


@pytest_asyncio.fixture
async def db_session():
    """测试数据库会话"""
    engine = create_async_engine("sqlite+aiosqlite:///:memory:")
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    
    async_session = async_sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)
    async with async_session() as session:
        yield session
    
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)
    
    await engine.dispose()


@pytest_asyncio.fixture
async def test_user(db_session: AsyncSession):
    """测试用户"""
    from src.models.user import User
    from src.core.auth import hash_password
    
    user = User(
        id=uuid.uuid4(),
        email="test@example.com",
        username="testuser",
        password_hash=hash_password("password123"),
    )
    db_session.add(user)
    await db_session.commit()
    return user


@pytest_asyncio.fixture
async def auth_client(db_session: AsyncSession, test_user):
    """带认证的 HTTP 客户端"""
    app = create_app()
    
    async def override_get_db():
        yield db_session
    
    app.dependency_overrides[get_db] = override_get_db
    
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        # 生成 token（简化版）
        token = create_access_token(test_user.id)
        client.headers["Authorization"] = f"Bearer {token}"
        yield client
```

### 10.3 API 测试示例

```python
import pytest


@pytest.mark.asyncio
class TestSkillsApi:
    """Skills API 测试"""
    
    async def test_create_skill(self, auth_client):
        """创建 Skill"""
        response = await auth_client.post(
            "/api/skills",
            json={"name": "Test Skill", "description": "A test skill"},
        )
        assert response.status_code == 201
        data = response.json()
        assert data["name"] == "Test Skill"
        assert "id" in data
    
    async def test_list_skills(self, auth_client, test_skill):
        """列出 Skills"""
        response = await auth_client.get("/api/skills")
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)
```

### 10.4 Journey 测试示例

```python
import pytest


@pytest.mark.asyncio
async def test_create_and_retrieve_skill(db_session, test_user):
    """创建并检索 Skill 的完整流程"""
    from src.application.handlers.create_skill_handler import handle_create_skill
    from src.api.dependencies.repositories import UnitOfWork
    from src.db.session import get_db
    
    # 1. 创建 Skill
    uow = UnitOfWork(db_session)
    skill = await handle_create_skill(
        user_id=test_user.id,
        name="My Skill",
        description="Test description",
        uow=uow,
    )
    
    # 2. 验证创建成功
    assert skill.name == "My Skill"
    assert str(skill.slug) == "my-skill"
    
    # 3. 检索 Skill
    from src.domain.repositories.skill_repository import SkillRepository
    from src.infra.persistence.repositories.sql_skill_repository import SqlSkillRepository
    
    repo = SqlSkillRepository(db_session)
    retrieved = await repo.get_by_id(skill.id)
    
    assert retrieved is not None
    assert retrieved.name == skill.name
```

### 10.5 不编写的测试

以下测试不需要编写：

| 不编写 | 原因 |
|--------|------|
| 领域对象单元测试 | 通过 Journey 测试覆盖 |
| 仓库层单独测试 | 通过 API 测试间接覆盖 |
| 简单的 Getter/Setter 测试 | 无业务逻辑，无测试价值 |

---

## 第十一章 代码注释与自解释代码规范

### 11.1 核心原则

除了 API 文档（用于 OpenAPI 生成），尽可能避免注释。代码本身应该能够揭示意图，而非依赖注释。好的命名、清晰的方法划分比任何注释都有效。

### 11.2 避免的注释类型

**解释 what 的注释**

```python
# 错误：解释代码做什么
# 判断用户是否已认证
if user.is_authenticated:
    ...

# 正确：通过代码揭示意图
if user.is_authenticated:
    ...
```

**显而易见的注释**

```python
# 错误
# 遍历用户列表
for user in users:
    ...

# 正确
for user in users:
    ...
```

**解释变量类型的注释**

```python
# 错误
user_id: str  # 用户 ID
skills: list[Skill]  # Skills 列表
```

### 11.3 通过代码揭示意图

**好的命名示例**

| 场景 | 差命名 | 好命名 | 说明 |
|------|--------|--------|------|
| 布尔判断 | check_user() | is_authenticated() | 明确返回布尔值 |
| 获取数据 | get_data() | fetch_active_skills() | 明确获取什么 |
| 验证方法 | validate() | is_valid_email_format() | 明确验证什么 |
| 列表过滤 | filter_items() | fetch_published_skills() | 明确过滤条件 |

**方法名解释意图**

```python
# 差：方法名不明确
def process():
    ...

# 好：方法名揭示意图
def activate_user():
    ...

def deactivate_user():
    ...

def publish_skill():
    ...
```

**提取复杂逻辑到命名良好的方法**

```python
# 差：逻辑堆在一起
def create_skill(request):
    if not request.name:
        raise ValidationError("Name is required")
    if len(request.name) < 3:
        raise ValidationError("Name must be at least 3 characters")
    if len(request.name) > 100:
        raise ValidationError("Name must not exceed 100 characters")
    # 更多验证...


# 好：提取为方法
def create_skill(request):
    self._validate_name(request.name)
    # 更多逻辑...


def _validate_name(name: str) -> None:
    if not name:
        raise ValidationError("Name is required")
    if len(name) < 3:
        raise ValidationError("Name must be at least 3 characters")
    if len(name) > 100:
        raise ValidationError("Name must not exceed 100 characters")
```

### 11.4 何时允许注释

**API Doc（用于 OpenAPI）**

```python
@router.post("/skills", response_model=CreateSkillResp)
async def create_skill(
    request: CreateSkillReq,
    skill_repo: SkillRepository = Depends(get_skill_repo),
) -> CreateSkillResp:
    """
    创建新 Skill
    
    创建一个新的 Skill 并返回创建结果
    """
    ...
```

**解释 why 的注释**

```python
# 为什么使用乐观锁：高并发场景下悲观锁会导致死锁
# 参考：https://example.com/ops/optimistic-locking
version: int = 1
```

**TODO/FIXME**

```python
# TODO: 当 PostgreSQL 16 支持后，移除此兼容性处理
# FIXME: 性能问题，需要优化查询
```

**复杂算法解释**

```python
# 使用 Luhn 算法验证信用卡号
# 参考：https://en.wikipedia.org/wiki/Luhn_algorithm
def luhn_checksum(card_number: str) -> int:
    ...
```

---

## 第十二章 命名与导入规范

### 12.1 文件命名速查表

| 类型 | 命名规则 | 示例 |
|------|----------|------|
| 值对象 | slug.py | `from src.domain.value_objects.slug import Slug` |
| 聚合根 | skill.py | `from src.domain.entities.skill import Skill` |
| 仓库接口 | skill_repository.py | `from src.domain.repositories.skill_repository import SkillRepository` |
| 仓库实现 | sql_skill_repository.py | `from src.infra.persistence.repositories.sql_skill_repository import SqlSkillRepository` |
| ORM 模型 | skill_model.py | `from src.infra.persistence.models.skill_model import SkillModel` |
| Handler | create_skill_handler.py | `from src.application.handlers.create_skill_handler import handle_create_skill` |
| 依赖注入 | repositories.py | `from src.api.dependencies.repositories import get_skill_repo` |
| 路由 | skills.py | `from src.api.routers.skills import router` |

### 12.2 类命名速查表

| 类型 | 命名规则 | 示例 |
|------|----------|------|
| 值对象 | 大驼峰，不可变 | `Slug`, `Email`, `Password` |
| 聚合根 | 大驼峰，实体 | `Skill`, `User`, `Project` |
| 仓库接口 | 大驼峰，可加 Repository | `SkillRepository`, `UserRepository` |
| 仓库实现 | Sql前缀+大驼峰 | `SqlSkillRepository`, `SqlUserRepository` |
| ORM 模型 | 大驼峰+Model | `SkillModel`, `UserModel` |
| 异常 | 大驼峰+Error | `DomainError`, `SkillNotFoundError` |
| Handler | handle_前缀+动作 | `handle_create_skill`, `handle_update_skill` |

### 12.3 函数命名速查表

| 类型 | 命名规则 | 示例 |
|------|----------|------|
| 领域方法 | 动词或动宾短语 | `create()`, `update()`, `delete()`, `assign_tree()` |
| Handler | handle_动作 | `handle_create_skill()`, `handle_list_skills()` |
| Repository 方法 | get_/save_/delete_前缀 | `get_by_id()`, `get_by_slug()`, `save()`, `delete()` |
| 工厂方法 | create_/new_前缀 | `create()`, `from_name()` |
| 布尔方法 | is_/has_/can_前缀 | `is_authenticated()`, `is_deleted()`, `has_permission()` |

### 12.4 导入规范

**绝对导入优先**

```python
# 推荐
from src.domain.entities.skill import Skill
from src.domain.value_objects.slug import Slug

# 避免
from ...domain.entities.skill import Skill
```

**分层导入**

```python
# API 层
from fastapi import APIRouter, Depends
from src.api.dependencies.repositories import get_skill_repo

# 应用层
from src.application.handlers.create_skill_handler import handle_create_skill

# 领域层
from src.domain.entities.skill import Skill
from src.domain.value_objects.slug import Slug
from src.domain.repositories.skill_repository import SkillRepository

# 基础设施层
from src.infra.persistence.repositories.sql_skill_repository import SqlSkillRepository
```

---

## 第十三章 快速检查清单

### 13.1 新功能检查清单

创建新功能时，按以下清单逐项检查：

- [ ] **领域对象封装业务行为**
  - [ ] 实体包含业务方法，不只是 getter/setter
  - [ ] 值对象在构造时验证数据
  - [ ] 业务规则封装在领域层

- [ ] **依赖方向正确**
  - [ ] domain/ 不导入 SQLAlchemy
  - [ ] domain/ 不导入 FastAPI
  - [ ] 领域层不知道基础设施层的存在

- [ ] **仓库模式正确**
  - [ ] 仓库接口在 domain/repositories/
  - [ ] 仓库实现在 infra/persistence/repositories/
  - [ ] ORM 模型包含 to_domain() 和 from_domain() 方法

- [ ] **应用层风格正确**
  - [ ] 使用函数式风格（模块+函数）
  - [ ] Handler 函数无状态
  - [ ] 依赖通过参数显式传入

- [ ] **Repository 注入正确**
  - [ ] 使用 FastAPI Depends 注入
  - [ ] 依赖注入函数在 api/dependencies/

- [ ] **DTO 命名正确**
  - [ ] 单个请求: `{Action}{Resource}Req`
  - [ ] 单个响应: `{Action}{Resource}Resp`
  - [ ] 列表项: `List{Resources}ItemResp`

- [ ] **异常处理正确**
  - [ ] 业务异常继承 DomainError
  - [ ] 使用全局异常处理器
  - [ ] 路由层无 try-catch

- [ ] **事务管理正确**
  - [ ] 使用 Unit of Work 管理事务
  - [ ] 事务边界在应用层
  - [ ] 乐观锁版本号字段

- [ ] **代码质量**
  - [ ] 无解释性注释
  - [ ] 方法名揭示意图
  - [ ] 类型提示完整

### 13.2 代码审查检查点

代码审查时重点检查：

1. **领域层是否纯粹**
   - 是否有 SQLAlchemy 导入？
   - 是否有 FastAPI 导入？
   - 是否有业务逻辑泄露到应用层？

2. **贫血模型检测**
   - 实体是否有业务方法？
   - 是否只是数据容器？

3. **依赖注入是否正确**
   - Repository 是否通过 Depends 注入？
   - 依赖是否通过参数传入？

4. **异常处理是否规范**
   - 是否使用 DomainError 子类？
   - 路由是否有 try-catch？
   - HTTP 状态码是否在 API 层映射？

---

## 附录：代码模板速查

### A.1 值对象模板

```python
from __future__ import annotations

import re
from dataclasses import dataclass


@dataclass(frozen=True)
class ValueObjectName:
    value: str
    
    def __post_init__(self) -> None:
        # 构造时验证
        object.__setattr__(self, 'value', self._validate(self.value))
    
    @classmethod
    def _validate(cls, value: str) -> str:
        if not value:
            raise ValueError("...")
        return value
    
    @classmethod
    def from_xxx(cls, ...) -> ValueObjectName:
        ...
    
    def __str__(self) -> str:
        return self.value
    
    def __eq__(self, other: object) -> bool:
        if not isinstance(other, ValueObjectName):
            return NotImplemented
        return self.value == other.value
    
    def __hash__(self) -> int:
        return hash(self.value)
```

### A.2 聚合根模板

```python
from dataclasses import dataclass, field
from datetime import datetime
import uuid


@dataclass
class AggregateRoot:
    id: uuid.UUID
    version: int
    created_at: datetime
    updated_at: datetime
    
    @classmethod
    def create(cls, ...) -> AggregateRoot:
        ...
    
    def update(self, ...) -> None:
        self._increment_version()
        self.updated_at = datetime.utcnow()
    
    def _increment_version(self) -> None:
        self.version += 1
```

### A.3 Handler 模板

```python
async def handle_action(
    param: str,
    repo: Repository,
    uow: UnitOfWork,
) -> Result:
    async with uow:
        # 业务逻辑
        await uow.repo.save(entity)
        return result
```

### A.4 Repository 接口模板

```python
from abc import ABC, abstractmethod
from typing import Optional
import uuid


class Repository(ABC):
    @abstractmethod
    async def get_by_id(self, id: uuid.UUID) -> Optional[Entity]:
        pass
    
    @abstractmethod
    async def save(self, entity: Entity) -> None:
        pass
```
