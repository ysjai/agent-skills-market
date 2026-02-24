---
agent: build
description: 继续执行指定计划的当前任务（断点续传）
---

**解析参数**：PLAN_NAME=$(echo "$ARGUMENTS" | awk '{print $1}')

如果 PLAN_NAME 为空，回复 "错误：请提供计划名称，如 /continue-plan prompt-share-implementation" 并退出。

**执行前检查**：

1. **Agent 检查**：如果当前不是 Atlas，执行 `/agents Atlas` 切换

2. **读取状态**：
   STATE_FILE=".sisyphus/plans/$PLAN_NAME/state.json"
   cat $STATE_FILE

3. **防重复执行检查**：
   - 如果 `execution.status` == "completed"，立即回复 "【系统】当前任务已标记完成，正在退出..." 并执行 `/exit`
   - 如果 `execution.status` == "running" 且进程存在，回复 "【系统】任务正在执行中..." 并 `/exit`

4. **声明执行**：
   读取 current.phase, current.wave, current.task，回复：
   "【Atlas 模式】计划: $PLAN_NAME | Phase $(jq -r '.current.phase' $STATE_FILE) | Wave $(jq -r '.current.wave' $STATE_FILE) | Task $(jq -r '.current.task' $STATE_FILE) | 开始执行..."

**执行流程**：

5. **加载策略**：
   - 读取 `.sisyphus/plans/$PLAN_NAME/00-execution-strategy.md`
   - 读取当前 Phase 文档（如 `0$(jq -r '.current.phase' $STATE_FILE)-phase-$(jq -r '.current.phase' $STATE_FILE)-*.md`）

6. **执行当前 Task**：
   - 严格按照 00-execution-strategy.md 的规则（TDD、审核等）
   - 完成代码编写和测试

7. **更新状态（原子操作）**：
   CURRENT_TASK=$(jq -r '.current.task' $STATE_FILE)
   CURRENT_WAVE=$(jq -r '.current.wave' $STATE_FILE)
   CURRENT_PHASE=$(jq -r '.current.phase' $STATE_FILE)
   
   更新 state.json（标记当前 task 完成，推进到下一个）：
   jq --arg task "$CURRENT_TASK" \
      --arg wave "$CURRENT_WAVE" \
      '.waves[$wave].completed_tasks += [$task] | 
       .version += 1 |
       .execution.status = "completed"' \
       $STATE_FILE &gt; ${STATE_FILE}.tmp && mv ${STATE_FILE}.tmp $STATE_FILE

8. **更新进度表**：
   更新 `schedule.md` 中对应 Task 的状态为 ✅，填写完成时间和 commit hash（先占位）

9. **Git 提交**：
   git add .
   git commit -m "feat: complete task $CURRENT_TASK [ci skip]"

10. **退出**：
    回复 "【Atlas】Task $CURRENT_TASK 完成，已提交，正在退出..." 并立即执行 `/exit`

**重要铁律**：
- 绝对禁止询问"接下来做什么"
- 必须更新 state.json 后才能 /exit
- 如果执行失败，将 execution.status 改为 "error" 后再 /exit