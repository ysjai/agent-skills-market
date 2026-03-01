# Prompt 管理功能

## TL;DR

> **Quick Summary**: 为 Agent Skills Manager 新增独立的 Prompt（提示词）管理功能，支持 CRUD、`{{variable}}` 变量模板、手动版本发布与历史查看、用户自定义标签、Markdown 导入/导出，采用左右分栏 UI 布局。
> 
> **Deliverables**:
> - 后端：Prompt 领域全栈（Aggregate/Factory/Repository/Handlers/Router/Schemas/Migration）
> - 后端：PromptVersion 版本历史功能（发布版本 + 查看历史版本内容）
> - 后端：Markdown 导入/导出 API
> - 前端：Prompts 页面（左右分栏：列表 + 编辑器）
> - 前端：版本历史面板
> - 前端：标签管理 UI
> - 前端：导入/导出对话框
> - 前端：顶部导航栏（Skills / Prompts 切换）
> - 自动化测试：后端 pytest + 前端 bun test
> - i18n：中英文翻译
> 
> **Estimated Effort**: Large
> **Parallel Execution**: YES - 4 waves
> **Critical Path**: Migration → Domain Layer → Handlers → Router → Frontend Types/Store → UI Components → Pages → Tests

---

## Context

### Original Request
用户想要在系统中增加一个 Prompt 管理功能：用户可以创建和导入提示词，进行修改和编辑，修改需要版本化管理。需要考虑后端 API、领域模型、表模型设计以及 UI 设计。

### Interview Summary
**Key Discussions**:
- 内容形式：支持 `{{variable}}` 双大括号变量语法的模板
- 版本化：手动标记版本（用户主动点击发布），支持版本历史列表 + 查看历史版本完整内容
- 标签：用户自定义标签，存储为 PostgreSQL ARRAY(String)
- 导入/导出：Markdown 格式，使用 YAML frontmatter 携带元数据
- Prompt 与 Skill 完全独立
- 数据结构：单文本内容（不使用 Tree/Blob）
- 编辑器：复用 Monaco Editor
- UI 布局：左右分栏（左侧 Prompt 列表，右侧编辑器）
- 导航：顶部导航栏添加 Skills/Prompts 切换
- 测试：包含自动化测试

**Research Findings**:
- 项目采用 DDD 四层架构（API/Application/Domain/Infrastructure）
- 现有 Skill 领域可作为完整模式参考
- 已有丰富可复用 UI 组件和 Monaco Editor
- i18n 支持 en/zh

### Metis Review
**Identified Gaps** (addressed):
- 标签存储方式 → 确认使用 ARRAY(String)，不建单独表
- 版本存储方式 → 确认使用完整快照，不用 diff
- 导航入口 → 确认添加顶部导航栏
- 导入导出格式 → 确认使用 YAML frontmatter + body
- 变量语法规则 → 不做验证/解析，仅作为文本存储
- 标签规范化 → 自动 lowercase + 去重
- 内容/标题长度限制 → title max 200, description max 1000, content TEXT, tag name max 50, max 20 tags

---

## Work Objectives

### Core Objective
构建完整的 Prompt 管理领域，遵循现有 DDD 架构模式，支持 CRUD、版本化发布、标签管理、Markdown 导入/导出。

### Concrete Deliverables
- `backend/src/domain/aggregates/prompt.py` - Prompt 聚合根
- `backend/src/domain/factories/prompt_factory.py` - Prompt 工厂
- `backend/src/domain/repositories/prompt_repository.py` - Repository 接口
- `backend/src/infra/persistence/models/prompt_model.py` - ORM 模型（含 PromptVersionModel）
- `backend/src/infra/persistence/repositories/sql_prompt_repository.py` - SQL Repository 实现
- `backend/alembic/versions/*_create_prompts.py` - 数据库迁移
- `backend/src/application/handlers/` - 10+ 个 Handler
- `backend/src/api/routers/prompts.py` - API 路由
- `backend/src/api/schemas/prompt.py` - Pydantic DTOs
- `frontend/types/prompt.ts` - TypeScript 类型
- `frontend/stores/promptsStore.ts` - Zustand Store
- `frontend/app/[locale]/prompts/page.tsx` - Prompts 页面
- `frontend/components/prompts/` - UI 组件
- `frontend/components/layout/TopNav.tsx` - 顶部导航栏
- 后端 pytest 测试
- 前端 bun test 测试
- i18n 中英文翻译

### Definition of Done
- [x] `alembic upgrade head` 成功执行，prompts + prompt_versions 表创建
- [x] `alembic downgrade -1` 成功回滚
- [x] 所有 Prompt CRUD API 端点返回正确状态码
- [x] 版本发布和历史查看 API 正常工作
- [x] Markdown 导入/导出 API 正常工作
- [x] `pytest tests/ -v` 所有测试通过
- [x] `bun test` 所有前端测试通过
- [x] 前端 Prompts 页面可访问且功能正常
- [x] 顶部导航栏在 Skills 和 Prompts 页面都显示

### Must Have
- Prompt CRUD（创建、读取、更新、删除）
- `{{variable}}` 变量模板语法（仅存储，不解析）
- 手动版本发布（创建版本快照）
- 版本历史列表 + 查看历史版本内容
- 用户自定义标签（ARRAY 存储，自动 lowercase + 去重）
- Markdown 导入（YAML frontmatter + body）
- Markdown 导出
- 左右分栏 UI（列表 + 编辑器）
- 按标签筛选
- 搜索（按标题）
- 顶部导航栏（Skills / Prompts）
- JWT 认证保护所有端点
- 用户数据隔离（只能看到自己的 Prompt）
- i18n 中英文支持
- 后端 pytest + 前端 bun test

### Must NOT Have (Guardrails)
- ❌ 不建单独的 Tag 表/聚合/仓储 — 标签仅为 ARRAY(String) 字段
- ❌ 不复用 Tree/Blob 文件管理系统 — Prompt 是单文本
- ❌ 不构建变量解析/验证/注册系统 — `{{var}}` 仅作为文本存储
- ❌ 不构建模板渲染/执行引擎
- ❌ 不构建版本 Diff 对比 UI
- ❌ 不构建版本回滚功能
- ❌ 不添加 Prompt-Skill 关联
- ❌ 不添加自定义 Monaco 语法高亮（使用 markdown 模式）
- ❌ 不添加 SQLAlchemy relationship() — 遵循项目约定，只用外键
- ❌ 不构建多用户协作功能
- ❌ 不添加流程控制语法（if/for）
- ❌ 不添加全局侧边栏 — 使用顶部导航栏
- ❌ 不支持批量导入/导出
- ❌ 不添加内容全文搜索（v1 仅标题搜索）

---

## Verification Strategy

> **ZERO HUMAN INTERVENTION** — ALL verification is agent-executed. No exceptions.

### Test Decision
- **Infrastructure exists**: YES (pytest + bun test)
- **Automated tests**: YES (Tests-after)
- **Framework**: pytest (backend), bun test (frontend)

### QA Policy
Every task MUST include agent-executed QA scenarios.
Evidence saved to `.sisyphus/evidence/task-{N}-{scenario-slug}.{ext}`.

- **Backend API**: Use Bash (curl) — Send requests, assert status + response fields
- **Frontend/UI**: Use Playwright (playwright skill) — Navigate, interact, assert DOM, screenshot
- **Database**: Use Bash (alembic/psql) — Run migrations, verify tables

---

## Execution Strategy

### Parallel Execution Waves

```
Wave 1 (Start Immediately — foundation):
├── Task 1: Database migration (prompts + prompt_versions tables) [quick]
├── Task 2: Domain layer - Prompt aggregate + PromptVersion entity [quick]
├── Task 3: Domain layer - Factory + Repository interface [quick]
├── Task 4: Frontend types + Zustand store [quick]
├── Task 5: i18n translations (en.json + zh.json) [quick]
└── Task 6: Frontend TopNav component [quick]

Wave 2 (After Wave 1 — backend core):
├── Task 7: Infrastructure - ORM models + SQL Repository (depends: 1,2,3) [unspecified-high]
├── Task 8: Application - CRUD Handlers (depends: 2,3) [unspecified-high]
├── Task 9: Application - Version Handlers (depends: 2,3) [unspecified-high]
├── Task 10: Application - Import/Export Handlers (depends: 2,3) [unspecified-high]
└── Task 11: Frontend - Prompt list + editor components (depends: 4,5,6) [visual-engineering]

Wave 3 (After Wave 2 — API + Frontend pages):
├── Task 12: API layer - Schemas + Router + Registration (depends: 7,8,9,10) [unspecified-high]
├── Task 13: Frontend - Prompts page + routing (depends: 11) [visual-engineering]
├── Task 14: Frontend - Version history panel (depends: 4,11) [visual-engineering]
└── Task 15: Frontend - Import/Export dialogs (depends: 4,5) [visual-engineering]

Wave 4 (After Wave 3 — testing + integration):
├── Task 16: Backend tests - pytest (depends: 12) [deep]
├── Task 17: Frontend tests - bun test (depends: 13,14,15) [unspecified-high]
└── Task 18: Integration testing + fixes (depends: 12,13) [deep]

Wave FINAL (After ALL tasks — independent review, 4 parallel):
├── Task F1: Plan compliance audit (oracle)
├── Task F2: Code quality review (unspecified-high)
├── Task F3: Real manual QA (unspecified-high)
└── Task F4: Scope fidelity check (deep)

Critical Path: Task 1 → Task 7 → Task 12 → Task 13 → Task 18 → F1-F4
Parallel Speedup: ~60% faster than sequential
Max Concurrent: 6 (Wave 1)
```

### Dependency Matrix

| Task | Depends On | Blocks | Wave |
|------|-----------|--------|------|
| 1 | — | 7 | 1 |
| 2 | — | 7,8,9,10 | 1 |
| 3 | — | 7,8,9,10 | 1 |
| 4 | — | 11,13,14,15,17 | 1 |
| 5 | — | 11,13,15 | 1 |
| 6 | — | 11,13 | 1 |
| 7 | 1,2,3 | 12 | 2 |
| 8 | 2,3 | 12 | 2 |
| 9 | 2,3 | 12 | 2 |
| 10 | 2,3 | 12 | 2 |
| 11 | 4,5,6 | 13,14,17 | 2 |
| 12 | 7,8,9,10 | 13,16,18 | 3 |
| 13 | 11,12 | 17,18 | 3 |
| 14 | 4,11 | 17 | 3 |
| 15 | 4,5 | 17 | 3 |
| 16 | 12 | F1-F4 | 4 |
| 17 | 13,14,15 | F1-F4 | 4 |
| 18 | 12,13 | F1-F4 | 4 |

### Agent Dispatch Summary

- **Wave 1**: **6** — T1-T3 → `quick`, T4-T5 → `quick`, T6 → `quick`
- **Wave 2**: **5** — T7 → `unspecified-high`, T8-T10 → `unspecified-high`, T11 → `visual-engineering`
- **Wave 3**: **4** — T12 → `unspecified-high`, T13 → `visual-engineering`, T14-T15 → `visual-engineering`
- **Wave 4**: **3** — T16 → `deep`, T17 → `unspecified-high`, T18 → `deep`
- **FINAL**: **4** — F1 → `oracle`, F2 → `unspecified-high`, F3 → `unspecified-high`, F4 → `deep`

---

## TODOs

- [x] 1. Database Migration — prompts + prompt_versions 表

  **What to do**:
  - 创建 Alembic 迁移文件 `backend/alembic/versions/20260214081025__create_prompts.py`
  - `revision = "v5_prompts"`, `down_revision = "v4_skills"`（遵循现有链：v1_users → v2_blobs → v3_trees → v4_skills）
  - 创建 `prompts` 表：
    - `id` UUID PK (server_default=gen_random_uuid())
    - `user_id` UUID FK→users.id (ondelete=CASCADE), index=True
    - `title` String(200), nullable=False
    - `content` Text, nullable=False, server_default=''
    - `description` String(1000), nullable=True
    - `tags` ARRAY(String), server_default='{}'
    - `version` Integer, nullable=False, server_default='1'
    - `created_at` DateTime(timezone=True), server_default=NOW()
    - `updated_at` DateTime(timezone=True), server_default=NOW()
  - 创建 `prompt_versions` 表：
    - `id` UUID PK (server_default=gen_random_uuid())
    - `prompt_id` UUID FK→prompts.id (ondelete=CASCADE), index=True
    - `version_number` Integer, nullable=False
    - `title` String(200), nullable=False
    - `content` Text, nullable=False
    - `description` String(1000), nullable=True
    - `tags` ARRAY(String), server_default='{}'
    - `created_at` DateTime(timezone=True), server_default=NOW()
  - 创建索引：`ix_prompts_user_id`, `ix_prompt_versions_prompt_id`
  - `downgrade()` 按顺序删除 prompt_versions → prompts

  **Must NOT do**:
  - 不添加 relationship() — 遵循项目约定
  - 不创建 Tag 表
  - 不使用 JSONB 存储标签

  **Recommended Agent Profile**:
  - **Category**: `quick`
    - Reason: 单个迁移文件，遵循既有模式，低复杂度
  - **Skills**: `[]`
  - **Skills Evaluated but Omitted**:
    - `git-master`: 不涉及 git 操作

  **Parallelization**:
  - **Can Run In Parallel**: YES
  - **Parallel Group**: Wave 1 (with Tasks 2, 3, 4, 5, 6)
  - **Blocks**: Task 7 (ORM + SQL Repository 依赖表结构)
  - **Blocked By**: None

  **References**:

  **Pattern References**:
  - `backend/alembic/versions/20260214081020__create_skills.py` — 完整迁移模式参考：revision 链、op.create_table 语法、PostgreSQL UUID 类型、索引创建、downgrade 顺序

  **API/Type References**:
  - `sqlalchemy.dialects.postgresql.ARRAY` — 用于 tags 字段的 ARRAY(String) 类型

  **WHY Each Reference Matters**:
  - 迁移文件必须与现有链保持一致（revision/down_revision），参考 skills 迁移可确保格式和模式完全匹配

  **Acceptance Criteria**:
  - [x] 迁移文件位于 `backend/alembic/versions/20260214081025__create_prompts.py`
  - [x] revision chain 正确：`revision = "v5_prompts"`, `down_revision = "v4_skills"`

  **QA Scenarios (MANDATORY):**

  ```
  Scenario: 迁移升级成功
    Tool: Bash
    Preconditions: PostgreSQL 运行中，数据库已执行到 v4_skills
    Steps:
      1. cd backend && alembic upgrade head
      2. 使用 psql 检查表存在：SELECT table_name FROM information_schema.tables WHERE table_schema='public' AND table_name IN ('prompts', 'prompt_versions');
      3. 检查 prompts 表列：SELECT column_name, data_type FROM information_schema.columns WHERE table_name='prompts' ORDER BY ordinal_position;
      4. 检查 prompt_versions 表列：SELECT column_name, data_type FROM information_schema.columns WHERE table_name='prompt_versions' ORDER BY ordinal_position;
    Expected Result: 两张表都存在，所有列名和类型正确
    Failure Indicators: alembic upgrade 报错、表不存在、列缺失
    Evidence: .sisyphus/evidence/task-1-migration-upgrade.txt

  Scenario: 迁移降级成功
    Tool: Bash
    Preconditions: 已成功执行 upgrade head
    Steps:
      1. cd backend && alembic downgrade -1
      2. SELECT table_name FROM information_schema.tables WHERE table_schema='public' AND table_name IN ('prompts', 'prompt_versions');
      3. cd backend && alembic upgrade head  # 重新升级确保可重复
    Expected Result: downgrade 后两张表都不存在，再次 upgrade 成功
    Failure Indicators: downgrade 报外键依赖错误、表残留
    Evidence: .sisyphus/evidence/task-1-migration-downgrade.txt
  ```

  **Commit**: YES
  - Message: `feat(prompt): add database migration for prompts and prompt_versions`
  - Files: `backend/alembic/versions/20260214081025__create_prompts.py`
  - Pre-commit: `cd backend && alembic upgrade head && alembic downgrade -1 && alembic upgrade head`

- [x] 2. Domain Layer — Prompt Aggregate + PromptVersion Entity

  **What to do**:
  - 创建 `backend/src/domain/aggregates/prompt.py`：
    - `@dataclass class Prompt`，字段：id(UUID), user_id(UUID), title(str), content(str), description(str|None), tags(list[str]), version(int), created_at(datetime), updated_at(datetime)
    - 方法：
      - `update_title(new_title: str)` — 校验非空, strip, 长度<=200，失败抛 ValidationError
      - `update_content(content: str)` — 更新 content + _mark_updated()
      - `update_description(description: str | None)` — 更新 + _mark_updated()
      - `update_tags(tags: list[str])` — 规范化(lowercase, strip, 去重, max 20, 每个 max 50 chars) + _mark_updated()
      - `publish_version()` → PromptVersion — 创建当前状态的快照，version += 1, _mark_updated()
      - `_mark_updated()` — self.updated_at = datetime.now(utc), self.version += 1
    - 仅使用标准库导入（dataclasses, datetime, uuid）+ domain 内部导入
  - 创建 `backend/src/domain/entities/prompt_version.py`：
    - `@dataclass class PromptVersion`，字段：id(UUID), prompt_id(UUID), version_number(int), title(str), content(str), description(str|None), tags(list[str]), created_at(datetime)
    - 纯数据类，无行为方法

  **Must NOT do**:
  - 不导入 SQLAlchemy — 这是 Domain 层
  - 不导入 FastAPI — 这是 Domain 层
  - 不添加 Slug/slug 字段 — Prompt 不需要 slug
  - 不添加 tree_id — Prompt 是单文本
  - 不添加变量解析/验证逻辑

  **Recommended Agent Profile**:
  - **Category**: `quick`
    - Reason: 两个 dataclass 文件，模式明确，低复杂度
  - **Skills**: `[]`

  **Parallelization**:
  - **Can Run In Parallel**: YES
  - **Parallel Group**: Wave 1 (with Tasks 1, 3, 4, 5, 6)
  - **Blocks**: Tasks 7, 8, 9, 10
  - **Blocked By**: None

  **References**:

  **Pattern References**:
  - `backend/src/domain/aggregates/skill.py` — Aggregate 模式参考：@dataclass 装饰器、字段定义（id/user_id/created_at/updated_at/version）、update_* 方法命名模式、_mark_updated() 实现（updated_at = datetime.now(utc), version += 1）
  - `backend/src/domain/entities/blob.py` — Entity 模式参考：纯 @dataclass 数据类

  **API/Type References**:
  - `backend/src/domain/exceptions.py:ValidationError` — 在 update_title/update_tags 中校验失败时抛出

  **WHY Each Reference Matters**:
  - Skill aggregate 是最接近的模式参考，Prompt 的字段结构和方法命名应完全对齐
  - PromptVersion 是纯数据快照，对标 Blob entity 的简单 dataclass 模式

  **Acceptance Criteria**:
  - [x] `backend/src/domain/aggregates/prompt.py` 存在且包含 Prompt dataclass
  - [x] `backend/src/domain/entities/prompt_version.py` 存在且包含 PromptVersion dataclass
  - [x] Prompt.update_tags() 执行 lowercase + strip + 去重 + max 20 + max 50 chars 校验
  - [x] Prompt.publish_version() 返回 PromptVersion 快照
  - [x] 无 SQLAlchemy/FastAPI 导入

  **QA Scenarios (MANDATORY):**

  ```
  Scenario: Prompt 聚合方法正确性
    Tool: Bash (python -c)
    Preconditions: backend 虚拟环境已激活
    Steps:
      1. cd backend && python -c "
         from src.domain.aggregates.prompt import Prompt
         from uuid import uuid4
         p = Prompt(id=uuid4(), user_id=uuid4(), title='Test', content='Hello {{name}}', tags=['Tag1', 'TAG1', '  tag2  '])
         p.update_tags(['Tag1', 'TAG1', '  tag2  '])
         assert p.tags == ['tag1', 'tag2'], f'Tags not normalized: {p.tags}'
         v = p.publish_version()
         assert v.title == 'Test'
         assert v.content == 'Hello {{name}}'
         assert v.tags == ['tag1', 'tag2']
         print('ALL PASS')"
    Expected Result: 输出 'ALL PASS'
    Failure Indicators: ImportError、AssertionError、AttributeError
    Evidence: .sisyphus/evidence/task-2-aggregate-methods.txt

  Scenario: 校验边界 — 标题为空抛 ValidationError
    Tool: Bash (python -c)
    Preconditions: backend 虚拟环境已激活
    Steps:
      1. cd backend && python -c "
         from src.domain.aggregates.prompt import Prompt
         from src.domain.exceptions import ValidationError
         from uuid import uuid4
         p = Prompt(id=uuid4(), user_id=uuid4(), title='Test', content='')
         try:
             p.update_title('')
             print('FAIL: no exception')
         except ValidationError:
             print('PASS: ValidationError raised')"
    Expected Result: 输出 'PASS: ValidationError raised'
    Failure Indicators: 输出 'FAIL: no exception'
    Evidence: .sisyphus/evidence/task-2-validation-error.txt
  ```

  **Commit**: YES (group with Task 3)
  - Message: `feat(prompt): add domain layer - aggregate, entity, factory, repository interface`
  - Files: `backend/src/domain/aggregates/prompt.py`, `backend/src/domain/entities/prompt_version.py`

- [x] 3. Domain Layer — PromptFactory + PromptRepository Interface

  **What to do**:
  - 创建 `backend/src/domain/factories/prompt_factory.py`：
    - `class PromptFactory` 类方法模式（参考 SkillFactory）
    - `_MAX_TITLE_LENGTH = 200`
    - `_MAX_DESCRIPTION_LENGTH = 1000`
    - `_MAX_TAG_LENGTH = 50`
    - `_MAX_TAGS_COUNT = 20`
    - `create(user_id, title, content, description=None, tags=None)` → Prompt
      - 校验 title（非空、strip、长度）
      - 校验 description（长度）
      - 校验并规范化 tags（lowercase, strip, 去重, 数量限制, 单个长度限制）
      - 使用 ValidationError 报错
    - `_validate_title()`, `_validate_description()`, `_validate_tags()` 私有方法
  - 创建 `backend/src/domain/repositories/prompt_repository.py`：
    - `class PromptRepository(ABC)` 抽象类
    - 方法：
      - `get_by_id(prompt_id: UUID) → Prompt | None`
      - `find_by_user(user_id: UUID, offset=0, limit=20, tag: str|None=None, search: str|None=None) → list[Prompt]`
      - `count_by_user(user_id: UUID, tag: str|None=None, search: str|None=None) → int`
      - `save(prompt: Prompt) → None`
      - `delete(prompt_id: UUID) → None`
      - `save_version(version: PromptVersion) → None`
      - `get_versions(prompt_id: UUID) → list[PromptVersion]`
      - `get_version_by_id(version_id: UUID) → PromptVersion | None`

  **Must NOT do**:
  - 不在 Factory 中做变量解析（`{{var}}` 仅作文本）
  - 不添加 Slug 相关逻辑
  - 不导入 SQLAlchemy/FastAPI

  **Recommended Agent Profile**:
  - **Category**: `quick`
    - Reason: 两个文件，模式完全参考 SkillFactory + SkillRepository
  - **Skills**: `[]`

  **Parallelization**:
  - **Can Run In Parallel**: YES
  - **Parallel Group**: Wave 1 (with Tasks 1, 2, 4, 5, 6)
  - **Blocks**: Tasks 7, 8, 9, 10
  - **Blocked By**: None

  **References**:

  **Pattern References**:
  - `backend/src/domain/factories/skill_factory.py` — Factory 模式参考：类方法 create()、_validate_* 私有方法、_MAX_* 常量、ValidationError 使用
  - `backend/src/domain/repositories/skill_repository.py` — Repository 接口参考：ABC 基类、@abstractmethod、方法签名模式（get_by_id, find_by_user, save, delete）

  **API/Type References**:
  - `backend/src/domain/aggregates/prompt.py` (Task 2 产出) — Prompt 类型定义
  - `backend/src/domain/entities/prompt_version.py` (Task 2 产出) — PromptVersion 类型
  - `backend/src/domain/exceptions.py:ValidationError` — 校验失败抛出

  **WHY Each Reference Matters**:
  - PromptFactory 必须与 SkillFactory 保持完全一致的代码风格和校验模式
  - PromptRepository 接口多了 tag 筛选、search 搜索、版本管理方法，但基础模式与 SkillRepository 一致

  **Acceptance Criteria**:
  - [x] `backend/src/domain/factories/prompt_factory.py` 存在
  - [x] `backend/src/domain/repositories/prompt_repository.py` 存在
  - [x] Factory.create() 校验 title 非空、description 长度、tags 规范化
  - [x] Repository 包含全部 8 个抽象方法
  - [x] 无 SQLAlchemy/FastAPI 导入

  **QA Scenarios (MANDATORY):**

  ```
  Scenario: Factory 创建和校验
    Tool: Bash (python -c)
    Preconditions: Task 2 完成
    Steps:
      1. cd backend && python -c "
         from src.domain.factories.prompt_factory import PromptFactory
         from src.domain.exceptions import ValidationError
         from uuid import uuid4
         uid = uuid4()
         p = PromptFactory.create(user_id=uid, title='My Prompt', content='Hello {{name}}', tags=['Test', 'TEST', 'demo'])
         assert p.title == 'My Prompt'
         assert p.tags == ['test', 'demo'], f'Tags: {p.tags}'
         assert p.user_id == uid
         try:
             PromptFactory.create(user_id=uid, title='', content='test')
             print('FAIL')
         except ValidationError:
             pass
         try:
             PromptFactory.create(user_id=uid, title='a'*201, content='test')
             print('FAIL')
         except ValidationError:
             pass
         print('ALL PASS')"
    Expected Result: 输出 'ALL PASS'
    Failure Indicators: ImportError、AssertionError、输出 'FAIL'
    Evidence: .sisyphus/evidence/task-3-factory-validation.txt

  Scenario: Repository 接口完整性
    Tool: Bash (python -c)
    Preconditions: 文件已创建
    Steps:
      1. cd backend && python -c "
         from src.domain.repositories.prompt_repository import PromptRepository
         import inspect
         methods = [m for m in dir(PromptRepository) if not m.startswith('_')]
         expected = ['count_by_user', 'delete', 'find_by_user', 'get_by_id', 'get_version_by_id', 'get_versions', 'save', 'save_version']
         assert sorted(methods) == sorted(expected), f'Methods: {methods}'
         print('ALL PASS')"
    Expected Result: 输出 'ALL PASS'
    Failure Indicators: AssertionError（方法缺失或多余）
    Evidence: .sisyphus/evidence/task-3-repo-interface.txt
  ```

  **Commit**: YES (group with Task 2)
  - Message: `feat(prompt): add domain layer - aggregate, entity, factory, repository interface`
  - Files: `backend/src/domain/factories/prompt_factory.py`, `backend/src/domain/repositories/prompt_repository.py`

- [x] 4. Frontend Types + Zustand Store

  **What to do**:
  - 创建 `frontend/types/prompt.ts`：
    - `interface Prompt`: id(string), user_id(string), title(string), content(string), description(string|null), tags(string[]), version(number), created_at(string), updated_at(string)
    - `interface PromptVersion`: id(string), prompt_id(string), version_number(number), title(string), content(string), description(string|null), tags(string[]), created_at(string)
    - `interface PromptListResponse`: items(Prompt[]), total(number)
    - `interface CreatePromptRequest`: title(string), content(string), description?(string), tags?(string[])
    - `interface UpdatePromptRequest`: title?(string), content?(string), description?(string), tags?(string[])
    - `interface ImportPromptRequest`: markdown_content(string)
    - `interface ExportPromptResponse`: markdown_content(string)
  - 创建 `frontend/stores/promptsStore.ts`：
    - 仿照 `skillsStore.ts` 模式
    - State: prompts(Prompt[]), selectedPrompt(Prompt|null), isLoading(boolean), errorMessage(string|null), searchQuery(string), selectedTag(string|null)
    - Actions: setPrompts, addPrompt, removePrompt, updatePrompt, setSelectedPrompt, setIsLoading, setErrorMessage, setSearchQuery, setSelectedTag, getFilteredPrompts()
    - `getFilteredPrompts()` 按 searchQuery 筛选 title + description，按 selectedTag 筛选 tags
  - 在 `frontend/stores/types.ts` 中添加 `PromptsState` 接口

  **Must NOT do**:
  - 不添加 slug 相关字段
  - 不添加 tree_id 相关字段
  - 不添加 API 调用逻辑到 Store（Store 仅管理状态）

  **Recommended Agent Profile**:
  - **Category**: `quick`
    - Reason: 两个文件 + 一处编辑，模式完全参考已有代码
  - **Skills**: `[]`

  **Parallelization**:
  - **Can Run In Parallel**: YES
  - **Parallel Group**: Wave 1 (with Tasks 1, 2, 3, 5, 6)
  - **Blocks**: Tasks 11, 13, 14, 15, 17
  - **Blocked By**: None

  **References**:

  **Pattern References**:
  - `frontend/types/skill.ts` — TypeScript 类型定义模式：interface 命名、字段类型约定（id 用 string、时间戳用 string、可选字段用 `|null`）、Request/Response 分离
  - `frontend/stores/skillsStore.ts` — Zustand store 模式：create<State>()、set/get 用法、getFilteredSkills() 计算过滤
  - `frontend/stores/types.ts:SkillsState` — Store 接口定义模式：State + Actions 全在一个 interface 中

  **API/Type References**:
  - `frontend/lib/api.ts:ApiClient` — 了解 API 客户端方法签名（get/post/put/delete）以确保 Store 与之兼容

  **WHY Each Reference Matters**:
  - Prompt 类型结构与 Skill 类似但更简单（无 slug、tree_id、is_public），参考 skill.ts 确保命名一致性
  - Store 需要额外的 selectedPrompt 和 selectedTag 状态，因为 Prompt 页面是左右分栏（不同于 Skill 的卡片列表）

  **Acceptance Criteria**:
  - [x] `frontend/types/prompt.ts` 存在且包含所有 7 个 interface
  - [x] `frontend/stores/promptsStore.ts` 存在且导出 `usePromptsStore`
  - [x] `frontend/stores/types.ts` 包含 `PromptsState` 接口
  - [x] TypeScript 编译无错误：`cd frontend && npx tsc --noEmit`

  **QA Scenarios (MANDATORY):**

  ```
  Scenario: TypeScript 编译通过
    Tool: Bash
    Preconditions: frontend 依赖已安装
    Steps:
      1. cd frontend && npx tsc --noEmit
    Expected Result: 无错误输出，退出码 0
    Failure Indicators: TS 类型错误
    Evidence: .sisyphus/evidence/task-4-tsc-check.txt

  Scenario: Store 功能正确
    Tool: Bash (node -e)
    Preconditions: frontend 代码已编译
    Steps:
      1. cd frontend && npx tsx -e "
         const { usePromptsStore } = require('./stores/promptsStore');
         const store = usePromptsStore.getState();
         console.log('keys:', Object.keys(store).sort().join(','));
         store.setPrompts([{id:'1',user_id:'u1',title:'Test',content:'Hello',description:null,tags:['tag1'],version:1,created_at:'',updated_at:''}]);
         store.setSearchQuery('test');
         console.log('filtered:', store.getFilteredPrompts().length);
         store.setSelectedTag('tag1');
         console.log('tagged:', store.getFilteredPrompts().length);
         console.log('ALL PASS');"
    Expected Result: 输出 'ALL PASS'
    Failure Indicators: ImportError、undefined method
    Evidence: .sisyphus/evidence/task-4-store-test.txt
  ```

  **Commit**: YES (group with Tasks 5, 6)
  - Message: `feat(prompt): add frontend types, store, i18n, and TopNav`
  - Files: `frontend/types/prompt.ts`, `frontend/stores/promptsStore.ts`, `frontend/stores/types.ts`

- [x] 5. i18n Translations — en.json + zh.json

  **What to do**:
  - 在 `frontend/i18n/locales/en.json` 中添加 `prompts` 命名空间（与 `skills` 平级）：
    ```json
    "prompts": {
      "title": "My Prompts",
      "newPrompt": "New Prompt",
      "createPrompt": "Create Prompt",
      "importPrompt": "Import Prompt",
      "exportPrompt": "Export Prompt",
      "deletePrompt": "Delete",
      "searchPlaceholder": "Search prompts...",
      "noPrompts": "No prompts yet",
      "noPromptsFound": "No prompts found",
      "createFirst": "Create your first prompt to start managing your templates",
      "tryAdjustSearch": "Try adjusting your search query or tag filter",
      "promptsCount": "{count} prompts",
      "version": "Version",
      "tags": "Tags",
      "addTag": "Add tag...",
      "publishVersion": "Publish Version",
      "versionHistory": "Version History",
      "versionNumber": "v{number}",
      "noVersions": "No versions published yet",
      "publishSuccess": "Version published successfully",
      "createSuccess": "Prompt created successfully",
      "updateSuccess": "Prompt updated successfully",
      "deleteSuccess": "Prompt deleted successfully",
      "deleteConfirm": "Are you sure you want to delete this prompt? This action cannot be undone.",
      "importSuccess": "Prompt imported successfully",
      "importError": "Failed to import prompt",
      "exportSuccess": "Prompt exported successfully",
      "titlePlaceholder": "Enter prompt title...",
      "contentPlaceholder": "Write your prompt template here...\nUse {{variable}} for template variables.",
      "descriptionPlaceholder": "Brief description of this prompt...",
      "loadFailed": "Failed to load prompts",
      "untitled": "Untitled Prompt"
    }
    ```
  - 在 `frontend/i18n/locales/zh.json` 中添加对应的中文翻译：
    ```json
    "prompts": {
      "title": "我的提示词",
      "newPrompt": "新建提示词",
      "createPrompt": "创建提示词",
      "importPrompt": "导入提示词",
      "exportPrompt": "导出提示词",
      "deletePrompt": "删除",
      "searchPlaceholder": "搜索提示词...",
      "noPrompts": "暂无提示词",
      "noPromptsFound": "未找到提示词",
      "createFirst": "创建您的第一个提示词，开始管理您的模板",
      "tryAdjustSearch": "请尝试调整搜索关键词或标签筛选",
      "promptsCount": "{count} 个提示词",
      "version": "版本",
      "tags": "标签",
      "addTag": "添加标签...",
      "publishVersion": "发布版本",
      "versionHistory": "版本历史",
      "versionNumber": "v{number}",
      "noVersions": "暂无已发布的版本",
      "publishSuccess": "版本发布成功",
      "createSuccess": "提示词创建成功",
      "updateSuccess": "提示词更新成功",
      "deleteSuccess": "提示词删除成功",
      "deleteConfirm": "确定要删除此提示词吗？此操作无法撤销。",
      "importSuccess": "提示词导入成功",
      "importError": "导入提示词失败",
      "exportSuccess": "提示词导出成功",
      "titlePlaceholder": "输入提示词标题...",
      "contentPlaceholder": "在此编写提示词模板...\n使用 {{variable}} 作为模板变量。",
      "descriptionPlaceholder": "简要描述此提示词的用途...",
      "loadFailed": "加载提示词失败",
      "untitled": "未命名提示词"
    }
    ```
  - 添加 `nav` 命名空间（两个文件都添加）用于顶部导航：
    - en: `"nav": { "skills": "Skills", "prompts": "Prompts" }`
    - zh: `"nav": { "skills": "技能", "prompts": "提示词" }`

  **Must NOT do**:
  - 不修改已有的翻译 key
  - 不添加 import/export 详细对话框的翻译（那些在 Task 15 中添加）

  **Recommended Agent Profile**:
  - **Category**: `quick`
    - Reason: 纯 JSON 编辑，低风险
  - **Skills**: `[]`

  **Parallelization**:
  - **Can Run In Parallel**: YES
  - **Parallel Group**: Wave 1 (with Tasks 1, 2, 3, 4, 6)
  - **Blocks**: Tasks 11, 13, 15
  - **Blocked By**: None

  **References**:

  **Pattern References**:
  - `frontend/i18n/locales/en.json:skills` (lines 55-78) — i18n key 命名模式：动词+名词（createSkill、deleteSkill）、占位符用 {count} 插值、确认消息用 xxxConfirm
  - `frontend/i18n/locales/zh.json:skills` (lines 55-78) — 中文翻译风格：简洁、避免过度翻译英文术语

  **WHY Each Reference Matters**:
  - 必须保持与 skills 命名空间完全一致的 key 命名规范和翻译风格
  - nav 命名空间是新增的，将被 TopNav 组件使用

  **Acceptance Criteria**:
  - [x] `en.json` 包含 `prompts` 和 `nav` 命名空间
  - [x] `zh.json` 包含 `prompts` 和 `nav` 命名空间
  - [x] 两个文件都是有效 JSON：`cd frontend && node -e "require('./i18n/locales/en.json'); require('./i18n/locales/zh.json'); console.log('VALID')"`
  - [x] prompts 命名空间包含至少 30 个 key

  **QA Scenarios (MANDATORY):**

  ```
  Scenario: JSON 文件有效性
    Tool: Bash
    Preconditions: 文件已编辑
    Steps:
      1. cd frontend && node -e "
         const en = require('./i18n/locales/en.json');
         const zh = require('./i18n/locales/zh.json');
         const enKeys = Object.keys(en.prompts || {});
         const zhKeys = Object.keys(zh.prompts || {});
         console.log('en prompts keys:', enKeys.length);
         console.log('zh prompts keys:', zhKeys.length);
         const missing = enKeys.filter(k => !zhKeys.includes(k));
         if (missing.length > 0) { console.log('FAIL: zh missing keys:', missing); process.exit(1); }
         if (!en.nav || !zh.nav) { console.log('FAIL: nav namespace missing'); process.exit(1); }
         console.log('ALL PASS');"
    Expected Result: 输出 'ALL PASS'，en/zh 的 prompts key 数量一致
    Failure Indicators: JSON 解析错误、key 不匹配
    Evidence: .sisyphus/evidence/task-5-i18n-validation.txt

  Scenario: 翻译 key 不与已有 key 冲突
    Tool: Bash
    Preconditions: 文件已编辑
    Steps:
      1. cd frontend && node -e "
         const en = require('./i18n/locales/en.json');
         const topKeys = Object.keys(en);
         const expected = ['home','common','auth','skills','skillForm','import','files','editor','errors','time','language','progress','conflict','fileViewer','download','prompts','nav'];
         const unexpected = topKeys.filter(k => !expected.includes(k));
         if (unexpected.length > 0) { console.log('FAIL: unexpected keys:', unexpected); process.exit(1); }
         console.log('ALL PASS');"
    Expected Result: 只有已知的 top-level key
    Failure Indicators: 出现意外的 top-level key
    Evidence: .sisyphus/evidence/task-5-i18n-no-conflicts.txt
  ```

  **Commit**: YES (group with Tasks 4, 6)
  - Message: `feat(prompt): add frontend types, store, i18n, and TopNav`
  - Files: `frontend/i18n/locales/en.json`, `frontend/i18n/locales/zh.json`

- [x] 6. Frontend TopNav Component

  **What to do**:
  - 创建 `frontend/components/layout/TopNav.tsx`：
    - 客户端组件（`'use client'`）
    - 接收当前路径，高亮当前 tab（Skills / Prompts）
    - 使用 `next-intl` 的 `useTranslations('nav')` 获取翻译
    - 使用 `next/link` + `usePathname()` 实现导航
    - 导航链接：`/{locale}/skills` 和 `/{locale}/prompts`
    - 当前页面 tab 高亮样式（下边框或背景色）
    - 右侧显示用户信息和语言切换（复用或参考现有 Skills 页面头部的用户菜单逻辑）
    - 响应式设计：移动端适配
  - 修改 `frontend/app/[locale]/skills/page.tsx`：
    - 在页面顶部添加 `<TopNav />` 组件
    - 移除或保留已有的页面标题，确保布局一致
  - **注意**：Prompts 页面的 TopNav 集成将在 Task 13 中完成

  **Must NOT do**:
  - 不添加全局侧边栏
  - 不修改 `app/[locale]/layout.tsx`（TopNav 是页面级组件，不是 layout 级）
  - 不破坏现有 Skills 页面的功能

  **Recommended Agent Profile**:
  - **Category**: `quick`
    - Reason: 单个新组件 + 一处集成，UI 模式简单
  - **Skills**: `[]`
  - **Skills Evaluated but Omitted**:
    - `frontend-ui-ux`: TopNav 是简单的 tab 导航，不需要复杂 UI 设计
    - `playwright`: 验证在 QA 场景中完成，不需要在实现阶段使用

  **Parallelization**:
  - **Can Run In Parallel**: YES
  - **Parallel Group**: Wave 1 (with Tasks 1, 2, 3, 4, 5)
  - **Blocks**: Tasks 11, 13
  - **Blocked By**: None

  **References**:

  **Pattern References**:
  - `frontend/app/[locale]/skills/page.tsx` (lines 1-50) — 现有页面头部结构：UserMenu、搜索栏、按钮布局，TopNav 需要与之协调
  - `frontend/components/ui/` — 可复用 UI 组件目录

  **API/Type References**:
  - `frontend/i18n/locales/en.json:nav` (Task 5 产出) — 导航翻译 key

  **External References**:
  - Next.js App Router `usePathname()`: 获取当前路径以确定 active tab
  - `next-intl` `useTranslations()`: 国际化翻译函数

  **WHY Each Reference Matters**:
  - Skills 页面的头部结构决定了 TopNav 的视觉集成方式——TopNav 应位于现有头部之上
  - TopNav 在两个页面间共享，但以组件方式（非 layout）引入，避免修改全局 layout

  **Acceptance Criteria**:
  - [x] `frontend/components/layout/TopNav.tsx` 存在
  - [x] Skills 页面显示 TopNav
  - [x] TopNav 包含 Skills 和 Prompts 两个导航链接
  - [x] 当前页面 tab 有高亮样式
  - [x] TypeScript 编译无错误

  **QA Scenarios (MANDATORY):**

  ```
  Scenario: TopNav 在 Skills 页面渲染
    Tool: Playwright (playwright skill)
    Preconditions: 前后端服务运行中，用户已登录
    Steps:
      1. 导航到 http://localhost:3000/en/skills
      2. 等待页面加载完成
      3. 查找 TopNav 组件（选择器：`nav` 或 `[data-testid="top-nav"]`）
      4. 验证存在 'Skills' 链接（href 包含 /skills）
      5. 验证存在 'Prompts' 链接（href 包含 /prompts）
      6. 验证 Skills 链接有 active 样式（检查 CSS class）
      7. 截图
    Expected Result: TopNav 可见，包含两个导航项，Skills 为 active 状态
    Failure Indicators: TopNav 不存在、链接缺失、无 active 样式
    Evidence: .sisyphus/evidence/task-6-topnav-skills.png

  Scenario: TopNav 导航链接正确指向
    Tool: Playwright (playwright skill)
    Preconditions: 用户已登录，在 Skills 页面
    Steps:
      1. 在 TopNav 中点击 'Prompts' 链接
      2. 验证 URL 变为 /en/prompts（可能 404，因为 Prompts 页面尚未创建）
      3. 返回 Skills 页面
      4. 验证 Skills 页面内容仍然正常显示
    Expected Result: 导航链接正确跳转，Skills 页面不受影响
    Failure Indicators: 链接 href 错误、Skills 页面损坏
    Evidence: .sisyphus/evidence/task-6-topnav-navigation.png
  ```

  **Commit**: YES (group with Tasks 4, 5)
  - Message: `feat(prompt): add frontend types, store, i18n, and TopNav`
  - Files: `frontend/components/layout/TopNav.tsx`, `frontend/app/[locale]/skills/page.tsx`


- [x] 7. Infrastructure Layer — ORM Models + SQL Repository

  **What to do**:
  - 创建 `backend/src/infra/persistence/models/prompt_model.py`：
    - `PromptModel(Base)`：`__tablename__ = "prompts"`，字段映射 domain aggregate 的所有属性
      - `id: Mapped[UUID]` PK default uuid4
      - `user_id: Mapped[UUID]` FK → users.id
      - `title: Mapped[str]` VARCHAR(200)
      - `content: Mapped[str]` TEXT
      - `description: Mapped[str | None]` VARCHAR(1000)
      - `tags: Mapped[list[str]]` — 使用 `ARRAY(String)` 类型（PostgreSQL）
      - `version: Mapped[int]` default 1
      - `created_at: Mapped[datetime]` server_default=text("NOW()")
      - `updated_at: Mapped[datetime]` server_default=text("NOW()"), onupdate=text("NOW()")
      - `to_domain() -> Prompt` 方法：转换为 domain aggregate
      - `from_domain(cls, prompt: Prompt) -> PromptModel` 类方法：从 domain 转换
    - `PromptVersionModel(Base)`：`__tablename__ = "prompt_versions"`
      - `id: Mapped[UUID]` PK default uuid4
      - `prompt_id: Mapped[UUID]` FK → prompts.id (CASCADE)
      - `version_number: Mapped[int]`
      - `title: Mapped[str]` VARCHAR(200)
      - `content: Mapped[str]` TEXT
      - `description: Mapped[str | None]` VARCHAR(1000)
      - `tags: Mapped[list[str]]` ARRAY(String)
      - `created_at: Mapped[datetime]` server_default=text("NOW()")
      - `to_domain() -> PromptVersion` 方法
      - `from_domain(cls, version: PromptVersion) -> PromptVersionModel` 类方法
    - **不使用 `relationship()`**，仅通过 ForeignKey 关联
  - 创建 `backend/src/infra/persistence/repositories/sql_prompt_repository.py`：
    - `SqlPromptRepository(PromptRepository)` 实现所有接口方法：
      - `__init__(self, db: AsyncSession)`
      - `async get_by_id(prompt_id: UUID) -> Prompt | None`：查询 PromptModel → to_domain()
      - `async find_by_user(user_id: UUID, offset=0, limit=20, tag: str | None = None, search: str | None = None) -> list[Prompt]`：
        - 基础条件：`user_id == user_id`
        - tag 过滤：`PromptModel.tags.any(tag)` （PostgreSQL ARRAY any）
        - search 过滤：`PromptModel.title.ilike(f"%{search}%")`
        - 排序：`updated_at DESC`
        - 分页：`offset + limit`
      - `async count_by_user(user_id: UUID, tag: str | None = None, search: str | None = None) -> int`：同条件 count
      - `async save(prompt: Prompt)`：`PromptModel.from_domain(prompt)` → `db.merge()` → `db.flush()`
      - `async delete(prompt_id: UUID)`：查询 → `db.delete()` → `db.flush()`
      - `async save_version(version: PromptVersion)`：`PromptVersionModel.from_domain(version)` → `db.merge()` → `db.flush()`
      - `async find_versions(prompt_id: UUID) -> list[PromptVersion]`：按 version_number DESC 排序
      - `async get_version(version_id: UUID) -> PromptVersion | None`

  **Must NOT do**:
  - 不在 ORM model 中使用 `relationship()`
  - 不导入 domain 层以外的模块（domain 模型仅用于类型引用）
  - 不在 repository 中添加业务逻辑（仅数据访问）
  - 不使用 `text()` 构建动态 SQL 查询（使用 SQLAlchemy ORM API）

  **Recommended Agent Profile**:
  - **Category**: `unspecified-high`
    - Reason: 涉及 SQLAlchemy 高级特性（ARRAY 类型、merge、ilike）、2 个 model + 1 个 repository 文件
  - **Skills**: `[]`
  - **Skills Evaluated but Omitted**:
    - `playwright`: 纯后端任务，不涉及 UI

  **Parallelization**:
  - **Can Run In Parallel**: YES (within Wave 2)
  - **Parallel Group**: Wave 2 (with Tasks 8, 9, 10, 11)
  - **Blocks**: Tasks 8, 9, 10, 12
  - **Blocked By**: Tasks 1 (migration), 2 (domain aggregate), 3 (domain factory + repo interface)

  **References**:

  **Pattern References**:
  - `backend/src/infra/persistence/models/skill_model.py` — ORM model 完整模式：`mapped_column` 声明、`to_domain()`/`from_domain()` 转换、`server_default=text("NOW()")` 时间戳、FK 声明无 relationship
  - `backend/src/infra/persistence/repositories/sql_skill_repository.py` — Repository 实现模式：AsyncSession 注入、select() 查询构建、merge + flush 保存、delete 实现
  - `backend/src/infra/persistence/db/base.py` — Base 类导入路径

  **API/Type References**:
  - `backend/src/domain/aggregates/prompt.py` (Task 2 产出) — domain Prompt aggregate 结构，ORM 的 `to_domain()`/`from_domain()` 必须与之匹配
  - `backend/src/domain/entities/prompt_version.py` (Task 2 产出) — PromptVersion entity 结构
  - `backend/src/domain/repositories/prompt_repository.py` (Task 3 产出) — 抽象接口定义，SQL 实现必须完全实现所有方法

  **WHY Each Reference Matters**:
  - SkillModel 是最相似的 ORM model，必须完全遵循其 `mapped_column` 风格、`text("NOW()")` 用法
  - SqlSkillRepository 展示了 `merge + flush` 保存模式和 `select()` 查询构建模式
  - ARRAY(String) 类型的 `any()` 过滤是 PostgreSQL 特有的——需要确保正确使用

  **Acceptance Criteria**:
  - [x] `backend/src/infra/persistence/models/prompt_model.py` 存在且包含 PromptModel + PromptVersionModel
  - [x] `backend/src/infra/persistence/repositories/sql_prompt_repository.py` 存在且实现所有接口方法
  - [x] ORM model 无 `relationship()` 调用
  - [x] Python 语法检查通过：`cd backend && python -c "from src.infra.persistence.models.prompt_model import PromptModel, PromptVersionModel; print('OK')"`
  - [x] Repository 可导入：`cd backend && python -c "from src.infra.persistence.repositories.sql_prompt_repository import SqlPromptRepository; print('OK')"`

  **QA Scenarios (MANDATORY):**

  ```
  Scenario: ORM Model 结构正确
    Tool: Bash
    Preconditions: Task 1 migration 已完成，Task 2 domain 层已完成
    Steps:
      1. cd backend && python -c "
         from src.infra.persistence.models.prompt_model import PromptModel, PromptVersionModel
         # 验证 PromptModel 字段
         assert hasattr(PromptModel, 'id'), 'Missing id'
         assert hasattr(PromptModel, 'user_id'), 'Missing user_id'
         assert hasattr(PromptModel, 'title'), 'Missing title'
         assert hasattr(PromptModel, 'content'), 'Missing content'
         assert hasattr(PromptModel, 'tags'), 'Missing tags'
         assert hasattr(PromptModel, 'version'), 'Missing version'
         assert PromptModel.__tablename__ == 'prompts', 'Wrong tablename'
         # 验证 PromptVersionModel 字段
         assert hasattr(PromptVersionModel, 'prompt_id'), 'Missing prompt_id'
         assert hasattr(PromptVersionModel, 'version_number'), 'Missing version_number'
         assert PromptVersionModel.__tablename__ == 'prompt_versions', 'Wrong tablename'
         print('ALL PASS')"
    Expected Result: 输出 'ALL PASS'
    Failure Indicators: ImportError、AssertionError
    Evidence: .sisyphus/evidence/task-7-orm-model-check.txt

  Scenario: to_domain / from_domain 往返转换
    Tool: Bash
    Preconditions: domain 层和 ORM model 均已就绪
    Steps:
      1. cd backend && python -c "
         from uuid import uuid4
         from src.domain.aggregates.prompt import Prompt
         from src.infra.persistence.models.prompt_model import PromptModel
         p = Prompt(id=uuid4(), user_id=uuid4(), title='Test', content='Hello {{name}}',
           description='desc', tags=['tag1','tag2'], version=1)
         model = PromptModel.from_domain(p)
         restored = model.to_domain()
         assert restored.title == 'Test', f'Title mismatch: {restored.title}'
         assert restored.tags == ['tag1','tag2'], f'Tags mismatch: {restored.tags}'
         assert restored.content == 'Hello {{name}}', f'Content mismatch'
         print('ALL PASS')"
    Expected Result: 输出 'ALL PASS'
    Failure Indicators: AssertionError、属性错误
    Evidence: .sisyphus/evidence/task-7-roundtrip.txt

  Scenario: Repository 无 relationship 违规
    Tool: Bash
    Preconditions: model 文件已创建
    Steps:
      1. cd backend && grep -n 'relationship(' src/infra/persistence/models/prompt_model.py || echo 'CLEAN'
    Expected Result: 输出 'CLEAN'（无 relationship 调用）
    Failure Indicators: 输出包含 relationship 行号
    Evidence: .sisyphus/evidence/task-7-no-relationship.txt
  ```

  **Commit**: YES
  - Message: `feat(prompt): add infrastructure layer - ORM models and SQL repository`
  - Files: `backend/src/infra/persistence/models/prompt_model.py`, `backend/src/infra/persistence/repositories/sql_prompt_repository.py`
  - Pre-commit: `cd backend && python -c "from src.infra.persistence.models.prompt_model import PromptModel; print('OK')"`

- [x] 8. Application Handlers — CRUD Operations

  **What to do**:
  - 创建以下 handler 文件（每个文件一个用例函数），放在 `backend/src/application/handlers/` 下：
  - `create_prompt_handler.py`：
    - `async def handle_create_prompt(user_id: UUID, title: str, content: str, description: str | None, tags: list[str], prompt_repo: PromptRepository) -> Prompt`
    - 使用 PromptFactory.create() 创建 aggregate
    - tags 自动规范化：lowercase + deduplicate（在 factory 或 handler 中处理）
    - 验证：title 长度 ≤ 200，description 长度 ≤ 1000，tags 数量 ≤ 20，tag 名称 ≤ 50 字符
    - 调用 `prompt_repo.save(prompt)` 保存
    - 返回创建的 Prompt aggregate
  - `list_prompts_handler.py`：
    - `async def handle_list_prompts(user_id: UUID, offset: int, limit: int, tag: str | None, search: str | None, prompt_repo: PromptRepository) -> tuple[list[Prompt], int]`
    - 调用 `prompt_repo.find_by_user()` 和 `prompt_repo.count_by_user()` 获取列表和总数
    - 返回 (prompts, total_count) tuple
  - `get_prompt_handler.py`：
    - `async def handle_get_prompt(user_id: UUID, prompt_id: UUID, prompt_repo: PromptRepository) -> Prompt`
    - 查询 prompt，如果不存在抛出 `ResourceNotFoundError`
    - 检查 ownership：`prompt.user_id != user_id` → 抛出 `ForbiddenError`
    - 返回 Prompt
  - `update_prompt_handler.py`：
    - `async def handle_update_prompt(user_id: UUID, prompt_id: UUID, title: str | None, content: str | None, description: str | None, tags: list[str] | None, prompt_repo: PromptRepository) -> Prompt`
    - 获取 prompt + ownership 检查（复用 get 逻辑）
    - 仅更新提供的非 None 字段
    - 如果更新了任何字段，`version += 1`
    - tags 规范化（如果提供了 tags）
    - 调用 `prompt_repo.save(prompt)` 保存
  - `delete_prompt_handler.py`：
    - `async def handle_delete_prompt(user_id: UUID, prompt_id: UUID, prompt_repo: PromptRepository) -> None`
    - 获取 prompt + ownership 检查
    - 调用 `prompt_repo.delete(prompt_id)` 删除（CASCADE 会自动删除版本）

  **Must NOT do**:
  - 不导入 FastAPI 或 HTTP 相关模块
  - 不导入 SQLAlchemy 或 ORM 模块
  - 不在 handler 中直接操作数据库
  - 不跳过 ownership 检查（get/update/delete 都必须检查）
  - 不使用 try/except 捕获 domain 异常（让它们冒泡到 API 层）

  **Recommended Agent Profile**:
  - **Category**: `unspecified-high`
    - Reason: 5 个 handler 文件，需要严格遵循 DDD 模式，涉及验证逻辑和 ownership 检查
  - **Skills**: `[]`

  **Parallelization**:
  - **Can Run In Parallel**: YES (within Wave 2, partially)
  - **Parallel Group**: Wave 2 (with Tasks 7, 9, 10, 11)
  - **Blocks**: Task 12 (API layer)
  - **Blocked By**: Tasks 2 (domain aggregate), 3 (factory + repo interface), 7 (SQL repository)

  **References**:

  **Pattern References**:
  - `backend/src/application/handlers/create_skill_handler.py` — Handler 函数签名模式：纯 async 函数，接收原始参数 + repository 接口，返回 domain 对象
  - `backend/src/application/handlers/get_skill_handler.py` — Ownership 检查模式：`if skill.user_id != user_id: raise ForbiddenError()`
  - `backend/src/application/handlers/update_skill_handler.py` — 更新模式：获取 → 检查 ownership → 逐字段更新 → save
  - `backend/src/application/handlers/list_skills_handler.py` — 列表查询模式

  **API/Type References**:
  - `backend/src/domain/aggregates/prompt.py` (Task 2 产出) — Prompt aggregate 结构和方法
  - `backend/src/domain/factories/prompt_factory.py` (Task 3 产出) — PromptFactory.create() 方法签名
  - `backend/src/domain/repositories/prompt_repository.py` (Task 3 产出) — Repository 接口方法签名
  - `backend/src/domain/exceptions.py` — ValidationError、ResourceNotFoundError、ForbiddenError 导入路径

  **WHY Each Reference Matters**:
  - create_skill_handler 展示了 Factory → repo.save 的标准流程
  - get_skill_handler 展示了 ownership 检查的精确模式（必须一致）
  - domain exceptions 是唯一允许的错误处理方式——不能使用 HTTPException

  **Acceptance Criteria**:
  - [x] 5 个 handler 文件都存在于 `backend/src/application/handlers/` 下
  - [x] 所有 handler 无 FastAPI/SQLAlchemy 导入
  - [x] 所有 handler 可导入：`cd backend && python -c "from src.application.handlers.create_prompt_handler import handle_create_prompt; print('OK')"`
  - [x] get/update/delete handler 包含 ownership 检查（grep ForbiddenError）

  **QA Scenarios (MANDATORY):**

  ```
  Scenario: 所有 CRUD handler 可导入
    Tool: Bash
    Preconditions: domain 层和 handler 文件已创建
    Steps:
      1. cd backend && python -c "
         from src.application.handlers.create_prompt_handler import handle_create_prompt
         from src.application.handlers.list_prompts_handler import handle_list_prompts
         from src.application.handlers.get_prompt_handler import handle_get_prompt
         from src.application.handlers.update_prompt_handler import handle_update_prompt
         from src.application.handlers.delete_prompt_handler import handle_delete_prompt
         import inspect
         # 验证都是 async 函数
         for fn in [handle_create_prompt, handle_list_prompts, handle_get_prompt, handle_update_prompt, handle_delete_prompt]:
           assert inspect.iscoroutinefunction(fn), f'{fn.__name__} is not async'
         print('ALL PASS')"
    Expected Result: 输出 'ALL PASS'
    Failure Indicators: ImportError、不是 async 函数
    Evidence: .sisyphus/evidence/task-8-crud-import.txt

  Scenario: Handler 无 FastAPI/SQLAlchemy 依赖
    Tool: Bash
    Preconditions: handler 文件已创建
    Steps:
      1. cd backend && for f in src/application/handlers/*prompt*.py; do
           echo "--- $f ---"
           grep -n 'from fastapi\|from sqlalchemy\|import fastapi\|import sqlalchemy' "$f" && echo 'FAIL' || echo 'CLEAN'
         done
    Expected Result: 所有文件输出 'CLEAN'
    Failure Indicators: 任何文件包含 fastapi 或 sqlalchemy 导入
    Evidence: .sisyphus/evidence/task-8-no-infra-imports.txt

  Scenario: Ownership 检查存在
    Tool: Bash
    Preconditions: handler 文件已创建
    Steps:
      1. cd backend && for f in get_prompt_handler.py update_prompt_handler.py delete_prompt_handler.py; do
           echo "--- $f ---"
           grep -c 'ForbiddenError' src/application/handlers/$f
         done
    Expected Result: 每个文件至少有 1 次 ForbiddenError 引用
    Failure Indicators: grep 输出 0
    Evidence: .sisyphus/evidence/task-8-ownership-check.txt
  ```

  **Commit**: YES (group with Tasks 9, 10)
  - Message: `feat(prompt): add application handlers - CRUD, versioning, import/export`
  - Files: `backend/src/application/handlers/create_prompt_handler.py`, `backend/src/application/handlers/list_prompts_handler.py`, `backend/src/application/handlers/get_prompt_handler.py`, `backend/src/application/handlers/update_prompt_handler.py`, `backend/src/application/handlers/delete_prompt_handler.py`

- [x] 9. Application Handlers — Version Management

  **What to do**:
  - 创建以下 handler 文件，放在 `backend/src/application/handlers/` 下：
  - `publish_prompt_version_handler.py`：
    - `async def handle_publish_prompt_version(user_id: UUID, prompt_id: UUID, prompt_repo: PromptRepository) -> PromptVersion`
    - 获取 prompt + ownership 检查
    - 调用 `prompt.publish_version()` 方法（aggregate 内部逻辑：snapshot 当前内容为新版本）
    - 调用 `prompt_repo.save_version(version)` 保存版本快照
    - 返回创建的 PromptVersion entity
  - `list_prompt_versions_handler.py`：
    - `async def handle_list_prompt_versions(user_id: UUID, prompt_id: UUID, prompt_repo: PromptRepository) -> list[PromptVersion]`
    - 获取 prompt + ownership 检查
    - 调用 `prompt_repo.find_versions(prompt_id)` 获取版本列表
  - `get_prompt_version_handler.py`：
    - `async def handle_get_prompt_version(user_id: UUID, prompt_id: UUID, version_id: UUID, prompt_repo: PromptRepository) -> PromptVersion`
    - 获取 prompt + ownership 检查
    - 调用 `prompt_repo.get_version(version_id)` 获取版本
    - 如果 version 不存在或 version.prompt_id != prompt_id 则抛出 ResourceNotFoundError

  **Must NOT do**:
  - 不导入 FastAPI 或 SQLAlchemy
  - 不跳过 ownership 检查
  - 不在 handler 中实现版本快照逻辑（这是 aggregate 的职责）

  **Recommended Agent Profile**:
  - **Category**: `quick`
    - Reason: 3 个简单 handler，遵循与 Task 8 相同的模式
  - **Skills**: `[]`

  **Parallelization**:
  - **Can Run In Parallel**: YES (within Wave 2)
  - **Parallel Group**: Wave 2 (with Tasks 7, 8, 10, 11)
  - **Blocks**: Task 12 (API layer)
  - **Blocked By**: Tasks 2 (domain aggregate), 3 (factory + repo interface), 7 (SQL repository)

  **References**:

  **Pattern References**:
  - `backend/src/application/handlers/get_skill_handler.py` — Ownership 检查 + ResourceNotFoundError 模式
  - Task 8 的 handler 文件 — 遵循相同的函数签名和 import 模式

  **API/Type References**:
  - `backend/src/domain/aggregates/prompt.py` (Task 2 产出) — `publish_version()` 方法：创建 PromptVersion snapshot
  - `backend/src/domain/entities/prompt_version.py` (Task 2 产出) — PromptVersion entity 结构
  - `backend/src/domain/repositories/prompt_repository.py` (Task 3 产出) — `save_version()`、`find_versions()`、`get_version()` 方法签名

  **WHY Each Reference Matters**:
  - publish_version() 是 aggregate 方法，handler 仅负责调用它——不要在 handler 中重新实现快照逻辑
  - version 的 ownership 检查通过 prompt 间接完成（先检查 prompt 的 owner，再操作 version）

  **Acceptance Criteria**:
  - [x] 3 个 handler 文件都存在
  - [x] 所有 handler 可导入
  - [x] 无 FastAPI/SQLAlchemy 导入
  - [x] 每个 handler 都有 ownership 检查

  **QA Scenarios (MANDATORY):**

  ```
  Scenario: Version handler 可导入且为 async
    Tool: Bash
    Preconditions: domain 层和 handler 文件已创建
    Steps:
      1. cd backend && python -c "
         from src.application.handlers.publish_prompt_version_handler import handle_publish_prompt_version
         from src.application.handlers.list_prompt_versions_handler import handle_list_prompt_versions
         from src.application.handlers.get_prompt_version_handler import handle_get_prompt_version
         import inspect
         for fn in [handle_publish_prompt_version, handle_list_prompt_versions, handle_get_prompt_version]:
           assert inspect.iscoroutinefunction(fn), f'{fn.__name__} is not async'
         print('ALL PASS')"
    Expected Result: 输出 'ALL PASS'
    Failure Indicators: ImportError、不是 async 函数
    Evidence: .sisyphus/evidence/task-9-version-import.txt

  Scenario: Version handler 无基础设施依赖
    Tool: Bash
    Preconditions: handler 文件已创建
    Steps:
      1. cd backend && for f in publish_prompt_version_handler.py list_prompt_versions_handler.py get_prompt_version_handler.py; do
           echo "--- $f ---"
           grep -n 'from fastapi\|from sqlalchemy' src/application/handlers/$f && echo 'FAIL' || echo 'CLEAN'
         done
    Expected Result: 所有文件输出 'CLEAN'
    Failure Indicators: 任何文件包含 fastapi/sqlalchemy 导入
    Evidence: .sisyphus/evidence/task-9-no-infra-imports.txt
  ```

  **Commit**: YES (group with Tasks 8, 10)
  - Message: `feat(prompt): add application handlers - CRUD, versioning, import/export`
  - Files: `backend/src/application/handlers/publish_prompt_version_handler.py`, `backend/src/application/handlers/list_prompt_versions_handler.py`, `backend/src/application/handlers/get_prompt_version_handler.py`

- [x] 10. Application Handlers — Import/Export

  **What to do**:
  - 创建以下 handler 文件，放在 `backend/src/application/handlers/` 下：
  - `import_prompt_handler.py`：
    - `async def handle_import_prompt(user_id: UUID, markdown_content: str, prompt_repo: PromptRepository) -> Prompt`
    - 解析 Markdown 内容，提取 YAML frontmatter：
      ```
      ---
      title: "Prompt Title"
      description: "Description"
      tags:
        - tag1
        - tag2
      ---
      Prompt content body here...
      ```
    - 使用 Python 标准库 `yaml`（PyYAML）或简单字符串解析提取 frontmatter
    - 从 frontmatter 提取 title、description、tags
    - frontmatter 之后的内容作为 prompt content
    - 如果无 frontmatter，整个内容作为 content，title 为 "Untitled Prompt"
    - tags 规范化：lowercase + deduplicate
    - 使用 PromptFactory.create() 创建 prompt
    - 调用 prompt_repo.save() 保存
    - 返回创建的 Prompt
  - `export_prompt_handler.py`：
    - `async def handle_export_prompt(user_id: UUID, prompt_id: UUID, prompt_repo: PromptRepository) -> str`
    - 获取 prompt + ownership 检查
    - 生成 Markdown 内容：YAML frontmatter + content body
    - frontmatter 包含：title、description（如果有）、tags（如果非空）
    - 返回完整的 Markdown 字符串

  **Must NOT do**:
  - 不导入 FastAPI 或 SQLAlchemy
  - 不使用外部 Markdown 解析库（frontmatter 解析用 yaml + 简单字符串分割即可）
  - 不验证 content 中的 `{{variable}}` 语法（存储为纯文本）

  **Recommended Agent Profile**:
  - **Category**: `unspecified-high`
    - Reason: 涉及 YAML frontmatter 解析和生成，需要正确处理边界情况（无 frontmatter、空 tags 等）
  - **Skills**: `[]`

  **Parallelization**:
  - **Can Run In Parallel**: YES (within Wave 2)
  - **Parallel Group**: Wave 2 (with Tasks 7, 8, 9, 11)
  - **Blocks**: Task 12 (API layer)
  - **Blocked By**: Tasks 2 (domain aggregate), 3 (factory + repo interface), 7 (SQL repository)

  **References**:

  **Pattern References**:
  - `backend/src/application/handlers/create_skill_handler.py` — Factory → repo.save 模式
  - `backend/src/application/handlers/get_skill_handler.py` — Ownership 检查模式（export 需要）

  **API/Type References**:
  - `backend/src/domain/factories/prompt_factory.py` (Task 3 产出) — PromptFactory.create() 签名
  - `backend/src/domain/aggregates/prompt.py` (Task 2 产出) — Prompt aggregate 属性（title, content, description, tags）

  **External References**:
  - Python `yaml` 模块（PyYAML）：`yaml.safe_load()` 用于解析 frontmatter、`yaml.dump()` 用于生成 frontmatter
  - YAML frontmatter 格式：`---\n` 分隔符之间的 YAML 内容

  **WHY Each Reference Matters**:
  - Import 流程：parse markdown → extract frontmatter → PromptFactory.create() → save，与 create handler 类似但多了解析步骤
  - Export 流程：get prompt → check ownership → generate markdown，与 get handler 类似但多了格式化步骤
  - frontmatter 格式是用户约定的——必须严格遵循 `---` 分隔符 + YAML 语法

  **Acceptance Criteria**:
  - [x] 2 个 handler 文件都存在
  - [x] import handler 能正确解析 YAML frontmatter
  - [x] export handler 能生成有效的 YAML frontmatter
  - [x] 无 FastAPI/SQLAlchemy 导入

  **QA Scenarios (MANDATORY):**

  ```
  Scenario: Import handler 解析 Markdown + YAML frontmatter
    Tool: Bash
    Preconditions: handler 文件已创建
    Steps:
      1. cd backend && python -c "
         # 测试 frontmatter 解析逻辑（不需要数据库）
         import yaml
         md = '''---
         title: \"Test Prompt\"
         description: \"A test\"
         tags:
           - Tag1
           - TAG2
           - tag1
         ---
         Hello {{name}}, welcome to {{place}}!'''
         parts = md.split('---', 2)
         assert len(parts) >= 3, 'Failed to split frontmatter'
         meta = yaml.safe_load(parts[1])
         content = parts[2].strip()
         assert meta['title'] == 'Test Prompt', f'Title: {meta[\"title\"]}'
         assert 'tag1' in [t.lower() for t in meta['tags']], 'Tags not found'
         # 验证 tags 去重（tag1 和 Tag1 lowercase 后相同）
         normalized = list(set(t.lower() for t in meta['tags']))
         assert len(normalized) == 2, f'Expected 2 unique tags, got {len(normalized)}'
         assert '{{name}}' in content, 'Variable not preserved'
         print('ALL PASS')"
    Expected Result: 输出 'ALL PASS'
    Failure Indicators: YAML 解析失败、tags 未正确规范化
    Evidence: .sisyphus/evidence/task-10-import-parse.txt

  Scenario: Export handler 生成有效 Markdown
    Tool: Bash
    Preconditions: handler 文件已创建
    Steps:
      1. cd backend && python -c "
         import yaml
         # 模拟 export 输出格式
         title = 'My Prompt'
         description = 'A useful prompt'
         tags = ['ai', 'coding']
         content = 'Write {{language}} code for {{task}}'
         # 生成 frontmatter
         meta = {'title': title, 'description': description, 'tags': tags}
         md = '---\n' + yaml.dump(meta, default_flow_style=False, allow_unicode=True) + '---\n' + content
         # 验证可以被 import 逻辑解析回来
         parts = md.split('---', 2)
         restored = yaml.safe_load(parts[1])
         assert restored['title'] == title, 'Title mismatch'
         assert restored['tags'] == tags, 'Tags mismatch'
         assert parts[2].strip() == content, 'Content mismatch'
         print('ALL PASS')"
    Expected Result: 输出 'ALL PASS'，导入导出往返一致
    Failure Indicators: YAML 格式错误、内容丢失
    Evidence: .sisyphus/evidence/task-10-export-roundtrip.txt

  Scenario: 无 frontmatter 的 Markdown 导入
    Tool: Bash
    Preconditions: handler 文件已创建
    Steps:
      1. cd backend && python -c "
         md = 'Just plain content without any frontmatter.\nLine 2.'
         # 验证无 frontmatter 的处理逻辑
         if not md.startswith('---'):
           title = 'Untitled Prompt'
           content = md
         else:
           raise Exception('Should not have frontmatter')
         assert title == 'Untitled Prompt', f'Title: {title}'
         assert content == md, 'Content mismatch'
         print('ALL PASS')"
    Expected Result: 输出 'ALL PASS'，无 frontmatter 时 title 为 'Untitled Prompt'
    Failure Indicators: 错误解析普通 Markdown 为 frontmatter
    Evidence: .sisyphus/evidence/task-10-import-no-frontmatter.txt
  ```

  **Commit**: YES (group with Tasks 8, 9)
  - Message: `feat(prompt): add application handlers - CRUD, versioning, import/export`
  - Files: `backend/src/application/handlers/import_prompt_handler.py`, `backend/src/application/handlers/export_prompt_handler.py`

- [x] 11. Frontend Prompt UI Components — List + Editor

  **What to do**:
  - 创建 `frontend/components/prompts/` 目录及以下组件：
  - `PromptList.tsx`（左侧面板组件）：
    - 客户端组件（`'use client'`）
    - 显示 prompt 列表，每项显示 title、tags、version、updated_at
    - 搜索框：绑定 `promptsStore.searchQuery`，实时过滤
    - Tag 过滤：显示所有已用 tags 作为可点击的 chip，点击设置 `selectedTag`
    - 选中状态：点击某个 prompt 设置 `selectedPrompt`，高亮当前项
    - 空状态：无 prompts 时显示 `t('prompts.noPrompts')` + 创建按钮
    - 搜索无结果时显示 `t('prompts.noPromptsFound')` + 调整搜索提示
    - 「新建」按钮：点击后调用创建 API 并选中新创建的 prompt
    - 列表项格式：标题（大字）+ 描述摘要（小字/灰色）+ tags chips + version badge
  - `PromptEditor.tsx`（右侧面板组件）：
    - 客户端组件
    - 当无 selectedPrompt 时显示空状态占位符
    - 当有 selectedPrompt 时显示：
      - 标题输入框：可编辑，绑定 title
      - 描述输入框：可编辑，绑定 description
      - Tags 输入：自由文本 chips 输入组件，回车添加 tag，点击 x 删除 tag
      - 内容编辑器：使用 Monaco Editor（`markdown` 语言模式），绑定 content
      - 工具栏：「保存」、「发布版本」、「导出」、「删除」按钮
    - 自动保存 debounce：内容修改后 2 秒自动保存（可选实现，也可仅手动保存）
    - 保存时调用 update API → 更新 store
    - 删除时显示确认对话框 → 调用 delete API → 从 store 移除 → 取消选中
  - `TagInput.tsx`（可复用 tags 输入组件）：
    - 接收 `tags: string[]` 和 `onChange: (tags: string[]) => void` props
    - 输入框 + chip 列表
    - 回车添加 tag（自动 lowercase + deduplicate）
    - chip 上的 x 按钮删除 tag
    - 验证：tag 名最长 50 字符，最多 20 个 tags
  - **注意**：这些组件在 Task 11 中仅创建，不集成到页面中（页面集成在 Task 13）

  **Must NOT do**:
  - 不直接在组件中调用 fetch/axios — 使用 `lib/api.ts` 的 ApiClient
  - 不创建页面文件（`app/[locale]/prompts/page.tsx` 在 Task 13）
  - 不实现版本历史面板（Task 14）
  - 不实现导入对话框（Task 15）
  - 不在组件中硬编码文本（使用 i18n: `useTranslations('prompts')`）

  **Recommended Agent Profile**:
  - **Category**: `visual-engineering`
    - Reason: 涉及复杂 UI 组件设计——左右分栏列表、Monaco 编辑器集成、Tags chips 输入、空状态等交互设计
  - **Skills**: `['frontend-ui-ux']`
    - `frontend-ui-ux`: 需要设计美观的列表项、编辑器布局、空状态、Tag chips 等 UI 元素，无设计稿需要 AI 自行设计
  - **Skills Evaluated but Omitted**:
    - `playwright`: 验证在 QA 场景中完成，不在实现阶段使用

  **Parallelization**:
  - **Can Run In Parallel**: YES (within Wave 2)
  - **Parallel Group**: Wave 2 (with Tasks 7, 8, 9, 10)
  - **Blocks**: Tasks 13 (Prompts page), 14 (Version history), 15 (Import/Export dialogs)
  - **Blocked By**: Tasks 4 (frontend types + store), 5 (i18n), 6 (TopNav)

  **References**:

  **Pattern References**:
  - `frontend/components/skills/` — Skill UI 组件目录结构和命名规范：SkillCard.tsx、SkillForm.tsx 等
  - `frontend/components/editors/` — Monaco Editor 集成模式：如何配置语言模式、主题、尺寸
  - `frontend/components/ui/` — 可复用 UI 组件（Button、Input、Dialog 等），TagInput 应参考类似样式
  - `frontend/app/[locale]/skills/page.tsx` — 页面如何组合组件、如何调用 store 和 API

  **API/Type References**:
  - `frontend/types/prompt.ts` (Task 4 产出) — Prompt、PromptVersion 等 TypeScript 类型
  - `frontend/stores/promptsStore.ts` (Task 4 产出) — Store 状态和方法签名
  - `frontend/lib/api.ts` — ApiClient 类的 get/post/put/delete 方法签名
  - `frontend/i18n/locales/en.json:prompts` (Task 5 产出) — i18n key 列表

  **External References**:
  - Monaco Editor for React: `@monaco-editor/react` — `<Editor language="markdown" />` 使用方式
  - next-intl `useTranslations()`: 国际化翻译函数

  **WHY Each Reference Matters**:
  - Skills 组件展示了项目的 React 组件模式（hooks 用法、状态管理、API 调用方式）
  - Monaco Editor 组件展示了编辑器的具体配置方式（可能已有包装组件）
  - Prompt 的 UI 布局（左右分栏）不同于 Skills（卡片列表），但组件粒度和交互模式应保持一致
  - TagInput 是新的通用组件——需要参考 `components/ui/` 的样式风格

  **Acceptance Criteria**:
  - [x] `frontend/components/prompts/PromptList.tsx` 存在
  - [x] `frontend/components/prompts/PromptEditor.tsx` 存在
  - [x] `frontend/components/prompts/TagInput.tsx` 存在
  - [x] 所有组件使用 `useTranslations('prompts')` 进行国际化
  - [x] PromptEditor 包含 Monaco Editor 集成
  - [x] TypeScript 编译无错误：`cd frontend && npx tsc --noEmit`

  **QA Scenarios (MANDATORY):**

  ```
  Scenario: 组件文件存在且可编译
    Tool: Bash
    Preconditions: Wave 1 任务完成（types、store、i18n）
    Steps:
      1. cd frontend && npx tsc --noEmit 2>&1 | head -20
    Expected Result: 无 TypeScript 错误
    Failure Indicators: 类型错误、缺少导入
    Evidence: .sisyphus/evidence/task-11-tsc-check.txt

  Scenario: PromptList 渲染空状态
    Tool: Playwright (playwright skill)
    Preconditions: 前后端运行中，用户已登录，无 prompts 数据
    Steps:
      1. 导航到 http://localhost:3000/en/prompts（如果 Task 13 未完成，可创建临时测试页面）
      2. 或者在浏览器 console 中直接渲染组件进行验证
      3. 如果 Task 13 已完成：验证左侧面板显示空状态文本
    Expected Result: 显示 'No prompts yet' 或对应国际化文本
    Failure Indicators: 组件渲染错误、白屏
    Evidence: .sisyphus/evidence/task-11-empty-state.png

  Scenario: TagInput 组件功能验证
    Tool: Playwright (playwright skill)
    Preconditions: TagInput 组件可渲染
    Steps:
      1. 渲染 TagInput 组件（通过测试页面或 Storybook）
      2. 在输入框中输入 'TestTag' 后按 Enter
      3. 验证显示 'testtag' chip（自动 lowercase）
      4. 输入 'testtag' 再次按 Enter
      5. 验证仍然只有 1 个 chip（自动去重）
      6. 点击 chip 上的 x 按钮
      7. 验证 chip 被移除
    Expected Result: Tag 自动 lowercase、去重、可删除
    Failure Indicators: 未 lowercase、重复添加、无法删除
    Evidence: .sisyphus/evidence/task-11-taginput.png
  ```

  **Commit**: YES
  - Message: `feat(prompt): add frontend prompt list and editor components`
  - Files: `frontend/components/prompts/PromptList.tsx`, `frontend/components/prompts/PromptEditor.tsx`, `frontend/components/prompts/TagInput.tsx`

- [x] 12. API Layer — Schemas, Router, Registration

  **What to do**:
  - 创建 `backend/src/api/schemas/prompt.py`：
    - Pydantic DTO 模型，用于请求/响应序列化：
    - `CreatePromptRequest`：title (str, max_length=200), content (str), description (str | None, max_length=1000), tags (list[str], default=[])
    - `UpdatePromptRequest`：title (str | None), content (str | None), description (str | None), tags (list[str] | None) — 所有字段 Optional
    - `ImportPromptRequest`：markdown_content (str)
    - `PromptResponse`：id, user_id, title, content, description, tags, version, created_at, updated_at + `from_domain(cls, prompt: Prompt)` classmethod
    - `PromptListResponse`：items (list[PromptResponse]), total (int), offset (int), limit (int)
    - `PromptVersionResponse`：id, prompt_id, version_number, title, content, description, tags, created_at + `from_domain(cls, version: PromptVersion)` classmethod
    - `ExportPromptResponse`：markdown_content (str)
  - 创建 `backend/src/api/routers/prompts.py`：
    - FastAPI router，前缀 `/api/prompts`，tags=["prompts"]
    - 所有端点要求 JWT 认证（使用现有的 `get_current_user` dependency）
    - 每个路由函数：注入 repository dependency → 调用 handler → 转换为 DTO 返回
    - `POST /` → create_prompt_handler → 201 Created
    - `GET /` → list_prompts_handler → 200 — Query params: offset, limit, tag, search
    - `GET /{prompt_id}` → get_prompt_handler → 200
    - `PUT /{prompt_id}` → update_prompt_handler → 200
    - `DELETE /{prompt_id}` → delete_prompt_handler → 204 No Content
    - `POST /{prompt_id}/versions` → publish_prompt_version_handler → 201
    - `GET /{prompt_id}/versions` → list_prompt_versions_handler → 200
    - `GET /{prompt_id}/versions/{version_id}` → get_prompt_version_handler → 200
    - `POST /import` → import_prompt_handler → 201
    - `GET /{prompt_id}/export` → export_prompt_handler → 200
    - 错误处理：捕获 domain exceptions → HTTP 状态码映射（参考 skills router 的模式）
  - 修改 `backend/src/api/dependencies/repositories.py`：
    - 添加 `get_prompt_repository` dependency，返回 `SqlPromptRepository(db)`
  - 修改 `backend/src/api/__init__.py` 或 `backend/src/main.py`：
    - 注册 prompts router：`app.include_router(prompts_router)`

  **Must NOT do**:
  - 不在 router 中实现业务逻辑（仅做 DTO 转换 + handler 调用）
  - 不跳过 JWT 认证
  - 不修改现有的 skills router
  - 不添加 CORS 或全局中间件配置

  **Recommended Agent Profile**:
  - **Category**: `unspecified-high`
    - Reason: 涉及 10 个 API 端点、DTO 设计、DI 集成、router 注册，需要严格遵循现有模式
  - **Skills**: `[]`

  **Parallelization**:
  - **Can Run In Parallel**: NO (depends on multiple Wave 2 tasks)
  - **Parallel Group**: Wave 3 (with Tasks 13, 14, 15)
  - **Blocks**: Tasks 16 (backend tests), 18 (integration)
  - **Blocked By**: Tasks 7 (SQL repository), 8 (CRUD handlers), 9 (version handlers), 10 (import/export handlers)

  **References**:

  **Pattern References**:
  - `backend/src/api/routers/skills.py` — 完整的 router 模式：装饰器用法、dependency 注入、handler 调用、DTO 返回、错误处理
  - `backend/src/api/schemas/skill.py` — Pydantic DTO 模式：`from_domain()` classmethod、字段验证、BaseModel 配置
  - `backend/src/api/dependencies/repositories.py` — DI 模式：`get_skill_repository` → `SqlSkillRepository(db)`
  - `backend/src/api/__init__.py` — Router 注册模式：`app.include_router()`

  **API/Type References**:
  - `backend/src/domain/aggregates/prompt.py` (Task 2 产出) — `from_domain()` 需要映射的 domain 属性
  - `backend/src/domain/entities/prompt_version.py` (Task 2 产出) — PromptVersion 的 domain 属性
  - 所有 10 个 handler 文件 (Tasks 8-10 产出) — handler 函数签名（参数顺序 + 返回类型）
  - `backend/src/infra/persistence/repositories/sql_prompt_repository.py` (Task 7 产出) — SqlPromptRepository 导入路径

  **WHY Each Reference Matters**:
  - Skills router 是最直接的参考——Prompts router 应完全复制其代码组织模式
  - DTO 的 `from_domain()` 方法是 domain → API 的桥梁，必须覆盖所有字段
  - DI 注册是必须的——否则 handler 无法获取 repository 实例

  **Acceptance Criteria**:
  - [x] `backend/src/api/schemas/prompt.py` 存在且包含所有 DTO
  - [x] `backend/src/api/routers/prompts.py` 存在且包含 10 个端点
  - [x] `backend/src/api/dependencies/repositories.py` 包含 `get_prompt_repository`
  - [x] Router 已注册到 app
  - [x] API 文档可访问：`curl http://localhost:8000/docs` 显示 prompts 端点
  - [x] 未认证请求返回 401：`curl -s -o /dev/null -w '%{http_code}' http://localhost:8000/api/prompts` → 401

  **QA Scenarios (MANDATORY):**

  ```
  Scenario: 创建 Prompt API 完整流程
    Tool: Bash (curl)
    Preconditions: 后端服务运行中，数据库 migration 已应用，有测试用户
    Steps:
      1. 登录获取 token：
         TOKEN=$(curl -s -X POST http://localhost:8000/api/auth/login \
           -H 'Content-Type: application/json' \
           -d '{"email":"test@example.com","password":"password123"}' | jq -r '.access_token')
      2. 创建 prompt：
         RESULT=$(curl -s -X POST http://localhost:8000/api/prompts \
           -H "Authorization: Bearer $TOKEN" \
           -H 'Content-Type: application/json' \
           -d '{"title":"Test Prompt","content":"Hello {{name}}","tags":["test","demo"]}')
         PROMPT_ID=$(echo $RESULT | jq -r '.id')
      3. 验证创建结果：
         echo $RESULT | jq '.title' | grep -q 'Test Prompt'
      4. 获取 prompt：
         curl -s http://localhost:8000/api/prompts/$PROMPT_ID \
           -H "Authorization: Bearer $TOKEN" | jq '.version'
    Expected Result: 创建返回 201，包含 id/title/content/tags，get 返回 version=1
    Failure Indicators: HTTP 错误码、缺少字段、JSON 解析失败
    Evidence: .sisyphus/evidence/task-12-create-flow.txt

  Scenario: 未认证请求被拒绝
    Tool: Bash (curl)
    Preconditions: 后端服务运行中
    Steps:
      1. curl -s -o /dev/null -w '%{http_code}' http://localhost:8000/api/prompts
      2. curl -s -o /dev/null -w '%{http_code}' -X POST http://localhost:8000/api/prompts \
           -H 'Content-Type: application/json' -d '{"title":"Test","content":"Hi"}'
    Expected Result: 两个请求都返回 401
    Failure Indicators: 返回 200 或其他状态码
    Evidence: .sisyphus/evidence/task-12-auth-check.txt

  Scenario: 列表查询 + 分页 + Tag 过滤
    Tool: Bash (curl)
    Preconditions: 已创建多个 prompts，部分带 tags
    Steps:
      1. 列表查询：
         curl -s 'http://localhost:8000/api/prompts?offset=0&limit=10' \
           -H "Authorization: Bearer $TOKEN" | jq '.total'
      2. Tag 过滤：
         curl -s 'http://localhost:8000/api/prompts?tag=test' \
           -H "Authorization: Bearer $TOKEN" | jq '.items | length'
      3. 标题搜索：
         curl -s 'http://localhost:8000/api/prompts?search=Test' \
           -H "Authorization: Bearer $TOKEN" | jq '.items | length'
    Expected Result: 返回包含 items 和 total 的分页结果，tag 过滤生效
    Failure Indicators: 无 total 字段、过滤无效
    Evidence: .sisyphus/evidence/task-12-list-filter.txt
  ```

  **Commit**: YES
  - Message: `feat(prompt): add API layer - schemas, router, registration`
  - Files: `backend/src/api/schemas/prompt.py`, `backend/src/api/routers/prompts.py`, `backend/src/api/dependencies/repositories.py`, `backend/src/api/__init__.py`
  - Pre-commit: `cd backend && python -c "from src.api.routers.prompts import router; print('OK')"`

- [x] 13. Frontend Prompts Page — 左右分栏布局

  **What to do**:
  - 创建 `frontend/app/[locale]/prompts/page.tsx`：
    - 服务端组件或客户端组件（参考 skills page 的模式）
    - 布局结构：
      ```
      <div> — 全屏容器
        <TopNav /> — 顶部导航（复用 Task 6 的组件）
        <div className="flex"> — 左右分栏容器
          <PromptList /> — 左侧面板（固定宽度 300-400px）
          <PromptEditor /> — 右侧面板（flex-1 填充剩余空间）
        </div>
      </div>
      ```
    - 页面加载时：调用 API 获取 prompts 列表，存入 promptsStore
    - 需要 JWT 认证：未登录重定向到登录页（参考 skills page 的保护模式）
    - 响应式设计：移动端左侧面板可收起/展开
  - 修改 `frontend/lib/api.ts`：
    - 添加 Prompt 相关 API 方法（如果 ApiClient 是通用的，可能不需要修改）
    - 或者创建 `frontend/lib/promptApi.ts` 专用 API 调用层

  **Must NOT do**:
  - 不使用卡片网格布局（必须是左右分栏）
  - 不修改 Skills 页面的功能（仅保持 TopNav 集成）
  - 不在页面中硬编码 API URL（使用 ApiClient）
  - 不实现版本历史或导入导出功能（Tasks 14, 15）

  **Recommended Agent Profile**:
  - **Category**: `visual-engineering`
    - Reason: 左右分栏布局、响应式设计、组件集成、API 数据加载
  - **Skills**: `['frontend-ui-ux']`
    - `frontend-ui-ux`: 需要设计左右分栏的视觉比例、响应式断点、加载状态 UI
  - **Skills Evaluated but Omitted**:
    - `playwright`: QA 验证在场景中完成

  **Parallelization**:
  - **Can Run In Parallel**: YES (within Wave 3)
  - **Parallel Group**: Wave 3 (with Tasks 12, 14, 15)
  - **Blocks**: Tasks 14 (version history panel), 15 (import/export dialogs), 17 (frontend tests), 18 (integration)
  - **Blocked By**: Tasks 4 (types + store), 5 (i18n), 6 (TopNav), 11 (UI components)

  **References**:

  **Pattern References**:
  - `frontend/app/[locale]/skills/page.tsx` — 页面组织模式：如何组合 TopNav + 内容、如何加载数据、如何处理认证
  - `frontend/components/prompts/PromptList.tsx` (Task 11 产出) — 左侧面板组件
  - `frontend/components/prompts/PromptEditor.tsx` (Task 11 产出) — 右侧编辑器组件
  - `frontend/components/layout/TopNav.tsx` (Task 6 产出) — 顶部导航组件

  **API/Type References**:
  - `frontend/types/prompt.ts` (Task 4 产出) — API 请求/响应类型
  - `frontend/stores/promptsStore.ts` (Task 4 产出) — Store actions: setPrompts, setSelectedPrompt
  - `frontend/lib/api.ts` — ApiClient.get/post/put/delete 方法签名

  **WHY Each Reference Matters**:
  - Skills page 展示了页面级别的代码组织模式，但 Prompts page 布局完全不同（左右分栏 vs 卡片列表）
  - 必须将 Task 11 的组件和 Task 6 的 TopNav 正确集成到页面中
  - API 数据加载需要配合 store 的状态更新模式

  **Acceptance Criteria**:
  - [x] `frontend/app/[locale]/prompts/page.tsx` 存在
  - [x] 页面包含 TopNav + 左右分栏布局
  - [x] 访问 `/en/prompts` 可正常渲染（已登录状态）
  - [x] TypeScript 编译无错误
  - [x] 未登录时访问重定向到登录页

  **QA Scenarios (MANDATORY):**

  ```
  Scenario: Prompts 页面加载 + 左右分栏布局
    Tool: Playwright (playwright skill)
    Preconditions: 前后端运行中，用户已登录
    Steps:
      1. 导航到 http://localhost:3000/en/prompts
      2. 等待页面加载完成（timeout: 10s）
      3. 验证 TopNav 存在（`[data-testid="top-nav"]` 或 `nav` 元素）
      4. 验证 TopNav 中 Prompts 为 active 状态
      5. 验证左侧面板存在（宽度 300-400px 区间）
      6. 验证右侧面板存在（占据剩余空间）
      7. 截图
    Expected Result: 页面显示 TopNav + 左右分栏布局
    Failure Indicators: 404、白屏、布局错误
    Evidence: .sisyphus/evidence/task-13-page-layout.png

  Scenario: 创建 Prompt 并在编辑器中显示
    Tool: Playwright (playwright skill)
    Preconditions: 用户已登录，在 Prompts 页面
    Steps:
      1. 点击左侧面板的「新建」按钮
      2. 等待右侧编辑器加载
      3. 在标题输入框输入 'My Test Prompt'
      4. 在 Monaco Editor 中输入 'Hello {{name}}, welcome!'
      5. 点击「保存」按钮
      6. 验证左侧列表中出现 'My Test Prompt' 项
      7. 截图
    Expected Result: 创建成功，列表和编辑器同步显示
    Failure Indicators: API 错误、列表未更新、编辑器无响应
    Evidence: .sisyphus/evidence/task-13-create-prompt.png

  Scenario: 未登录时重定向
    Tool: Playwright (playwright skill)
    Preconditions: 浏览器未登录状态
    Steps:
      1. 导航到 http://localhost:3000/en/prompts
      2. 等待重定向完成
      3. 验证 URL 包含 /login 或 /auth
    Expected Result: 重定向到登录页
    Failure Indicators: 显示 Prompts 页面内容、API 返回数据
    Evidence: .sisyphus/evidence/task-13-auth-redirect.png
  ```

  **Commit**: YES (group with Tasks 14, 15)
  - Message: `feat(prompt): add frontend prompts page, version history, import/export`
  - Files: `frontend/app/[locale]/prompts/page.tsx`, `frontend/lib/promptApi.ts` (如需要)

- [x] 14. Frontend Version History Panel

  **What to do**:
  - 创建 `frontend/components/prompts/VersionHistory.tsx`：
    - 客户端组件
    - 实现为右侧滑出面板或编辑器下方的可展开区域：
      - 「版本历史」标题 + 版本列表
      - 每项显示：版本号（v1, v2, ...）、创建时间、标题摘要
      - 点击版本可查看该版本的完整内容（只读模式）
      - 查看版本时在右侧显示版本内容（只读 Monaco 或纯文本）
      - 「返回编辑」按钮切回当前编辑状态
    - 空状态：无版本时显示 `t('prompts.noVersions')`
    - 发布版本按钮：调用 publish version API → 刷新版本列表
  - 在 PromptEditor 中集成 VersionHistory 组件：
    - 工具栏的「版本历史」按钮切换显示/隐藏 VersionHistory 面板
    - 「发布版本」按钮即触发版本发布 + 打开版本历史面板

  **Must NOT do**:
  - 不实现版本对比/diff 功能
  - 不实现版本回滚/恢复功能
  - 不硬编码文本（使用 i18n）

  **Recommended Agent Profile**:
  - **Category**: `visual-engineering`
    - Reason: 滑出面板/可展开区域、版本列表、只读模式切换 — UI 交互复杂
  - **Skills**: `['frontend-ui-ux']`
    - `frontend-ui-ux`: 版本历史面板的视觉设计需要專业判断

  **Parallelization**:
  - **Can Run In Parallel**: YES (within Wave 3)
  - **Parallel Group**: Wave 3 (with Tasks 12, 13, 15)
  - **Blocks**: Task 17 (frontend tests)
  - **Blocked By**: Tasks 11 (UI components), 13 (Prompts page)

  **References**:

  **Pattern References**:
  - `frontend/components/prompts/PromptEditor.tsx` (Task 11 产出) — 编辑器组件结构，VersionHistory 需要与之集成
  - `frontend/components/ui/` — Dialog/Panel UI 组件参考

  **API/Type References**:
  - `frontend/types/prompt.ts` (Task 4 产出) — PromptVersion 类型
  - `frontend/stores/promptsStore.ts` (Task 4 产出) — versions 相关 state 和 actions
  - `frontend/i18n/locales/en.json:prompts` (Task 5 产出) — version 相关 i18n key

  **WHY Each Reference Matters**:
  - VersionHistory 必须无缝嵌入 PromptEditor——需要理解其状态管理和工具栏结构
  - version API 调用需要使用正确的类型和 store actions

  **Acceptance Criteria**:
  - [x] `frontend/components/prompts/VersionHistory.tsx` 存在
  - [x] PromptEditor 中可切换显示/隐藏版本历史面板
  - [x] 版本列表显示版本号和时间
  - [x] 点击版本可查看该版本内容（只读）
  - [x] TypeScript 编译无错误

  **QA Scenarios (MANDATORY):**

  ```
  Scenario: 发布版本并查看版本历史
    Tool: Playwright (playwright skill)
    Preconditions: 已创建一个 prompt，在编辑器中打开
    Steps:
      1. 点击工具栏的「发布版本」按钮
      2. 等待发布完成提示
      3. 点击「版本历史」按钮打开面板
      4. 验证版本列表中有 v1 条目
      5. 点击 v1 条目
      6. 验证显示该版本的完整内容（只读模式）
      7. 截图
    Expected Result: 版本发布成功，历史面板显示版本列表，可查看版本内容
    Failure Indicators: 发布失败、列表为空、内容不显示
    Evidence: .sisyphus/evidence/task-14-version-history.png

  Scenario: 无版本的空状态
    Tool: Playwright (playwright skill)
    Preconditions: 新创建的 prompt，未发布版本
    Steps:
      1. 打开版本历史面板
      2. 验证显示空状态文本
    Expected Result: 显示 'No versions published yet' 或对应国际化文本
    Failure Indicators: 显示错误或空白
    Evidence: .sisyphus/evidence/task-14-no-versions.png
  ```

  **Commit**: YES (group with Tasks 13, 15)
  - Message: `feat(prompt): add frontend prompts page, version history, import/export`
  - Files: `frontend/components/prompts/VersionHistory.tsx`, 可能修改 `frontend/components/prompts/PromptEditor.tsx`

- [x] 15. Frontend Import/Export Dialogs

  **What to do**:
  - 创建 `frontend/components/prompts/ImportDialog.tsx`：
    - 客户端组件，使用 Dialog/Modal UI
    - 导入方式：
      - 文件上传：拖拽或点击选择 `.md` 文件，读取内容后调用 import API
      - 粘贴导入：文本区域粘贴 Markdown 内容，点击确认导入
    - 导入成功后：关闭 dialog、刷新列表、选中新导入的 prompt
    - 导入失败：显示错误提示 `t('prompts.importError')`
  - 创建 `frontend/components/prompts/ExportDialog.tsx`（或直接触发下载）：
    - 调用 export API 获取 Markdown 内容
    - 触发浏览器下载为 `.md` 文件（文件名：`{title}.md`）
    - 或者显示 Dialog 内预览 + 复制按钮 + 下载按钮
  - 在 PromptList 或 PromptEditor 中集成：
    - 左侧面板的「导入」按钮打开 ImportDialog
    - 编辑器工具栏的「导出」按钮触发导出
  - 添加 import/export 相关的 i18n key（如果 Task 5 未完全覆盖）：
    - dialog 标题、确认按钮、文件选择提示等

  **Must NOT do**:
  - 不支持非 Markdown 格式的导入（仅 .md 文件）
  - 不在前端解析 YAML frontmatter（解析在后端完成）
  - 不修改后端 API（API 在 Task 12 中已完成）

  **Recommended Agent Profile**:
  - **Category**: `visual-engineering`
    - Reason: 文件上传/拖拽 UI、Dialog 组件、下载触发 — UI 交互复杂
  - **Skills**: `['frontend-ui-ux']`
    - `frontend-ui-ux`: 导入 dialog 的文件拖拽区域、预览、错误提示需要美观设计

  **Parallelization**:
  - **Can Run In Parallel**: YES (within Wave 3)
  - **Parallel Group**: Wave 3 (with Tasks 12, 13, 14)
  - **Blocks**: Task 17 (frontend tests)
  - **Blocked By**: Tasks 5 (i18n), 11 (UI components), 13 (Prompts page)

  **References**:

  **Pattern References**:
  - `frontend/components/ui/` — Dialog/Modal UI 组件参考
  - `frontend/components/prompts/PromptList.tsx` (Task 11 产出) — 导入按钮的集成位置
  - `frontend/components/prompts/PromptEditor.tsx` (Task 11 产出) — 导出按钮的集成位置

  **API/Type References**:
  - `frontend/types/prompt.ts` (Task 4 产出) — ImportPromptRequest, ExportPromptResponse 类型
  - `frontend/lib/api.ts` — ApiClient.post (import)、ApiClient.get (export) 方法
  - `frontend/i18n/locales/en.json:prompts` (Task 5 产出) — import/export 相关 i18n key

  **WHY Each Reference Matters**:
  - Dialog 组件需要复用项目已有的 Modal/Dialog 模式
  - 导入流程：文件读取 → API 调用 → 刷新列表，需要配合 store 和 API 层
  - 导出流程：API 调用 → 生成 Blob → 触发下载，需要浏览器下载技巧

  **Acceptance Criteria**:
  - [x] `frontend/components/prompts/ImportDialog.tsx` 存在
  - [x] `frontend/components/prompts/ExportDialog.tsx` 存在（或导出逻辑嵌入工具栏按钮）
  - [x] 导入功能支持文件上传和粘贴导入
  - [x] 导出功能触发 .md 文件下载
  - [x] TypeScript 编译无错误

  **QA Scenarios (MANDATORY):**

  ```
  Scenario: 文件导入流程
    Tool: Playwright (playwright skill)
    Preconditions: 前后端运行中，用户已登录，在 Prompts 页面
    Steps:
      1. 点击「导入」按钮，打开 ImportDialog
      2. 验证 dialog 显示（文件上传区域 + 粘贴文本区域）
      3. 在粘贴区域输入：
         ---
         title: "Imported Prompt"
         tags:
           - imported
         ---
         This is imported content.
      4. 点击确认导入按钮
      5. 等待 dialog 关闭
      6. 验证左侧列表中出现 'Imported Prompt' 项
      7. 截图
    Expected Result: 导入成功，列表刷新，新 prompt 显示
    Failure Indicators: API 错误、dialog 未关闭、列表未更新
    Evidence: .sisyphus/evidence/task-15-import.png

  Scenario: 导出为 Markdown 文件
    Tool: Playwright (playwright skill)
    Preconditions: 已有一个 prompt，在编辑器中打开
    Steps:
      1. 点击工具栏的「导出」按钮
      2. 等待下载开始（或导出预览 dialog 显示）
      3. 验证下载的文件名为 `{title}.md`
      4. 或验证预览内容包含 YAML frontmatter + content
    Expected Result: 导出成功，文件包含正确的 frontmatter 格式
    Failure Indicators: 下载未触发、内容缺失
    Evidence: .sisyphus/evidence/task-15-export.png

  Scenario: 导入失败错误处理
    Tool: Playwright (playwright skill)
    Preconditions: 前后端运行中
    Steps:
      1. 打开 ImportDialog
      2. 粘贴空内容或无效 Markdown
      3. 点击确认导入
      4. 验证显示错误提示
    Expected Result: 显示导入失败提示，dialog 不关闭
    Failure Indicators: 无错误提示、崩溃、白屏
    Evidence: .sisyphus/evidence/task-15-import-error.png
  ```

  **Commit**: YES (group with Tasks 13, 14)
  - Message: `feat(prompt): add frontend prompts page, version history, import/export`
  - Files: `frontend/components/prompts/ImportDialog.tsx`, `frontend/components/prompts/ExportDialog.tsx`

- [x] 16. Backend Tests — Domain, Handlers, API

  **What to do**:
  - 创建后端测试目录结构（如果不存在）：`backend/tests/`
  - 创建 `backend/tests/conftest.py`：
    - pytest fixtures：测试数据库会话、测试客户端、认证 token
    - 参考现有的 conftest.py（如果有）或从零创建
    - 使用 `httpx.AsyncClient` + `app` fixture 进行 API 测试
  - 创建 `backend/tests/test_prompt_domain.py`：
    - 测试 Prompt aggregate 创建、属性设置、publish_version()
    - 测试 PromptFactory.create() 的参数验证
    - 测试 tags 规范化：lowercase + deduplicate
    - 测试边界条件：空 title、超长 title、超多 tags
  - 创建 `backend/tests/test_prompt_handlers.py`：
    - 测试每个 handler 的核心逻辑（使用 mock repository）
    - 测试 ownership 检查：非拥有者操作抛出 ForbiddenError
    - 测试 ResourceNotFoundError 场景
    - 测试 import handler 的 YAML frontmatter 解析
    - 测试 export handler 的 Markdown 生成
  - 创建 `backend/tests/test_prompt_api.py`：
    - API 集成测试：实际 HTTP 请求 → 数据库 → 响应
    - 测试全部 10 个端点：CRUD + 版本 + 导入导出
    - 测试认证：未登录返回 401
    - 测试权限：访问他人的 prompt 返回 403
    - 测试分页、tag 过滤、标题搜索
    - 测试版本发布 + 版本列表 + 版本详情
    - 测试 import/export 往返一致性

  **Must NOT do**:
  - 不测试纯框架功能（FastAPI、SQLAlchemy 本身）
  - 不创建过于复杂的 test fixtures（保持简单）
  - 不在测试中调用真实外部服务

  **Recommended Agent Profile**:
  - **Category**: `deep`
    - Reason: 涉及 3 个测试文件、2层测试（单元 + 集成）、mock 设置、数据库 fixture
  - **Skills**: `[]`

  **Parallelization**:
  - **Can Run In Parallel**: YES (within Wave 4)
  - **Parallel Group**: Wave 4 (with Tasks 17, 18)
  - **Blocks**: Final Verification Wave
  - **Blocked By**: Tasks 7 (ORM), 8-10 (handlers), 12 (API layer)

  **References**:

  **Pattern References**:
  - `backend/tests/` — 现有测试目录结构和 conftest.py（如果存在）
  - 现有测试文件（如果有）— pytest 用法、fixture 模式、assert 风格

  **API/Type References**:
  - Tasks 2-3 产出的 domain 层文件 — 测试对象
  - Tasks 8-10 产出的 handler 文件 — 测试对象
  - Task 12 产出的 API 层文件 — 集成测试对象
  - `backend/src/domain/exceptions.py` — 异常类型用于 assert 测试

  **WHY Each Reference Matters**:
  - 现有测试的 conftest.py 决定了数据库 session 和 client 的设置方式
  - handler 测试需要 mock PromptRepository — 必须匹配接口签名
  - API 测试需要完整的 app fixture — 包含数据库和认证

  **Acceptance Criteria**:
  - [x] `backend/tests/test_prompt_domain.py` 存在且测试通过
  - [x] `backend/tests/test_prompt_handlers.py` 存在且测试通过
  - [x] `backend/tests/test_prompt_api.py` 存在且测试通过
  - [x] `cd backend && python -m pytest tests/ -v` → 所有测试通过
  - [x] 测试覆盖 10 个 API 端点 + ownership + 认证

  **QA Scenarios (MANDATORY):**

  ```
  Scenario: 全部后端测试通过
    Tool: Bash
    Preconditions: 后端依赖已安装，测试数据库可用
    Steps:
      1. cd backend && python -m pytest tests/ -v --tb=short 2>&1
    Expected Result: 所有测试通过，0 failures
    Failure Indicators: FAILED 测试、ImportError、fixture 错误
    Evidence: .sisyphus/evidence/task-16-pytest-results.txt

  Scenario: 测试覆盖 ownership 检查
    Tool: Bash
    Preconditions: 测试文件已创建
    Steps:
      1. cd backend && grep -c 'ForbiddenError\|403\|forbidden' tests/test_prompt_handlers.py tests/test_prompt_api.py
    Expected Result: 每个文件至少 2 次引用（get + update + delete 的 ownership 测试）
    Failure Indicators: 引用次数为 0
    Evidence: .sisyphus/evidence/task-16-ownership-coverage.txt
  ```

  **Commit**: YES
  - Message: `test(prompt): add backend domain, handler, and API tests`
  - Files: `backend/tests/conftest.py`, `backend/tests/test_prompt_domain.py`, `backend/tests/test_prompt_handlers.py`, `backend/tests/test_prompt_api.py`
  - Pre-commit: `cd backend && python -m pytest tests/ -v`

- [x] 17. Frontend Tests

  **What to do**:
  - 创建前端测试文件（使用项目现有测试框架，如 `bun test` 或 `vitest`）：
  - `frontend/__tests__/stores/promptsStore.test.ts`：
    - 测试 store 初始状态
    - 测试 setPrompts、setSelectedPrompt、setSearchQuery、setSelectedTag
    - 测试 getFilteredPrompts：按搜索词过滤、按 tag 过滤、组合过滤
    - 测试边界：空搜索、空 tag、空列表
  - `frontend/__tests__/components/prompts/TagInput.test.tsx`：
    - 测试渲染 tags chips
    - 测试添加 tag（回车触发）
    - 测试 tag 自动 lowercase + deduplicate
    - 测试删除 tag（点击 x）
    - 测试限制：最多 20 个 tags、tag 名最长 50 字符
  - `frontend/__tests__/components/prompts/PromptList.test.tsx`（可选，视测试框架支持）：
    - 测试空状态渲染
    - 测试有数据时的列表渲染
    - 测试搜索框交互

  **Must NOT do**:
  - 不测试第三方库功能（Monaco Editor、next-intl 本身）
  - 不创建 E2E 测试（Playwright E2E 在 Final Verification 中完成）
  - 不过度 mock（优先测试真实行为）

  **Recommended Agent Profile**:
  - **Category**: `unspecified-high`
    - Reason: 涉及 React 组件测试、Zustand store 测试、可能需要 jsdom 配置
  - **Skills**: `[]`

  **Parallelization**:
  - **Can Run In Parallel**: YES (within Wave 4)
  - **Parallel Group**: Wave 4 (with Tasks 16, 18)
  - **Blocks**: Final Verification Wave
  - **Blocked By**: Tasks 4 (types + store), 11 (UI components), 13 (page), 14 (version history), 15 (import/export)

  **References**:

  **Pattern References**:
  - `frontend/__tests__/` — 现有测试目录和配置（如果存在）
  - `frontend/package.json` — 测试脚本和测试框架配置

  **API/Type References**:
  - `frontend/stores/promptsStore.ts` (Task 4 产出) — Store 测试对象
  - `frontend/components/prompts/TagInput.tsx` (Task 11 产出) — 组件测试对象
  - `frontend/types/prompt.ts` (Task 4 产出) — 测试数据类型

  **WHY Each Reference Matters**:
  - 现有测试目录决定了测试文件的放置位置和命名规范
  - package.json 的测试配置决定了使用哪个测试框架和如何运行

  **Acceptance Criteria**:
  - [x] Store 测试文件存在且测试通过
  - [x] TagInput 测试文件存在且测试通过
  - [x] `cd frontend && bun test` → 所有测试通过

  **QA Scenarios (MANDATORY):**

  ```
  Scenario: 全部前端测试通过
    Tool: Bash
    Preconditions: 前端依赖已安装
    Steps:
      1. cd frontend && bun test 2>&1
    Expected Result: 所有测试通过，0 failures
    Failure Indicators: FAIL 测试、ImportError、渲染错误
    Evidence: .sisyphus/evidence/task-17-frontend-tests.txt

  Scenario: Store 过滤逻辑测试覆盖
    Tool: Bash
    Preconditions: store 测试文件已创建
    Steps:
      1. cd frontend && bun test --grep 'getFilteredPrompts' 2>&1
    Expected Result: 至少 3 个过滤测试通过（按搜索、按 tag、组合）
    Failure Indicators: 无匹配测试、测试失败
    Evidence: .sisyphus/evidence/task-17-filter-tests.txt
  ```

  **Commit**: YES
  - Message: `test(prompt): add frontend store and component tests`
  - Files: `frontend/__tests__/stores/promptsStore.test.ts`, `frontend/__tests__/components/prompts/TagInput.test.tsx`
  - Pre-commit: `cd frontend && bun test`

- [x] 18. Integration Testing + Final Polish

  **What to do**:
  - 确保前后端全链路工作：
    - 启动后端：`cd backend && uvicorn src.main:app --host 0.0.0.0 --port 8000`
    - 启动前端：`cd frontend && npm run dev`
    - 运行 migration：`cd backend && alembic upgrade head`
  - 前后端集成验证：
    - 登录 → 创建 prompt → 编辑 → 保存 → 发布版本 → 查看版本历史 → 导出 → 导入 → 删除
    - 验证 TopNav 在 Skills 和 Prompts 页面间切换正常
    - 验证 i18n 在中英文间切换正常
    - 验证认证保护：未登录时无法访问任何 prompt API
  - 修复集成问题：
    - 如果发现前后端接口不匹配，修复 DTO 或 API 调用
    - 如果发现 UI 问题，修复组件样式或交互
    - 确保 TypeScript 编译无错误：`cd frontend && npx tsc --noEmit`
    - 确保后端测试通过：`cd backend && python -m pytest tests/ -v`

  **Must NOT do**:
  - 不添加新功能（仅修复集成问题）
  - 不修改现有的 Skills 功能
  - 不进行不必要的重构

  **Recommended Agent Profile**:
  - **Category**: `deep`
    - Reason: 需要跨前后端调试、理解全链路数据流、修复集成问题
  - **Skills**: `['playwright', 'frontend-ui-ux']`
    - `playwright`: 需要在浏览器中端到端验证前后端集成
    - `frontend-ui-ux`: 可能需要修复 UI 样式或布局问题

  **Parallelization**:
  - **Can Run In Parallel**: NO (depends on all previous tasks)
  - **Parallel Group**: Wave 4 (with Tasks 16, 17, but runs after them if issues found)
  - **Blocks**: Final Verification Wave
  - **Blocked By**: Tasks 12 (API), 13 (page), 14 (version history), 15 (import/export)

  **References**:

  **Pattern References**:
  - 所有前后端文件 (Tasks 1-15 产出) — 全量参考，根据集成问题定位具体文件

  **WHY Each Reference Matters**:
  - 集成测试需要理解前后端的完整数据流：前端组件 → API 调用 → router → handler → repository → 数据库

  **Acceptance Criteria**:
  - [x] 前后端服务可同时启动无报错
  - [x] 完整 CRUD 流程在浏览器中可完成
  - [x] TopNav 切换正常
  - [x] i18n 中英文切换正常
  - [x] `cd frontend && npx tsc --noEmit` → 无错误
  - [x] `cd backend && python -m pytest tests/ -v` → 所有通过

  **QA Scenarios (MANDATORY):**

  ```
  Scenario: 完整 CRUD 流程端到端验证
    Tool: Playwright (playwright skill)
    Preconditions: 前后端运行中，用户已登录
    Steps:
      1. 通过 TopNav 导航到 Prompts 页面
      2. 点击「新建」按钮创建 prompt
      3. 输入标题 'Integration Test Prompt'
      4. 在 Monaco Editor 输入 'Hello {{name}}, you are {{role}}!'
      5. 添加 tags: 'test', 'integration'
      6. 点击「保存」
      7. 验证左侧列表更新
      8. 修改标题为 'Updated Prompt'，点击「保存」
      9. 点击「发布版本」，查看版本历史显示 v1
      10. 点击「导出」，验证下载文件包含 frontmatter
      11. 点击「删除」，确认删除，验证列表清空
      12. 截图每个步骤
    Expected Result: 全流程无报错，数据一致
    Failure Indicators: 任何步骤失败、数据不同步、UI 崩溃
    Evidence: .sisyphus/evidence/task-18-full-crud.png

  Scenario: TopNav + i18n 集成验证
    Tool: Playwright (playwright skill)
    Preconditions: 前后端运行中
    Steps:
      1. 导航到 http://localhost:3000/en/skills
      2. 验证 TopNav 显示 'Skills' 和 'Prompts'
      3. 点击 TopNav 的 'Prompts' 链接
      4. 验证 URL 变为 /en/prompts
      5. 验证页面正常加载
      6. 切换语言到中文
      7. 验证 TopNav 显示 '技能' 和 '提示词'
      8. 截图
    Expected Result: 导航、语言切换、页面内容都正确
    Failure Indicators: 链接断裂、翻译缺失、页面 404
    Evidence: .sisyphus/evidence/task-18-topnav-i18n.png

  Scenario: 认证保护验证
    Tool: Bash (curl)
    Preconditions: 后端服务运行中
    Steps:
      1. curl -s -o /dev/null -w '%{http_code}' http://localhost:8000/api/prompts
      2. curl -s -o /dev/null -w '%{http_code}' -X POST http://localhost:8000/api/prompts \
           -H 'Content-Type: application/json' -d '{"title":"Hack","content":"x"}'
      3. curl -s -o /dev/null -w '%{http_code}' http://localhost:8000/api/prompts/00000000-0000-0000-0000-000000000001/export
    Expected Result: 所有请求返回 401 或 403
    Failure Indicators: 返回 200 或数据
    Evidence: .sisyphus/evidence/task-18-auth-protection.txt
  ```

  **Commit**: YES
  - Message: `feat(prompt): integration fixes and final polish`
  - Files: 根据实际修复决定
  - Pre-commit: `cd backend && python -m pytest tests/ -v && cd ../frontend && bun test && npx tsc --noEmit`

## Final Verification Wave

- [x] F1. **Plan Compliance Audit** — `oracle`
  Read the plan end-to-end. For each "Must Have": verify implementation exists (read file, curl endpoint, run command). For each "Must NOT Have": search codebase for forbidden patterns — reject with file:line if found. Check evidence files exist in .sisyphus/evidence/. Compare deliverables against plan.
  Output: `Must Have [N/N] | Must NOT Have [N/N] | Tasks [N/N] | VERDICT: APPROVE/REJECT`

- [x] F2. **Code Quality Review** — `unspecified-high`
  Run `python -m pytest` + linter + `bun test`. Review all changed files for: `as any`/`@ts-ignore`, empty catches, console.log in prod, commented-out code, unused imports. Check AI slop: excessive comments, over-abstraction, generic names (data/result/item/temp). Verify all backend code follows DDD conventions (no SQLAlchemy imports in domain/, no FastAPI imports in domain/).
  Output: `Build [PASS/FAIL] | Lint [PASS/FAIL] | Tests [N pass/N fail] | Files [N clean/N issues] | VERDICT`

- [x] F3. **Real Manual QA** — `unspecified-high` (+ `playwright` skill)
  Start from clean state. Navigate to Prompts page via TopNav. Test full CRUD: create prompt, edit content with `{{variables}}`, add tags, publish version, view version history, view specific version content, export to Markdown, import from Markdown, delete prompt. Test edge cases: empty content, special chars in tags, very long content. Test auth: cannot access without login. Save screenshots to `.sisyphus/evidence/final-qa/`.
  Output: `Scenarios [N/N pass] | Integration [N/N] | Edge Cases [N tested] | VERDICT`

- [x] F4. **Scope Fidelity Check** — `deep`
  For each task: read "What to do", read actual diff (git log/diff). Verify 1:1 — everything in spec was built (no missing), nothing beyond spec was built (no creep). Check "Must NOT do" compliance: no Tree/Blob usage, no Tag table, no relationship(), no variable parsing, no diff UI, no rollback. Flag unaccounted changes.
  Output: `Tasks [N/N compliant] | Contamination [CLEAN/N issues] | Unaccounted [CLEAN/N files] | VERDICT`

---

## Commit Strategy

| Wave | Commit Message | Key Files | Pre-commit Check |
|------|---------------|-----------|-----------------|
| 1 | `feat(prompt): add database migration for prompts and prompt_versions` | alembic/versions/*.py | `alembic upgrade head` |
| 1 | `feat(prompt): add domain layer - aggregate, factory, repository interface` | domain/aggregates/prompt.py, domain/factories/*, domain/repositories/* | — |
| 1 | `feat(prompt): add frontend types, store, i18n, and TopNav` | frontend/types/prompt.ts, stores/promptsStore.ts, i18n/*, components/layout/* | `bun test` |
| 2 | `feat(prompt): add infrastructure layer - ORM models and SQL repository` | infra/persistence/models/*, infra/persistence/repositories/* | — |
| 2 | `feat(prompt): add application handlers - CRUD, versioning, import/export` | application/handlers/*.py | — |
| 2 | `feat(prompt): add frontend prompt list and editor components` | components/prompts/* | — |
| 3 | `feat(prompt): add API layer - schemas, router, registration` | api/routers/prompts.py, api/schemas/prompt.py | `pytest tests/ -v` |
| 3 | `feat(prompt): add frontend prompts page, version history, import/export` | app/[locale]/prompts/*, components/prompts/* | — |
| 4 | `test(prompt): add backend and frontend tests` | tests/*, __tests__/* | `pytest && bun test` |
| 4 | `feat(prompt): integration fixes and final polish` | various | `pytest && bun test` |

---

## Success Criteria

### Verification Commands
```bash
# Database migration
cd backend && alembic upgrade head     # Expected: success, tables created
cd backend && alembic downgrade -1     # Expected: success, tables removed
cd backend && alembic upgrade head     # Expected: success, re-apply

# Backend tests
cd backend && python -m pytest tests/ -v  # Expected: all pass

# Frontend tests
cd frontend && bun test                   # Expected: all pass

# API smoke test
TOKEN=$(curl -s -X POST http://localhost:8000/api/auth/login \
  -H "Content-Type: application/json" \
  -d '{"email":"test@example.com","password":"password123"}' | jq -r '.access_token')

# Create prompt
curl -s -X POST http://localhost:8000/api/prompts \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"title":"Test","content":"Hello {{name}}","tags":["test"]}' | jq '.id'
# Expected: UUID returned, status 201

# TypeScript check
cd frontend && npx tsc --noEmit  # Expected: no errors
```

### Final Checklist
- [x] All "Must Have" present
- [x] All "Must NOT Have" absent
- [x] All backend tests pass
- [x] All frontend tests pass
- [x] Migration upgrade + downgrade works
- [x] TopNav appears on both Skills and Prompts pages
- [x] i18n works in both en and zh
