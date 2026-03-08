# Prompt 分享 + Skill 分享改造 实施计划

> **For Claude:** REQUIRED SUB-SKILL: Use superpowers:executing-plans to implement this plan task-by-task.

**Goal:** 实现 Prompt 的分享/点赞/收藏功能（实时橱窗 + 收藏快照 + 变更提醒），同时将 Skill 分享改造为实时模式（去掉 SharedSkill 快照字段），并在市场页和收藏页增加 Skills/Prompts tab 切换。

**Architecture:** 
- 后端遵循现有 DDD 四层架构：Domain（聚合根/实体/工厂/仓库接口）→ Application（handlers）→ API（routers/schemas/dependencies）→ Infra（ORM 模型/仓库实现）。
- Prompt 分享创建 `SharedPrompt` 聚合根（无快照，实时读取原 Prompt），`PromptLike` 实体，`PromptFavorite` 聚合根（收藏时快照 + version 变更检测）。
- Skill 分享改造去掉 `SharedSkill` 的 snapshot 字段，市场展示改为实时读取原 Skill + User 数据。
- 前端市场页和收藏页增加 tab 切换，新增 Prompt 市场详情页和收藏详情页。

**Tech Stack:** FastAPI (Python) / PostgreSQL / Alembic / Next.js 15 / React 19 / TypeScript / Zustand / next-intl

---

## Part A: Skill 分享改造（去掉快照，改为实时）

### Task 1: 数据库迁移 — SharedSkill 去掉 snapshot 列

**Files:**
- Create: `backend/alembic/versions/20260308000001__remove_shared_skill_snapshots.py`

**Step 1: 创建迁移文件**

```python
"""remove shared skill snapshot columns

Revision ID: v9_remove_shared_skill_snapshots
Revises: v8_skill_favorites
Create Date: 2026-03-08
"""
from alembic import op
import sqlalchemy as sa

revision = "v9_remove_shared_skill_snapshots"
down_revision = "v8_skill_favorites"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.drop_column("shared_skills", "snapshot_name")
    op.drop_column("shared_skills", "snapshot_description")
    op.drop_column("shared_skills", "snapshot_author_name")


def downgrade() -> None:
    op.add_column("shared_skills", sa.Column("snapshot_author_name", sa.String(100), nullable=False, server_default=""))
    op.add_column("shared_skills", sa.Column("snapshot_description", sa.Text(), nullable=True))
    op.add_column("shared_skills", sa.Column("snapshot_name", sa.String(200), nullable=False, server_default=""))
```

**Step 2: 运行迁移**

Run: `cd backend && alembic upgrade head`
Expected: 迁移成功，shared_skills 表去掉三个 snapshot 列

**Step 3: Commit**

```bash
git add backend/alembic/versions/20260308000001__remove_shared_skill_snapshots.py
git commit -m "migrate: remove snapshot columns from shared_skills table"
```

---

### Task 2: 更新 SharedSkill 域模型和工厂

**Files:**
- Modify: `backend/src/domain/aggregates/shared_skill.py`
- Modify: `backend/src/domain/factories/shared_skill_factory.py`
- Modify: `backend/tests/unit/domain/aggregates/test_shared_skill.py` (如果存在)

**Step 1: 写测试 — SharedSkill 不再有 snapshot 字段**

在 `backend/tests/unit/domain/aggregates/test_shared_skill.py` 中确认 SharedSkill 创建不需要 snapshot 参数：

```python
import pytest
from uuid import uuid4
from backend.src.domain.aggregates.shared_skill import SharedSkill


def test_create_shared_skill_without_snapshots():
    skill_id = uuid4()
    user_id = uuid4()
    category_id = uuid4()
    ss = SharedSkill(
        skill_id=skill_id,
        user_id=user_id,
        category_id=category_id,
    )
    assert ss.skill_id == skill_id
    assert ss.user_id == user_id
    assert ss.status == "active"
    assert ss.like_count == 0
    assert not hasattr(ss, 'snapshot_name') or 'snapshot_name' not in ss.__dataclass_fields__


def test_withdraw_sets_status_and_clears_skill_id():
    ss = SharedSkill(skill_id=uuid4(), user_id=uuid4(), category_id=uuid4())
    ss.withdraw()
    assert ss.status == "withdrawn"
    assert ss.skill_id is None


def test_mark_skill_deleted_clears_skill_id_and_withdraws():
    ss = SharedSkill(skill_id=uuid4(), user_id=uuid4(), category_id=uuid4())
    ss.mark_skill_deleted()
    assert ss.skill_id is None
    assert ss.status == "withdrawn"
```

**Step 2: 运行测试确认失败**

Run: `cd backend && python -m pytest tests/unit/domain/aggregates/test_shared_skill.py -v`
Expected: FAIL（当前 SharedSkill 仍有 snapshot 字段）

**Step 3: 更新 SharedSkill 聚合根**

修改 `backend/src/domain/aggregates/shared_skill.py`，去掉 `snapshot_name`、`snapshot_description`、`snapshot_author_name` 字段。同时更新 `mark_skill_deleted()` 使其也将 status 设为 `withdrawn`（原 Skill 删除 → 市场自动下架）：

```python
from dataclasses import dataclass, field
from datetime import datetime, timezone
from uuid import UUID, uuid4


@dataclass
class SharedSkill:
    skill_id: UUID | None = None
    user_id: UUID = field(default_factory=uuid4)
    category_id: UUID = field(default_factory=uuid4)
    share_message: str | None = None
    like_count: int = 0
    favorite_count: int = 0
    status: str = "active"
    id: UUID = field(default_factory=uuid4)
    created_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    updated_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))

    def __post_init__(self):
        if self.status not in ("active", "withdrawn"):
            raise ValueError(f"Invalid status: {self.status}")
        if self.like_count < 0:
            raise ValueError("like_count cannot be negative")
        if self.favorite_count < 0:
            raise ValueError("favorite_count cannot be negative")

    def withdraw(self):
        self.status = "withdrawn"
        self.skill_id = None
        self._mark_updated()

    def mark_skill_deleted(self):
        self.skill_id = None
        self.status = "withdrawn"
        self._mark_updated()

    def increment_like_count(self):
        self.like_count += 1
        self._mark_updated()

    def decrement_like_count(self):
        self.like_count = max(0, self.like_count - 1)
        self._mark_updated()

    def increment_favorite_count(self):
        self.favorite_count += 1
        self._mark_updated()

    def decrement_favorite_count(self):
        self.favorite_count = max(0, self.favorite_count - 1)
        self._mark_updated()

    def _mark_updated(self):
        self.updated_at = datetime.now(timezone.utc)
```

**Step 4: 更新 SharedSkillFactory — 不再做快照**

修改 `backend/src/domain/factories/shared_skill_factory.py`：

```python
from uuid import UUID
from backend.src.domain.aggregates.shared_skill import SharedSkill


class SharedSkillFactory:
    @staticmethod
    def create(
        skill_id: UUID,
        user_id: UUID,
        category_id: UUID,
        share_message: str | None = None,
    ) -> SharedSkill:
        return SharedSkill(
            skill_id=skill_id,
            user_id=user_id,
            category_id=category_id,
            share_message=share_message,
        )
```

**Step 5: 运行测试确认通过**

Run: `cd backend && python -m pytest tests/unit/domain/aggregates/test_shared_skill.py -v`
Expected: PASS

**Step 6: Commit**

```bash
git add backend/src/domain/aggregates/shared_skill.py backend/src/domain/factories/shared_skill_factory.py backend/tests/unit/domain/aggregates/test_shared_skill.py
git commit -m "refactor: remove snapshot fields from SharedSkill, auto-withdraw on skill deletion"
```

---

### Task 3: 更新 SharedSkill ORM 模型和仓库实现

**Files:**
- Modify: `backend/src/infra/persistence/models/shared_skill_model.py`
- Modify: `backend/src/infra/persistence/repositories/sql_shared_skill_repository.py`

**Step 1: 更新 SharedSkillModel — 去掉 snapshot 列**

在 `backend/src/infra/persistence/models/shared_skill_model.py` 中：
- 删除 `snapshot_name`、`snapshot_description`、`snapshot_author_name` 列定义
- 更新 `to_domain()` 和 `from_domain()` 方法，去掉 snapshot 字段映射

**Step 2: 更新 SqlSharedSkillRepository**

在 `backend/src/infra/persistence/repositories/sql_shared_skill_repository.py` 中：
- `find_active_by_filters` 的 keyword 搜索现在不能直接搜 `snapshot_name` 了。需要 join `skills` 表按 `name` 搜索。
- 更新搜索逻辑：

```python
from backend.src.infra.persistence.models.skill_model import SkillModel

# 在 find_active_by_filters 中
if keyword:
    stmt = stmt.join(SkillModel, SharedSkillModel.skill_id == SkillModel.id, isouter=True)
    stmt = stmt.where(
        sa.or_(
            SkillModel.name.ilike(f"%{keyword}%"),
            SkillModel.description.ilike(f"%{keyword}%"),
        )
    )
```

注意：count 查询也需要同样的 join。

**Step 3: 运行现有测试确认无破坏**

Run: `cd backend && python -m pytest tests/unit -v --ignore=tests/unit/core/test_auth.py --ignore=tests/unit/core/test_main.py --ignore=tests/unit/infra/persistence/db/test_db_session.py`
Expected: PASS（可能有 snapshot 相关测试需要同步更新）

**Step 4: Commit**

```bash
git add backend/src/infra/persistence/models/shared_skill_model.py backend/src/infra/persistence/repositories/sql_shared_skill_repository.py
git commit -m "refactor: update SharedSkill ORM model and repository for live data mode"
```

---

### Task 4: 更新 SharedSkill API Schema 和路由

**Files:**
- Modify: `backend/src/api/schemas/shared_skill.py`
- Modify: `backend/src/api/routers/market.py`
- Modify: `backend/src/application/handlers/shared_skill_handlers.py`

**Step 1: 更新 API Schema**

修改 `backend/src/api/schemas/shared_skill.py`：
- `ShareSkillResp` 去掉 `snapshot_name`、`snapshot_description`、`snapshot_author_name`
- `MarketSkillResp` 新增 `name`、`description`、`author_name` 字段（从实时数据填充）
- 保持 `FavoriteResp` 不变（收藏仍用快照）

```python
class MarketSkillResp(BaseModel):
    id: UUID
    skill_id: UUID | None
    user_id: UUID
    name: str  # 实时从 Skill 读取
    description: str | None  # 实时从 Skill 读取
    author_name: str  # 实时从 User 读取
    category_id: UUID
    share_message: str | None
    like_count: int
    favorite_count: int
    status: str
    created_at: datetime
    is_liked: bool = False
    is_favorited: bool = False
    category: CategoryResp | None = None
```

**Step 2: 更新市场路由 — 列表和详情接口实时读取**

修改 `backend/src/api/routers/market.py`：
- `GET /market/skills` 列表接口：需要在返回数据中加入实时的 name/description/author_name。可以在 handler 层或路由层 join 查询。
- `GET /market/skills/{id}` 详情接口：通过 `shared_skill.skill_id` 读取原 Skill 和 User 数据。

详情接口改造：

```python
@router.get("/market/skills/{shared_skill_id}", response_model=MarketSkillResp)
async def get_market_skill_detail(
    shared_skill_id: Annotated[UUID, Path()],
    shared_skill_repo: Annotated[SharedSkillRepository, Depends(get_shared_skill_repo)],
    skill_repo: Annotated[SkillRepository, Depends(get_skill_repo)],
    user_repo: Annotated[UserRepository, Depends(get_user_repo)],
    current_user: Annotated[User | None, Depends(get_optional_current_user)],
):
    shared_skill = shared_skill_repo.find_by_id(shared_skill_id)
    if not shared_skill:
        raise HTTPException(status_code=404)
    
    # 实时读取 Skill 和 User
    name, description, author_name = "", None, ""
    if shared_skill.skill_id:
        skill = await skill_repo.get_by_id(shared_skill.skill_id)
        if skill:
            name = skill.name
            description = skill.description
        user = await user_repo.get_by_id(shared_skill.user_id)
        if user:
            author_name = user.username
    
    # 检查 is_liked, is_favorited
    is_liked = False
    is_favorited = False
    if current_user:
        like = await shared_skill_repo.find_like(current_user.id, shared_skill.id)
        is_liked = like is not None
        fav = await favorite_repo.find_by_user_and_shared_skill(current_user.id, shared_skill.id)
        is_favorited = fav is not None
    
    return MarketSkillResp(
        id=shared_skill.id,
        skill_id=shared_skill.skill_id,
        user_id=shared_skill.user_id,
        name=name,
        description=description,
        author_name=author_name,
        # ... 其余字段
    )
```

**Step 3: 更新 share_skill_handler — 工厂不再需要 skill/user 对象做快照**

修改 `backend/src/application/handlers/shared_skill_handlers.py`：
- `SharedSkillFactory.create()` 现在只需要 `skill_id`, `user_id`, `category_id`, `share_message`
- 不再传入完整的 `skill` 和 `user` 对象

**Step 4: 更新 delete_skill_handler — 级联处理 SharedSkill 和 Favorites**

修改 `backend/src/application/handlers/delete_skill_handler.py`：
- 删除 Skill 时，找到关联的 SharedSkill，调用 `mark_skill_deleted()`（自动 withdraw）
- 批量更新关联的 SkillFavorite 状态为 `skill_deleted`

```python
# 在 handle_delete_skill 中添加
shared_skills = await shared_skill_repo.find_all_by_skill_id(skill.id)
for ss in shared_skills:
    ss.mark_skill_deleted()
    await shared_skill_repo.save(ss)
    await favorite_repo.update_snapshot_status_batch(ss.id, "skill_deleted")
```

**Step 5: 运行测试**

Run: `cd backend && python -m pytest tests/unit -v --ignore=tests/unit/core/test_auth.py --ignore=tests/unit/core/test_main.py --ignore=tests/unit/infra/persistence/db/test_db_session.py`
Expected: PASS

**Step 6: Commit**

```bash
git add backend/src/api/schemas/shared_skill.py backend/src/api/routers/market.py backend/src/application/handlers/shared_skill_handlers.py backend/src/application/handlers/delete_skill_handler.py
git commit -m "refactor: market API reads live Skill/User data, cascade delete SharedSkill on skill deletion"
```

---

### Task 5: 更新前端 SharedSkillDetail 和市场列表页

**Files:**
- Modify: `frontend/components/market/SharedSkillDetail.tsx`
- Modify: `frontend/app/[locale]/market/page.tsx`
- Modify: `frontend/types/market.ts`

**Step 1: 更新 TypeScript 类型**

在 `frontend/types/market.ts` 中，更新 `SharedSkill` 类型：
- 去掉 `snapshot_name`、`snapshot_description`、`snapshot_author_name`
- 新增 `name`、`description`、`author_name`

```typescript
export interface SharedSkill {
  id: string;
  skill_id: string | null;
  user_id: string;
  name: string;           // 实时数据
  description: string | null;  // 实时数据
  author_name: string;    // 实时数据
  category_id: string;
  share_message: string | null;
  like_count: number;
  favorite_count: number;
  status: string;
  created_at: string;
  is_liked?: boolean;
  is_favorited?: boolean;
  category?: Category;
}
```

**Step 2: 更新 SharedSkillDetail 组件**

在 `frontend/components/market/SharedSkillDetail.tsx` 中：
- 将所有 `skill.snapshot_name` 替换为 `skill.name`
- 将 `skill.snapshot_description` 替换为 `skill.description`
- 将 `skill.snapshot_author_name` 替换为 `skill.author_name`

**Step 3: 更新市场列表页**

在 `frontend/app/[locale]/market/page.tsx` 和相关的 `MarketSkillCard` 组件中，同样替换 snapshot 字段为实时字段。

**Step 4: 更新收藏页面**

`frontend/app/[locale]/favorites/page.tsx` **不需要改**——收藏仍然使用快照数据（`snapshot_name` 等），这些数据来自 `SkillFavorite` 而非 `SharedSkill`。

**Step 5: 验证构建**

Run: `cd frontend && npx next build`
Expected: 构建成功

**Step 6: Commit**

```bash
git add frontend/types/market.ts frontend/components/market/SharedSkillDetail.tsx frontend/app/\[locale\]/market/page.tsx
git commit -m "refactor: frontend uses live data instead of snapshots for market display"
```

---

## Part B: Prompt 分享功能（新建）

### Task 6: 数据库迁移 — 创建 shared_prompts、prompt_likes、prompt_favorites 表

**Files:**
- Create: `backend/alembic/versions/20260308000002__create_shared_prompts.py`
- Create: `backend/alembic/versions/20260308000003__create_prompt_favorites.py`

**Step 1: 创建 shared_prompts + prompt_likes 迁移**

```python
"""create shared_prompts and prompt_likes tables

Revision ID: v10_shared_prompts
Revises: v9_remove_shared_skill_snapshots
Create Date: 2026-03-08
"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects.postgresql import UUID

revision = "v10_shared_prompts"
down_revision = "v9_remove_shared_skill_snapshots"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "shared_prompts",
        sa.Column("id", UUID(as_uuid=True), primary_key=True),
        sa.Column("prompt_id", UUID(as_uuid=True), sa.ForeignKey("prompts.id", ondelete="SET NULL"), nullable=True),
        sa.Column("user_id", UUID(as_uuid=True), sa.ForeignKey("users.id", ondelete="CASCADE"), nullable=False),
        sa.Column("share_message", sa.Text(), nullable=True),
        sa.Column("like_count", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("favorite_count", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("status", sa.String(20), nullable=False, server_default="active"),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
    )
    op.create_index("ix_shared_prompts_status", "shared_prompts", ["status"])
    op.create_index("ix_shared_prompts_user_id", "shared_prompts", ["user_id"])

    op.create_table(
        "prompt_likes",
        sa.Column("id", UUID(as_uuid=True), primary_key=True),
        sa.Column("user_id", UUID(as_uuid=True), sa.ForeignKey("users.id", ondelete="CASCADE"), nullable=False),
        sa.Column("shared_prompt_id", UUID(as_uuid=True), sa.ForeignKey("shared_prompts.id", ondelete="CASCADE"), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
        sa.UniqueConstraint("user_id", "shared_prompt_id", name="uq_prompt_likes_user_shared_prompt"),
    )


def downgrade() -> None:
    op.drop_table("prompt_likes")
    op.drop_table("shared_prompts")
```

**Step 2: 创建 prompt_favorites 迁移**

```python
"""create prompt_favorites table

Revision ID: v11_prompt_favorites
Revises: v10_shared_prompts
Create Date: 2026-03-08
"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects.postgresql import UUID, ARRAY

revision = "v11_prompt_favorites"
down_revision = "v10_shared_prompts"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "prompt_favorites",
        sa.Column("id", UUID(as_uuid=True), primary_key=True),
        sa.Column("user_id", UUID(as_uuid=True), sa.ForeignKey("users.id", ondelete="CASCADE"), nullable=False),
        sa.Column("shared_prompt_id", UUID(as_uuid=True), nullable=True),
        sa.Column("snapshot_title", sa.String(200), nullable=False),
        sa.Column("snapshot_content", sa.Text(), nullable=False),
        sa.Column("snapshot_description", sa.Text(), nullable=True),
        sa.Column("snapshot_tags", ARRAY(sa.String()), nullable=False, server_default="{}"),
        sa.Column("snapshot_author_name", sa.String(100), nullable=False),
        sa.Column("snapshot_version", sa.Integer(), nullable=False),
        sa.Column("snapshot_status", sa.String(30), nullable=False, server_default="active"),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
        sa.UniqueConstraint("user_id", "shared_prompt_id", name="uq_prompt_favorites_user_shared_prompt"),
    )
    op.create_index("ix_prompt_favorites_user_id", "prompt_favorites", ["user_id"])


def downgrade() -> None:
    op.drop_table("prompt_favorites")
```

**Step 3: 运行迁移**

Run: `cd backend && alembic upgrade head`
Expected: 3 张新表创建成功

**Step 4: Commit**

```bash
git add backend/alembic/versions/20260308000002__create_shared_prompts.py backend/alembic/versions/20260308000003__create_prompt_favorites.py
git commit -m "migrate: create shared_prompts, prompt_likes, prompt_favorites tables"
```

---

### Task 7: SharedPrompt 域模型 + 工厂 + 仓库接口

**Files:**
- Create: `backend/src/domain/aggregates/shared_prompt.py`
- Create: `backend/src/domain/factories/shared_prompt_factory.py`
- Create: `backend/src/domain/entities/prompt_like.py`
- Create: `backend/src/domain/repositories/shared_prompt_repository.py`
- Create: `backend/tests/unit/domain/aggregates/test_shared_prompt.py`

**Step 1: 写测试**

```python
# backend/tests/unit/domain/aggregates/test_shared_prompt.py
import pytest
from uuid import uuid4
from backend.src.domain.aggregates.shared_prompt import SharedPrompt
from backend.src.domain.factories.shared_prompt_factory import SharedPromptFactory


def test_create_shared_prompt():
    prompt_id = uuid4()
    user_id = uuid4()
    sp = SharedPrompt(prompt_id=prompt_id, user_id=user_id)
    assert sp.prompt_id == prompt_id
    assert sp.user_id == user_id
    assert sp.status == "active"
    assert sp.like_count == 0
    assert sp.favorite_count == 0


def test_factory_create():
    prompt_id = uuid4()
    user_id = uuid4()
    sp = SharedPromptFactory.create(prompt_id=prompt_id, user_id=user_id, share_message="hello")
    assert sp.prompt_id == prompt_id
    assert sp.share_message == "hello"


def test_withdraw():
    sp = SharedPrompt(prompt_id=uuid4(), user_id=uuid4())
    sp.withdraw()
    assert sp.status == "withdrawn"
    assert sp.prompt_id is None


def test_mark_prompt_deleted():
    sp = SharedPrompt(prompt_id=uuid4(), user_id=uuid4())
    sp.mark_prompt_deleted()
    assert sp.prompt_id is None
    assert sp.status == "withdrawn"


def test_increment_decrement_like():
    sp = SharedPrompt(prompt_id=uuid4(), user_id=uuid4())
    sp.increment_like_count()
    assert sp.like_count == 1
    sp.decrement_like_count()
    assert sp.like_count == 0
    sp.decrement_like_count()
    assert sp.like_count == 0  # 不会负


def test_increment_decrement_favorite():
    sp = SharedPrompt(prompt_id=uuid4(), user_id=uuid4())
    sp.increment_favorite_count()
    assert sp.favorite_count == 1
    sp.decrement_favorite_count()
    assert sp.favorite_count == 0


def test_invalid_status():
    with pytest.raises(ValueError):
        SharedPrompt(prompt_id=uuid4(), user_id=uuid4(), status="invalid")
```

**Step 2: 运行测试确认失败**

Run: `cd backend && python -m pytest tests/unit/domain/aggregates/test_shared_prompt.py -v`
Expected: FAIL（模块不存在）

**Step 3: 实现 SharedPrompt 聚合根**

```python
# backend/src/domain/aggregates/shared_prompt.py
from dataclasses import dataclass, field
from datetime import datetime, timezone
from uuid import UUID, uuid4


@dataclass
class SharedPrompt:
    prompt_id: UUID | None = None
    user_id: UUID = field(default_factory=uuid4)
    share_message: str | None = None
    like_count: int = 0
    favorite_count: int = 0
    status: str = "active"
    id: UUID = field(default_factory=uuid4)
    created_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    updated_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))

    def __post_init__(self):
        if self.status not in ("active", "withdrawn"):
            raise ValueError(f"Invalid status: {self.status}")
        if self.like_count < 0:
            raise ValueError("like_count cannot be negative")
        if self.favorite_count < 0:
            raise ValueError("favorite_count cannot be negative")

    def withdraw(self):
        self.status = "withdrawn"
        self.prompt_id = None
        self._mark_updated()

    def mark_prompt_deleted(self):
        self.prompt_id = None
        self.status = "withdrawn"
        self._mark_updated()

    def increment_like_count(self):
        self.like_count += 1
        self._mark_updated()

    def decrement_like_count(self):
        self.like_count = max(0, self.like_count - 1)
        self._mark_updated()

    def increment_favorite_count(self):
        self.favorite_count += 1
        self._mark_updated()

    def decrement_favorite_count(self):
        self.favorite_count = max(0, self.favorite_count - 1)
        self._mark_updated()

    def _mark_updated(self):
        self.updated_at = datetime.now(timezone.utc)
```

**Step 4: 实现 SharedPromptFactory**

```python
# backend/src/domain/factories/shared_prompt_factory.py
from uuid import UUID
from backend.src.domain.aggregates.shared_prompt import SharedPrompt


class SharedPromptFactory:
    @staticmethod
    def create(
        prompt_id: UUID,
        user_id: UUID,
        share_message: str | None = None,
    ) -> SharedPrompt:
        return SharedPrompt(
            prompt_id=prompt_id,
            user_id=user_id,
            share_message=share_message,
        )
```

**Step 5: 实现 PromptLike 实体**

```python
# backend/src/domain/entities/prompt_like.py
from dataclasses import dataclass, field
from datetime import datetime, timezone
from uuid import UUID, uuid4


@dataclass
class PromptLike:
    user_id: UUID = field(default_factory=uuid4)
    shared_prompt_id: UUID = field(default_factory=uuid4)
    id: UUID = field(default_factory=uuid4)
    created_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
```

**Step 6: 实现 SharedPromptRepository 接口**

```python
# backend/src/domain/repositories/shared_prompt_repository.py
from abc import ABC, abstractmethod
from uuid import UUID
from backend.src.domain.aggregates.shared_prompt import SharedPrompt
from backend.src.domain.entities.prompt_like import PromptLike


class SharedPromptRepository(ABC):
    @abstractmethod
    async def save(self, shared_prompt: SharedPrompt) -> SharedPrompt: ...

    @abstractmethod
    async def find_by_id(self, id: UUID) -> SharedPrompt | None: ...

    @abstractmethod
    async def find_by_prompt_id(self, prompt_id: UUID) -> SharedPrompt | None: ...

    @abstractmethod
    async def find_by_user_and_prompt(self, user_id: UUID, prompt_id: UUID) -> SharedPrompt | None: ...

    @abstractmethod
    async def find_all_by_prompt_id(self, prompt_id: UUID) -> list[SharedPrompt]: ...

    @abstractmethod
    async def find_active_by_filters(
        self, keyword: str | None, tags: list[str] | None, sort_by: str, skip: int, limit: int
    ) -> list[SharedPrompt]: ...

    @abstractmethod
    async def count_active_by_filters(self, keyword: str | None, tags: list[str] | None) -> int: ...

    @abstractmethod
    async def delete(self, shared_prompt_id: UUID) -> None: ...

    # Like 操作
    @abstractmethod
    async def find_like(self, user_id: UUID, shared_prompt_id: UUID) -> PromptLike | None: ...

    @abstractmethod
    async def save_like(self, like: PromptLike) -> PromptLike: ...

    @abstractmethod
    async def delete_like(self, user_id: UUID, shared_prompt_id: UUID) -> None: ...

    @abstractmethod
    async def increment_like_count(self, shared_prompt_id: UUID) -> None: ...

    @abstractmethod
    async def decrement_like_count(self, shared_prompt_id: UUID) -> None: ...

    @abstractmethod
    async def increment_favorite_count(self, shared_prompt_id: UUID) -> None: ...

    @abstractmethod
    async def decrement_favorite_count(self, shared_prompt_id: UUID) -> None: ...
```

**Step 7: 运行测试确认通过**

Run: `cd backend && python -m pytest tests/unit/domain/aggregates/test_shared_prompt.py -v`
Expected: PASS

**Step 8: Commit**

```bash
git add backend/src/domain/aggregates/shared_prompt.py backend/src/domain/factories/shared_prompt_factory.py backend/src/domain/entities/prompt_like.py backend/src/domain/repositories/shared_prompt_repository.py backend/tests/unit/domain/aggregates/test_shared_prompt.py
git commit -m "feat: add SharedPrompt aggregate, PromptLike entity, factory, and repository interface"
```

---

### Task 8: PromptFavorite 域模型 + 工厂 + 仓库接口

**Files:**
- Create: `backend/src/domain/aggregates/prompt_favorite.py`
- Create: `backend/src/domain/factories/prompt_favorite_factory.py`
- Create: `backend/src/domain/repositories/prompt_favorite_repository.py`
- Create: `backend/tests/unit/domain/aggregates/test_prompt_favorite.py`

**Step 1: 写测试**

```python
# backend/tests/unit/domain/aggregates/test_prompt_favorite.py
import pytest
from uuid import uuid4
from backend.src.domain.aggregates.prompt_favorite import PromptFavorite
from backend.src.domain.factories.prompt_favorite_factory import PromptFavoriteFactory
from unittest.mock import MagicMock


def test_create_prompt_favorite():
    pf = PromptFavorite(
        user_id=uuid4(),
        shared_prompt_id=uuid4(),
        snapshot_title="Test",
        snapshot_content="# Hello",
        snapshot_description="A test prompt",
        snapshot_tags=["python", "test"],
        snapshot_author_name="user1",
        snapshot_version=3,
    )
    assert pf.snapshot_status == "active"
    assert pf.snapshot_version == 3


def test_mark_prompt_withdrawn():
    pf = PromptFavorite(
        user_id=uuid4(),
        shared_prompt_id=uuid4(),
        snapshot_title="Test",
        snapshot_content="content",
        snapshot_author_name="user1",
        snapshot_version=1,
    )
    pf.mark_prompt_withdrawn()
    assert pf.snapshot_status == "prompt_withdrawn"


def test_mark_prompt_deleted():
    pf = PromptFavorite(
        user_id=uuid4(),
        shared_prompt_id=uuid4(),
        snapshot_title="Test",
        snapshot_content="content",
        snapshot_author_name="user1",
        snapshot_version=1,
    )
    pf.mark_prompt_deleted()
    assert pf.snapshot_status == "prompt_deleted"
    assert pf.shared_prompt_id is None


def test_is_version_stale():
    pf = PromptFavorite(
        user_id=uuid4(),
        shared_prompt_id=uuid4(),
        snapshot_title="Test",
        snapshot_content="content",
        snapshot_author_name="user1",
        snapshot_version=3,
    )
    assert pf.is_version_stale(5) is True
    assert pf.is_version_stale(3) is False
    assert pf.is_version_stale(2) is False


def test_refresh_snapshot():
    pf = PromptFavorite(
        user_id=uuid4(),
        shared_prompt_id=uuid4(),
        snapshot_title="Old Title",
        snapshot_content="Old Content",
        snapshot_description="Old Desc",
        snapshot_tags=["old"],
        snapshot_author_name="user1",
        snapshot_version=1,
    )
    pf.refresh_snapshot(
        title="New Title",
        content="New Content",
        description="New Desc",
        tags=["new", "updated"],
        version=5,
    )
    assert pf.snapshot_title == "New Title"
    assert pf.snapshot_content == "New Content"
    assert pf.snapshot_description == "New Desc"
    assert pf.snapshot_tags == ["new", "updated"]
    assert pf.snapshot_version == 5


def test_factory_create():
    prompt = MagicMock()
    prompt.title = "My Prompt"
    prompt.content = "# Hello World"
    prompt.description = "A great prompt"
    prompt.tags = ["python"]
    prompt.version = 3

    user = MagicMock()
    user.username = "author1"

    shared_prompt_id = uuid4()
    user_id = uuid4()

    pf = PromptFavoriteFactory.create(
        user_id=user_id,
        shared_prompt_id=shared_prompt_id,
        prompt=prompt,
        author=user,
    )
    assert pf.user_id == user_id
    assert pf.shared_prompt_id == shared_prompt_id
    assert pf.snapshot_title == "My Prompt"
    assert pf.snapshot_content == "# Hello World"
    assert pf.snapshot_tags == ["python"]
    assert pf.snapshot_version == 3
    assert pf.snapshot_author_name == "author1"
```

**Step 2: 运行测试确认失败**

Run: `cd backend && python -m pytest tests/unit/domain/aggregates/test_prompt_favorite.py -v`
Expected: FAIL

**Step 3: 实现 PromptFavorite 聚合根**

```python
# backend/src/domain/aggregates/prompt_favorite.py
from dataclasses import dataclass, field
from datetime import datetime, timezone
from uuid import UUID, uuid4


@dataclass
class PromptFavorite:
    user_id: UUID = field(default_factory=uuid4)
    shared_prompt_id: UUID | None = None
    snapshot_title: str = ""
    snapshot_content: str = ""
    snapshot_description: str | None = None
    snapshot_tags: list[str] = field(default_factory=list)
    snapshot_author_name: str = ""
    snapshot_version: int = 1
    snapshot_status: str = "active"
    id: UUID = field(default_factory=uuid4)
    created_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))

    def mark_prompt_withdrawn(self):
        self.snapshot_status = "prompt_withdrawn"

    def mark_prompt_deleted(self):
        self.snapshot_status = "prompt_deleted"
        self.shared_prompt_id = None

    def is_version_stale(self, current_version: int) -> bool:
        return current_version > self.snapshot_version

    def refresh_snapshot(
        self,
        title: str,
        content: str,
        description: str | None,
        tags: list[str],
        version: int,
    ):
        self.snapshot_title = title
        self.snapshot_content = content
        self.snapshot_description = description
        self.snapshot_tags = tags
        self.snapshot_version = version
        self.snapshot_status = "active"
```

**Step 4: 实现 PromptFavoriteFactory**

```python
# backend/src/domain/factories/prompt_favorite_factory.py
from uuid import UUID
from backend.src.domain.aggregates.prompt_favorite import PromptFavorite
from backend.src.domain.aggregates.prompt import Prompt


class PromptFavoriteFactory:
    @staticmethod
    def create(
        user_id: UUID,
        shared_prompt_id: UUID,
        prompt: Prompt,
        author,  # User object
    ) -> PromptFavorite:
        return PromptFavorite(
            user_id=user_id,
            shared_prompt_id=shared_prompt_id,
            snapshot_title=prompt.title,
            snapshot_content=prompt.content,
            snapshot_description=prompt.description,
            snapshot_tags=list(prompt.tags),
            snapshot_author_name=author.username,
            snapshot_version=prompt.version,
        )
```

**Step 5: 实现 PromptFavoriteRepository 接口**

```python
# backend/src/domain/repositories/prompt_favorite_repository.py
from abc import ABC, abstractmethod
from uuid import UUID
from backend.src.domain.aggregates.prompt_favorite import PromptFavorite


class PromptFavoriteRepository(ABC):
    @abstractmethod
    async def save(self, favorite: PromptFavorite) -> PromptFavorite: ...

    @abstractmethod
    async def delete(self, user_id: UUID, shared_prompt_id: UUID) -> None: ...

    @abstractmethod
    async def find_by_user_and_shared_prompt(self, user_id: UUID, shared_prompt_id: UUID) -> PromptFavorite | None: ...

    @abstractmethod
    async def find_by_user(self, user_id: UUID, skip: int = 0, limit: int = 20) -> list[PromptFavorite]: ...

    @abstractmethod
    async def count_by_user(self, user_id: UUID) -> int: ...

    @abstractmethod
    async def find_all_by_shared_prompt_id(self, shared_prompt_id: UUID) -> list[PromptFavorite]: ...

    @abstractmethod
    async def update_snapshot_status_batch(self, shared_prompt_id: UUID, new_status: str) -> None: ...
```

**Step 6: 运行测试确认通过**

Run: `cd backend && python -m pytest tests/unit/domain/aggregates/test_prompt_favorite.py -v`
Expected: PASS

**Step 7: Commit**

```bash
git add backend/src/domain/aggregates/prompt_favorite.py backend/src/domain/factories/prompt_favorite_factory.py backend/src/domain/repositories/prompt_favorite_repository.py backend/tests/unit/domain/aggregates/test_prompt_favorite.py
git commit -m "feat: add PromptFavorite aggregate with version-based change detection"
```

---

### Task 9: SharedPrompt + PromptLike + PromptFavorite ORM 模型和仓库实现

**Files:**
- Create: `backend/src/infra/persistence/models/shared_prompt_model.py`
- Create: `backend/src/infra/persistence/models/prompt_favorite_model.py`
- Create: `backend/src/infra/persistence/repositories/sql_shared_prompt_repository.py`
- Create: `backend/src/infra/persistence/repositories/sql_prompt_favorite_repository.py`

**Step 1: 实现 SharedPromptModel + PromptLikeModel**

参照 `shared_skill_model.py` 的模式创建，包含 `to_domain()`/`from_domain()` 转换。

`SharedPromptModel`:
- 表名: `shared_prompts`
- 字段映射: `id`, `prompt_id`, `user_id`, `share_message`, `like_count`, `favorite_count`, `status`, `created_at`, `updated_at`

`PromptLikeModel`:
- 表名: `prompt_likes`
- 字段映射: `id`, `user_id`, `shared_prompt_id`, `created_at`

**Step 2: 实现 PromptFavoriteModel**

参照 `skill_favorite_model.py` 的模式：
- 表名: `prompt_favorites`
- 字段映射: 所有 snapshot 字段 + 基本字段
- `snapshot_tags` 使用 `ARRAY(String())`

**Step 3: 实现 SqlSharedPromptRepository**

参照 `sql_shared_skill_repository.py`，实现所有 `SharedPromptRepository` 接口方法。
- `find_active_by_filters` 需要 join `prompts` 表按 title/content 搜索，支持 tags 过滤（使用 PostgreSQL ARRAY `@>` 操作符或 `ANY`）
- Like 操作同 SkillLike 模式

**Step 4: 实现 SqlPromptFavoriteRepository**

参照 `sql_skill_favorite_repository.py` 实现。

**Step 5: Commit**

```bash
git add backend/src/infra/persistence/models/shared_prompt_model.py backend/src/infra/persistence/models/prompt_favorite_model.py backend/src/infra/persistence/repositories/sql_shared_prompt_repository.py backend/src/infra/persistence/repositories/sql_prompt_favorite_repository.py
git commit -m "feat: add ORM models and SQL repositories for SharedPrompt, PromptLike, PromptFavorite"
```

---

### Task 10: Prompt 分享/取消分享 Handler

**Files:**
- Create: `backend/src/application/handlers/shared_prompt_handlers.py`
- Create: `backend/tests/unit/application/handlers/test_shared_prompt_handlers.py`

**Step 1: 写测试**

```python
# backend/tests/unit/application/handlers/test_shared_prompt_handlers.py
import pytest
from uuid import uuid4
from unittest.mock import AsyncMock, MagicMock
from backend.src.application.handlers.shared_prompt_handlers import (
    handle_share_prompt,
    handle_unshare_prompt,
)


@pytest.mark.asyncio
async def test_share_prompt_success():
    prompt = MagicMock()
    prompt.id = uuid4()
    prompt.user_id = uuid4()

    user = MagicMock()
    user.id = prompt.user_id

    prompt_repo = AsyncMock()
    prompt_repo.get_by_id.return_value = prompt

    shared_prompt_repo = AsyncMock()
    shared_prompt_repo.find_by_user_and_prompt.return_value = None
    shared_prompt_repo.save.side_effect = lambda sp: sp

    result = await handle_share_prompt(
        prompt_id=prompt.id,
        user=user,
        prompt_repo=prompt_repo,
        shared_prompt_repo=shared_prompt_repo,
    )
    assert result.prompt_id == prompt.id
    assert result.user_id == user.id
    assert result.status == "active"


@pytest.mark.asyncio
async def test_share_prompt_not_owner():
    prompt = MagicMock()
    prompt.id = uuid4()
    prompt.user_id = uuid4()

    user = MagicMock()
    user.id = uuid4()  # different user

    prompt_repo = AsyncMock()
    prompt_repo.get_by_id.return_value = prompt

    shared_prompt_repo = AsyncMock()

    with pytest.raises(Exception):  # PermissionError or similar
        await handle_share_prompt(
            prompt_id=prompt.id,
            user=user,
            prompt_repo=prompt_repo,
            shared_prompt_repo=shared_prompt_repo,
        )


@pytest.mark.asyncio
async def test_unshare_prompt_success():
    shared_prompt = MagicMock()
    shared_prompt.id = uuid4()
    shared_prompt.user_id = uuid4()
    shared_prompt.prompt_id = uuid4()

    user = MagicMock()
    user.id = shared_prompt.user_id

    prompt_repo = AsyncMock()
    prompt = MagicMock()
    prompt.id = shared_prompt.prompt_id
    prompt.user_id = shared_prompt.user_id
    prompt_repo.get_by_id.return_value = prompt

    shared_prompt_repo = AsyncMock()
    shared_prompt_repo.find_by_prompt_id.return_value = shared_prompt
    shared_prompt_repo.save.side_effect = lambda sp: sp

    favorite_repo = AsyncMock()

    result = await handle_unshare_prompt(
        prompt_id=prompt.id,
        user=user,
        shared_prompt_repo=shared_prompt_repo,
        prompt_repo=prompt_repo,
        favorite_repo=favorite_repo,
    )
    shared_prompt.withdraw.assert_called_once()
    favorite_repo.update_snapshot_status_batch.assert_called_once()
```

**Step 2: 实现 handler**

```python
# backend/src/application/handlers/shared_prompt_handlers.py
from uuid import UUID
from backend.src.domain.factories.shared_prompt_factory import SharedPromptFactory
from backend.src.api.dependencies.repositories import ResourceNotFoundError, ResourceConflictError, PermissionDeniedError


async def handle_share_prompt(prompt_id, user, prompt_repo, shared_prompt_repo):
    prompt = await prompt_repo.get_by_id(prompt_id)
    if not prompt:
        raise ResourceNotFoundError("Prompt not found")
    if prompt.user_id != user.id:
        raise PermissionDeniedError("Not the owner")
    
    existing = await shared_prompt_repo.find_by_user_and_prompt(user.id, prompt_id)
    if existing and existing.status == "active":
        raise ResourceConflictError("Prompt already shared")
    
    shared_prompt = SharedPromptFactory.create(
        prompt_id=prompt.id,
        user_id=user.id,
    )
    return await shared_prompt_repo.save(shared_prompt)


async def handle_unshare_prompt(prompt_id, user, shared_prompt_repo, prompt_repo, favorite_repo):
    prompt = await prompt_repo.get_by_id(prompt_id)
    if not prompt:
        raise ResourceNotFoundError("Prompt not found")
    if prompt.user_id != user.id:
        raise PermissionDeniedError("Not the owner")
    
    shared_prompt = await shared_prompt_repo.find_by_prompt_id(prompt_id)
    if not shared_prompt or shared_prompt.status != "active":
        raise ResourceNotFoundError("No active share found")
    
    shared_prompt.withdraw()
    await shared_prompt_repo.save(shared_prompt)
    await favorite_repo.update_snapshot_status_batch(shared_prompt.id, "prompt_withdrawn")
    return shared_prompt
```

**Step 3: 运行测试**

Run: `cd backend && python -m pytest tests/unit/application/handlers/test_shared_prompt_handlers.py -v`
Expected: PASS

**Step 4: Commit**

```bash
git add backend/src/application/handlers/shared_prompt_handlers.py backend/tests/unit/application/handlers/test_shared_prompt_handlers.py
git commit -m "feat: add share/unshare prompt handlers with unit tests"
```

---

### Task 11: Prompt 点赞/收藏 Handler

**Files:**
- Create: `backend/src/application/handlers/prompt_like_handlers.py`
- Create: `backend/src/application/handlers/prompt_favorite_handlers.py`
- Create: `backend/tests/unit/application/handlers/test_prompt_like_handlers.py`
- Create: `backend/tests/unit/application/handlers/test_prompt_favorite_handlers.py`

**Step 1: 实现点赞 handler**

参照 `like_handlers.py` 模式：
- `handle_like_prompt(shared_prompt_id, user, shared_prompt_repo)` — 检查存在 + 防重复 + 创建 PromptLike + increment
- `handle_unlike_prompt(shared_prompt_id, user, shared_prompt_repo)` — 检查存在 + 删除 + decrement

**Step 2: 实现收藏 handler**

参照 `favorite_handlers.py` 模式，但增加变更检测和刷新逻辑：
- `handle_favorite_prompt(shared_prompt_id, user, shared_prompt_repo, favorite_repo, prompt_repo, user_repo)` — 检查 shared_prompt active + 防重复 + 读取原 Prompt 做快照 + 创建 PromptFavorite + increment
- `handle_unfavorite_prompt(shared_prompt_id, user, shared_prompt_repo, favorite_repo)` — 删除 + decrement
- `handle_list_prompt_favorites(user, favorite_repo, skip, limit)` — 分页列表
- `handle_check_favorite_version(favorite_id, user, favorite_repo, prompt_repo, shared_prompt_repo)` — 检查版本是否过期，返回 `{is_stale: bool, current_version: int}`
- `handle_refresh_favorite(favorite_id, user, favorite_repo, prompt_repo, shared_prompt_repo)` — 用最新 Prompt 数据刷新快照

**Step 3: 写测试并确认通过**

**Step 4: Commit**

```bash
git add backend/src/application/handlers/prompt_like_handlers.py backend/src/application/handlers/prompt_favorite_handlers.py backend/tests/unit/application/handlers/test_prompt_like_handlers.py backend/tests/unit/application/handlers/test_prompt_favorite_handlers.py
git commit -m "feat: add prompt like/favorite handlers with version change detection"
```

---

### Task 12: Prompt 市场 API Schema + 依赖注入

**Files:**
- Create: `backend/src/api/schemas/shared_prompt.py`
- Modify: `backend/src/api/dependencies/repositories.py`

**Step 1: 创建 Prompt 市场 Schema**

```python
# backend/src/api/schemas/shared_prompt.py
from pydantic import BaseModel
from uuid import UUID
from datetime import datetime


class SharePromptResp(BaseModel):
    id: UUID
    prompt_id: UUID | None
    user_id: UUID
    share_message: str | None
    like_count: int
    favorite_count: int
    status: str
    created_at: datetime


class MarketPromptResp(BaseModel):
    id: UUID
    prompt_id: UUID | None
    user_id: UUID
    title: str  # 实时从 Prompt 读取
    description: str | None  # 实时
    content: str  # 实时
    tags: list[str]  # 实时
    author_name: str  # 实时从 User 读取
    share_message: str | None
    like_count: int
    favorite_count: int
    status: str
    created_at: datetime
    is_liked: bool = False
    is_favorited: bool = False


class MarketPromptListResp(BaseModel):
    items: list[MarketPromptResp]
    total: int


class PromptLikeResp(BaseModel):
    shared_prompt_id: UUID
    like_count: int
    message: str


class PromptFavoriteResp(BaseModel):
    id: UUID
    user_id: UUID
    shared_prompt_id: UUID | None
    snapshot_title: str
    snapshot_content: str
    snapshot_description: str | None
    snapshot_tags: list[str]
    snapshot_author_name: str
    snapshot_version: int
    snapshot_status: str
    created_at: datetime
    is_stale: bool = False  # 前端用于显示变更提醒


class ListPromptFavoritesResp(BaseModel):
    items: list[PromptFavoriteResp]
    total: int


class RefreshFavoriteResp(BaseModel):
    message: str
    favorite: PromptFavoriteResp
```

**Step 2: 更新依赖注入**

在 `backend/src/api/dependencies/repositories.py` 中添加：

```python
async def get_shared_prompt_repo(db: AsyncSession = Depends(get_db)):
    from backend.src.infra.persistence.repositories.sql_shared_prompt_repository import SqlSharedPromptRepository
    return SqlSharedPromptRepository(db)

async def get_prompt_favorite_repo(db: AsyncSession = Depends(get_db)):
    from backend.src.infra.persistence.repositories.sql_prompt_favorite_repository import SqlPromptFavoriteRepository
    return SqlPromptFavoriteRepository(db)
```

**Step 3: Commit**

```bash
git add backend/src/api/schemas/shared_prompt.py backend/src/api/dependencies/repositories.py
git commit -m "feat: add Prompt market API schemas and dependency injection"
```

---

### Task 13: Prompt 市场路由 + 分享/导出路由

**Files:**
- Modify: `backend/src/api/routers/market.py` — 添加 Prompt 市场端点
- Modify: `backend/src/api/routers/prompts.py` — 添加分享/取消分享端点

**Step 1: 在 market.py 中添加 Prompt 市场端点**

添加以下端点：
- `GET /market/prompts` — 市场 Prompt 列表（搜索、标签筛选、分页、可选认证）
- `GET /market/prompts/{shared_prompt_id}` — Prompt 详情（实时读取原 Prompt，可选认证）
- `POST /market/prompts/{shared_prompt_id}/like` — 点赞
- `DELETE /market/prompts/{shared_prompt_id}/like` — 取消点赞
- `POST /market/prompts/{shared_prompt_id}/favorite` — 收藏
- `DELETE /market/prompts/{shared_prompt_id}/favorite` — 取消收藏
- `GET /market/prompts/{shared_prompt_id}/export` — 导出为 Markdown
- `GET /favorites/prompts` — 我的 Prompt 收藏列表
- `POST /favorites/prompts/{favorite_id}/refresh` — 刷新收藏快照

详情接口需要实时读取原 Prompt 和 User 数据，参照 Task 4 中 Skill 详情的模式。

**Step 2: 在 prompts.py 中添加分享/取消分享端点**

```python
# POST /prompts/{prompt_id}/share — 分享到市场
# DELETE /prompts/{prompt_id}/share — 取消分享
```

**Step 3: 收藏列表接口需要检查版本是否过期**

`GET /favorites/prompts` 返回列表时，需要对每个收藏项检查原 Prompt 的当前 version 是否大于 `snapshot_version`，设置 `is_stale` 字段。

**Step 4: 运行所有后端测试**

Run: `cd backend && python -m pytest tests/unit -v --ignore=tests/unit/core/test_auth.py --ignore=tests/unit/core/test_main.py --ignore=tests/unit/infra/persistence/db/test_db_session.py`
Expected: PASS

**Step 5: Commit**

```bash
git add backend/src/api/routers/market.py backend/src/api/routers/prompts.py
git commit -m "feat: add Prompt market API endpoints and share/unshare routes"
```

---

### Task 14: 更新 Prompt 删除 handler — 级联处理 SharedPrompt

**Files:**
- Modify: `backend/src/application/handlers/delete_prompt_handler.py` (如果存在) 或 prompts.py 路由中的删除逻辑

**Step 1: 在 Prompt 删除逻辑中添加级联处理**

当 Prompt 被删除时：
1. 查找关联的 `SharedPrompt`，调用 `mark_prompt_deleted()`（自动 withdraw）
2. 批量更新关联的 `PromptFavorite` 状态为 `prompt_deleted`

```python
# 在删除 prompt 的逻辑中添加
shared_prompts = await shared_prompt_repo.find_all_by_prompt_id(prompt.id)
for sp in shared_prompts:
    sp.mark_prompt_deleted()
    await shared_prompt_repo.save(sp)
    await prompt_favorite_repo.update_snapshot_status_batch(sp.id, "prompt_deleted")
```

**Step 2: Commit**

```bash
git commit -m "feat: cascade delete SharedPrompt and update favorites when Prompt is deleted"
```

---

## Part C: 前端改造

### Task 15: 前端类型定义和 API 方法

**Files:**
- Create: `frontend/types/prompt-market.ts`
- Modify: `frontend/types/market.ts`
- Modify: `frontend/lib/api.ts`

**Step 1: 创建 Prompt 市场类型**

```typescript
// frontend/types/prompt-market.ts
export interface SharedPrompt {
  id: string;
  prompt_id: string | null;
  user_id: string;
  title: string;
  description: string | null;
  content: string;
  tags: string[];
  author_name: string;
  share_message: string | null;
  like_count: number;
  favorite_count: number;
  status: string;
  created_at: string;
  is_liked?: boolean;
  is_favorited?: boolean;
}

export interface SharedPromptListResponse {
  items: SharedPrompt[];
  total: number;
}

export interface PromptFavorite {
  id: string;
  user_id: string;
  shared_prompt_id: string | null;
  snapshot_title: string;
  snapshot_content: string;
  snapshot_description: string | null;
  snapshot_tags: string[];
  snapshot_author_name: string;
  snapshot_version: number;
  snapshot_status: "active" | "prompt_withdrawn" | "prompt_deleted";
  created_at: string;
  is_stale: boolean;
}

export interface PromptFavoriteListResponse {
  items: PromptFavorite[];
  total: number;
}
```

**Step 2: 更新 market.ts 中的 SharedSkill 类型**

去掉 `snapshot_name` 等，改为 `name`, `description`, `author_name`。

**Step 3: 添加 API 方法**

在 `frontend/lib/api.ts` 中添加：
- `getMarketPrompts(params)` — GET `/market/prompts`
- `getMarketPromptDetail(id)` — GET `/market/prompts/${id}`
- `likeSharedPrompt(id)` — POST `/market/prompts/${id}/like`
- `unlikeSharedPrompt(id)` — DELETE `/market/prompts/${id}/like`
- `favoriteSharedPrompt(id)` — POST `/market/prompts/${id}/favorite`
- `unfavoriteSharedPrompt(id)` — DELETE `/market/prompts/${id}/favorite`
- `getMyPromptFavorites(skip, limit)` — GET `/favorites/prompts`
- `refreshPromptFavorite(favoriteId)` — POST `/favorites/prompts/${id}/refresh`
- `exportMarketPrompt(id)` — GET `/market/prompts/${id}/export`
- `sharePrompt(promptId)` — POST `/prompts/${id}/share`
- `unsharePrompt(promptId)` — DELETE `/prompts/${id}/share`

**Step 4: Commit**

```bash
git commit -m "feat: add frontend types and API methods for Prompt market"
```

---

### Task 16: 市场页 tab 切换 — Skills / Prompts

**Files:**
- Modify: `frontend/app/[locale]/market/page.tsx`
- Create: `frontend/components/market/MarketPromptCard.tsx`
- Create: `frontend/stores/marketPromptStore.ts` (Zustand store for prompt market)

**Step 1: 创建 Prompt 市场 Zustand store**

参照 `marketStore`，管理 Prompt 市场列表状态：搜索、标签筛选、排序、分页、乐观更新点赞。

**Step 2: 创建 MarketPromptCard 组件**

展示 Prompt 卡片：标题、描述、作者、标签、点赞数、收藏数。

**Step 3: 市场页添加 tab**

在市场页顶部添加 Skills / Prompts tab 切换，使用 URL 参数或 state 管理当前 tab。

**Step 4: 构建验证**

Run: `cd frontend && npx next build`
Expected: PASS

**Step 5: Commit**

```bash
git commit -m "feat: add Skills/Prompts tab to market page with PromptCard component"
```

---

### Task 17: Prompt 市场详情页

**Files:**
- Create: `frontend/components/market/SharedPromptDetail.tsx`
- Create: `frontend/app/[locale]/market/prompts/[id]/page.tsx`

**Step 1: 创建 SharedPromptDetail 组件**

展示：
- 标题、描述、作者、时间、标签
- 点赞/收藏按钮（乐观更新）
- Markdown 内容只读预览（复用 MarkdownViewer）
- 导出按钮

接受 `backPath` 和 `backLabelKey` 参数（和 SharedSkillDetail 一样的模式，方便收藏详情页复用）。

**Step 2: 创建市场 Prompt 详情页路由**

```typescript
// frontend/app/[locale]/market/prompts/[id]/page.tsx
'use client';
import { use } from 'react';
import { SharedPromptDetail } from '@/components/market/SharedPromptDetail';

export default function MarketPromptDetailPage({ params }: { params: Promise<{ id: string }> }) {
  const { id } = use(params);
  return <SharedPromptDetail id={id} backPath="/market" backLabelKey="back_to_market" />;
}
```

**Step 3: 构建验证**

**Step 4: Commit**

```bash
git commit -m "feat: add Prompt market detail page with Markdown preview and export"
```

---

### Task 18: 收藏页 tab 切换 + Prompt 收藏详情页

**Files:**
- Modify: `frontend/app/[locale]/favorites/page.tsx`
- Create: `frontend/stores/promptFavoritesStore.ts`
- Create: `frontend/app/[locale]/favorites/prompts/[id]/page.tsx`
- Create: `frontend/components/market/PromptFavoriteDetail.tsx`

**Step 1: 收藏页添加 Skills / Prompts tab**

参照市场页的 tab 模式，收藏页也分 tab。Skills tab 展示现有的 SkillFavorite 列表，Prompts tab 展示 PromptFavorite 列表。

**Step 2: 创建 Prompt 收藏 Zustand store**

管理 Prompt 收藏列表状态。

**Step 3: 创建 PromptFavoriteDetail 组件**

展示收藏的 Prompt 快照内容 + 变更提醒逻辑：
- 如果 `is_stale` 为 true，展示"内容已变更"横幅 + 刷新按钮
- 刷新按钮调用 `api.refreshPromptFavorite(favoriteId)`
- 刷新成功后更新本地数据

**Step 4: 创建收藏 Prompt 详情页路由**

```typescript
// frontend/app/[locale]/favorites/prompts/[id]/page.tsx
```

**Step 5: 构建验证**

**Step 6: Commit**

```bash
git commit -m "feat: add Skills/Prompts tab to favorites page with change detection"
```

---

### Task 19: Prompt 编辑页添加分享/取消分享按钮

**Files:**
- Modify: `frontend/app/[locale]/prompts/page.tsx`

**Step 1: 在 Prompt 编辑页添加分享按钮**

在 Prompt 列表/编辑页面中添加分享/取消分享功能，类似 Skill 的分享入口。
- 如果 Prompt 已分享：显示"取消分享"按钮
- 如果未分享：显示"分享到市场"按钮

**Step 2: 构建验证**

**Step 3: Commit**

```bash
git commit -m "feat: add share/unshare prompt button to prompts page"
```

---

### Task 20: i18n 翻译 + AppHeader 导航更新

**Files:**
- Modify: `frontend/i18n/locales/en.json`
- Modify: `frontend/i18n/locales/zh.json`
- Modify: `frontend/components/layout/AppHeader.tsx` (如果需要)

**Step 1: 添加翻译 key**

新增以下 key（en/zh）：
- `market.tabs.skills` / `market.tabs.prompts`
- `market.back_to_market_prompts`
- `favorites.tabs.skills` / `favorites.tabs.prompts`
- `favorites.back_to_favorites_prompts`
- `favorites.prompt_changed` / `favorites.refresh_prompt`
- `prompts.share` / `prompts.unshare` / `prompts.shared`
- `market.export_prompt`

**Step 2: 验证 AppHeader**

确认市场页路由 `/market/prompts/[id]` 时 tab 仍然正确高亮"市场"（因为 `parts[0]` 仍然是 `market`）。

**Step 3: Commit**

```bash
git commit -m "feat: add i18n keys for Prompt market and favorites"
```

---

### Task 21: 全量验证

**Step 1: 运行后端测试**

Run: `cd backend && python -m pytest tests/unit -v --ignore=tests/unit/core/test_auth.py --ignore=tests/unit/core/test_main.py --ignore=tests/unit/infra/persistence/db/test_db_session.py`
Expected: ALL PASS

**Step 2: 运行前端构建**

Run: `cd frontend && npx next build`
Expected: 构建成功

**Step 3: 运行前端测试**

Run: `cd frontend && bun test`
Expected: PASS（排除预先存在的失败）

**Step 4: Commit any fixes**

**Step 5: Final commit**

```bash
git commit -m "chore: final validation pass"
```
