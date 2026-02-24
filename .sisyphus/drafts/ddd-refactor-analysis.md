# Draft: 后端架构分析与 DDD 重构规划

## 📋 项目概述

**Agent Skills Manager** - 一个 Agent Skills 管理平台

**核心业务功能**:
1. **用户管理**: 注册、登录、JWT认证
2. **Skill管理**: 创建、编辑、版本管理 Skills
3. **项目管理**: 绑定项目到用户
4. **Tree系统**: Git-like 目录树结构管理
5. **Blob存储**: 内容寻址存储（CAS）
6. **版本历史**: 支持 Skill 版本控制

---

## 🔍 当前架构分析

### 技术栈
- **框架**: FastAPI 0.129.0+
- **ORM**: SQLAlchemy 2.0+ (异步)
- **数据库**: PostgreSQL 16+
- **迁移**: Alembic
- **认证**: JWT (PyJWT + python-jose)

### 当前目录结构

```
backend/app/
├── api/              # API路由组装
├── core/             # 配置、认证、日志
├── crud/             # CRUD操作 (Repository层)
├── db/               # 数据库连接、Base类
├── models/           # SQLAlchemy 模型
├── routers/          # FastAPI 路由 (Controller层)
├── schemas/          # Pydantic 验证模型 (DTO)
├── services/         # 业务逻辑服务层
├── auth.py           # JWT工具函数
└── main.py           # 应用入口
```

### 当前架构模式评估

**当前模式**: 接近 **分层架构** (Layered Architecture)，但不是严格的DDD

**问题识别**:

1. **❌ Anemic Domain Model (贫血领域模型)**
   - Models (User, Skill, Tree, etc.) 只是数据载体，没有任何业务行为
   - 所有业务逻辑都在 `services/` 和 `crud/` 中
   - 违反"将业务规则放在领域对象中"的DDD原则

2. **❌ 业务逻辑分散**
   - Skill slug 验证在 `services/skill_service.py` (line 51-55)
   - Path traversal 验证在 `routers/trees.py` (line 44-67)
   - 业务规则散落在不同层级

3. **❌ 领域概念模糊**
   - `Tree` 作为数据结构存储在 JSONB 中，缺乏领域行为封装
   - `Skill` 应该有版本管理领域概念，但目前只是简单外键关联
   - 缺少明确的 Aggregate Root 定义

4. **❌ 基础设施耦合**
   - `skill_service.py` 直接依赖 `db.flush()`, `db.refresh()`
   - 业务逻辑与数据库事务控制混合
   - 测试困难（需要完整的数据库）

5. **❌ 缺少值对象 (Value Objects)**
   - `Slug`, `Path`, `Email` 等应该封装为值对象
   - 目前用原始字符串到处传递，验证逻辑重复

6. **✅ 好的地方**
   - 使用了 Repository 模式 (`crud/`)
   - 分离了 Schemas (DTOs)
   - 服务层有一定抽象

---

## 🎯 DDD 分层架构建议

### 目标架构

```
backend/app/
├── api/                    # 接入层 (Interface/Presentation Layer)
│   ├── routers/           # FastAPI 路由
│   ├── schemas/           # Pydantic DTOs
│   └── dependencies/      # FastAPI 依赖注入
├── application/           # 应用层 (Application Layer) ⭐ NEW
│   ├── commands/          # CQRS - 写操作
│   ├── queries/           # CQRS - 读操作
│   ├── handlers/          # 命令处理器
│   └── events/            # 领域事件处理器
├── domain/                # 领域层 (Domain Layer) ⭐ CORE
│   ├── entities/          # 领域实体 (富对象)
│   ├── value_objects/     # 值对象
│   ├── aggregates/        # 聚合根
│   ├── repositories/      # 仓库接口 (仅接口!)
│   ├── domain_events/     # 领域事件
│   ├── services/          # 领域服务 (跨实体逻辑)
│   └── policies/          # 策略/规则
├── infrastructure/        # 基础设施层 (Infrastructure Layer) ⭐ NEW
│   ├── persistence/       # SQLAlchemy实现
│   │   ├── models/        # ORM 模型
│   │   ├── repositories/  # 仓库实现
│   │   └── migrations/    # Alembic迁移
│   ├── auth/              # JWT实现
│   ├── storage/           # Blob存储实现
│   ├── events/            # 事件总线实现
│   └── config/            # 配置
└── shared/                # 共享内核
    ├── exceptions.py      # 领域异常
    └── types.py           # 类型定义
```

### 核心概念映射

| 当前概念 | DDD概念 | 说明 |
|---------|--------|------|
| User | Aggregate Root | 用户及其数据的一致边界 |
| Skill | Aggregate Root | Skill及其版本历史的一致边界 |
| Tree | Entity (part of Skill) | 作为Skill的一部分 |
| Blob | Value Object | 内容寻址，无身份 |
| slug, path, email | Value Objects | 带验证和业务规则的值对象 |

---

## 🔧 具体重构建议

### 1. 创建领域层 (Domain Layer)

#### 1.1 值对象示例 - `Slug`

```python
# domain/value_objects/slug.py
import re
from dataclasses import dataclass

SLUG_PATTERN = re.compile(r"^[a-z0-9]+(-[a-z0-9]+)*$")

@dataclass(frozen=True)
class Slug:
    value: str
    
    def __post_init__(self):
        if not self.value:
            raise ValueError("Slug cannot be empty")
        if not SLUG_PATTERN.match(self.value):
            raise ValueError(f"Invalid slug format: {self.value}")
    
    @classmethod
    def from_name(cls, name: str) -> "Slug":
        return cls(value=name.lower())
    
    def __str__(self) -> str:
        return self.value
```

#### 1.2 富领域实体 - `Skill`

```python
# domain/aggregates/skill.py
from dataclasses import dataclass, field
from datetime import datetime
from uuid import UUID

from domain.value_objects.slug import Slug
from domain.events.skill_created import SkillCreatedEvent
from domain.exceptions import DomainException

@dataclass
class Skill:
    id: UUID
    user_id: UUID
    name: str
    slug: Slug
    description: str
    tree_id: UUID | None = None
    version: int = field(default=1)
    is_public: bool = field(default=False)
    created_at: datetime = field(default_factory=datetime.utcnow)
    updated_at: datetime = field(default_factory=datetime.utcnow)
    
    # 领域事件
    _events: list = field(default_factory=list, repr=False)
    
    @classmethod
    def create(
        cls,
        user_id: UUID,
        name: str,
        slug: Slug,
        description: str,
    ) -> "Skill":
        """工厂方法 - 创建新的 Skill."""
        skill = cls(
            id=uuid4(),
            user_id=user_id,
            name=name,
            slug=slug,
            description=description,
        )
        skill._events.append(SkillCreatedEvent(skill_id=skill.id))
        return skill
    
    def update_metadata(self, name: str | None = None, 
                       description: str | None = None) -> None:
        """更新元数据 - 领域行为."""
        if name is not None:
            self.name = name
        if description is not None:
            self.description = description
        self.updated_at = datetime.utcnow()
        self.version += 1
    
    def change_slug(self, new_slug: Slug) -> None:
        """修改 slug - 业务规则验证."""
        if self.slug == new_slug:
            return
        self.slug = new_slug
        self.updated_at = datetime.utcnow()
        self.version += 1
    
    def attach_tree(self, tree_id: UUID) -> None:
        """关联文件树."""
        self.tree_id = tree_id
        self.updated_at = datetime.utcnow()
    
    def publish(self) -> None:
        """公开 skill."""
        self.is_public = True
        self.updated_at = datetime.utcnow()
    
    def unpublish(self) -> None:
        """取消公开."""
        self.is_public = False
        self.updated_at = datetime.utcnow()
    
    def pull_events(self) -> list:
        """获取并清空领域事件."""
        events = self._events.copy()
        self._events.clear()
        return events
```

#### 1.3 仓库接口

```python
# domain/repositories/skill_repository.py
from abc import ABC, abstractmethod
from uuid import UUID

from domain.aggregates.skill import Skill
from domain.value_objects.slug import Slug

class SkillRepository(ABC):
    @abstractmethod
    async def get_by_id(self, skill_id: UUID) -> Skill | None:
        pass
    
    @abstractmethod
    async def get_by_slug(self, slug: Slug, user_id: UUID) -> Skill | None:
        pass
    
    @abstractmethod
    async def find_by_user(self, user_id: UUID, skip: int = 0, limit: int = 100) -> list[Skill]:
        pass
    
    @abstractmethod
    async def save(self, skill: Skill) -> None:
        """保存聚合根（包含事务）."""
        pass
    
    @abstractmethod
    async def delete(self, skill_id: UUID) -> None:
        pass
```

### 2. 创建应用层 (Application Layer)

```python
# application/commands/create_skill.py
from uuid import UUID

from application.interfaces.unit_of_work import UnitOfWork
from domain.aggregates.skill import Skill
from domain.value_objects.slug import Slug
from domain.repositories.skill_repository import SkillRepository
from domain.exceptions import SkillAlreadyExistsError

class CreateSkillCommand:
    def __init__(self, user_id: UUID, name: str, description: str):
        self.user_id = user_id
        self.name = name
        self.description = description

class CreateSkillHandler:
    def __init__(
        self,
        skill_repo: SkillRepository,
        uow: UnitOfWork,
    ):
        self.skill_repo = skill_repo
        self.uow = uow
    
    async def handle(self, command: CreateSkillCommand) -> Skill:
        # 生成 slug
        slug = Slug.from_name(command.name)
        
        # 业务规则：检查 slug 是否已存在
        existing = await self.skill_repo.get_by_slug(slug, command.user_id)
        if existing:
            raise SkillAlreadyExistsError(f"Skill with slug '{slug}' already exists")
        
        # 创建领域对象
        skill = Skill.create(
            user_id=command.user_id,
            name=command.name,
            slug=slug,
            description=command.description,
        )
        
        # 保存
        await self.skill_repo.save(skill)
        await self.uow.commit()
        
        # 发布领域事件
        for event in skill.pull_events():
            await self.uow.publish(event)
        
        return skill
```

### 3. 基础设施层实现

```python
# infrastructure/persistence/repositories/sql_skill_repository.py
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from domain.repositories.skill_repository import SkillRepository
from domain.aggregates.skill import Skill
from domain.value_objects.slug import Slug
from infrastructure.persistence.mappers.skill_mapper import SkillMapper
from infrastructure.persistence.models.skill_model import SkillModel

class SqlSkillRepository(SkillRepository):
    def __init__(self, session: AsyncSession):
        self.session = session
        self.mapper = SkillMapper()
    
    async def get_by_id(self, skill_id: UUID) -> Skill | None:
        result = await self.session.get(SkillModel, skill_id)
        return self.mapper.to_domain(result) if result else None
    
    async def get_by_slug(self, slug: Slug, user_id: UUID) -> Skill | None:
        result = await self.session.execute(
            select(SkillModel).where(
                SkillModel.slug == str(slug),
                SkillModel.user_id == user_id
            )
        )
        model = result.scalar_one_or_none()
        return self.mapper.to_domain(model) if model else None
    
    async def save(self, skill: Skill) -> None:
        model = self.mapper.to_model(skill)
        await self.session.merge(model)
```

### 4. API层适配器

```python
# api/routers/skills.py
from fastapi import APIRouter, Depends

from application.commands.create_skill import CreateSkillCommand, CreateSkillHandler
from api.dependencies import get_create_skill_handler
from api.schemas.skill import SkillCreateRequest, SkillResponse

router = APIRouter(prefix="/skills")

@router.post("", response_model=SkillResponse)
async def create_skill(
    request: SkillCreateRequest,
    handler: CreateSkillHandler = Depends(get_create_skill_handler),
) -> SkillResponse:
    command = CreateSkillCommand(
        user_id=request.user_id,
        name=request.name,
        description=request.description,
    )
    skill = await handler.handle(command)
    return SkillResponse.from_domain(skill)
```

---

## 🏗️ 重构步骤建议

### 阶段1: 建立领域层 (2-3周)
- [ ] 创建 `domain/` 目录结构
- [ ] 提取值对象 (Slug, Path, Email)
- [ ] 重构 Skill 为富实体
- [ ] 定义仓库接口

### 阶段2: 建立应用层 (1-2周)
- [ ] 创建命令/查询对象
- [ ] 实现命令处理器
- [ ] 添加领域事件支持

### 阶段3: 基础设施迁移 (2-3周)
- [ ] 实现 SQLAlchemy 仓库
- [ ] 添加领域-ORM 映射器
- [ ] 实现工作单元 (Unit of Work)

### 阶段4: API层重构 (1-2周)
- [ ] 适配新应用层
- [ ] 移除旧服务层
- [ ] 端到端测试

---

## ⚠️ 风险与考虑

### 收益
- 业务逻辑集中，易于理解和维护
- 更好的测试性（领域层无外部依赖）
- 更清晰的边界，支持微服务拆分
- 更好的可扩展性

### 挑战
- 学习曲线较陡
- 初期代码量增加
- 需要团队理解DDD概念
- 可能需要引入CQRS/Event Sourcing等进阶模式

### 建议
1. **渐进式重构**: 不要一次性全部重写，逐个模块迁移
2. **从核心域开始**: 先重构 Skill/Tree 核心逻辑
3. **保持旧代码运行**: 使用适配器模式过渡
4. **写足测试**: 重构前确保有充分的测试覆盖
