# 代码重构工作计划

## 目标

1. **业务逻辑抽取到 Service 层** - 路由只做 HTTP 处理
2. **Service 层统一事务管理** - 解决双重提交、批量操作无事务问题
3. **常量内聚到各自领域** - 不创建 constants.py
4. **CRUD 层支持可选提交** - 支持事务控制

---

## 文件变更概览

```
改动文件:
├── src/routers/skills.py           # 精简为 HTTP 处理
├── src/routers/trees.py            # 精简为 HTTP 处理
├── src/services/skill_service.py   # 完善业务逻辑
├── src/services/tree_service.py     # 完善业务逻辑
├── src/crud/base.py                # 支持可选提交
├── src/crud/skill.py               # 使用 commit=False
├── src/crud/tree.py                # 使用 commit=False
├── src/crud/blob.py                # 使用 commit=False
├── src/dependencies/auth.py        # 认证常量
└── src/schemas/                    # 分页常量

新增文件:
├── src/services/transactional.py    # @transactional 装饰器
```

---

## Phase 1: 完善 SkillService

### 目标
将 `routers/skills.py` 中的业务逻辑抽取到 `services/skill_service.py`

### 任务列表

#### 1.1 分析现有代码
- [x] 分析 `routers/skills.py` 中 `create_skill` 的完整业务逻辑
  - 验证 slug 格式
  - 检查 slug 是否已存在
  - 生成 SKILL.md 内容
  - 创建/复用 blob
  - 创建 tree
  - 创建 skill
  - 关联 tree_id
- [x] 分析 `routers/skills.py` 中其他端点的业务逻辑

#### 1.2 抽取 create_skill 到 SkillService
- [x] 在 `services/skill_service.py` 中完善 `create_skill` 方法
- [x] 添加事务管理（使用现有的 `self.transaction(db)`）
- [x] 确保单次提交（解决双重提交问题）

#### 1.3 抽取 update_skill 到 SkillService
- [x] 移动更新逻辑到 service 层
- [x] 处理 slug 冲突检查

#### 1.4 抽取 delete_skill 到 SkillService
- [x] 移动删除逻辑到 service 层
- [x] 处理 blob 引用清理
- [x] 处理 tree 级联删除

#### 1.5 抽取 import_skill 到 SkillService
- [x] 移动导入逻辑到 service 层

#### 1.6 精简 Router 层
- [x] 修改 `routers/skills.py` 改为调用 Service
- [x] 移除直接 CRUD 调用
- [x] 移除业务逻辑（验证、blob 创建等）
- [x] 只保留：参数解析 → 调用 Service → 格式化响应

### 验证标准
- [x] Router 中无直接 CRUD 调用（除了 get）
- [x] 所有写操作经过 Service 层
- [x] 事务在 Service 层统一管理
- [x] create_skill 只提交一次

---

## Phase 2: 完善 TreeService

### 目标
将 `routers/trees.py` 中的业务逻辑抽取到 `services/tree_service.py`，并修复批量操作无事务问题

### 任务列表

#### 2.1 分析现有代码
- [ ] 分析 `routers/trees.py` 中所有端点的业务逻辑
- [ ] 特别关注：batch_upload、upload_folder 的事务问题

#### 2.2 抽取批量操作（含事务修复）
- [ ] 抽取 `batch_upload_files` 到 TreeService
- [ ] **关键**：添加事务包装，解决当前无事务问题
- [ ] 修复异常吞噬问题（至少记录日志）

#### 2.3 抽取文件夹上传
- [ ] 抽取 `upload_folder` 到 TreeService
- [ ] 添加事务包装

#### 2.4 抽取文件操作
- [ ] 抽取 add_entry 到 TreeService
- [ ] 抽取 delete_entry 到 TreeService
- [ ] 抽取 rename_entry 到 TreeService
- [ ] 抽取 move_entry 到 TreeService
- [ ] 抽取 update_entry_content 到 TreeService

#### 2.5 精简 Router 层
- [ ] 修改 `routers/trees.py` 改为调用 Service
- [ ] 移除直接 CRUD 调用
- [ ] 移除业务逻辑

### 验证标准
- [ ] 批量操作有事务保护
- [ ] 异常不再静默吞噬
- [ ] Router 只做 HTTP 处理

---

## Phase 3: CRUD 层改造

### 目标
修改 CRUD 层支持可选提交，由 Service 层控制事务

### 任务列表

#### 3.1 修改 BaseCRUD
- [ ] 修改 `crud/base.py` 的 `create()` 方法
  - 添加 `commit: bool = True` 参数
  - 当 `commit=False` 时只 flush，不 commit
- [ ] 修改 `update()` 方法支持 `commit` 参数
- [ ] 修改 `delete()` 方法支持 `commit` 参数

#### 3.2 更新所有 CRUD 实例
- [ ] 更新 `crud/skill.py` 使用 `commit=False`
- [ ] 更新 `crud/tree.py` 使用 `commit=False`
- [ ] 更新 `crud/blob.py` 使用 `commit=False`
- [ ] 检查并更新其他 CRUD 文件

### 验证标准
- [ ] CRUD 不再自动提交（当传入 `commit=False`）
- [ ] 事务由 Service 层控制

---

## Phase 4: 事务管理优化

### 目标
统一事务模式，提供可选装饰器简化

### 任务列表

#### 4.1 验证事务正确性
- [ ] 运行所有 Journey 测试验证事务正确
- [ ] 运行所有 API 测试验证无回归

#### 4.2 创建 @transactional 装饰器
- [ ] 创建 `src/services/transactional.py`
- [ ] 实现装饰器（作为备选，不强制使用）
- [ ] 添加文档说明用法

#### 4.3 验证所有 Service 方法
- [ ] 检查所有 Service 方法事务使用正确
- [ ] 确保无嵌套事务问题

### 验证标准
- [ ] 无双重提交
- [ ] 批量操作原子性保证
- [ ] 所有测试通过

---

## Phase 5: 常量内聚

### 目标
移除魔法数字到各自领域

### 任务列表

#### 5.1 认证常量
- [ ] 将 `TOKEN_EXPIRE_MINUTES` 等移到 `src/dependencies/auth.py` 或 `src/core/auth.py`

#### 5.2 分页常量
- [ ] 将默认分页大小移到 `src/schemas/` 或相关 CRUD

#### 5.3 模型常量
- [ ] 将 `NAME_MAX_LENGTH`, `SLUG_MAX_LENGTH` 等移到 `src/models/skill.py`
- [ ] 检查其他模型的常量

#### 5.4 压缩相关常量
- [ ] 将 `ZSTD_COMPRESSION_LEVEL` 移到 `src/crud/blob.py`

### 验证标准
- [ ] 无魔法数字
- [ ] 常量在对应领域模块中

---

## 测试策略

### 重构期间
- 每完成一个任务，运行相关测试
- 确保无测试失败后再继续

### 测试命令
```bash
# 运行所有测试
pytest tests/ -v

# 运行 Journey 测试
pytest tests/integration/journey/ -v

# 运行 API 测试
pytest tests/integration/api/ -v

# 运行单个测试
pytest tests/integration/journey/test_journey_creation.py -v
```

---

## 风险控制

### 每次提交的小步骤
1. 先在 Service 层添加新方法（保留 Router 旧逻辑）
2. 修改 Router 调用新方法
3. 测试通过后，删除 Router 旧逻辑

### 回滚计划
- 如果测试失败，立即回滚
- 使用 git 保存中间状态

---

## 预期收益

| 改进前 | 改进后 |
|--------|--------|
| 业务逻辑分散在 Router 和 Service | 全部在 Service 层 |
| 批量操作无事务，数据可能不一致 | 事务统一管理，原子性保证 |
| Router 500+ 行，难以维护 | Router 精简到 ~150 行 |
| 魔法数字散落各处 | 常量内聚到领域 |
| CRUD 每次都提交 | 可控提交，事务由 Service 决定 |

---

## 时间估算

| Phase | 任务数 | 预计时间 |
|-------|--------|----------|
| Phase 1 | 6 | 2-3 小时 |
| Phase 2 | 5 | 2-3 小时 |
| Phase 3 | 2 | 1 小时 |
| Phase 4 | 3 | 1 小时 |
| Phase 5 | 4 | 1 小时 |
| **总计** | **20** | **8-10 小时** |
