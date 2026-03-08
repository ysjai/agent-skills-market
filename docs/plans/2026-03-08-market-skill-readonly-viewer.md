# Market Skill 只读详情查看器 实现计划

> **Status:** ✅ Completed (2026-03-08)

> **For Claude:** REQUIRED SUB-SKILL: Use superpowers:executing-plans to implement this plan task-by-task.

**Goal:** 让用户（包括收藏用户）在市场详情页能以只读方式查看 Skill 的完整文件内容（文件树 + 文件预览）。

**Architecture:** 在后端新增 API 端点，通过 `SharedSkill.skill_id` 找到原始 Skill 的 `tree_id`，返回文件树数据。前端在市场详情页集成只读文件树和文件预览组件，复用现有的 `FileTree` + `FilePreview` 组件。

**Tech Stack:** FastAPI (Python) / Next.js 15 / React 19 / TypeScript / Zustand / DDD 四层架构

---

## Task 1: 后端 - 新增获取市场技能文件树的 Handler

**Files:**
- Create: `backend/src/application/handlers/get_market_skill_tree_handler.py`
- Test: `backend/tests/unit/application/handlers/test_get_market_skill_tree_handler.py`

**Step 1: 编写单元测试**

```python
# backend/tests/unit/application/handlers/test_get_market_skill_tree_handler.py
from __future__ import annotations

import uuid
from unittest.mock import AsyncMock

import pytest

from src.domain.aggregates.shared_skill import SharedSkill
from src.domain.aggregates.skill import Skill
from src.domain.aggregates.tree import Tree
from src.domain.exceptions import ResourceNotFoundError


@pytest.fixture
def shared_skill_repo():
    return AsyncMock()


@pytest.fixture
def skill_repo():
    return AsyncMock()


@pytest.fixture
def tree_repo():
    return AsyncMock()


class TestGetMarketSkillTreeHandler:
    @pytest.mark.asyncio
    async def should_return_tree_when_get_market_skill_tree_given_active_shared_skill(
        self, shared_skill_repo, skill_repo, tree_repo
    ):
        from src.application.handlers.get_market_skill_tree_handler import (
            handle_get_market_skill_tree,
        )

        shared_skill_id = uuid.uuid4()
        skill_id = uuid.uuid4()
        tree_id = uuid.uuid4()

        shared_skill = SharedSkill(id=shared_skill_id, skill_id=skill_id, status="active")
        skill = Skill(id=skill_id, tree_id=tree_id)
        tree = Tree(id=tree_id, entries=[])

        shared_skill_repo.find_by_id.return_value = shared_skill
        skill_repo.get_by_id.return_value = skill
        tree_repo.get_by_id.return_value = tree

        result = await handle_get_market_skill_tree(
            shared_skill_id=shared_skill_id,
            shared_skill_repo=shared_skill_repo,
            skill_repo=skill_repo,
            tree_repo=tree_repo,
        )

        assert result.id == tree_id

    @pytest.mark.asyncio
    async def should_raise_not_found_when_get_market_skill_tree_given_nonexistent_shared_skill(
        self, shared_skill_repo, skill_repo, tree_repo
    ):
        from src.application.handlers.get_market_skill_tree_handler import (
            handle_get_market_skill_tree,
        )

        shared_skill_repo.find_by_id.return_value = None

        with pytest.raises(ResourceNotFoundError):
            await handle_get_market_skill_tree(
                shared_skill_id=uuid.uuid4(),
                shared_skill_repo=shared_skill_repo,
                skill_repo=skill_repo,
                tree_repo=tree_repo,
            )

    @pytest.mark.asyncio
    async def should_raise_not_found_when_get_market_skill_tree_given_withdrawn_skill(
        self, shared_skill_repo, skill_repo, tree_repo
    ):
        from src.application.handlers.get_market_skill_tree_handler import (
            handle_get_market_skill_tree,
        )

        shared_skill = SharedSkill(id=uuid.uuid4(), skill_id=None, status="withdrawn")
        shared_skill_repo.find_by_id.return_value = shared_skill

        with pytest.raises(ResourceNotFoundError):
            await handle_get_market_skill_tree(
                shared_skill_id=shared_skill.id,
                shared_skill_repo=shared_skill_repo,
                skill_repo=skill_repo,
                tree_repo=tree_repo,
            )

    @pytest.mark.asyncio
    async def should_raise_not_found_when_get_market_skill_tree_given_skill_without_tree(
        self, shared_skill_repo, skill_repo, tree_repo
    ):
        from src.application.handlers.get_market_skill_tree_handler import (
            handle_get_market_skill_tree,
        )

        skill_id = uuid.uuid4()
        shared_skill = SharedSkill(id=uuid.uuid4(), skill_id=skill_id, status="active")
        skill = Skill(id=skill_id, tree_id=None)

        shared_skill_repo.find_by_id.return_value = shared_skill
        skill_repo.get_by_id.return_value = skill

        with pytest.raises(ResourceNotFoundError):
            await handle_get_market_skill_tree(
                shared_skill_id=shared_skill.id,
                shared_skill_repo=shared_skill_repo,
                skill_repo=skill_repo,
                tree_repo=tree_repo,
            )
```

**Step 2: 运行测试确认失败**

```bash
cd backend && python -m pytest tests/unit/application/handlers/test_get_market_skill_tree_handler.py -v
```

Expected: FAIL - module not found

**Step 3: 编写 Handler 实现**

```python
# backend/src/application/handlers/get_market_skill_tree_handler.py
from __future__ import annotations

from uuid import UUID

from src.domain.aggregates.tree import Tree
from src.domain.exceptions import ResourceNotFoundError
from src.domain.repositories.shared_skill_repository import SharedSkillRepository
from src.domain.repositories.skill_repository import SkillRepository
from src.domain.repositories.tree_repository import TreeRepository


async def handle_get_market_skill_tree(
    shared_skill_id: UUID,
    shared_skill_repo: SharedSkillRepository,
    skill_repo: SkillRepository,
    tree_repo: TreeRepository,
) -> Tree:
    shared_skill = await shared_skill_repo.find_by_id(shared_skill_id)
    if shared_skill is None:
        raise ResourceNotFoundError("Shared skill not found")

    if shared_skill.skill_id is None:
        raise ResourceNotFoundError("Skill content is no longer available")

    skill = await skill_repo.get_by_id(shared_skill.skill_id)
    if skill is None:
        raise ResourceNotFoundError("Original skill not found")

    if skill.tree_id is None:
        raise ResourceNotFoundError("Skill has no file tree")

    tree = await tree_repo.get_by_id(skill.tree_id)
    if tree is None:
        raise ResourceNotFoundError("File tree not found")

    return tree
```

**Step 4: 运行测试确认通过**

```bash
cd backend && python -m pytest tests/unit/application/handlers/test_get_market_skill_tree_handler.py -v
```

Expected: ALL PASS

**Step 5: 提交**

```bash
git add backend/src/application/handlers/get_market_skill_tree_handler.py backend/tests/unit/application/handlers/test_get_market_skill_tree_handler.py
git commit -m "feat: add handler for getting market skill file tree"
```

---

## Task 2: 后端 - 在 market router 中新增文件树端点

**Files:**
- Modify: `backend/src/api/routers/market.py`
- Test: `backend/tests/integration/api/test_market_tree_api.py`

**Step 1: 编写 API 集成测试**

```python
# backend/tests/integration/api/test_market_tree_api.py
from __future__ import annotations

import pytest
from httpx import AsyncClient


class TestGetMarketSkillTree:
    @pytest.mark.asyncio
    async def should_return_tree_when_get_market_skill_tree_given_shared_skill_with_tree(
        self, auth_client: AsyncClient, test_user
    ):
        # 创建 skill + tree
        skill_resp = await auth_client.post("/api/skills", json={
            "name": "Test Skill",
            "slug": "test-skill",
            "description": "Test description",
        })
        assert skill_resp.status_code == 201
        skill_id = skill_resp.json()["id"]

        # 创建 tree
        tree_resp = await auth_client.post("/api/trees", json={"entries": []})
        assert tree_resp.status_code == 201
        tree_id = tree_resp.json()["id"]

        # 添加文件到 tree
        await auth_client.post(f"/api/trees/{tree_id}/files", json={
            "path": "SKILL.md",
            "type": "blob",
            "content": "# Test Skill",
        })

        # 关联 tree 到 skill
        await auth_client.put(f"/api/skills/{skill_id}", json={"tree_id": tree_id})

        # 创建分类
        # 注意：需要根据实际的分类获取方式调整
        cats_resp = await auth_client.get("/api/categories")
        category_id = cats_resp.json()["items"][0]["id"]

        # 分享 skill
        share_resp = await auth_client.post(f"/api/skills/{skill_id}/share", json={
            "category_id": category_id,
            "share_message": "Check this out",
        })
        assert share_resp.status_code == 201
        shared_skill_id = share_resp.json()["id"]

        # 获取文件树
        tree_resp = await auth_client.get(f"/api/market/skills/{shared_skill_id}/tree")
        assert tree_resp.status_code == 200
        data = tree_resp.json()
        assert "entries" in data
        assert data["id"] == tree_id

    @pytest.mark.asyncio
    async def should_return_404_when_get_market_skill_tree_given_nonexistent_shared_skill(
        self, auth_client: AsyncClient
    ):
        import uuid
        fake_id = str(uuid.uuid4())
        resp = await auth_client.get(f"/api/market/skills/{fake_id}/tree")
        assert resp.status_code == 404
```

**Step 2: 运行测试确认失败**

```bash
cd backend && python -m pytest tests/integration/api/test_market_tree_api.py -v
```

Expected: FAIL - 404 (route not found)

**Step 3: 在 market.py 中添加路由**

在 `backend/src/api/routers/market.py` 中添加：

1. 导入新增的依赖（tree_repo, skill_repo）
2. 添加新路由 `GET /market/skills/{shared_skill_id}/tree`

```python
# 新增导入
from src.api.dependencies.repositories import get_tree_repo
from src.api.schemas.tree import GetTreeResp
from src.domain.repositories.tree_repository import TreeRepository

# 新增 handler 类型和导入
_market_tree_handler = import_module("src.application.handlers.get_market_skill_tree_handler")
handle_get_market_skill_tree = _market_tree_handler.handle_get_market_skill_tree

# 新增路由 - 放在 get_market_skill_detail 之后
@market_router.get("/market/skills/{shared_skill_id}/tree", response_model=GetTreeResp)
async def get_market_skill_tree(
    shared_skill_id: UUID,
    shared_skill_repo: Annotated[SharedSkillRepository, Depends(get_shared_skill_repo)],
    skill_repo: Annotated[SkillRepository, Depends(get_skill_repo)],
    tree_repo: Annotated[TreeRepository, Depends(get_tree_repo)],
) -> GetTreeResp:
    tree = await handle_get_market_skill_tree(
        shared_skill_id=shared_skill_id,
        shared_skill_repo=shared_skill_repo,
        skill_repo=skill_repo,
        tree_repo=tree_repo,
    )
    return GetTreeResp.from_domain(tree)
```

**Step 4: 运行测试确认通过**

```bash
cd backend && python -m pytest tests/integration/api/test_market_tree_api.py -v
```

Expected: ALL PASS

**Step 5: 运行全量后端测试确保无回归**

```bash
cd backend && python -m pytest -x -v
```

Expected: ALL PASS

**Step 6: 提交**

```bash
git add backend/src/api/routers/market.py backend/tests/integration/api/test_market_tree_api.py
git commit -m "feat: add GET /market/skills/{id}/tree endpoint"
```

---

## Task 3: 后端 - 新增 market blob 公开访问端点

**说明：** 现有的 `GET /blobs/{blob_id}` 需要认证（`get_current_user`），且不验证用户是否有权访问该 blob。市场查看场景需要一个不要求登录的 blob 读取端点，但需要验证 blob 属于一个已分享的 skill。

**Files:**
- Modify: `backend/src/api/routers/market.py`
- Create: `backend/src/application/handlers/get_market_blob_handler.py`
- Test: `backend/tests/unit/application/handlers/test_get_market_blob_handler.py`

**Step 1: 编写 Handler 测试**

```python
# backend/tests/unit/application/handlers/test_get_market_blob_handler.py
from __future__ import annotations

import uuid
from unittest.mock import AsyncMock

import pytest

from src.domain.aggregates.shared_skill import SharedSkill
from src.domain.aggregates.skill import Skill
from src.domain.exceptions import ResourceNotFoundError


@pytest.fixture
def shared_skill_repo():
    return AsyncMock()


@pytest.fixture
def skill_repo():
    return AsyncMock()


@pytest.fixture
def tree_repo():
    return AsyncMock()


@pytest.fixture
def blob_repo():
    return AsyncMock()


class TestGetMarketBlobHandler:
    @pytest.mark.asyncio
    async def should_return_blob_when_given_valid_shared_skill_and_blob(
        self, shared_skill_repo, skill_repo, tree_repo, blob_repo
    ):
        from src.application.handlers.get_market_blob_handler import (
            handle_get_market_blob,
        )
        from src.domain.aggregates.tree import Tree, TreeEntry
        from src.domain.value_objects.path import Path
        from src.domain.entities.blob import Blob

        blob_id = uuid.uuid4()
        tree_id = uuid.uuid4()
        skill_id = uuid.uuid4()
        shared_skill_id = uuid.uuid4()

        shared_skill = SharedSkill(id=shared_skill_id, skill_id=skill_id, status="active")
        skill = Skill(id=skill_id, tree_id=tree_id)
        tree = Tree(id=tree_id, entries=[
            TreeEntry(path=Path("SKILL.md"), blob_id=blob_id, entry_type="blob"),
        ])
        blob = Blob(id=blob_id, content=b"# Hello", content_hash="abc123")

        shared_skill_repo.find_by_id.return_value = shared_skill
        skill_repo.get_by_id.return_value = skill
        tree_repo.get_by_id.return_value = tree
        blob_repo.get_by_id.return_value = blob

        result = await handle_get_market_blob(
            shared_skill_id=shared_skill_id,
            blob_id=blob_id,
            shared_skill_repo=shared_skill_repo,
            skill_repo=skill_repo,
            tree_repo=tree_repo,
            blob_repo=blob_repo,
        )

        assert result.id == blob_id

    @pytest.mark.asyncio
    async def should_raise_not_found_when_blob_not_in_tree(
        self, shared_skill_repo, skill_repo, tree_repo, blob_repo
    ):
        from src.application.handlers.get_market_blob_handler import (
            handle_get_market_blob,
        )
        from src.domain.aggregates.tree import Tree

        tree_id = uuid.uuid4()
        skill_id = uuid.uuid4()
        shared_skill_id = uuid.uuid4()

        shared_skill = SharedSkill(id=shared_skill_id, skill_id=skill_id, status="active")
        skill = Skill(id=skill_id, tree_id=tree_id)
        tree = Tree(id=tree_id, entries=[])

        shared_skill_repo.find_by_id.return_value = shared_skill
        skill_repo.get_by_id.return_value = skill
        tree_repo.get_by_id.return_value = tree

        with pytest.raises(ResourceNotFoundError):
            await handle_get_market_blob(
                shared_skill_id=shared_skill_id,
                blob_id=uuid.uuid4(),
                shared_skill_repo=shared_skill_repo,
                skill_repo=skill_repo,
                tree_repo=tree_repo,
                blob_repo=blob_repo,
            )
```

**Step 2: 运行测试确认失败**

```bash
cd backend && python -m pytest tests/unit/application/handlers/test_get_market_blob_handler.py -v
```

**Step 3: 编写 Handler**

```python
# backend/src/application/handlers/get_market_blob_handler.py
from __future__ import annotations

from uuid import UUID

from src.domain.entities.blob import Blob
from src.domain.exceptions import ResourceNotFoundError
from src.domain.repositories.blob_repository import BlobRepository
from src.domain.repositories.shared_skill_repository import SharedSkillRepository
from src.domain.repositories.skill_repository import SkillRepository
from src.domain.repositories.tree_repository import TreeRepository


async def handle_get_market_blob(
    shared_skill_id: UUID,
    blob_id: UUID,
    shared_skill_repo: SharedSkillRepository,
    skill_repo: SkillRepository,
    tree_repo: TreeRepository,
    blob_repo: BlobRepository,
) -> Blob:
    shared_skill = await shared_skill_repo.find_by_id(shared_skill_id)
    if shared_skill is None or shared_skill.skill_id is None:
        raise ResourceNotFoundError("Shared skill not found")

    skill = await skill_repo.get_by_id(shared_skill.skill_id)
    if skill is None or skill.tree_id is None:
        raise ResourceNotFoundError("Skill content not available")

    tree = await tree_repo.get_by_id(skill.tree_id)
    if tree is None:
        raise ResourceNotFoundError("File tree not found")

    blob_ids_in_tree = {entry.blob_id for entry in tree.entries if entry.blob_id}
    if blob_id not in blob_ids_in_tree:
        raise ResourceNotFoundError("Blob not found in this skill")

    blob = await blob_repo.get_by_id(blob_id)
    if blob is None:
        raise ResourceNotFoundError("Blob not found")

    return blob
```

**Step 4: 运行测试确认通过**

```bash
cd backend && python -m pytest tests/unit/application/handlers/test_get_market_blob_handler.py -v
```

**Step 5: 在 market.py 中添加 blob 路由**

```python
# 添加到 market.py

from src.api.dependencies.repositories import get_blob_repo
from src.domain.repositories.blob_repository import BlobRepository
from fastapi.responses import Response

_market_blob_handler = import_module("src.application.handlers.get_market_blob_handler")
handle_get_market_blob = _market_blob_handler.handle_get_market_blob

@market_router.get("/market/skills/{shared_skill_id}/blobs/{blob_id}")
async def get_market_skill_blob(
    shared_skill_id: UUID,
    blob_id: UUID,
    shared_skill_repo: Annotated[SharedSkillRepository, Depends(get_shared_skill_repo)],
    skill_repo: Annotated[SkillRepository, Depends(get_skill_repo)],
    tree_repo: Annotated[TreeRepository, Depends(get_tree_repo)],
    blob_repo: Annotated[BlobRepository, Depends(get_blob_repo)],
    content_type: str | None = None,
) -> Response:
    blob = await handle_get_market_blob(
        shared_skill_id=shared_skill_id,
        blob_id=blob_id,
        shared_skill_repo=shared_skill_repo,
        skill_repo=skill_repo,
        tree_repo=tree_repo,
        blob_repo=blob_repo,
    )
    media_type = content_type or "application/octet-stream"
    return Response(
        content=blob.get_raw_content(),
        media_type=media_type,
    )
```

**Step 6: 运行全量测试**

```bash
cd backend && python -m pytest -x -v
```

**Step 7: 提交**

```bash
git add backend/src/application/handlers/get_market_blob_handler.py backend/tests/unit/application/handlers/test_get_market_blob_handler.py backend/src/api/routers/market.py
git commit -m "feat: add market blob endpoint for public skill content access"
```

---

## Task 4: 前端 - 添加市场 API 方法和只读文件树 Hook

**Files:**
- Modify: `frontend/lib/api.ts` (新增 getMarketSkillTree, getMarketSkillBlob)
- Create: `frontend/hooks/useMarketFileTree.ts`

**Step 1: 在 api.ts 中新增方法**

在 `getMarketSkillDetail` 方法后面添加：

```typescript
async getMarketSkillTree(sharedSkillId: string): Promise<{
  id: string;
  entries: Array<{ path: string; blob_id: string | null; type: string }>;
  created_at: string;
}> {
  return this.get(`/market/skills/${sharedSkillId}/tree`);
}

async getMarketSkillBlob(sharedSkillId: string, blobId: string): Promise<Blob> {
  return this.getBlob(`/market/skills/${sharedSkillId}/blobs/${blobId}`);
}
```

**Step 2: 创建只读文件树 Hook**

```typescript
// frontend/hooks/useMarketFileTree.ts
'use client';

import { useState, useEffect, useCallback } from 'react';
import { api } from '@/lib/api';

export interface MarketFileNode {
  id: string;
  name: string;
  path: string;
  type: 'blob' | 'tree';
  blob_id?: string;
  children: MarketFileNode[];
  isExpanded: boolean;
  depth: number;
}

interface UseMarketFileTreeOptions {
  sharedSkillId: string;
}

export function useMarketFileTree({ sharedSkillId }: UseMarketFileTreeOptions) {
  const [nodes, setNodes] = useState<MarketFileNode[]>([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [selectedPath, setSelectedPath] = useState('');
  const [selectedBlobId, setSelectedBlobId] = useState('');

  const buildTree = useCallback(
    (entries: Array<{ path: string; blob_id: string | null; type: string }>): MarketFileNode[] => {
      const root: MarketFileNode[] = [];
      const map = new Map<string, MarketFileNode>();

      const sorted = [...entries].sort((a, b) => {
        if (a.type !== b.type) return a.type === 'tree' ? -1 : 1;
        return a.path.localeCompare(b.path);
      });

      for (const entry of sorted) {
        const parts = entry.path.split('/');
        const name = parts[parts.length - 1];
        const depth = parts.length - 1;

        const node: MarketFileNode = {
          id: entry.path,
          name,
          path: entry.path,
          type: entry.type as 'blob' | 'tree',
          blob_id: entry.blob_id || undefined,
          children: [],
          isExpanded: depth === 0,
          depth,
        };

        map.set(entry.path, node);

        if (parts.length === 1) {
          root.push(node);
        } else {
          const parentPath = parts.slice(0, -1).join('/');
          const parent = map.get(parentPath);
          if (parent) {
            parent.children.push(node);
          }
        }
      }

      return root;
    },
    []
  );

  useEffect(() => {
    if (!sharedSkillId) return;

    let cancelled = false;
    setLoading(true);
    setError(null);

    api
      .getMarketSkillTree(sharedSkillId)
      .then((data) => {
        if (!cancelled) {
          setNodes(buildTree(data.entries));
        }
      })
      .catch((err) => {
        if (!cancelled) {
          setError(err instanceof Error ? err.message : 'Failed to load file tree');
        }
      })
      .finally(() => {
        if (!cancelled) setLoading(false);
      });

    return () => {
      cancelled = true;
    };
  }, [sharedSkillId, buildTree]);

  const toggleNode = useCallback((path: string) => {
    setNodes((prev) => {
      const toggle = (items: MarketFileNode[]): MarketFileNode[] =>
        items.map((item) => {
          if (item.path === path) {
            return { ...item, isExpanded: !item.isExpanded };
          }
          if (item.children.length > 0) {
            return { ...item, children: toggle(item.children) };
          }
          return item;
        });
      return toggle(prev);
    });
  }, []);

  const selectNode = useCallback((path: string, blobId?: string) => {
    setSelectedPath(path);
    setSelectedBlobId(blobId || '');
  }, []);

  return {
    nodes,
    loading,
    error,
    selectedPath,
    selectedBlobId,
    toggleNode,
    selectNode,
  };
}
```

**Step 3: 提交**

```bash
git add frontend/lib/api.ts frontend/hooks/useMarketFileTree.ts
git commit -m "feat: add market file tree API methods and readonly hook"
```

---

## Task 5: 前端 - 创建只读文件树和预览组件

**Files:**
- Create: `frontend/components/market/MarketSkillFileTree.tsx`
- Create: `frontend/components/market/MarketSkillViewer.tsx`

**Step 1: 创建只读文件树组件**

```tsx
// frontend/components/market/MarketSkillFileTree.tsx
'use client';

import { useTranslations } from 'next-intl';
import { FolderTree, ChevronRight, ChevronDown, FileText, Folder, FolderOpen } from 'lucide-react';
import { cn } from '@/lib/utils';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/Card';
import type { MarketFileNode } from '@/hooks/useMarketFileTree';
import { getFileIcon } from '@/components/ui/FileIcons';

interface MarketSkillFileTreeProps {
  nodes: MarketFileNode[];
  selectedPath: string;
  loading: boolean;
  error: string | null;
  onSelect: (path: string, blobId?: string) => void;
  onToggle: (path: string) => void;
  className?: string;
}

function FileTreeNode({
  node,
  selectedPath,
  onSelect,
  onToggle,
}: {
  node: MarketFileNode;
  selectedPath: string;
  onSelect: (path: string, blobId?: string) => void;
  onToggle: (path: string) => void;
}) {
  const isSelected = node.path === selectedPath;
  const isFolder = node.type === 'tree';

  return (
    <div>
      <button
        onClick={() => {
          if (isFolder) {
            onToggle(node.path);
          } else {
            onSelect(node.path, node.blob_id);
          }
        }}
        className={cn(
          'flex w-full items-center gap-1.5 rounded-md px-2 py-1.5 text-left text-sm transition-colors',
          isSelected
            ? 'bg-blue-50 text-blue-700'
            : 'text-gray-700 hover:bg-gray-50'
        )}
        style={{ paddingLeft: `${node.depth * 16 + 8}px` }}
      >
        {isFolder ? (
          <>
            {node.isExpanded ? (
              <ChevronDown className="h-3.5 w-3.5 shrink-0 text-gray-400" />
            ) : (
              <ChevronRight className="h-3.5 w-3.5 shrink-0 text-gray-400" />
            )}
            {node.isExpanded ? (
              <FolderOpen className="h-4 w-4 shrink-0 text-amber-500" />
            ) : (
              <Folder className="h-4 w-4 shrink-0 text-amber-500" />
            )}
          </>
        ) : (
          <>
            <span className="h-3.5 w-3.5 shrink-0" />
            {getFileIcon(node.name, node.path)}
          </>
        )}
        <span className="truncate">{node.name}</span>
      </button>

      {isFolder && node.isExpanded && node.children.length > 0 && (
        <div>
          {node.children.map((child) => (
            <FileTreeNode
              key={child.path}
              node={child}
              selectedPath={selectedPath}
              onSelect={onSelect}
              onToggle={onToggle}
            />
          ))}
        </div>
      )}
    </div>
  );
}

export function MarketSkillFileTree({
  nodes,
  selectedPath,
  loading,
  error,
  onSelect,
  onToggle,
  className,
}: MarketSkillFileTreeProps) {
  const t = useTranslations('files');

  if (loading) {
    return (
      <Card className={cn('h-full', className)}>
        <CardContent className="flex h-full items-center justify-center p-8">
          <p className="text-gray-500">{t('loading')}</p>
        </CardContent>
      </Card>
    );
  }

  if (error) {
    return (
      <Card className={cn('h-full', className)}>
        <CardContent className="flex h-full items-center justify-center p-8">
          <p className="text-red-500">{error}</p>
        </CardContent>
      </Card>
    );
  }

  return (
    <Card className={cn('flex h-full flex-col', className)}>
      <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-3">
        <CardTitle className="flex items-center gap-2 text-base font-semibold">
          <FolderTree className="h-5 w-5 text-gray-600" />
          {t('title')}
        </CardTitle>
      </CardHeader>
      <CardContent className="flex-1 overflow-auto py-2">
        {nodes.length === 0 ? (
          <div className="flex flex-col items-center justify-center py-8 text-center">
            <FolderTree className="h-12 w-12 text-gray-300" />
            <p className="mt-2 text-sm text-gray-500">{t('noFiles')}</p>
          </div>
        ) : (
          <div className="space-y-0.5">
            {nodes.map((node) => (
              <FileTreeNode
                key={node.path}
                node={node}
                selectedPath={selectedPath}
                onSelect={onSelect}
                onToggle={onToggle}
              />
            ))}
          </div>
        )}
      </CardContent>
    </Card>
  );
}
```

**Step 2: 创建市场技能查看器组件**

```tsx
// frontend/components/market/MarketSkillViewer.tsx
'use client';

import { useTranslations } from 'next-intl';
import { FileText, Menu } from 'lucide-react';
import { Button } from '@/components/ui/Button';
import { MarketSkillFileTree } from './MarketSkillFileTree';
import { useMarketFileTree } from '@/hooks/useMarketFileTree';
import { useBlobContent } from '@/hooks/useBlobContent';
import { MarkdownViewer } from '@/components/editors/MarkdownViewer';
import { TextViewer } from '@/components/editors/TextViewer';
import { getFileType } from '@/lib/file-utils';
import { ImagePreview } from '@/components/file-tree/ImagePreview';
import { PdfPreview } from '@/components/file-tree/PdfPreview';

interface MarketSkillViewerProps {
  sharedSkillId: string;
}

export function MarketSkillViewer({ sharedSkillId }: MarketSkillViewerProps) {
  const tEditor = useTranslations('editor');
  const { nodes, loading, error, selectedPath, selectedBlobId, toggleNode, selectNode } =
    useMarketFileTree({ sharedSkillId });

  const fileName = selectedPath.split('/').pop() || '';
  const fileType = fileName ? getFileType(fileName) : 'text';

  const renderPreview = () => {
    if (!selectedBlobId) {
      return (
        <div className="flex h-full flex-col items-center justify-center rounded-xl border-2 border-dashed border-gray-200 bg-white p-4">
          <div className="flex h-14 w-14 items-center justify-center rounded-full bg-gray-100">
            <FileText className="h-7 w-7 text-gray-400" />
          </div>
          <h3 className="mt-4 text-base font-medium text-gray-900">{tEditor('selectFile')}</h3>
          <p className="mt-1 max-w-xs text-center text-sm text-gray-500">
            {tEditor('selectFileDesc')}
          </p>
        </div>
      );
    }

    const blobUrl = `/market/skills/${sharedSkillId}/blobs/${selectedBlobId}`;

    switch (fileType) {
      case 'image':
        return <ImagePreview blobId={selectedBlobId} fileName={fileName} height="calc(100vh - 300px)" blobUrl={blobUrl} />;
      case 'pdf':
        return <PdfPreview blobId={selectedBlobId} fileName={fileName} height="calc(100vh - 300px)" blobUrl={blobUrl} />;
      case 'markdown':
        return (
          <MarkdownViewer
            blobId={selectedBlobId}
            filePath={selectedPath}
            fileName={fileName}
            height="calc(100vh - 300px)"
            blobUrl={blobUrl}
          />
        );
      case 'text':
      default:
        return (
          <TextViewer
            blobId={selectedBlobId}
            filePath={selectedPath}
            fileName={fileName}
            height="calc(100vh - 300px)"
            blobUrl={blobUrl}
          />
        );
    }
  };

  return (
    <div className="flex h-[600px] gap-4 mt-6">
      <div className="w-64 shrink-0">
        <MarketSkillFileTree
          nodes={nodes}
          selectedPath={selectedPath}
          loading={loading}
          error={error}
          onSelect={selectNode}
          onToggle={toggleNode}
        />
      </div>
      <div className="flex-1 overflow-hidden">
        {renderPreview()}
      </div>
    </div>
  );
}
```

**Step 3: 提交**

```bash
git add frontend/components/market/MarketSkillFileTree.tsx frontend/components/market/MarketSkillViewer.tsx
git commit -m "feat: add readonly market skill file tree and viewer components"
```

---

## Task 6: 前端 - 集成查看器到市场详情页

**Files:**
- Modify: `frontend/app/[locale]/market/[id]/page.tsx`

**Step 1: 查看现有详情页（确认已读取）**

已在之前读取过。

**Step 2: 在市场详情页中集成 MarketSkillViewer**

在现有的描述信息下方添加 `MarketSkillViewer` 组件，只在 `skill.status !== 'withdrawn'` 时显示。

在页面中添加：
```tsx
import { MarketSkillViewer } from '@/components/market/MarketSkillViewer';
```

在描述信息区域下方添加：
```tsx
{!isWithdrawn && (
  <MarketSkillViewer sharedSkillId={id} />
)}
```

**Step 3: 验证页面可构建**

```bash
cd frontend && npm run build
```

**Step 4: 提交**

```bash
git add frontend/app/[locale]/market/[id]/page.tsx
git commit -m "feat: integrate readonly file viewer into market skill detail page"
```

---

## Task 7: 前端 - 确保 blob 内容加载走 market 端点

**说明：** 现有的 `useBlobContent` hook 和 `MarkdownViewer`/`TextViewer` 组件通过 `/blobs/{blob_id}` 加载文件内容，需要确认它们是否支持自定义 blob URL，或者需要修改以支持 market blob 端点 (`/market/skills/{sharedSkillId}/blobs/{blobId}`)。

**Files:**
- 需要检查和可能修改:
  - `frontend/hooks/useBlobContent.ts`
  - `frontend/components/editors/MarkdownViewer.tsx`
  - `frontend/components/editors/TextViewer.tsx`
  - `frontend/components/file-tree/ImagePreview.tsx`
  - `frontend/components/file-tree/PdfPreview.tsx`

**Step 1: 检查 useBlobContent hook 和 viewer 组件是否支持自定义 blobUrl**

如果这些组件使用硬编码的 `/blobs/{blobId}` 路径，需要添加一个可选的 `blobUrl` prop 来覆盖默认路径。

**Step 2: 按需修改组件以支持 `blobUrl` prop**

对每个需要加载 blob 的组件添加可选的 `blobUrl` 参数。当提供 `blobUrl` 时用它加载内容，否则使用默认的 `/blobs/{blobId}`。

**Step 3: 运行前端测试**

```bash
cd frontend && bun test
```

**Step 4: 提交**

```bash
git add -A
git commit -m "feat: support custom blob URL in viewer components for market access"
```

---

## Task 8: 国际化 - 添加新增文案

**Files:**
- Modify: `frontend/i18n/locales/en.json`
- Modify: `frontend/i18n/locales/zh.json`

**Step 1: 检查是否需要新增翻译 key**

检查 Task 5/6 中使用的翻译 key 是否已存在。已有的 key 如 `files.title`、`files.noFiles`、`editor.selectFile`、`editor.selectFileDesc` 应该可以复用。

如果需要新增，在两个语言文件中添加对应的翻译。

**Step 2: 提交**

```bash
git add frontend/i18n/locales/en.json frontend/i18n/locales/zh.json
git commit -m "feat: add i18n keys for market skill viewer"
```

---

## Task 9: 全量测试和验证

**Step 1: 运行后端全量测试**

```bash
cd backend && python -m pytest -x -v
```

**Step 2: 运行后端代码质量检查**

```bash
cd backend && make lint && make type-check
```

**Step 3: 运行前端测试**

```bash
cd frontend && bun test
```

**Step 4: 运行前端构建**

```bash
cd frontend && npm run build
```

**Step 5: 运行前端 lint**

```bash
cd frontend && npm run lint
```

Expected: ALL PASS
