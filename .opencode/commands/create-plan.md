---
agent: build
description: 创建新的 Sisyphus 执行计划，按 Phase/Wave 拆分
---

接收参数: $ARGUMENTS
PLAN_NAME=$(echo "$ARGUMENTS" | awk '{print $1}')

如果 PLAN_NAME 为空，回复 "错误：请提供计划名称，如 /create-plan my-project" 并退出。

**执行步骤**：

**1. 创建目录结构**
mkdir -p .sisyphus/plans/$PLAN_NAME

**2. 创建 state.json**
创建 `.sisyphus/plans/$PLAN_NAME/state.json`：

{
  "plan_id": "prompt-share-implementation",
  "version": 1,
  "current": {
    "phase": 1,
    "wave": "1.1"
  },
  "execution": {
    "status": "idle",
    "agent": "Atlas",
    "started_at": null,
    "pid": null
  },
  "completed_waves": ["0.0"],
  "stats": {
    "total_waves": 8,
    "completed_count": 0
  }
}

**3. 创建 schedule.md**
创建 `.sisyphus/plans/$PLAN_NAME/schedule.md`：

# $PLAN_NAME 执行进度表

&gt; 最后更新: $(date)

## 当前执行
- **Phase**: 1
- **Wave**: 1.1
- **状态**: 🟡 待开始

## 已完成 Waves
*暂无*

## 统计
- 完成: 0/0 Waves (0%)

**4. 创建 00-execution-strategy.md**
创建 `.sisyphus/plans/$PLAN_NAME/00-execution-strategy.md`：

# $PLAN_NAME - 执行策略

## 架构
Plan: $PLAN_NAME
├── Phase 1 (Foundation)
│   ├── Wave 1.1 - [待定义]
│   └── Wave 1.2 - [待定义]
└── Phase 2 (Domain)
    └── Wave 2.1 - [待定义]

## 执行规则（铁律）

### 1. Wave 原子性
- **Wave 是执行的最小单位**，每个 Wave 包含若干 Tasks
- Atlas 每次唤起执行**整个 Wave**（所有 Tasks），不是单个 Task
- Wave 必须全部完成才能标记为 completed

### 2. TDD 流程
每个 Wave 内的 Tasks 必须遵循：
1. 编写/更新测试
2. 运行测试（应失败）
3. 实现功能
4. 运行测试（应通过）
5. Metis 审核（命名、测试质量）
6. Momus 审核（代码质量、边界条件）
7. 标记 Task 完成

### 3. Wave 完成协议
当 Wave 内所有 Tasks 完成后：
1. 运行全量测试：`bun test` 或 `pytest`
2. 检查覆盖率（如果 Phase &gt;= 6）
3. 更新 `state.json`：
   - `completed_waves` 添加当前 wave
   - `execution.status` = "completed"
   - `version` + 1
4. 更新 `schedule.md`：标记 Wave 完成时间和 Git Commit
5. Git 提交：`git add . && git commit -m "feat: complete wave X.Y"`
6. **立即执行 `/exit`**（禁止继续执行下一个 Wave）

### 4. 状态管理
- Atlas **不负责推进 Wave**，只负责执行当前 Wave 并标记 completed
- Bash 脚本检测到 completed 后，自动推进 `current.wave` 并重置为 idle
- 如果执行失败，设置 `execution.status` = "error" 后 `/exit`

### 5. 禁止事项
- 禁止询问"接下来做什么"
- 禁止跨 Wave 执行（即使看到下一个 Wave 的文档）
- 禁止在没有 git commit 的情况下标记 Wave 完成

**5. 创建 Phase 模板文件**
创建 `.sisyphus/plans/$PLAN_NAME/01-phase-1-foundation.md`：

# Phase 1: Foundation

## 目标
[描述本 Phase 的目标]

## Wave 1.1: [Wave 名称]

### Tasks
1. **Task 1**: [描述]
   - 验收标准: [标准]
   - 测试要求: [要求]

2. **Task 2**: [描述]
   - 验收标准: [标准]

### 完成标准
- [ ] 所有 Tasks 完成并通过测试
- [ ] Metis 审核通过
- [ ] Momus 审核通过
- [ ] Git commit: "feat: complete wave 1.1"

## Wave 1.2: [Wave 名称]
...

[继续创建 02-phase-2-domain.md 等，根据讨论的规划]

**6. 更新 state.json 的 total_waves**
根据创建的 Phase 文件，统计总 Wave 数量，更新到 `stats.total_waves`。

**7. 完成确认**
回复：
"计划 $PLAN_NAME 已创建：

📁 目录结构：
.sisyphus/plans/$PLAN_NAME/
├── state.json          # 执行状态（当前: Phase 1, Wave 1.1）
├── schedule.md         # 进度跟踪
├── 00-execution-strategy.md  # 执行规则
├── 01-phase-1-foundation.md  # Phase 1 详情
└── [其他 Phase 文件]

🚀 下一步：
1. 填充各 Phase 文件中的具体 Tasks
2. 运行 Bash 脚本开始执行：
   ./sisyphus-daemon.sh $PLAN_NAME
3. 或手动唤起 Atlas：
   /continue-plan $PLAN_NAME"