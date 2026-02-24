# Agent Skills Manager - 工作计划 (MVP)

> **目标**：构建一个 B/S 架构的系统，帮助用户集中管理、同步和分享自定义 Agent Skills
> **范围**：MVP 先实现 Skills 管理，Command 和 Agent 后续迭代
> **技术栈**：Next.js + Python FastAPI + PostgreSQL + Python 守护进程

---

## TL;DR

### 核心交付物

1. **Web 管理界面** - 创建、编辑、版本管理 Skills
2. **本地守护进程** - 自动同步、项目发现、文件监听
3. **云端 API 服务** - 存储、版本控制、实时推送
4. **用户系统** - 注册登录、个人 Skills 管理

### 关键特性

- ✅ 多文件 Skills 管理（SKILL.md + templates/ + examples/）
- ✅ 本地项目自动发现（扫描 + 监控）
- ✅ 双向实时同步（Web ↔ 本地）
- ✅ 版本历史（Git-like，可回滚）
- ✅ 支持 Claude Code 和 OpenCode
- ✅ 开源可自托管

### 执行策略

- **Wave 1** (Week 1-2): 基础设施（数据库、API、基础 Web）
- **Wave 2** (Week 2-3): 核心功能（Skills CRUD、文件存储）
- **Wave 3** (Week 3-4): 本地同步（守护进程、项目发现）
- **Wave 4** (Week 4):  polish（UI 优化、文档）

**预计工期**: 4 周
**并行度**: Wave 1→2→3 串行，Wave 4 与 3 部分并行

---

## Context

### 原始需求

用户希望解决以下痛点：

1. Skills 分散在 GitHub/本地，难以集中管理
2. 不同 Agent 平台目录不同（.claude/ vs .opencode/）
3. 跨项目需要手动复制粘贴
4. 个人 Skills 缺乏分享平台

### 相关文档

**设计文档**:

- 📐 UI/UX 设计规范: `.sisyphus/drafts/web-ui-design-spec.md`
  - 视觉风格（简约高阶，参考 Linear/Vercel）
  - 登录认证流程
  - 界面布局（响应式，暗色模式）
  - 交互细节和动画规范

**调研文档**:

- 🔍 市场调研: `.sisyphus/drafts/agent-skills-manager.md`
  - 痛点验证
  - 竞品分析
  - 技术架构讨论

### 调研结论

- **痛点真实存在**：已有 ccsync、claude-stacks、SkillMD.ai 等工具，但都只解决部分问题
- **市场空白**：缺少开源、自托管、多平台统一的解决方案
- **技术可行**：基于文件同步的架构清晰，有成熟模式可参考

### 技术栈版本要求（截至 2025-02-14）

```
后端：
- Python: 3.12+（最新稳定版，使用新类型注解语法）
- FastAPI: 0.129.0+（最新版，已移除 Python 3.9 支持，优化性能）
- Pydantic: 2.10+（V2 版本，性能大幅提升）
- SQLAlchemy: 2.0+（现代化 ORM，类型安全）
- PostgreSQL: 16+（最新版，JSONB 和性能优化）
- uvicorn: 0.34+（ASGI 服务器）

前端：
- Next.js: 15+（最新版，React Server Components）
- React: 19+（最新版，并发特性）
- TypeScript: 5.7+（最新版）
- Tailwind CSS: 4.0+（最新版）

本地守护进程：
- Python: 3.12+
- WebSocket-client: 1.8+
- watchdog: 6.0+（文件监控）
```

**FastAPI 0.129.0 更新说明**：

- ✅ 移除 Python 3.9 支持（最低要求 Python 3.10）
- ✅ 依赖包版本升级
- ✅ 文档改进
- ✅ 性能优化

### 架构决策

- **数据模型**：Skills 单独表（多文件、复杂版本控制），Command/Agent 后续再添加
- **存储策略**：云端 PostgreSQL + 本地文件缓存 + 符号链接到项目
- **同步机制**：WebSocket 实时推送 + 文件系统监听
- **安装方式**：命令行一键安装 + npm 包 + Homebrew

---

## Work Objectives

### Core Objective

构建一个可自托管的 Agent Skills 管理系统，让用户能够在 Web 界面集中管理 Skills，并自动同步到本地所有项目。

### Concrete Deliverables (MVP)

1. **数据库 Schema** - skills, versions, blobs, trees, projects, users 表
2. **FastAPI 后端** - REST API + WebSocket，完整的 Skills CRUD
3. **Next.js 前端** - Skills 编辑器、版本历史、项目管理界面
4. **Python 守护进程** - 项目扫描、文件监听、双向同步
5. **安装脚本** - 一键安装，支持 macOS/Linux
6. **使用文档** - 安装指南、快速开始、API 文档

### Definition of Done

- [ ] 用户可以在 Web 创建多文件 Skill
- [ ] 本地守护进程自动发现项目
- [ ] Web 关联 Skill 到项目后，本地自动同步
- [ ] 本地修改 Skill 后，Web 端能看到新版本
- [ ] 支持 Claude Code 和 OpenCode 两个平台
- [ ] 开源代码推送到 GitHub

### Must Have (MVP)

- Skills 多文件管理（目录结构）
- 版本历史（完整回滚）
- 本地项目自动发现
- 双向实时同步
- Claude Code 支持
- OpenCode 支持
- **用户注册登录**（邮箱 + 密码 + JWT，保留手机号字段用于后期扩展）

### Must NOT Have (MVP)

- Command 管理（Phase 2）
- Agent 管理（Phase 2）
- GitHub OAuth 登录（Phase 2）
- 手机号验证码登录（Phase 2）
- 团队/组织功能（Phase 3）
- 公开市场（Phase 3）
- Cursor/GitHub Copilot 支持（Phase 2）

---

## Verification Strategy

### 测试策略

**MVP 阶段不强制要求单元测试，但关键路径需要验证**：

- 文件上传/下载
- 版本创建/回滚
- 同步流程

**Agent-Executed QA Scenarios（主要验证方式）**

### 关键验证场景

**Scenario 1: 完整用户旅程**

```
Tool: Playwright + Bash
Preconditions: 后端运行，数据库已初始化

Steps:
  1. 访问 http://localhost:3000
  2. 注册新用户 (test@example.com / password123)
  3. 登录后进入 Skills 页面
  4. 点击 "创建 Skill"
  5. 输入名称 "test-skill"
  6. 在编辑器输入 SKILL.md 内容
  7. 点击 "保存"
  8. 验证：页面显示 Skill 列表包含 "test-skill"
  9. 验证：数据库 skills 表有记录

Expected: Skill 创建成功，数据正确存储
Evidence: 截图 .sisyphus/evidence/scenario-1-create-skill.png
```

**Scenario 2: 本地守护进程安装**

```
Tool: Bash
Preconditions: 干净的 macOS/Linux 环境

Steps:
  1. 运行安装脚本: curl -fsSL https://install.agent-skills.io | bash
  2. 验证：/usr/local/bin/agent-skills 存在
  3. 验证：~/.agent-skills/ 目录已创建
  4. 运行: agent-skills --version
  5. 验证：显示版本号

Expected: 安装成功，命令可用
Evidence: 终端输出保存
```

**Scenario 3: 项目发现和同步**

```
Tool: Bash + WebSocket 客户端
Preconditions: 守护进程运行，Web 服务运行

Steps:
  1. 在 ~/projects/ 创建测试项目: mkdir -p ~/projects/test-app/.claude
  2. 运行: agent-skills projects scan
  3. 验证：找到 test-app 项目
  4. 在 Web 界面关联 skill 到 test-app
  5. 验证：~/.agent-skills/cache/skills/{skill}/current/ 有文件
  6. 验证：~/projects/test-app/.claude/skills/{skill} 是符号链接
  7. 在 Web 修改 Skill 内容
  8. 验证：本地文件自动更新

Expected: 项目发现、关联、同步全部正常工作
Evidence: 文件列表截图
```

---

## Execution Strategy

### Wave 1: 基础设施 (Week 1-2)

**目标**: 搭建可运行的基础框架

| 任务                       | 依赖     | 并行 | Agent 建议 |
| -------------------------- | -------- | ---- | ---------- |
| 1.1 数据库 Schema 设计     | 无       | -    | quick      |
| 1.2 PostgreSQL 配置        | 1.1      | -    | quick      |
| 1.3 配置 Alembic Migration | 1.2      | -    | quick      |
| 1.4 FastAPI 项目骨架       | 无       | 1.1  | quick      |
| 1.5 基础模型和 CRUD        | 1.3, 1.4 | -    | quick      |
| 1.6 Next.js 项目初始化     | 无       | 1.4  | quick      |
| 1.7 基础 UI 组件           | 1.6      | -    | quick      |
| 1.8 用户认证 (JWT)         | 1.5      | -    | quick      |

### Wave 2: 核心功能 (Week 2-3)

**目标**: 实现 Skills 的完整管理

| 任务                     | 依赖     | 并行 | Agent 建议         |
| ------------------------ | -------- | ---- | ------------------ |
| 2.1 Skills 表和 API      | 1.4      | -    | quick              |
| 2.2 文件上传/存储 (Blob) | 2.1      | -    | quick              |
| 2.3 目录树存储 (Tree)    | 2.2      | -    | quick              |
| 2.4 版本历史系统         | 2.2, 2.3 | -    | quick              |
| 2.5 Web 文件树编辑器     | 1.6, 2.1 | -    | visual-engineering |
| 2.6 Markdown 编辑器      | 2.5      | -    | visual-engineering |
| 2.7 版本历史界面         | 2.4, 2.5 | -    | visual-engineering |

### Wave 3: 本地同步 (Week 3-4)

**目标**: 实现守护进程和同步机制

| 任务                 | 依赖     | 并行 | Agent 建议 |
| -------------------- | -------- | ---- | ---------- |
| 3.1 守护进程骨架     | 无       | -    | quick      |
| 3.2 项目扫描器       | 3.1      | -    | quick      |
| 3.3 WebSocket 客户端 | 3.1      | -    | quick      |
| 3.4 文件系统监听     | 3.1      | -    | quick      |
| 3.5 本地缓存管理     | 3.2, 3.4 | -    | quick      |
| 3.6 符号链接管理     | 3.5      | -    | quick      |
| 3.7 双向同步逻辑     | 3.3, 3.6 | -    | quick      |
| 3.8 安装脚本         | 3.1      | 3.7  | quick      |

### Wave 4: Polish (Week 4)

**目标**: 优化体验和完成文档

| 任务                  | 依赖     | 并行 | Agent 建议         |
| --------------------- | -------- | ---- | ------------------ |
| 4.1 UI 优化和响应式   | 2.7      | -    | visual-engineering |
| 4.2 错误处理和提示    | 3.7      | -    | quick              |
| 4.3 使用文档          | 全部     | -    | writing            |
| 4.4 API 文档          | 全部     | -    | writing            |
| 4.5 README 和开源准备 | 4.3, 4.4 | -    | writing            |

---

## TODOs

### Wave 1: 基础设施

#### [ ] 1.1 设计数据库 Schema

**What to do**:

- 设计 skills, versions, blobs, trees, projects, users 表
- 创建 ER 图
- 编写 migration 脚本

**References**:

- Draft: `.sisyphus/drafts/agent-skills-manager.md` - 存储部分

**Acceptance Criteria**:

- [ ] 所有表定义完整
- [ ] migration 脚本可运行
- [ ] 外键和索引正确

**Agent-Executed QA**:

```
Scenario: Database schema validation
  Tool: Bash
  Steps:
    1. Run: psql -f migrations/001_initial.sql
    2. Verify: \dt 显示所有表
    3. Verify: \d skills 显示正确结构
  Expected: 无错误，表结构正确
```

**Commit**: `feat(db): initial schema design`

---

#### [ ] 1.2 配置 PostgreSQL

**What to do**:

- Docker Compose 配置 PostgreSQL
- 配置连接池
- 环境变量管理

**Acceptance Criteria**:

- [ ] docker-compose up 启动成功
- [ ] 应用可连接数据库
- [ ] 连接池配置合理

**Agent-Executed QA**:

```
Scenario: Database connectivity
  Tool: Bash
  Steps:
    1. Run: docker-compose up -d postgres
    2. Run: python -c "from app.db import test_connection; test_connection()"
  Expected: 连接成功
```

---

#### [ ] 1.3 配置 Alembic Migration

**What to do**:

- 安装 alembic 和 asyncpg: `pip install alembic asyncpg`
- 初始化 Alembic: `alembic init alembic`
- 配置 `alembic.ini` (数据库 URL、脚本位置)
- 配置 `alembic/env.py` (适配异步 SQLAlchemy、导入模型)
- 创建 Base 和数据库连接配置
- 编写初始 migration 脚本

**配置要点**:

```python
# alembic/env.py 关键配置
from sqlalchemy.ext.asyncio import async_engine_from_config
from app.db.base import Base  # 导入所有模型基类
from app.models import user, skill  # 导入所有模型

target_metadata = Base.metadata

# 异步引擎配置
connectable = async_engine_from_config(
    config.get_section(config.config_ini_section, {}),
    prefix="sqlalchemy.",
    poolclass=pool.NullPool,
)
```

**项目结构**:

```
backend/
├── alembic/
│   ├── versions/          # 迁移脚本目录
│   ├── env.py             # Alembic 环境配置
│   └── alembic.ini        # 配置文件
├── app/
│   ├── db/
│   │   ├── base.py        # SQLAlchemy Base 和引擎
│   │   └── session.py     # 异步会话管理
│   └── models/            # 所有 ORM 模型
```

**常用命令**:

```bash
# 生成迁移脚本（自动检测模型变化）
alembic revision --autogenerate -m "create users table"

# 执行迁移
alembic upgrade head

# 查看当前版本
alembic current

# 回滚一个版本
alembic downgrade -1
```

**Acceptance Criteria**:

- [ ] `alembic init` 成功，目录结构正确
- [ ] `alembic revision --autogenerate` 能检测到模型变化
- [ ] `alembic upgrade head` 能成功创建所有表
- [ ] `alembic downgrade -1` 能成功回滚
- [ ] FastAPI 启动时能自动执行 migration（开发环境）

**Agent-Executed QA**:

```
Scenario: Alembic migration workflow
  Tool: Bash
  Steps:
    1. Run: alembic revision --autogenerate -m "initial schema"
    2. Verify: alembic/versions/ 目录有新生成的脚本
    3. Run: alembic upgrade head
    4. Verify: psql -c "\dt" 显示所有表已创建
    5. Run: alembic downgrade -1
    6. Verify: 表被正确删除或修改
    7. Run: alembic upgrade head
  Expected: 升级和回滚都正常工作
```

**Commit**: `chore(db): setup alembic migration`

---

#### [ ] 1.4 FastAPI 项目骨架

**What to do**:

- 创建 FastAPI 项目结构
- 配置依赖 (requirements.txt)
- 基础路由和中间件

**Project Structure**:

```
backend/
├── app/
│   ├── __init__.py
│   ├── main.py
│   ├── config.py
│   ├── db/
│   ├── models/
│   ├── routers/
│   └── services/
├── alembic/
├── tests/
├── requirements.txt
└── Dockerfile
```

**Acceptance Criteria**:

- [ ] 项目可启动
- [ ] /health 端点返回 200
- [ ] 目录结构清晰

**Agent-Executed QA**:

```
Scenario: API server startup
  Tool: Bash
  Steps:
    1. Run: pip install -r requirements.txt
    2. Run: uvicorn app.main:app --reload
    3. Run: curl http://localhost:8000/health
  Expected: {"status": "ok"}
```

---

#### [ ] 1.5 基础模型和 CRUD

**What to do**:

- SQLAlchemy 模型定义
- 基础 CRUD 操作
- Pydantic schemas

**Models**:

- User
- Skill (简化版，先支持单文件)
- Project

**Acceptance Criteria**:

- [ ] 所有模型可创建/读取/更新/删除
- [ ] 序列化正确
- [ ] 基础验证工作

---

#### [ ] 1.6 Next.js 项目初始化

**What to do**:

- 创建 Next.js 14+ 项目
- 配置 Tailwind CSS
- 配置 TypeScript
- 项目结构

**Project Structure**:

```
frontend/
├── app/
│   ├── layout.tsx
│   ├── page.tsx
│   ├── skills/
│   ├── login/
│   └── api/
├── components/
├── lib/
├── types/
├── package.json
└── next.config.js
```

**Acceptance Criteria**:

- [ ] 项目可启动
- [ ] 首页可访问
- [ ] TypeScript 无错误

---

#### [ ] 1.7 基础 UI 组件

**What to do**:

- 配置 shadcn/ui
- 创建基础组件 (Button, Input, Card, Dialog)
- 布局组件 (Header, Sidebar)

**Acceptance Criteria**:

- [ ] 组件可复用
- [ ] 样式一致
- [ ] 响应式基础

---

#### [ ] 1.8 用户认证 (JWT)

**What to do**:

- 用户模型（邮箱作为主账号，用户名默认使用邮箱前缀，预留手机号字段）
- 注册/登录 API（邮箱 + 密码）
- JWT token 生成和验证（access_token + refresh_token）
- 密码哈希（bcrypt）
- 前端登录/注册页面

**Database Schema**:

```sql
CREATE TABLE users (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    email VARCHAR(255) UNIQUE NOT NULL,        -- 主账号（登录用）
    username VARCHAR(255) UNIQUE,              -- 默认同邮箱前缀，可修改
    phone VARCHAR(20),                         -- 预留，后期用于手机号验证码登录
    password_hash VARCHAR(255) NOT NULL,
    is_active BOOLEAN DEFAULT true,
    email_verified BOOLEAN DEFAULT false,
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW()
);
```

**API Endpoints**:

- `POST /api/auth/register` - 邮箱注册
- `POST /api/auth/login` - 邮箱登录
- `POST /api/auth/refresh` - 刷新 token
- `GET /api/auth/me` - 获取当前用户信息

**Note**: MVP 只支持邮箱+密码登录，手机号仅保留字段不启用，GitHub OAuth 推迟到 Phase 2

**Acceptance Criteria**:

- [ ] 可注册新用户
- [ ] 可登录获取 token
- [ ] 受保护路由需要认证
- [ ] Token 可刷新

---

### Wave 2: 核心功能

#### [ ] 2.1 Skills 表和 API

**What to do**:

- 完整的 Skill 模型（支持多文件）
- REST API: POST/GET/PUT/DELETE /skills
- 查询和过滤

**Acceptance Criteria**:

- [ ] 可创建 Skill（带 metadata）
- [ ] 可列出用户的所有 Skills
- [ ] 可更新 Skill
- [ ] 可删除 Skill

---

#### [ ] 2.2 文件上传/存储 (Blob)

**What to do**:

- 文件上传端点
- 内容寻址存储（SHA-256）
- 压缩存储（zstd）
- 去重

**Acceptance Criteria**:

- [ ] 可上传文件
- [ ] 相同内容只存一份
- [ ] 可下载文件
- [ ] 压缩有效

---

#### [ ] 2.3 目录树存储 (Tree)

**What to do**:

- Tree 模型（Git-like）
- 从文件列表创建树
- 树序列化

**Acceptance Criteria**:

- [ ] 可创建树对象
- [ ] 可解析树结构
- [ ] 哈希计算正确

---

#### [ ] 2.4 版本历史系统

**What to do**:

- Version 模型
- 创建新版本逻辑
- 列出版本历史
- 获取特定版本

**Acceptance Criteria**:

- [ ] 修改 Skill 创建新版本
- [ ] 可列出所有版本
- [ ] 可获取历史版本内容
- [ ] 版本号递增正确

---

#### [ ] 2.5 Web 文件树编辑器

**What to do**:

- 文件树组件（可展开/折叠）
- 添加/删除/重命名文件
- 拖拽上传

**Acceptance Criteria**:

- [ ] 显示文件树结构
- [ ] 可添加新文件
- [ ] 可删除文件
- [ ] 可重命名文件

---

#### [ ] 2.6 Markdown 编辑器

**What to do**:

- 集成 Monaco Editor 或 CodeMirror
- Markdown 语法高亮
- 实时预览（可选）

**Acceptance Criteria**:

- [ ] 可编辑 Markdown
- [ ] 语法高亮正常
- [ ] 自动保存（防抖）

---

#### [ ] 2.7 版本历史界面

**What to do**:

- 版本列表（时间线）
- 版本对比（diff）
- 回滚功能

**Acceptance Criteria**:

- [ ] 显示版本历史
- [ ] 可对比两个版本
- [ ] 可回滚到历史版本

---

### Wave 3: 本地同步

#### [ ] 3.1 守护进程骨架

**What to do**:

- Python CLI 项目结构
- 基础命令（start, stop, status）
- 配置文件管理

**Project Structure**:

```
daemon/
├── agent_skills/
│   ├── __init__.py
│   ├── cli.py
│   ├── daemon.py
│   ├── config.py
│   └── sync/
├── setup.py
└── requirements.txt
```

**Acceptance Criteria**:

- [ ] 可安装: pip install -e .
- [ ] 命令行可用: agent-skills --help
- [ ] 配置文件正确创建

---

#### [ ] 3.2 项目扫描器

**What to do**:

- 扫描常见目录
- 检测项目类型（.git, package.json 等）
- 检测 AI Agent 平台（.claude, .opencode）

**Acceptance Criteria**:

- [ ] 找到本地项目
- [ ] 正确识别平台
- [ ] 结果保存到配置

---

#### [ ] 3.3 WebSocket 客户端

**What to do**:

- 连接到后端 WebSocket
- 心跳机制
- 重连逻辑

**Acceptance Criteria**:

- [ ] 成功连接
- [ ] 断线自动重连
- [ ] 可接收推送消息

---

#### [ ] 3.4 文件系统监听

**What to do**:

- watchdog 监听 ~/.agent-skills/
- 监听项目 skills 目录
- 变更检测

**Acceptance Criteria**:

- [ ] 检测到文件修改
- [ ] 检测到文件创建
- [ ] 检测到文件删除

---

#### [ ] 3.5 本地缓存管理

**What to do**:

- 下载 Skills 到本地缓存
- 目录结构管理
- 缓存清理

**Acceptance Criteria**:

- [ ] Skills 下载到 ~/.agent-skills/cache/
- [ ] 文件结构正确
- [ ] 可清理旧版本

---

#### [ ] 3.6 符号链接管理

**What to do**:

- 创建符号链接到项目
- 多平台路径适配
- 链接验证

**Acceptance Criteria**:

- [ ] 在项目目录创建链接
- [ ] 链接指向正确
- [ ] 支持 macOS/Linux

---

#### [ ] 3.7 双向同步逻辑

**What to do**:

- Web → 本地推送
- 本地 → Web 上报
- 冲突检测

**Acceptance Criteria**:

- [ ] Web 修改同步到本地
- [ ] 本地修改上报到 Web
- [ ] 检测到冲突

---

#### [ ] 3.8 安装脚本

**What to do**:

- 一键安装脚本
- LaunchAgent/Systemd 配置
- 版本检查

**Acceptance Criteria**:

- [ ] curl | bash 安装成功
- [ ] 守护进程自动启动
- [ ] 可更新版本

---

### Wave 4: Polish

#### [ ] 4.1 UI 优化和响应式

**What to do**:

- 移动端适配
- 加载状态
- 错误提示

---

#### [ ] 4.2 错误处理和提示

**What to do**:

- 全局错误边界
- 友好的错误消息
- 日志记录

---

#### [ ] 4.3 使用文档

**What to do**:

- 快速开始指南
- 用户手册
- 故障排查

---

#### [ ] 4.4 API 文档

**What to do**:

- OpenAPI/Swagger 文档
- 接口说明
- 示例代码

---

#### [ ] 4.5 README 和开源准备

**What to do**:

- 项目 README
- LICENSE
- CONTRIBUTING.md
- GitHub Actions CI

---

## Commit Strategy

| After Task | Message                                      | Files                     |
| ---------- | -------------------------------------------- | ------------------------- |
| 1.1        | `feat(db): design initial schema`          | docs/schema.md            |
| 1.2        | `chore(db): setup postgresql with docker`  | docker-compose.yml        |
| 1.3        | `chore(db): setup alembic migration`       | alembic/, app/db/         |
| 1.4        | `feat(api): fastapi project skeleton`      | backend/                  |
| 1.8        | `feat(auth): implement jwt authentication` | backend/app/auth/         |
| 2.1        | `feat(skills): implement skills crud api`  | backend/app/skills/       |
| 2.4        | `feat(skills): add version history system` | backend/app/versions/     |
| 3.1        | `feat(daemon): daemon skeleton and cli`    | daemon/                   |
| 3.7        | `feat(sync): implement bidirectional sync` | daemon/agent_skills/sync/ |

---

## Success Criteria

### Verification Commands

```bash
# 1. 启动服务
docker-compose up -d

# 2. 验证后端
curl http://localhost:8000/health
# Expected: {"status": "ok"}

# 3. 验证前端
curl http://localhost:3000
# Expected: HTML 页面

# 4. 测试完整流程
# - 注册登录
# - 创建 Skill
# - 关联到项目
# - 验证本地文件存在
ls -la ~/projects/test-app/.claude/skills/
# Expected: 符号链接指向 ~/.agent-skills/cache/
```

### Final Checklist

- [ ] 所有 TODO 完成
- [ ] QA Scenarios 通过
- [ ] 文档完整
- [ ] 代码推送到 GitHub
- [ ] README 有安装说明
- [ ] 可成功演示完整用户旅程

---

## Future Work (Phase 2+)

### Phase 2: Command & Agent Management

- Command 表和 API（单文件，简化存储）
- Agent 表和 API（单文件 + 配置）
- 统一的 Web 界面
- Cursor/GitHub Copilot 支持

### Phase 3: 三级共享体系

基于 MVP 架构扩展支持**个人 → 团队 → 全网**三级共享

#### Phase 3a: 团队/组织级别（2-3 周）

**目标**：实现组织内 Skills 共享

**数据库变更**：

```sql
-- 新增表
CREATE TABLE organizations (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    name VARCHAR(255) NOT NULL,
    slug VARCHAR(255) UNIQUE NOT NULL,
    description TEXT,
    owner_id UUID REFERENCES users(id),
    settings JSONB DEFAULT '{}',
    created_at TIMESTAMP DEFAULT NOW()
);

CREATE TABLE organization_members (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    organization_id UUID REFERENCES organizations(id),
    user_id UUID REFERENCES users(id),
    role VARCHAR(50) DEFAULT 'member',  -- owner, admin, member
    joined_at TIMESTAMP DEFAULT NOW(),
    UNIQUE(organization_id, user_id)
);

-- 扩展 skills 表
ALTER TABLE skills ADD COLUMN organization_id UUID REFERENCES organizations(id);

-- 更新唯一约束：支持个人和组织空间
ALTER TABLE skills DROP CONSTRAINT IF EXISTS skills_user_id_slug_key;
CREATE UNIQUE INDEX idx_skills_user_unique ON skills(user_id, slug) WHERE organization_id IS NULL;
CREATE UNIQUE INDEX idx_skills_org_unique ON skills(organization_id, slug) WHERE organization_id IS NOT NULL;
```

**功能清单**：

- [ ] 创建/管理组织
- [ ] 邀请成员（邮箱/链接）
- [ ] 角色管理（owner, admin, member）
- [ ] 组织 Skills 创建和编辑
- [ ] 成员自动同步组织 Skills 到本地
- [ ] 组织权限控制

**权限模型**：

```
组织级别权限：
- owner: 全部权限（删除组织、管理成员、管理 Skills）
- admin: 管理 Skills、邀请成员
- member: 使用 Skills、查看成员列表
```

#### Phase 3b: 全网级别（2-3 周）

**目标**：实现公开分享和市场发现

**数据库变更**：

```sql
-- 扩展现有表
ALTER TABLE skills ADD COLUMN visibility VARCHAR(50) DEFAULT 'private';
-- private, organization, public

ALTER TABLE skills ADD COLUMN status VARCHAR(50) DEFAULT 'draft';
-- draft, published, archived

ALTER TABLE skills ADD COLUMN metadata JSONB DEFAULT '{}';
-- {
--   "downloads": 1250,
--   "rating": 4.5,
--   "rating_count": 23,
--   "tags": ["react", "frontend"],
--   "license": "MIT"
-- }

-- 新增分类系统
CREATE TABLE skill_categories (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    name VARCHAR(255) NOT NULL,
    slug VARCHAR(255) UNIQUE NOT NULL,
    description TEXT,
    parent_id UUID REFERENCES skill_categories(id),
    sort_order INTEGER DEFAULT 0
);

CREATE TABLE skill_category_mappings (
    skill_id UUID REFERENCES skills(id),
    category_id UUID REFERENCES skill_categories(id),
    PRIMARY KEY(skill_id, category_id)
);

-- 统计和社交功能
CREATE TABLE skill_stats (
    skill_id UUID PRIMARY KEY REFERENCES skills(id),
    download_count INTEGER DEFAULT 0,
    view_count INTEGER DEFAULT 0,
    star_count INTEGER DEFAULT 0,
    last_downloaded_at TIMESTAMP,
    updated_at TIMESTAMP DEFAULT NOW()
);

CREATE TABLE skill_stars (
    user_id UUID REFERENCES users(id),
    skill_id UUID REFERENCES skills(id),
    created_at TIMESTAMP DEFAULT NOW(),
    PRIMARY KEY(user_id, skill_id)
);

-- 技能 Fork 记录（追溯来源）
CREATE TABLE skill_forks (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    source_skill_id UUID REFERENCES skills(id),  -- 原技能
    forked_skill_id UUID REFERENCES skills(id),  -- Fork 后的技能
    forked_by_user_id UUID REFERENCES users(id),
    forked_at TIMESTAMP DEFAULT NOW()
);
```

**功能清单**：

- [ ] Skills 发布流程（draft → published）
- [ ] 分类浏览（Frontend, Backend, DevOps 等）
- [ ] 搜索功能（全文检索）
- [ ] 热门/趋势排行榜
- [ ] 一键安装（Fork 到个人空间）
- [ ] Rating 和评论
- [ ] 下载统计

**发现算法**：

```python
# 热门算法（综合考虑下载、评分、时间）
def calculate_popularity(skill):
    downloads = skill.stats.download_count
    rating = skill.metadata.get('rating', 0)
    days_since_publish = (now() - skill.created_at).days
  
    # 时间衰减
    time_decay = 1 / (1 + days_since_publish / 30)  # 30天衰减
  
    # 评分加成
    rating_bonus = rating * 0.2 if rating else 0
  
    return (downloads * 0.7 + rating_bonus * downloads * 0.3) * time_decay
```

#### Phase 3c: 完整权限系统（可选）

**细粒度权限控制**：

```sql
CREATE TABLE skill_permissions (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    skill_id UUID REFERENCES skills(id),
    user_id UUID REFERENCES users(id),  -- null = 应用于所有用户
    organization_id UUID REFERENCES organizations(id),
  
    permission VARCHAR(50) NOT NULL,
    -- read, write, delete, sync, fork, share
  
    granted_by UUID REFERENCES users(id),
    granted_at TIMESTAMP DEFAULT NOW(),
    expires_at TIMESTAMP  -- null = 永久
);
```

**权限层级**：

```
权限继承链（从高到低）：
1. 显式权限（skill_permissions 表）
2. 角色权限（organization_members.role）
3. 可见性权限（visibility: public/organization/private）
4. 默认权限（owner 全部，其他只读）
```

### Phase 4: 高级功能

- **Skill 审核流程**：公开发布前审核
- **付费/订阅**：Skill 付费下载
- **CI/CD 集成**：GitHub Actions 自动发布
- **版本锁定**：项目锁定使用特定版本
- **离线模式**：完全离线使用本地缓存

### 扩展架构优势

当前架构为扩展提供了良好基础：

| 扩展点   | 当前支持               | 扩展难度  |
| -------- | ---------------------- | --------- |
| 组织功能 | `is_public` 字段预留 | ⭐ 低     |
| 市场发现 | 基础表结构已设计       | ⭐⭐ 中   |
| 权限系统 | 需要新增表             | ⭐⭐ 中   |
| 付费模式 | 需要支付集成           | ⭐⭐⭐ 高 |

**核心优势**：

- 文件同步机制无需改动
- 版本历史系统直接复用
- 本地守护进程无需大改
- 主要是数据层和 API 扩展

---

**计划创建完成** ✅
**下一步**: 运行 `/start-work` 开始执行

*Created by Prometheus on 2024-02-14*
