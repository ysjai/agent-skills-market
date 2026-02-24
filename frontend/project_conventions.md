# Project Conventions

## 工程概述

基于 **Next.js 15 + React 19 + TypeScript 5** 构建的前端工程，采用 Feature-based 目录结构，已完成为期 4 Wave 的全面重构。

---

## 目录结构规范

```
├── app/                    # Next.js App Router
│   ├── [locale]/          # i18n 路由 (en/zh)
│   └── globals.css        # Tailwind v4 CSS-first 配置
├── components/            # React 组件 (Feature-based)
│   ├── ui/               # 基础 UI 组件 (Button, Card, Dialog 等)
│   ├── skills/           # Skill 功能组件
│   ├── file-tree/        # 文件树功能组件
│   ├── editors/          # 编辑器组件 (Markdown/Text)
│   ├── providers/        # Context Providers
│   └── misc/             # 杂项组件
├── lib/                   # 工具函数 (非 React)
│   ├── __tests__/        # 测试文件统一存放
│   ├── api.ts            # API 客户端
│   ├── errors.ts         # 统一错误处理
│   └── *.ts              # 工具函数
├── hooks/                 # React Hooks
│   ├── file-tree/        # 文件树相关 hooks (拆分后的)
│   └── *.ts              # 其他 hooks
├── stores/                # Zustand 全局状态
│   ├── index.ts          # Barrel export
│   ├── types.ts          # Store 类型定义
│   └── *Store.ts         # 具体 Store 实现
├── types/                 # TypeScript 类型
│   ├── index.ts          # Barrel export
│   └── *.ts              # 领域类型
├── i18n/                  # 国际化配置
│   ├── config/           # request.ts, routing.ts
│   └── locales/          # 翻译文件 (en.json, zh.json)
└── features/              # 可选: 大型功能模块
```

---

## 编码规范

### 1. 导入路径

**使用 `@/` 路径别名，禁止相对路径 (`../`)**

```typescript
// ✅ 正确
import { Button } from '@/components/ui/button';
import { api } from '@/lib/api';
import type { Skill } from '@/types';

// ❌ 错误
import { Button } from '../../../components/ui/button';
import { api } from '../lib/api';
```

### 2. 类型定义

**类型文件使用 `type` 导出，通过 barrel 文件集中暴露**

```typescript
// types/skill.ts
export interface Skill {
  id: string;
  name: string;
}

// types/index.ts - Barrel export
export type { Skill } from './skill';

// 使用时
import type { Skill } from '@/types';
```

### 3. 组件规范

**使用函数声明 + React.memo 优化**

```typescript
import { memo, useCallback } from 'react';

interface SkillCardProps {
  skill: Skill;
  onDelete: (id: string) => void;
}

// 函数声明更清晰
function SkillCard({ skill, onDelete }: SkillCardProps) {
  // 回调使用 useCallback
  const handleDelete = useCallback(() => {
    onDelete(skill.id);
  }, [onDelete, skill.id]);

  return <div>{skill.name}</div>;
}

// 默认导出使用 memo
export default memo(SkillCard);
```

### 4. Hook 规范

**单一职责，拆分到 feature 目录**

```typescript
// hooks/file-tree/useTreeState.ts - 专注状态管理
export function useTreeState() {
  const [nodes, setNodes] = useState<TreeNode[]>([]);
  return { nodes, setNodes };
}

// hooks/file-tree/index.ts - Barrel export
export { useTreeState } from './useTreeState';
export { useTreeOperations } from './useTreeOperations';

// 主 hook 组合使用
export function useFileTree() {
  const { nodes } = useTreeState();
  const { addNode } = useTreeOperations();
  return { nodes, addNode };
}
```

### 5. Store 规范 (Zustand)

**状态、派生数据、操作分离**

```typescript
// stores/skillsStore.ts
export const useSkillsStore = create<SkillsState>((set, get) => ({
  // 状态
  skills: [],
  searchQuery: '',
  
  // 操作
  setSearchQuery: (query) => set({ searchQuery: query }),
  
  // 派生数据 (通过 get() 访问)
  getFilteredSkills: () => {
    const { skills, searchQuery } = get();
    return skills.filter(s => 
      s.name.toLowerCase().includes(searchQuery.toLowerCase())
    );
  },
}));
```

### 6. 错误处理

**统一使用 `lib/errors.ts`**

```typescript
import { parseApiError } from '@/lib/errors';

try {
  await api.skills.create(data);
} catch (err) {
  // 统一错误解析
  const message = parseApiError(err);
  toast.error(message);
}
```

### 7. API 调用

**使用封装后的 api 客户端**

```typescript
import { api } from '@/lib/api';

// 直接使用封装好的方法
const skills = await api.skills.list();
const skill = await api.skills.get(id);
```

---

## 性能规范

### React.memo

列表项组件必须使用 `memo` 包裹

```typescript
export default memo(SkillCard);
```

### useMemo

过滤/转换逻辑必须使用 `useMemo`

```typescript
const filteredSkills = useMemo(() => {
  if (!searchQuery) return skills;
  return skills.filter(s => 
    s.name.toLowerCase().includes(searchQuery.toLowerCase())
  );
}, [skills, searchQuery]);
```

### useCallback

传递给子组件的回调必须使用 `useCallback`

```typescript
const handleDelete = useCallback((id: string) => {
  deleteSkill(id);
}, [deleteSkill]);
```

---

## 测试规范

```
lib/
├── __tests__/           # 测试文件统一放在这里
│   ├── auth.test.ts
│   └── file-utils.test.ts
├── auth.ts
└── file-utils.ts
```

- 测试文件与源码同目录时使用 `.test.ts` 后缀
- 测试文件集中存放时使用 `__tests__/` 目录
- 使用 Bun Test + @testing-library

---

## 质量门禁

所有代码变更必须通过以下检查：

```bash
# 类型检查
npx tsc --noEmit

# ESLint 检查
bun lint

# 单元测试
bun test

# 构建验证
bun build
```

---

## 禁止事项

| 禁止 | 替代方案 |
|------|----------|
| `any` 类型 | 明确定义类型或使用 `unknown` |
| 相对路径 `../` | `@/` 路径别名 |
| `console.log` | `console.warn/error` 或 logger |
| 重复的错误处理 | 统一使用 `lib/errors.ts` |
| 庞大的 hook (400+ 行) | 拆分到 feature 目录 |
| 跨目录导入 | 通过重构解决，不临时修复 |

---

## Tailwind v4 注意

- **不使用** `tailwind.config.ts` (已删除)
- 主题配置在 `app/globals.css` 中使用 `@theme` 指令
- 自定义颜色: `--color-*` 变量

---

*Last updated: 2025-02-19 (Post-Refactoring)*
