# 后端测试实施工作计划

## 📋 计划概览

**目标**: 实现95%测试覆盖率，补充缺失的Domain层、API边界和Journey测试
**预期工作量**: 4周（1人全职）
**关键约束**: 每步必须通过 Metis + Momus 双重审核

---

## 🎯 核心原则：严格的质量门禁

### 每步执行的强制检查点

```
┌─────────────────────────────────────────────────────────────┐
│ 执行步骤 → 测试通过 → Metis审核 → 修改 → Momus审核 → 修改 → 完成 │
└─────────────────────────────────────────────────────────────┘
```

**每个检查点的通过标准**:

#### 1. 测试执行检查

- ✅ 所有新增测试必须通过 (`pytest -xvs`)
- ✅ 无语法错误、无ImportError
- ✅ 无被注释掉的测试代码
- ✅ 测试运行时间合理（单测试<1秒，整个套件<30秒）

#### 2. Metis 审核（严格检查）

- ✅ 业务价值：此测试能发现真实bug吗？
- ✅ 断言有效性：断言足够且有意义吗？杜绝 `assert True`
- ✅ 无效断言检查：没有模糊断言（如 `assert result is not None`而无具体验证）
- ✅ 场景完整性：边界条件覆盖了吗？
- ✅ 代码质量：遵循项目代码规范了吗？

#### 3. Momus 终审（最终把关）

✅ 测试可维护性：代码清晰、可读吗？

- ✅ 无重复：没有复制粘贴的重复代码（使用fixtures/pytest.mark.parametrize）
- ✅ 文档完整：必要的注释说明了测试意图
- ✅ 无副作用：测试不会修改全局状态或留下脏数据
- ✅ 整体一致：与项目其他测试风格一致吗？

---

## 🌊 分波浪实施计划

### Wave 1: Domain层基础（Week 1）- P0最高优先级

#### 任务 1.1: Path Value Object 测试

**目标**: 实现路径遍历攻击防护测试
**文件**: `tests/unit/domain/value_objects/test_path.py`

**场景清单**（来自test-cases-domain.md 1.2节）:

- [X] 有效路径创建（7个场景 - ✅ 完成）
- [X] 无效路径验证（10个场景，含Metis新增的规范化后遍历 - ✅ 完成）
- [X] 路径操作（13个场景 - ✅ 完成）
- [X] 相等性比较（5个场景 - ✅ 完成）

**审核流程**:

1. ✅ 编写测试 → 本地运行通过（32个测试）
2. ✅ **Metis审核**: 发现2个关键遗漏（规范化后遍历、单点/双点）
3. ✅ 根据建议修改（新增3个测试）
4. ✅ **Momus审核**: 代码质量优秀，通过
5. ✅ 最终提交（35个测试全部通过）

**交付状态**: ✅ **已完成** | 测试数: 35 | 运行时间: 0.02s

---

#### 任务 1.2: Slug Value Object 测试 ✅ **已完成**

**目标**: 实现Slug验证规则测试
**文件**: `tests/unit/domain/value_objects/test_slug.py`

**场景清单**:

- [X] 有效Slug创建（4个通过场景 + 1个xfail已知缺陷）
- [X] 无效Slug验证（10个场景 - 含Metis新增的2个边界测试）
- [X] from_name工厂方法（7个场景 - 含Metis新增的1个边界测试）
- [X] 相等性比较（3个场景）

**审核流程**:

1. ✅ 编写测试 → 本地运行通过（23个测试）
2. ✅ **Metis审核**: 建议添加strict=True、2个边界测试，发现1个已知缺陷
3. ✅ 根据建议修改（新增2个测试）
4. ✅ **Momus审核**: 代码质量优秀，通过终审
5. ✅ 最终交付（25个测试，24通过 + 1 xfail）

**关键发现**: 测试发现Slug实现缺陷 - 大写转小写在验证之后进行，导致大写输入直接失败

---

#### 任务 1.3: Email Value Object 测试 ✅ **已完成**

**目标**: 实现邮箱验证测试
**文件**: `tests/unit/domain/value_objects/test_email.py`

**场景清单**:

- [X] 有效邮箱创建（7个场景 - 含空格修剪、大小写规范化）
- [X] 无效邮箱验证（10个场景 - 含Metis新增的domain无点号测试）
- [X] 邮箱解析（2个场景 - local_part/domain属性）
- [X] 相等性比较（5个场景）
- [X] 不可变性（2个场景）

**审核流程**:

1. ✅ 编写测试 → 本地运行通过（25个测试）
2. ✅ **Metis审核**: 建议小幅优化，补充1个边界测试
3. ✅ 根据建议修改（新增domain无点号测试）
4. ✅ **Momus审核**: 代码质量优秀，通过终审
5. ✅ 最终交付（26个测试全部通过）

**状态**: ✅ **已完成** | 测试数: 26 | 运行时间: 0.02s

---

#### 任务 1.4: Tree Aggregate 核心方法测试 ✅ **已完成**

**目标**: 实现文件树操作测试
**文件**: `tests/unit/domain/aggregates/test_tree.py`

**场景清单**:

- [X] Tree创建（2个场景）
- [X] add_entry（5个场景，包含重复路径冲突、blob_id验证）
- [X] delete_entry（4个场景，包含目录级联删除）
- [X] rename_entry（6个场景，包含目录重命名）
- [X] move_entry（4个场景 + 1个xfail已知bug）
- [X] update_entry_content（3个场景）
- [X] TreeEntry验证（5个场景）
- [X] 工具方法（4个场景）
- [X] 序列化（4个场景）

**审核流程**: 同上

**状态**: ✅ **已完成** | 测试数: 43 (42通过 + 1 xfail) | 运行时间: 0.04s

**关键发现**: 测试发现 `move_entry` 方法存在bug - 在修改条目后才检查冲突，无法正确检测目标路径已存在的情况

---

---

### Wave 2: API边界测试（Week 2）

#### 任务 2.1: 文件大小限制测试（用户明确要求）✅ **已完成**

**目标**: 实现10MB文件大小限制
**文件**:

- `backend/app/core/config.py` - 添加MAX_FILE_SIZE配置
- `backend/app/application/handlers/create_blob_handler.py` - 实现大小验证
- `tests/integration/api/test_blobs_boundary.py` - API边界测试

**场景清单**:

- [X] 上传10.1MB文件返回413
- [X] 上传9MB可压缩内容（压缩后<1MB）应该成功
- [X] 上传10MB文件刚好成功
- [X] PUT更新超大文件返回413
- [X] 验证压缩前检查大小
- [X] 刚好超过限制(10MB+1)测试
- [X] 刚好低于限制(10MB-1)测试

**实现要点**:

- MAX_FILE_SIZE = 10 * 1024 * 1024 (10MB)
- 在handler层验证（压缩前）
- 使用HTTP 413 Payload Too Large
- 测试使用mock数据（不实际传输大文件）

**状态**: ✅ **已完成** | 测试数: 7 | 运行时间: ~2s

---

#### 任务 2.2: 路径遍历攻击防护API测试 ✅ **已完成**

**目标**: 验证API层的路径安全
**文件**: `tests/integration/api/test_trees_security.py`

**场景清单**:

- [X] POST /api/trees/{id}/files 使用 `../../../etc/passwd`
- [X] PUT /api/trees/{id}/files/rename 使用遍历序列
- [X] PUT /api/trees/{id}/files/move 使用遍历序列
- [X] DELETE /api/trees/{id}/files 使用遍历序列
- [X] PUT /api/trees/{id}/files/content 使用遍历序列
- [X] 超长路径（>512字符）测试
- [X] 波浪号路径（~/.bashrc）测试

**状态**: ✅ **已完成** | 测试数: 16 | 运行时间: 4.11s

---

#### 任务 2.3: Token安全测试（用户明确要求）✅ **已完成**

**目标**: 实现Token撤销和轮换测试
**文件**:

- `tests/integration/journey/auth/test_token_security.py` (9个测试)
- `tests/integration/journey/auth/TOKEN_SECURITY_ROADMAP.md` (实现路线图)

**场景清单**:

- [X] 用户撤销会话后Token失效 (2 xfail - 功能待实现)
- [X] 密码修改后Token失效策略 (1 xfail - 功能待实现)
- [X] Refresh Token一次性使用 (2 xfail - 功能待实现)
- [X] 并发刷新竞态条件 (2 xpass + 验证)
- [X] 当前行为验证 (2 passed)

**关键发现**:

- Logout只是stub，无实际Token撤销
- 无密码修改API
- 无Token黑名单机制
- 无Refresh Token轮换

**状态**: ✅ **已完成** | 测试数: 9 (2p/5xf/2xp) | 运行时间: ~2.4s

---

### Wave 3: 数据一致性验证（Week 3）

#### 任务 3.1: Skill-Tree级联删除 ✅ **已完成**

**文件**: `tests/integration/journey/test_cascade_deletion.py`

**场景清单**:

- [X] 删除Skill后Tree被清理
- [X] 删除Skill后Blob引用计数减少
- [X] 多Skill共享Blob的引用计数准确性

**Metis审核重点**: 级联删除是否完整、引用计数是否准确

**状态**: ✅ **已完成** | 测试数: 3 | 运行时间: 1.22s

---

#### 任务 3.2: 并发安全测试 ✅ **已完成**

**文件**: `tests/unit/domain/concurrency/test_blob_concurrency.py`

**场景清单**:

- [X] 10个线程并发增加引用计数
- [X] 10个线程并发减少引用计数
- [X] 混合操作并发测试
- [X] 竞态条件文档化
- [X] 并发安全解决方案文档

**特别注意事项**:

- 并发测试容易flaky，需要确定性的同步机制
- Metis需仔细审查并发场景的有效性
- Momus需检查测试稳定性

**状态**: ✅ **已完成** | 测试数: 10 (3p/7xp) | 运行时间: 0.01s

**关键发现**:

- CPython GIL使简单操作(`+=`, `-=`)在当前版本下偶然线程安全
- 测试标记为xfail以文档化潜在风险
- 提供了三种并发安全解决方案文档

---

### Wave 4: 剩余API和Journey测试（Week 4）

#### 任务 4.1: 缺失API端点测试

**文件**:

- `tests/integration/api/test_skills_update.py` (PUT /api/skills/{id})
- `tests/integration/api/test_trees_batch.py` (POST batch/folder)
- `tests/integration/api/test_health.py` (GET /api/health)

#### 任务 4.2: 批量操作Journey测试

**文件**: `tests/integration/journey/test_batch_operations.py`

---

## 🔍 审核检查清单模板

### Metis 审核清单（每步必填）

```markdown
## Metis 审核报告 - [任务名称]

### 业务价值评估
- [ ] 每个测试都能发现真实bug吗？
- [ ] 有无效或冗余的测试吗？
- [ ] 边界条件覆盖充分吗？

### 断言有效性检查
- [ ] 无模糊断言（如`assert result is not None`）
- [ ] 断言具体且有业务意义
- [ ] 错误消息验证充分

### 场景完整性
- [ ] 正常场景 ✓
- [ ] 异常场景 ✓
- [ ] 边界场景 ✓

### 改进建议（如有）
1. [建议1]
2. [建议2]

### 审核结论
[ ] 通过  [ ] 需要修改
```

### Momus 审核清单（每步必填）

```markdown
## Momus 审核报告 - [任务名称]

### 代码质量
- [ ] 代码清晰可读
- [ ] 无重复代码（使用fixtures/parametrize）
- [ ] 遵循项目代码规范

### 可维护性
- [ ] 测试意图明确（注释或函数名）
- [ ] 测试数据构建清晰
- [ ] 无副作用（不修改全局状态）

### 稳定性
- [ ] 无flaky test风险
- [ ] 测试运行速度快
- [ ] 不依赖外部状态

### 改进建议（如有）
1. [建议1]
2. [建议2]

### 审核结论
[ ] 通过  [ ] 需要修改
```

---

## 📈 进度跟踪

### 每周交付物

**Week 1交付**: Domain层单元测试（Path/Slug/Email/Tree）

- 预期新增测试: ~50个
- 目标覆盖率提升: Domain层从0%到80%+

**Week 2交付**: API边界测试 + Token安全

- 预期新增测试: ~30个
- 包含用户明确要求的10MB限制和Token安全

**Week 3交付**: 数据一致性 + 并发安全

- 预期新增测试: ~25个
- 最复杂的部分，需要严格审核

**Week 4交付**: 剩余API + Journey测试

- 预期新增测试: ~35个
- 收尾和清理

### 质量指标

| 指标            | 目标 | 检查方式               |
| --------------- | ---- | ---------------------- |
| 测试通过率      | 100% | `pytest -x` 必须全过 |
| 代码覆盖率      | 95%  | `pytest --cov`       |
| Metis审核通过率 | 100% | 每步都需Metis签字      |
| Momus审核通过率 | 100% | 每步都需Momus签字      |
| 注释率          | <5%  | 代码自解释为主         |
| Flaky test      | 0    | 无不稳定测试           |

---

## ⚠️ 风险与应对

### 风险1: 并发测试不稳定

**应对**:

- 使用pytest-asyncio的确定性同步
- 避免使用sleep/wait
- Metis和Momus双重检查并发逻辑

### 风险2: 文件大小限制测试耗时

**应对**:

- 使用mock/fake文件，不实际传输
- 在CI中设置超时
- 大文件测试标记为slow，非CI必跑

### 风险3: 审核循环过多导致延期

**应对**:

- 每个任务最多2轮审核（Metis→修改→Momus→修改）
- 如仍有争议，由Prometheus仲裁
- 小修改可在下一轮顺带修复

---

## 🚀 快速启动命令

```bash
# 1. 安装依赖
pip install pytest pytest-asyncio pytest-cov factory-boy

# 2. 运行特定Wave测试
pytest tests/unit/domain/value_objects/ -xvs  # Wave 1
pytest tests/integration/api/test_blobs_boundary.py -xvs  # Wave 2

# 3. 检查覆盖率
pytest --cov=app.domain --cov-report=html

# 4. 运行所有测试
pytest -x --tb=short
```

---

## ✅ 开始执行

执行此计划:

```bash
/start-work backend-test-implementation
```

Sisyphus将按照此计划逐步执行，每步都会：

1. 实现测试
2. 确保全部通过
3. 提交Metis审核
4. 根据建议修改
5. 提交Momus审核
6. 根据建议修改
7. 标记完成，进入下一步

全部步骤完成了，要检查测试覆盖率是否达到95%，如果没达到，务必继续严格执行：

1. 分析需要补充的测试场景
2. 让Metis和Momus审核，有建议就改，没问题就补充到test case文档中
3. 继续循环执行：
   * 实现测试
   * 确保测试全部通过，并提交Metis审核（关注命名规范、场景有效性、断言是否有效和足够、是否有没必要的注释）
   * 根据Metis建议修改测试
   * 确保测试全部通过，并提交Momus审核（关注命名规范、场景有效性、断言是否有效和足够、是否有没必要的注释）
   * 根据Momus建议修改测试
   * 确保测试全部通过
4. 检查测试覆盖率，如果没达到95%就严格继续 1~4 步的循环

---

**计划版本**: 1.0
**审核机制**: Metis + Momus 双重门禁
**生成时间**: 2026-02-20
**预期完成**: 4周后（约2026-03-20）
