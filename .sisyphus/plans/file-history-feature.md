# 文件手动保存与历史记录功能

## TL;DR

> **快速摘要**: 将文件编辑从自动保存改为手动保存，每次保存生成文件变更历史，用户可通过侧边栏查看和恢复任意历史版本，未保存内容在离开页面时提示确认。
> 
> **交付物**:
> - 后端: FileVersion 模型 + 3个 API 端点
> - 前端: 手动保存逻辑 + 未保存提示 + 文件历史侧边栏 UI
> 
> **预计工作量**: Medium
> **并行执行**: YES - 前后端可并行
> **关键路径**: 后端模型 → API → 前端保存逻辑 → 未保存提示 → 历史UI

---

## Context

### 原始需求
用户希望对文件编辑功能做如下变更：
1. 文件编辑去掉自动保存，改为手动点击保存按钮
2. 每次保存生成该文件的变更记录（时间+内容），可回溯查看历史版本
3. 检测到用户有未保存内容时，在刷新/返回/切换文件/点击菜单等场景提示确认
4. 文件历史查看的 UI 需要在侧边栏展开，点击历史版本后展示只读内容，用户可恢复

### 额外需求（2026-02-17 补充）
1. **删除原有 Version 模型** - 业务变更，原有 Skill 级别的版本不再需要
2. **前端删除 Skill 历史 UI** - 去掉 VersionHistory 相关组件和页面
3. **迁移整理** - 按表分开，保持正确版本顺序

### 技术决策
- **存储策略**: 保留所有历史 Blob（最简单，直接通过 blob_id 回溯）
- **数据模型**: 新建 FileVersion 模型（不复用现有 Version）
- **保存描述**: 不需要，纯时间戳
- **未保存场景**: 全部（刷新、切换文件、返回、菜单、关闭标签页）
- **历史查看**: 侧边栏展开，点击后只读预览 + 恢复按钮
- **迁移策略**: 按表分开，001_skills.py, 002_trees.py, 003_blobs.py, 004_file_versions.py

### 研究发现
- 现有 Version 模型是 Skill 级别的整体快照，关联 skill_id + tree_id
- TextEditor 当前有 1 秒 debounced 自动保存逻辑
- 前端使用 Next.js App Router，可通过路由守卫检测页面切换

---

## Work Objectives

### 核心目标
实现文件级别的手动保存和历史记录功能，用户必须手动点击保存，每次保存生成可回溯的历史版本。

### 具体交付物

**后端 - 删除旧版本相关**:
- [x] 删除 Version 模型 (backend/app/models/version.py)
- [x] 删除 Version Schema (backend/app/schemas/version.py)
- [x] 删除 Version CRUD (backend/app/crud/version.py)
- [x] 删除 Version Router (backend/app/routers/versions.py)
- [x] 删除 versions 路由注册 (backend/app/main.py)
- [x] 删除 versions 迁移文件

**后端 - 新功能**:
- [ ] FileVersion 模型 (backend/app/models/file_version.py)
- [ ] FileVersion Schema (backend/app/schemas/file_version.py)
- [ ] FileVersion CRUD (backend/app/crud/file_version.py)
- [ ] API: POST /file-versions - 创建文件版本
- [ ] API: GET /file-versions?skill_id=&file_path= - 获取文件历史列表
- [ ] API: GET /file-versions/{id} - 获取特定版本详情

**数据库迁移**:
- [ ] 001_users.py - 用户表
- [ ] 002_skills.py - 技能表
- [ ] 003_trees.py - 文件树表
- [ ] 004_blobs.py - 文件内容表
- [ ] 005_file_versions.py - 文件版本表

**前端 - 删除旧版本相关**:
- [ ] 删除 VersionHistory 组件 (frontend/components/VersionHistory.tsx)
- [ ] 删除 VersionCompare 组件 (frontend/components/VersionCompare.tsx)
- [ ] 删除技能详情页的历史 Tab (SkillEditorArea.tsx)
- [ ] 删除版本相关类型定义

**前端 - 新功能**:
- [ ] TextEditor: 移除自动保存，添加 isModified 状态
- [ ] 保存按钮: 默认 disabled，有修改时 enabled
- [ ] 未保存提示: beforeunload 事件 + 路由守卫
- [ ] 文件树: 每个文件添加历史图标（时钟）
- [ ] FileHistorySidebar: 侧边栏历史列表组件
- [ ] 历史版本查看: 只读预览 + 恢复按钮

### 验收标准
- [ ] 编辑文件后不自动保存，必须点击保存按钮
- [ ] 保存按钮在无修改时不可点击，有修改时可点击
- [ ] 保存后可在文件树侧边栏查看该文件的历史列表
- [ ] 点击历史版本后在编辑器显示只读内容
- [ ] 点击恢复按钮可恢复到选中的历史版本
- [ ] 刷新页面/切换文件/返回时如有未保存内容弹出确认框

---

## Verification Strategy

### 测试决策
- **基础设施**: 项目有 pytest (backend) 和 playwright (frontend)
- **自动化测试**: Tests-after 模式
- **框架**: backend: pytest, frontend: playwright
- **Agent-Executed QA**: 全部场景通过 Agent 执行验证

### QA 场景示例
1. **手动保存**: 编辑内容 → 点击保存 → 刷新页面 → 内容保留
2. **保存按钮状态**: 未修改时按钮 disabled，有修改后 enabled
3. **历史查看**: 保存后点击时钟图标 → 侧边栏展开 → 点击历史 → 编辑器显示内容
4. **恢复功能**: 点击历史版本 → 点击恢复 → 编辑器内容替换
5. **未保存提示**: 编辑内容 → 点击其他文件 → 弹出确认框

---

## Execution Strategy

### 阶段划分

```
Wave 1 (后端 - 删除旧版本 + 迁移整理):
├── T1: 删除 Version 模型/Schema/CRUD/Router
├── T2: 整理迁移文件（按表分开）
└── T3: 数据库迁移

Wave 2 (后端 - 新功能):
├── T4: FileVersion 模型 + Schema + CRUD
├── T5: 文件历史 API 端点（创建/列表/详情）
├── T6: 数据库迁移（005_file_versions.py）
└── T6c: FileVersion API 单元测试

Wave 3 (前端核心逻辑 - 依赖 T1-T6):
├── T7: TextEditor 移除自动保存，添加修改状态
├── T8: 保存按钮状态管理
├── T9: 未保存内容检测（beforeunload + 路由守卫）
├── T10: 删除旧版本 UI 组件
└── T11: API 调用封装

Wave 4 (前端 UI - 依赖 T7-T11):
├── T12: 文件树添加历史图标
├── T13: FileHistorySidebar 侧边栏组件
├── T14: 历史版本只读预览
└── T15: 恢复功能实现

Wave 5 (测试 - 依赖所有功能):
├── T16: 整体集成测试
├── T16b: 后端 Journey 测试
├── T16c: 前端 E2E Journey 测试
└── T16d: 前端 API 集成测试
```

### 依赖矩阵

| 任务 | 依赖 | 阻塞 |
|------|------|------|
| T1 删除旧Version | - | - |
| T2 整理迁移 | T1 | T3 |
| T3 执行迁移 | T2 | T16b |
| T4 FileVersion模型 | - | T5 |
| T5 文件历史API | T4 | T6, T11 |
| T6 迁移file_versions | T5 | T6c |
| T6c API单元测试 | T6 | T16b |
| T7 TextEditor修改状态 | - | T8 |
| T8 保存按钮状态 | T7 | T14 |
| T9 未保存提示 | T7 | T16c |
| T10 删除旧版本UI | - | - |
| T11 API封装 | T5, T6 | T12-T15 |
| T12 文件树历史图标 | T10 | T13 |
| T13 历史侧边栏 | T11, T12 | T14 |
| T14 只读预览 | T13 | - |
| T15 恢复功能 | T8, T14 | T16, T16c |
| T16 集成测试 | T3, T6c, T9, T15 | T16b, T16c |
| T16b 后端Journey测试 | T3, T6c | - |
| T16c 前端E2E测试 | T14, T15, T16 | - |

---

## TODOs

### Wave 1: 后端 - 删除旧版本 + 迁移整理

- [ ] T1. **删除 Version 模型及相关代码**

  **What to do**:
  - 删除 `backend/app/models/version.py`
  - 删除 `backend/app/schemas/version.py`
  - 删除 `backend/app/crud/version.py`
  - 删除 `backend/app/routers/versions.py`
  - 从 `backend/app/main.py` 移除 versions 路由注册
  - 删除 `backend/alembic/versions/` 下的 versions 相关迁移

  **Recommended Agent Profile**:
  - **Category**: `quick`
  - **Skills**: []

  **Parallelization**:
  - **Can Run In Parallel**: YES
  - **Parallel Group**: Wave 1
  - **Blocks**: T2
  - **Blocked By**: None

  **Acceptance Criteria**:
  - [ ] Version 模型完全删除
  - [ ] 路由注册移除
  - [ ] 代码无引用错误

- [x] T2. **整理迁移文件（按表分开）**

  **What to do**:
  - 整理现有迁移，保持版本顺序
  - 001_users.py - 用户表
  - 002_skills.py - 技能表  
  - 003_trees.py - 文件树表
  - 004_blobs.py - 文件内容表

  **Recommended Agent Profile**:
  - **Category**: `quick`
  - **Skills**: []

  **Parallelization**:
  - **Can Run In Parallel**: YES
  - **Parallel Group**: Wave 1
  - **Blocks**: T3
  - **Blocked By**: T1

  **Acceptance Criteria**:
  - [ ] 迁移文件按表分开
  - [ ] 版本顺序正确
  - [ ] 无物理依赖

- [x] T3. **执行迁移**

  **What to do**:
  - 运行 alembic upgrade head 验证迁移

  **Recommended Agent Profile**:
  - **Category**: `quick`
  - **Skills**: []

  **Acceptance Criteria**:
  - [x] 迁移成功执行

---

### Wave 2: 后端 - 新功能

- [ ] T4. **FileVersion 数据模型**

  **What to do**:
  - 创建 `backend/app/models/file_version.py`
  - 字段: id, skill_id, file_path, blob_id, created_at
  - 外键关联: skill_id → skills, blob_id → blobs

  **Recommended Agent Profile**:
  - **Category**: `quick`
  - **Skills**: []

  **Parallelization**:
  - **Can Run In Parallel**: YES
  - **Parallel Group**: Wave 2
  - **Blocks**: T5
  - **Blocked By**: None

  **References**:
  - `backend/app/models/blob.py` - 参考 blob 外键关联

  **Acceptance Criteria**:
  - [ ] 模型文件创建成功
  - [ ] 字段定义正确
  - [ ] 外键关联正确

- [ ] T5. **FileVersion Schema + CRUD**

  **What to do**:
  - 创建 `backend/app/schemas/file_version.py`
  - 创建 `backend/app/crud/file_version.py`
  - 实现: create, get_by_file_path, get_by_id

  **Recommended Agent Profile**:
  - **Category**: `quick`
  - **Skills**: []

  **Parallelization**:
  - **Can Run In Parallel**: YES
  - **Parallel Group**: Wave 2
  - **Blocks**: T6, T11
  - **Blocked By**: T4

  **Acceptance Criteria**:
  - [ ] Schema 定义完整
  - [ ] CRUD 方法可用

- [ ] T6. **文件历史 API 端点**

  **What to do**:
  - 在 `backend/app/routers/` 下创建 `file_versions.py`
  - POST /file-versions - 创建版本
  - GET /file-versions?skill_id=&file_path= - 列表
  - GET /file-versions/{id} - 详情
  - 注册到 main.py

  **Recommended Agent Profile**:
  - **Category**: `unspecified-high`
  - **Skills**: []

  **Parallelization**:
  - **Can Run In Parallel**: YES
  - **Parallel Group**: Wave 2
  - **Blocks**: T11
  - **Blocked By**: T5

  **References**:
  - `backend/app/routers/trees.py` - 参考文件相关API

  **Acceptance Criteria**:
  - [ ] API 可正常调用
  - [ ] 权限检查正确

- [ ] T6b. **005_file_versions.py 迁移**

  **What to do**:
  - 创建 file_versions 表迁移

  **Recommended Agent Profile**:
  - **Category**: `quick`
  - **Skills**: []

  **Parallelization**:
  - **Can Run In Parallel**: YES
  - **Parallel Group**: Wave 2
  - **Blocks**: T11
  - **Blocked By**: T4

  **Acceptance Criteria**:
  - [ ] 迁移成功
  - [ ] 表创建成功

- [ ] T6c. **FileVersion API 单元测试**

  **What to do**:
  - 创建 `backend/tests/integration/api/test_file_versions_api.py`
  - 测试 POST /file-versions 创建版本
  - 测试 GET /file-versions?skill_id=&file_path= 列表
  - 测试 GET /file-versions/{id} 详情
  - 测试权限检查（未授权访问）

  **Recommended Agent Profile**:
  - **Category**: `unspecified-high`
  - **Skills**: []

  **Parallelization**:
  - **Can Run In Parallel**: YES
  - **Parallel Group**: Wave 2
  - **Blocked By**: T6

  **References**:
  - `backend/tests/integration/api/test_blobs_api.py` - 参考API测试模式

  **Acceptance Criteria**:
  - [ ] 所有 API 端点测试通过
  - [ ] 权限检查测试通过

---

### Wave 3: 前端核心逻辑

- [ ] T7. **删除旧版本 UI 组件**

  **What to do**:
  - 删除 `frontend/components/VersionHistory.tsx`
  - 删除 `frontend/components/VersionCompare.tsx`
  - 从 `frontend/components/skills/SkillEditorArea.tsx` 移除 versions tab
  - 清理相关类型定义

  **Recommended Agent Profile**:
  - **Category**: `quick`
  - **Skills**: []

  **Parallelization**:
  - **Can Run In Parallel**: YES
  - **Parallel Group**: Wave 3
  - **Blocks**: T12
  - **Blocked By**: None

  **Acceptance Criteria**:
  - [ ] 旧组件完全删除
  - [ ] 页面无引用错误

- [ ] T8. **TextEditor 修改状态检测**

  **What to do**:
  - 移除 debouncedSave 和 saveTimeoutRef
  - 添加 isModified 状态: 比较当前内容与原始内容
  - onChange 时设置 isModified = true
  - 保存成功后设置 isModified = false

  **Recommended Agent Profile**:
  - **Category**: `quick`
  - **Skills**: []

  **Parallelization**:
  - **Can Run In Parallel**: YES
  - **Parallel Group**: Wave 3
  - **Blocks**: T9
  - **Blocked By**: None

  **References**:
  - `frontend/components/TextEditor.tsx` - 当前实现

  **Acceptance Criteria**:
  - [ ] 移除自动保存
  - [ ] isModified 状态正确

- [ ] T9. **保存按钮状态管理**

  **What to do**:
  - 保存按钮默认 disabled
  - isModified 为 true 时 enabled
  - 保存中状态保持 enabled

  **Recommended Agent Profile**:
  - **Category**: `quick`
  - **Skills**: []

  **Parallelization**:
  - **Can Run In Parallel**: YES
  - **Parallel Group**: Wave 3
  - **Blocks**: T15
  - **Blocked By**: T8

  **Acceptance Criteria**:
  - [ ] 无修改时按钮不可点击
  - [ ] 有修改时按钮可点击

- [ ] T10. **未保存内容检测和提示**

  **What to do**:
  - beforeunload 事件: 页面刷新/关闭时提示
  - 路由守卫: 切换路由时检测 isModified
  - 弹出确认框组件

  **Recommended Agent Profile**:
  - **Category**: `unspecified-high`
  - **Skills**: []

  **Parallelization**:
  - **Can Run In Parallel**: YES
  - **Parallel Group**: Wave 3
  - **Blocked By**: T8

  **References**:
  - Next.js 路由守卫 (router.events 或 usePathname hook)
  - `frontend/components/ui/ConfirmDialog.tsx` - 确认框组件

  **Acceptance Criteria**:
  - [ ] 刷新页面时提示
  - [ ] 切换文件时提示
  - [ ] 点击返回按钮提示

- [ ] T11. **API 调用封装**

  **What to do**:
  - 在 `frontend/lib/api.ts` 添加文件历史相关调用

  **Recommended Agent Profile**:
  - **Category**: `quick`
  - **Skills**: []

  **Blocked By**: T6

  **Acceptance Criteria**:
  - [ ] API 封装可用

---

### Wave 4: 前端 UI + 测试

- [ ] T12. **文件树历史图标**

  **What to do**:
  - 在 FileTreeItem 添加时钟图标
  - 点击图标触发展开历史侧边栏

  **Recommended Agent Profile**:
  - **Category**: `visual-engineering`
  - **Skills**: []

  **Parallelization**:
  - **Can Run In Parallel**: YES
  - **Parallel Group**: Wave 4
  - **Blocks**: T13
  - **Blocked By**: T7, T11

  **References**:
  - `frontend/components/FileTreeItem.tsx`

  **Acceptance Criteria**:
  - [ ] 每个文件显示时钟图标
  - [ ] 点击触发事件

- [ ] T13. **FileHistorySidebar 侧边栏组件**

  **What to do**:
  - 创建 `frontend/components/FileHistorySidebar.tsx`
  - 展示文件历史列表
  - 点击历史项触发选中

  **Recommended Agent Profile**:
  - **Category**: `visual-engineering`
  - **Skills**: []

  **Parallelization**:
  - **Can Run In Parallel**: YES
  - **Parallel Group**: Wave 4
  - **Blocks**: T14
  - **Blocked By**: T11, T12

  **References**:
  - `frontend/components/skills/SkillSidebar.tsx` - 侧边栏模式

  **Acceptance Criteria**:
  - [ ] 侧边栏展开
  - [ ] 历史列表正确显示

- [ ] T14. **历史版本只读预览 + 恢复**

  **What to do**:
  - 点击历史版本后编辑器显示只读内容
  - 添加"恢复"按钮
  - 点击恢复替换当前内容

  **Recommended Agent Profile**:
  - **Category**: `unspecified-high`
  - **Skills**: []

  **Parallelization**:
  - **Can Run In Parallel**: YES
  - **Parallel Group**: Wave 4
  - **Blocks**: T16, T16c
  - **Blocked By**: T9, T13

  **References**:
  - `frontend/components/TextEditor.tsx` - 编辑器只读模式

  **Acceptance Criteria**:
  - [ ] 只读预览正常
  - [ ] 恢复功能正常

- [ ] T15. **恢复功能**

  **What to do**:
  - 点击恢复按钮替换编辑器内容

  **Recommended Agent Profile**:
  - **Category**: `unspecified-high`
  - **Skills**: []

  **Parallelization**:
  - **Can Run In Parallel**: YES
  - **Parallel Group**: Wave 4
  - **Blocked By**: T8, T14

  **Acceptance Criteria**:
  - [ ] 恢复功能正常

---

### Wave 5: 测试

- [ ] T16. **整体集成测试**

  **What to do**:
  - 端到端测试完整流程

  **Recommended Agent Profile**:
  - **Category**: `unspecified-high`
  - **Skills**: []

  **Parallelization**:
  - **Can Run In Parallel**: NO (sequential)
  - **Blocked By**: T3, T6c, T10, T14
  - **Blocks**: T16c

  **Acceptance Criteria**:
  - [ ] 完整流程可用

- [ ] T16b. **后端 Journey 测试**

  **What to do**:
  - 创建/更新 `backend/tests/integration/journey/` 下的文件历史journey测试
  - 测试完整流程：创建skill → 编辑文件 → 手动保存 → 查看历史 → 恢复版本
  - 测试未保存提示场景（可选）

  **Recommended Agent Profile**:
  - **Category**: `deep`
  - **Skills**: []

  **Parallelization**:
  - **Can Run In Parallel**: YES
  - **Parallel Group**: Wave 5
  - **Blocked By**: T3, T6c

  **References**:
  - `backend/tests/integration/journey/test_journey_file_ops.py` - 参考journey测试模式

  **Acceptance Criteria**:
  - [ ] 文件编辑-保存-历史流程测试通过
  - [ ] 历史版本恢复测试通过

- [ ] T16c. **前端 E2E Journey 测试**

  **What to do**:
  - 创建/更新 `frontend/playwright/pages.e2e.ts` 或新文件
  - 测试手动保存流程
  - 测试未保存提示弹窗
  - 测试文件历史侧边栏展开
  - 测试历史版本预览和恢复

  **Recommended Agent Profile**:
  - **Category**: `unspecified-high`
  - **Skills**: ["playwright"]

  **Parallelization**:
  - **Can Run In Parallel**: YES
  - **Parallel Group**: Wave 5
  - **Blocked By**: T14, T15, T16

  **References**:
  - `frontend/playwright/pages.e2e.ts` - 参考E2E测试模式

  **Acceptance Criteria**:
  - [ ] 手动保存 E2E 测试通过
  - [ ] 未保存提示 E2E 测试通过
  - [ ] 文件历史查看 E2E 测试通过

- [ ] T16d. **前端 API 集成测试**

  **What to do**:
  - 创建 `frontend/lib/__tests__/file-versions-api.test.ts`
  - 测试 POST /file-versions 创建版本
  - 测试 GET /file-versions 列表
  - 测试 GET /file-versions/{id} 详情
  - 参考现有 `api.integration.test.ts` 的 mock 模式

  **Recommended Agent Profile**:
  - **Category**: `quick`
  - **Skills**: []

  **Parallelization**:
  - **Can Run In Parallel**: YES
  - **Parallel Group**: Wave 5
  - **Blocked By**: T11

  **References**:
  - `frontend/lib/__tests__/api.integration.test.ts` - 参考API测试模式

  **Acceptance Criteria**:
  - [ ] FileVersion API 调用测试通过
  - [ ] 错误处理测试通过

---

## Success Criteria

### 验证命令
```bash
# 后端测试
cd backend && pytest

# 前端构建
cd frontend && npm run build
```

### 最终检查
- [ ] 手动保存功能正常
- [ ] 保存按钮状态正确
- [ ] 未保存提示覆盖全部场景
- [ ] 文件历史侧边栏可用
- [ ] 历史版本可预览和恢复
