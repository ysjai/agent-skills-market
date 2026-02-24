# 前端重构计划 - 渐进式

## 用户选择
- **策略**: 基础设施优先
- **提交粒度**: 极细粒度 (每个小改动单独提交)
- **测试**: 有部分测试 (api.test.ts, auth.test.ts)

## 阶段规划

### Phase 1: 基础设施层 (最安全，从工具函数开始)
1. 创建 `lib/errors.ts` - 统一错误处理
2. 创建 `components/ui/Toast.tsx` - 替换 alert()
3. 提取 Monaco 配置到 `lib/monaco-config.ts`
4. 统一日期格式化到 `lib/date-utils.ts`

### Phase 2: 类型安全
1. 安装 Monaco Editor 类型定义
2. 消除 `any` 类型
3. 启用 TypeScript strict 模式检查

### Phase 3: 大组件拆分 (需要测试护航)
1. FileTree.tsx 拆分
2. skills/page.tsx 拆分
3. skills/[id]/page.tsx 拆分

### Phase 4: 状态管理优化
1. 提取 Dialog 组件复用
2. 考虑引入状态管理库

## 待确认
- 每个阶段内部的具体任务顺序
- 是否需要补充测试
