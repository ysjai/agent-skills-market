我现在有个思路，你帮我看看有可行不：
1. 我创建一个slash command，.opencode.commands/create-plan.md，当我跟Prometheus讨论好规划后，运行这个命令/create-plan
2. create-plan命令里是一些提示词，目的是让Prometheus把计划按照Phase拆成独立的文件，每个Phase下有多个Wave，每个Wave下有多个Task，比如这个计划 :prompt-share-implementation，如图所示，
  - schedule.md 是create-plan让Prometheus生成的计划进展跟踪记录表。
  - state.json 文件就是我们Mac本地这个bash要读取的状态依据
  - 00-execution-strategy.md 是固定存在的文件，它描述了一些项目执行规则，比如TDD和遵守项目规范，另外比较重要的规则是：每执行完Phase中的一个Wave都要跟新进度状态，要跟新 .sisyphus/plans/prompt-share-implementation/state.json，.sisyphus/plans/prompt-share-implementation/schedule.md。
4. 本地Bash就可以运行起来定时任务之后，每间隔10分钟去读 .sisyphus/plans/prompt-share-implementation/state.json，根据 execution status 来决定要不要bash执行唤起 opencode，唤起opencode要让opencode去检查计划名称为prompt-share-implementation，让它检查这个计划进行到哪里了，然后继续严格按照 .sisyphus/plans/prompt-share-implementation/00-execution-strategy.md 里的规则执行。
5. Bash 中运行 opencode run "检查计划名称为prompt-share-implementation，让它检查这个计划进行到哪里了，然后继续严格按照 .sisyphus/plans/prompt-share-implementation/00-execution-strategy.md 里的规则执行" 可以后台执行


这样子是不是就形成了闭环，至于怎么让LLM有效怎么有效检查计划进度，需要你给点建议。

另外有几个问题需要确认一下：
1. opencode run 执行完一个Wave后，会自动退出来么？会回回到Mac Terminal么？Bash运行的定时任务还会在持续工作么？

我现在已经写了create-plan.md和bash脚本execute-plan-interval.sh，你帮我看看可以达成目的么？
