# FileTree.tsx 拆分计划

## 当前状态
- **FileTree.tsx**: 1166 行
- **FileTreeItem.tsx**: 已独立 (约 300 行)
- **目标**: 拆分后主组件 < 400 行

---

## 1. 识别的职责

### 1.1 工具函数 (纯函数，可复用)

| 函数 | 行号 | 职责 | 提取建议 |
|------|------|------|----------|
| `generateId()` | 34 | 生成唯一 ID | `lib/file-tree-utils.ts` |
| `normalizePath()` | 36-38 | 路径规范化 | `lib/file-tree-utils.ts` |
| `buildTree()` | 40-96 | 构建树结构 + 排序 | `lib/file-tree-utils.ts` |
| `sortNodes()` | 80-92 | 节点排序逻辑 | `lib/file-tree-utils.ts` |

### 1.2 状态管理

| 状态 | 行号 | 用途 |
|------|------|------|
| `nodes` | 105 | 树数据 |
| `selectedPath` | 108 | 选中路径 |
| `loading` | 106 | 加载状态 |
| `error` | 107 | 错误状态 |
| `dialogOpen/dialogType/dialogParentPath/dialogError` | 124-127 | 创建文件/文件夹对话框 |
| `conflictDialogOpen/conflictFileName/pendingUploadFiles/currentUploadIndex` | 129-132 | 上传冲突处理 |
| `deleteConfirmOpen/deleteTargetPath/deleteTargetName/isDeleting/deleteError` | 135-139 | 删除确认对话框 |
| `isDragging/dragSource/dragOverTarget` | 109-111 | 拖拽状态 |

### 1.3 LocalStorage 操作

| 函数 | 行号 | 职责 |
|------|------|------|
| `getExpandedStateKey()` | 141-143 | 获取展开状态存储 key |
| `getSelectedPathKey()` | 146-148 | 获取选中路径存储 key |
| `saveSelectedPath()` | 151-158 | 保存选中路径 |
| `loadSelectedPath()` | 161-168 | 加载选中路径 |
| `saveExpandedState()` | 171-189 | 保存展开状态 |
| `loadExpandedState()` | 192-204 | 加载展开状态 |
| `applyExpandedState()` | 207-218 | 应用展开状态到节点 |

### 1.4 树操作函数

| 函数 | 行号 | 职责 |
|------|------|------|
| `addNodeToTree()` | 404-461 | 添加节点到树 |
| `removeNodeFromTree()` | 463-493 | 从树中移除节点 |
| `updateNodePath()` | 495-519 | 更新节点路径 (重命名) |
| `checkNameExists()` | 521-532 | 检查名称是否已存在 |
| `findNodeByPath()` | 634-643 | 根据路径查找节点 |
| `findFirstFileInDirectory()` | 221-252 | 查找目录中第一个文件 |

### 1.5 API 操作

| 函数 | 行号 | 职责 |
|------|------|------|
| `fetchTree()` | 254-323 | 获取树数据 |
| `handleDialogConfirm()` | 541-584 | 创建文件/文件夹 |
| `handleRename()` | 594-631 | 重命名文件/文件夹 |
| `executeDelete()` | 654-684 | 删除文件/文件夹 |
| `handleMove()` | 686-720 | 移动文件/文件夹 |
| `processFileUpload()` | 776-858 | 处理文件上传 |
| `handleConflictResolution()` | 861-934 | 处理上传冲突 |
| `uploadBinaryFile()` | 760-773 | 上传二进制文件 |

### 1.6 事件处理

| 函数 | 行号 | 职责 |
|------|------|------|
| `handleToggle()` | 372-393 | 展开/折叠 |
| `handleSelect()` | 396-402 | 选中文件 |
| `handleAddFile()` | 586-588 | 添加文件 |
| `handleAddFolder()` | 590-592 | 添加文件夹 |
| `handleDelete()` | 645-652 | 删除操作 |
| `handleDragEnter/Leave/Over` | 724-742 | 拖拽事件 |
| `handleDrop()` | 937-951 | 拖放文件 |
| `handleFileInputChange()` | 954-965 | 文件输入变化 |

### 1.7 UI 渲染

- 主树渲染逻辑 (1080-1100)
- 工具栏 (1001-1039)
- 空状态 (1064-1078)
- 加载/错误状态 (1058-1062)
- 对话框 (1105-1142) - 已使用独立组件
- 内联冲突对话框 (1145-1163) - **可提取**

---

## 2. 可提取的独立函数/Hook

### 2.1 工具函数 (lib/file-tree-utils.ts)

```typescript
// 新文件: lib/file-tree-utils.ts
export const generateId = () => Math.random().toString(36).substring(2, 9);
export const normalizePath = (path: string): string => ...
export const buildTree = (entries: TreeEntry[]): FileTreeNode[] => ...
export const findNodeByPath = (nodes: FileTreeNode[], path: string): FileTreeNode | null => ...
export const findFirstFileInDirectory = (targetPath: string, nodes: FileTreeNode[]): ... => ...
export const applyExpandedState = (nodes: FileTreeNode[], expanded: string[]): FileTreeNode[] => ...
export const sortNodes = (nodes: FileTreeNode[]): void => ...
```

### 2.2 LocalStorage 工具 (lib/file-tree-storage.ts)

```typescript
// 新文件: lib/file-tree-storage.ts
export const getExpandedStateKey = (treeId?: string): string => ...
export const getSelectedPathKey = (treeId?: string): string => ...
export const saveSelectedPath = (path: string | undefined, key: string): void => ...
export const loadSelectedPath = (key: string): string | undefined => ...
export const saveExpandedState = (nodes: FileTreeNode[], key: string): void => ...
export const loadExpandedState = (key: string): string[] => ...
```

### 2.3 Tree Operations Hook (hooks/useFileTree.ts)

```typescript
// 新文件: hooks/useFileTree.ts
interface UseFileTreeOptions {
  treeId?: string;
  onFileSelect?: (path: string, blobId?: string) => void;
}

interface UseFileTreeReturn {
  // State
  nodes: FileTreeNode[];
  selectedPath: string | undefined;
  loading: boolean;
  error: string | null;
  // Actions
  fetchTree: () => Promise<void>;
  addNode: (entry: TreeEntry, autoSelect?: boolean) => void;
  removeNode: (path: string, isDirectory?: boolean) => void;
  updateNode: (oldPath: string, newPath: string, newBlobId?: string) => void;
  toggleNode: (nodeId: string) => void;
  selectNode: (path: string, blobId?: string) => void;
  // Ref
  ref: React.RefObject<FileTreeRef>;
}
```

### 2.4 Dialog Hook (hooks/useFileTreeDialogs.ts)

```typescript
// 新文件: hooks/useFileTreeDialogs.ts
interface UseFileTreeDialogsOptions {
  treeId?: string;
  nodes: FileTreeNode[];
  onAddNode: (entry: TreeEntry, autoSelect: boolean) => void;
  onRemoveNode: (path: string, isDirectory: boolean) => void;
  onUpdateNode: (oldPath: string, newPath: string, newBlobId?: string) => void;
  onSelectNode: (path: string, blobId?: string) => void;
  onFileSelect?: (path: string, blobId?: string) => void;
  onFileReload?: (path: string, blobId: string) => void;
}

interface UseFileTreeDialogsReturn {
  // Dialog states
  dialogOpen: boolean;
  dialogType: 'file' | 'folder';
  dialogParentPath: string;
  dialogError?: string;
  conflictDialogOpen: boolean;
  deleteConfirmOpen: boolean;
  // Actions
  openAddDialog: (type: 'file' | 'folder', parentPath: string) => void;
  handleDialogConfirm: (name: string) => Promise<void>;
  handleDelete: (path: string) => void;
  executeDelete: () => Promise<void>;
  handleRename: (oldPath: string, newPath: string) => Promise<boolean>;
  // Delete state
  deleteTargetPath: string;
  deleteTargetName: string;
  isDeleting: boolean;
  deleteError: string | null;
}
```

### 2.5 Upload Hook (hooks/useFileUpload.ts)

```typescript
// 新文件: hooks/useFileUpload.ts
interface UseFileUploadOptions {
  treeId?: string;
  nodes: FileTreeNode[];
  onUploadComplete: () => void;
}

interface UseFileUploadReturn {
  isDragging: boolean;
  pendingFiles: File[];
  currentIndex: number;
  // Actions
  handleDrop: (e: React.DragEvent) => Promise<void>;
  handleFileInputChange: (e: React.ChangeEvent<HTMLInputElement>) => Promise<void>;
  handleConflictResolution: (overwrite: boolean) => Promise<void>;
}
```

---

## 3. 建议的拆分文件

### 文件结构

```
frontend/
├── lib/
│   ├── file-tree-utils.ts      # [NEW] 树构建和查找工具
│   └── file-tree-storage.ts    # [NEW] LocalStorage 操作
├── hooks/
│   ├── useFileTree.ts         # [NEW] 树状态和操作
│   ├── useFileTreeDialogs.ts  # [NEW] 对话框逻辑
│   └── useFileUpload.ts       # [NEW] 上传逻辑
├── components/
│   └── FileTree/
│       ├── FileTree.tsx       # [MODIFIED] 主组件 ~350 行
│       ├── FileTreeItem.tsx   # [EXISTING]
│       └── ConflictDialog.tsx  # [NEW] 冲突对话框
```

### 拆分后行数估算

| 文件 | 行数 |
|------|------|
| `file-tree-utils.ts` | ~80 行 |
| `file-tree-storage.ts` | ~50 行 |
| `useFileTree.ts` | ~200 行 |
| `useFileTreeDialogs.ts` | ~200 行 |
| `useFileUpload.ts` | ~150 行 |
| `ConflictDialog.tsx` | ~30 行 |
| `FileTree.tsx` (最终) | ~350 行 |

---

## 4. 组件边界

### 4.1 FileTree.tsx 边界

```
Props Input:
├── treeId?: string
├── onFileSelect?: (path: string, blobId?: string) => void
├── className?: string
├── selectedFilePath?: string
├── onFileReload?: (path: string, blobId: string) => void
└── onFileDownload?: (path: string, blobId: string, fileName: string) => void

Public API (via ref):
├── updateBlobId(path, blobId)
└── selectFile(path, blobId)

Child Components:
├── FileTreeItem (已独立)
├── Card / CardHeader / CardContent
├── InputDialog (已独立)
├── ConfirmDialog (已独立)
└── ConflictDialog (待提取)
```

### 4.2 Hook 边界

```
useFileTree:
├── Input: treeId, onFileSelect
├── Output: nodes, selectedPath, loading, error, ref
└── Internal: LocalStorage, fetchTree, tree mutations

useFileTreeDialogs:
├── Input: treeId, nodes, mutation callbacks
├── Output: dialog states, action handlers
└── Internal: API calls for create/rename/delete

useFileUpload:
├── Input: treeId, nodes, onUploadComplete
├── Output: isDragging, pendingFiles, handlers
└── Internal: file processing, conflict detection
```

---

## 5. 实施顺序

### Phase 1: 提取工具函数
1. 创建 `lib/file-tree-utils.ts`
2. 迁移 `generateId`, `normalizePath`, `buildTree`, `findNodeByPath`, `findFirstFileInDirectory`, `applyExpandedState`

### Phase 2: 提取 Storage 工具
1. 创建 `lib/file-tree-storage.ts`
2. 迁移所有 LocalStorage 相关函数

### Phase 3: 提取 Hooks
1. 创建 `hooks/useFileTree.ts` - 核心状态管理
2. 创建 `hooks/useFileTreeDialogs.ts` - 对话框逻辑
3. 创建 `hooks/useFileUpload.ts` - 上传逻辑

### Phase 4: 提取 UI 组件
1. 创建 `components/FileTree/ConflictDialog.tsx`
2. 重构 `FileTree.tsx` 使用 hooks

### Phase 5: 清理
1. 移除重复代码
2. 简化类型导出
3. 更新 imports

---

## 6. 注意事项

### 不变原则
- ✅ 不改变用户交互行为
- ✅ 不改变 API 调用逻辑
- ✅ 不改变数据结构
- ✅ 保持所有回调函数签名一致

### 潜在风险
- ⚠️ Hooks 之间的状态同步需要仔细设计
- ⚠️ LocalStorage 错误处理需保持一致
- ⚠️ 冲突对话框的 z-index 和样式需匹配现有设计

### 测试策略
1. 拆分前确保现有测试通过
2. 每个新文件独立测试
3. 集成测试验证整体行为不变
