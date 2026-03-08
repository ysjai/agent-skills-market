# 市场技能下载功能 实施计划

> **Status:** ✅ Completed (2026-03-08)

> **For Claude:** REQUIRED SUB-SKILL: Use superpowers:executing-plans to implement this plan task-by-task.

**Goal:** 在市场详情页和收藏详情页中添加技能下载功能（整体 ZIP 下载 + 单文件下载），并在后端实现权限控制：公开技能任何人可下载，未公开技能只有创建者能下载。

**Architecture:** 后端修改 `handle_download_skill` handler 的权限逻辑，增加 SharedSkillRepository 依赖来检查技能是否公开分享。前端改造现有 `DownloadDialog` 组件支持 `market` 模式（使用公开 API 路径），在 `SharedSkillDetail` 添加下载按钮，在 `MarketSkillFileTree` 添加单文件下载图标。

**Tech Stack:** FastAPI / Python / Next.js 15 / React 19 / TypeScript / JSZip / File System Access API

---

## Part A: 后端权限控制

### Task 1: 修改下载 handler 权限逻辑

**Files:**
- Modify: `backend/src/application/handlers/download_skill_handler.py`

**Step 1: 修改 `handle_download_skill` 函数签名和权限逻辑**

将当前的"只有创建者可下载"改为"创建者可下载 OR 技能已公开分享可下载"。

```python
# 修改 handle_download_skill 的签名，增加 shared_skill_repo 参数
# 将 user_id 改为 Optional（支持未登录用户下载公开技能）
async def handle_download_skill(
    skill_id: UUID,
    platform: str | None,
    skill_repo: SkillRepository,
    tree_repo: TreeRepository,
    blob_repo: BlobRepository,
    shared_skill_repo: SharedSkillRepository,
    user_id: UUID | None = None,
) -> tuple[bytes, str, str]:
    skill = await skill_repo.get_by_id(skill_id)
    if skill is None:
        raise ResourceNotFoundError("Skill not found")

    # 权限检查：创建者 OR 已公开分享
    is_owner = user_id is not None and skill.user_id == user_id
    if not is_owner:
        shared_skill = await shared_skill_repo.find_by_skill_id(skill_id)
        if shared_skill is None:
            raise ForbiddenError("Not authorized to download this skill")

    # 以下逻辑不变...
```

**Step 2: 验证修改**

运行: `cd backend && python -m pytest tests/ -k "download" -v` (如果有相关测试)
如果没有现成测试，手动确认修改语法正确即可。

**Step 3: Commit**

```bash
git add backend/src/application/handlers/download_skill_handler.py
git commit -m "feat: allow download of publicly shared skills by anyone"
```

---

### Task 2: 修改下载路由注入 SharedSkillRepository

**Files:**
- Modify: `backend/src/api/routers/skills.py`

**Step 1: 修改路由添加 shared_skill_repo 依赖**

在 `download_skill` 路由中增加 `shared_skill_repo` 参数，并将 `current_user` 改为可选（使用 `get_optional_user` 依赖）。

```python
# 在 skills.py 的 download_skill 路由中：
# 1. 添加 shared_skill_repo 依赖
# 2. 将 current_user 改为 optional_user（允许未登录用户下载公开技能）
@router.get("/{skill_id}/download")
async def download_skill(
    skill_id: UUID,
    platform: str | None = Query(None),
    skill_repo: SkillRepository = Depends(get_skill_repo),
    tree_repo: TreeRepository = Depends(get_tree_repo),
    blob_repo: BlobRepository = Depends(get_blob_repo),
    shared_skill_repo: SharedSkillRepository = Depends(get_shared_skill_repo),
    optional_user: User | None = Depends(get_optional_user),
) -> StreamingResponse:
    content, media_type, filename = await handle_download_skill(
        skill_id=skill_id,
        platform=platform,
        skill_repo=skill_repo,
        tree_repo=tree_repo,
        blob_repo=blob_repo,
        shared_skill_repo=shared_skill_repo,
        user_id=optional_user.id if optional_user else None,
    )
    return StreamingResponse(
        iter([content]),
        media_type=media_type,
        headers={"Content-Disposition": f"attachment; filename={filename}"},
    )
```

注意：需要确认 `get_optional_user` 是否已存在。如果不存在，需要检查 `backend/src/api/dependencies/auth.py` 中的可选用户认证依赖。

**Step 2: 确认 imports**

确保 skills.py 中导入了 `get_shared_skill_repo` 和 `SharedSkillRepository`（已确认 skills.py:12 已有 `get_shared_skill_repo` 导入）。

**Step 3: Commit**

```bash
git add backend/src/api/routers/skills.py
git commit -m "feat: inject SharedSkillRepository in download route for public access"
```

---

## Part B: 前端下载功能

### Task 3: 创建市场下载工具函数

**Files:**
- Modify: `frontend/lib/download.ts`

**Step 1: 添加 `downloadMarketSkillAsZip` 函数**

在 `download.ts` 中新增一个函数，使用市场公开 API 获取文件并打包 ZIP：

```typescript
export async function downloadMarketSkillAsZip(
  sharedSkillId: string,
  skillName: string,
  onProgress?: (current: number, total: number) => void
): Promise<void> {
  // 1. 获取文件树
  const tree = await api.getMarketSkillTree(sharedSkillId);
  const files = tree.entries.filter((e) => e.type === 'blob' && e.blob_id);

  if (files.length === 0) {
    throw new Error('No files found in this skill');
  }

  // 2. 用 JSZip 打包
  const JSZip = (await import('jszip')).default;
  const zip = new JSZip();

  for (let i = 0; i < files.length; i++) {
    const file = files[i];
    const blob = await api.getMarketSkillBlob(sharedSkillId, file.blob_id!);
    zip.file(file.path, blob);
    onProgress?.(i + 1, files.length);
  }

  // 3. 生成并下载 ZIP
  const zipBlob = await zip.generateAsync({ type: 'blob' });
  const url = URL.createObjectURL(zipBlob);
  const a = document.createElement('a');
  a.href = url;
  a.download = `${skillName}.zip`;
  a.click();
  URL.revokeObjectURL(url);
}
```

**Step 2: 添加 `downloadAndExtractMarketSkill` 函数**

用于直接写入本地目录（File System Access API）模式：

```typescript
export interface MarketDownloadAndExtractOptions {
  sharedSkillId: string;
  skillName: string;
  platform: Platform;
  dirHandle: FileSystemDirectoryHandle;
  onProgress?: (progress: number, currentFile?: number, totalFiles?: number) => void;
  preserveNames?: boolean;
}

export async function downloadAndExtractMarketSkill(
  options: MarketDownloadAndExtractOptions
): Promise<DownloadResult> {
  const { sharedSkillId, skillName, platform, dirHandle, onProgress, preserveNames } = options;

  try {
    const tree = await api.getMarketSkillTree(sharedSkillId);
    const files = tree.entries.filter((e) => e.type === 'blob');

    if (files.length === 0) {
      return { success: false, filesExtracted: 0, targetPath: '', error: 'No files found' };
    }

    const platformDir = PLATFORM_DIRS[platform];
    const dirParts = platformDir.split('/');
    let currentHandle = dirHandle;
    for (const part of dirParts) {
      if (part) currentHandle = await currentHandle.getDirectoryHandle(part, { create: true });
    }

    const finalSkillName = preserveNames ? skillName : sanitizeFileName(skillName);
    const skillHandle = await currentHandle.getDirectoryHandle(finalSkillName, { create: true });

    let filesExtracted = 0;
    const totalFiles = files.length;

    for (let i = 0; i < files.length; i++) {
      const file = files[i];
      if (!file.blob_id) {
        filesExtracted++;
        onProgress?.(Math.round((filesExtracted / totalFiles) * 100), filesExtracted, totalFiles);
        continue;
      }
      const blob = await api.getMarketSkillBlob(sharedSkillId, file.blob_id);
      await writeFileToDirectory(skillHandle, file.path, blob, preserveNames);
      filesExtracted++;
      onProgress?.(Math.round((filesExtracted / totalFiles) * 100), filesExtracted, totalFiles);
    }

    return { success: true, filesExtracted, targetPath: `${platformDir}/${skillName}` };
  } catch (error) {
    return {
      success: false, filesExtracted: 0, targetPath: '',
      error: error instanceof Error ? error.message : 'Download failed',
    };
  }
}
```

**Step 3: Commit**

```bash
git add frontend/lib/download.ts
git commit -m "feat: add market skill download utilities using public API"
```

---

### Task 4: 改造 DownloadDialog 支持 market 模式

**Files:**
- Modify: `frontend/components/misc/DownloadDialog.tsx`

**Step 1: 添加 market 模式 props**

在 `DownloadDialog` 的 props 中增加可选的 `mode` 和 `sharedSkillId`：

```typescript
interface DownloadDialogProps {
  open: boolean;
  skillId: string;
  skillName: string;
  onClose: () => void;
  onSuccess?: () => void;
  // 新增：市场模式
  mode?: 'private' | 'market';
  sharedSkillId?: string;
}
```

**Step 2: 修改 ZIP 下载逻辑**

在 `handleDownloadZip` 函数中，根据 `mode` 使用不同的 API：

- `mode === 'private'`（默认）: 使用现有的 `/skills/${skillId}/files` + `/blobs/${blobId}`
- `mode === 'market'`: 使用 `downloadMarketSkillAsZip(sharedSkillId, skillName, onProgress)`

**Step 3: 修改直接写入逻辑**

在 `handleDownloadReplace` 函数中，根据 `mode` 调用不同的下载函数：

- `mode === 'private'`: 调用现有的 `downloadAndExtractSkill`
- `mode === 'market'`: 调用新的 `downloadAndExtractMarketSkill`

**Step 4: Commit**

```bash
git add frontend/components/misc/DownloadDialog.tsx
git commit -m "feat: support market mode in DownloadDialog for public skill download"
```

---

### Task 5: 在 SharedSkillDetail 添加下载按钮

**Files:**
- Modify: `frontend/components/market/SharedSkillDetail.tsx`

**Step 1: 添加下载状态和 Dialog**

在组件中添加 `showDownloadDialog` state，以及 `DownloadDialog` 组件的渲染。

**Step 2: 在按钮区域添加 Download 按钮**

在 Like/Favorite 按钮旁边（`<div className="flex gap-3">` 区域）添加一个 Download 按钮：

```tsx
<Button variant="outline" size="sm" onClick={() => setShowDownloadDialog(true)}>
  <Download className="mr-1.5 h-4 w-4" />
  {t('download')}
</Button>
```

**Step 3: 渲染 DownloadDialog**

```tsx
{showDownloadDialog && skill && (
  <DownloadDialog
    open={showDownloadDialog}
    skillId={skill.skill?.id || ''}
    skillName={skill.skill?.name || skill.skill?.slug || 'skill'}
    sharedSkillId={id}
    mode="market"
    onClose={() => setShowDownloadDialog(false)}
  />
)}
```

**Step 4: Commit**

```bash
git add frontend/components/market/SharedSkillDetail.tsx
git commit -m "feat: add download button to market/favorites skill detail page"
```

---

### Task 6: 在 MarketSkillFileTree 添加单文件下载图标

**Files:**
- Modify: `frontend/components/market/MarketSkillFileTree.tsx`
- Modify: `frontend/components/market/MarketSkillViewer.tsx` (传入 sharedSkillId)

**Step 1: 给 MarketSkillFileTree 添加 sharedSkillId prop**

```typescript
interface MarketSkillFileTreeProps {
  nodes: MarketFileNode[];
  selectedPath: string;
  loading: boolean;
  error: string | null;
  onSelect: (path: string, blobId?: string) => void;
  onToggle: (path: string) => void;
  sharedSkillId: string; // 新增
}
```

**Step 2: 在每个 blob 文件节点上添加下载图标**

在 `FileTreeNode` 组件中，为 type === 'blob' 的节点添加一个下载图标按钮（悬停时显示）：

```tsx
{node.type === 'blob' && node.blob_id && (
  <button
    onClick={async (e) => {
      e.stopPropagation();
      const blob = await api.getMarketSkillBlob(sharedSkillId, node.blob_id!);
      const url = URL.createObjectURL(blob);
      const a = document.createElement('a');
      a.href = url;
      a.download = node.name;
      a.click();
      URL.revokeObjectURL(url);
    }}
    className="opacity-0 group-hover:opacity-100 p-0.5 hover:bg-gray-200 rounded"
    title="Download file"
  >
    <Download className="h-3.5 w-3.5 text-gray-500" />
  </button>
)}
```

**Step 3: 在 MarketSkillViewer 中传入 sharedSkillId**

```tsx
<MarketSkillFileTree
  nodes={nodes}
  selectedPath={selectedPath}
  loading={loading}
  error={error}
  onSelect={selectNode}
  onToggle={toggleNode}
  sharedSkillId={sharedSkillId}  // 新增
/>
```

**Step 4: Commit**

```bash
git add frontend/components/market/MarketSkillFileTree.tsx frontend/components/market/MarketSkillViewer.tsx
git commit -m "feat: add per-file download icon in market skill file tree"
```

---

### Task 7: 添加 i18n 翻译（如需要）

**Files:**
- Modify: `frontend/i18n/locales/en.json`
- Modify: `frontend/i18n/locales/zh.json`

**Step 1: 检查并添加缺失的翻译 key**

检查 market namespace 中是否已有 `download` key。如果没有，添加：

```json
// en.json market 下
"download": "Download"

// zh.json market 下
"download": "下载"
```

**Step 2: Commit**

```bash
git add frontend/i18n/locales/en.json frontend/i18n/locales/zh.json
git commit -m "feat: add download i18n keys for market pages"
```

---

### Task 8: 端到端验证

**Step 1: 启动后端**

```bash
cd backend && uvicorn src.main:app --reload --port 8000
```

**Step 2: 启动前端**

```bash
cd frontend && npm run dev
```

**Step 3: 验证市场页下载**

1. 打开市场页 `http://localhost:3000/market`
2. 点击一个已分享的技能，进入详情页
3. 点击 Download 按钮，验证 DownloadDialog 弹出
4. 测试 ZIP 下载和直接写入两种模式
5. 测试文件树中单个文件的下载图标

**Step 4: 验证收藏页下载**

1. 打开收藏页 `http://localhost:3000/favorites`
2. 点击一个已收藏的技能，进入详情页
3. 同样验证下载功能正常

**Step 5: 验证权限控制**

1. 未登录状态下，访问一个公开技能的详情页，验证可以下载
2. 未登录状态下，直接调用未公开技能的下载 API，验证返回 403
3. 登录为技能创建者，验证可以下载自己的技能（无论是否公开）

**Step 6: 用 Playwright 截图验证 UI**

截图市场详情页，确认 Download 按钮和文件树下载图标显示正确。
