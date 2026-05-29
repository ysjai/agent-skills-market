# Vercel + Render + Supabase 部署指南

本文档对应如下部署拓扑：

- 前端：Vercel
- 后端：Render Web Service
- 数据库：Supabase PostgreSQL
- CI/CD：GitHub Actions

## 目标效果

- 合并到 `main` 或 `master` 后：
  - 前端 workflow 自动部署到 Vercel Production
  - 后端 workflow 在检查通过后自动触发 Render Deploy Hook
- Pull Request 时：
  - 前端 workflow 自动创建 Vercel Preview 部署
- 数据库迁移：
  - Render 每次部署前自动执行 `alembic upgrade head`

## 仓库中已提供的部署文件

- `.github/workflows/frontend-ci.yml`
  - PR：构建并部署 Vercel Preview
  - Push 到 `main/master`：部署 Vercel Production
- `.github/workflows/backend-ci.yml`
  - 运行后端 lint/test/security
  - Push 到 `main/master` 且检查通过后触发 Render Deploy Hook
- `render.yaml`
  - Render Blueprint 配置
- `backend/src/core/config.py`
  - 支持从 `DATABASE_URL` 自动派生 `POSTGRES_*`
  - 支持 `ALLOWED_ORIGIN_REGEX`，用于放行 Vercel Preview 动态域名

## 一、Supabase 配置

### 1. 创建项目

1. 登录 Supabase
2. 创建一个新 Project
3. 记录以下信息：
   - Project URL
   - Database password
   - Project reference

### 2. 选择连接方式

对 Render 上的长生命周期 FastAPI 服务，优先推荐：

- `Session pooler` 连接串

原因：

- 比 direct connection 更适合 IPv4/IPv6 不确定的托管环境
- 比 transaction pooler 更适合 SQLAlchemy/asyncpg 这类长连接服务
- 避免 transaction mode 下 prepared statements 的兼容性问题

在 Supabase 控制台中：

1. 打开项目
2. 点击 `Connect`
3. 选择 `Session pooler`
4. 复制连接串

Supabase 给出的格式通常类似：

```text
postgres://postgres.<project-ref>:<password>@aws-0-<region>.pooler.supabase.com:5432/postgres
```

本项目后端使用 SQLAlchemy + `asyncpg`，所以需要改成：

```text
postgresql+asyncpg://postgres.<project-ref>:<password>@aws-0-<region>.pooler.supabase.com:5432/postgres?ssl=require
```

注意：

- 把协议头从 `postgres://` 改成 `postgresql+asyncpg://`
- 保留 `?ssl=require`
- 不要使用 transaction pooler 的 `6543` 端口作为当前 FastAPI 主连接

### 3. Supabase 里你至少需要保留的信息

- `DATABASE_URL`
- 数据库密码
- Project URL（仅当未来要接入 Supabase JS/Data API 时才需要）

当前这套部署中，GitHub Actions 不直接连接 Supabase，因此：

- 不需要在 GitHub Secrets 中存 Supabase URL
- 不需要在 GitHub Secrets 中存数据库密码
- 数据库连接串只需要配置在 Render 服务环境变量中

## 二、Render 配置

### 1. 创建 Web Service

推荐两种方式：

1. 直接在 Render Dashboard 里从 GitHub 导入仓库
2. 使用仓库根目录的 `render.yaml` 作为 Blueprint 导入

建议使用 Blueprint：

1. 登录 Render
2. 选择 `New +`
3. 选择 `Blueprint`
4. 连接你的 GitHub 仓库
5. 让 Render 读取仓库根目录 `render.yaml`

### 2. `render.yaml` 说明

当前仓库提供的关键配置：

- `rootDir: backend`
- `buildCommand: uv sync --frozen`
- `preDeployCommand: uv run alembic upgrade head`
- `startCommand: uv run uvicorn src.main:app --host 0.0.0.0 --port $PORT`
- `healthCheckPath: /health`
- `autoDeployTrigger: off`

这里把 Render 自动部署关掉，是为了避免与 GitHub Actions 的 Deploy Hook 重复触发。

### 3. Render 环境变量

在 Render 服务的 `Environment` 中配置：

#### 必填

```text
ENVIRONMENT=production
DATABASE_URL=postgresql+asyncpg://postgres.<project-ref>:<password>@aws-0-<region>.pooler.supabase.com:5432/postgres?ssl=require
SECRET_KEY=<长度至少 32 的随机字符串>
```

生成 `SECRET_KEY`：

```bash
openssl rand -hex 32
```

#### CORS 相关

正式域名放在 `ALLOWED_ORIGINS`，Vercel Preview 动态域名放在 `ALLOWED_ORIGIN_REGEX`。

示例：

```text
ALLOWED_ORIGINS=https://your-project.vercel.app,https://app.your-domain.com
ALLOWED_ORIGIN_REGEX=^https://.*\.vercel\.app$
```

说明：

- `ALLOWED_ORIGINS`：放正式生产域名和固定域名
- `ALLOWED_ORIGIN_REGEX`：用于放行 `https://*.vercel.app` 这种预览域名

如果你不需要 PR Preview 访问真实后端，也可以不配置 `ALLOWED_ORIGIN_REGEX`。

### 4. 获取 Deploy Hook

在 Render 服务创建完成后：

1. 打开服务页面
2. 进入 `Settings`
3. 找到 `Deploy Hook`
4. 复制 Deploy Hook URL

这个 URL 稍后要放入 GitHub Secret：`RENDER_DEPLOY_HOOK_URL`

## 三、Vercel 配置

### 1. 创建项目

1. 登录 Vercel
2. `Add New...` -> `Project`
3. 导入同一个 GitHub 仓库
4. Root Directory 选择：`frontend`

### 2. 建议关闭 Vercel 的 Git 自动部署

因为当前仓库已经通过 GitHub Actions 调用 Vercel CLI 部署。为了避免重复部署，建议：

1. 在 Vercel 项目设置中关闭 Git auto-deploy
2. 改由 GitHub Actions 统一触发 Preview / Production 部署

如果你保留 Vercel Git 自动部署，也能用，但会重复部署同一提交。

### 3. Vercel 环境变量

在 Vercel 项目的 `Settings` -> `Environment Variables` 中配置：

#### 必填

```text
NEXT_PUBLIC_API_URL=https://<your-render-service>.onrender.com/api
```

说明：

- 这里必须是浏览器可访问的完整后端地址
- 生产和 Preview 都可以先共用同一个 Render 后端地址
- 如果以后你有单独的 staging backend，再把 Preview 环境改指向 staging

### 4. 获取 Vercel CLI 需要的参数

在本地执行：

```bash
cd frontend
vercel login
vercel link
```

执行完成后，在 `frontend/.vercel/project.json` 中找到：

- `projectId`
- `orgId`

另外还需要：

- `VERCEL_TOKEN`

获取方法：

1. 打开 Vercel Account Settings
2. 创建 API Token

## 四、GitHub Actions Secrets 与 Variables

### 1. 必填 GitHub Secrets

在 GitHub 仓库中打开：

- `Settings` -> `Secrets and variables` -> `Actions`

添加以下 `Repository secrets`：

| 名称 | 是否必需 | 用途 |
| --- | --- | --- |
| `VERCEL_TOKEN` | 是 | GitHub Actions 调用 Vercel CLI 部署 |
| `VERCEL_ORG_ID` | 是 | Vercel CLI 识别组织/账号 |
| `VERCEL_PROJECT_ID` | 是 | Vercel CLI 识别前端项目 |
| `RENDER_DEPLOY_HOOK_URL` | 是 | GitHub Actions 触发 Render 部署 |

### 2. 当前不需要的 GitHub Secrets

当前这套部署里，下面这些不需要放进 GitHub Secrets：

- `DATABASE_URL`
- `SUPABASE_URL`
- `SUPABASE_ANON_KEY`
- `SECRET_KEY`

原因：

- 前端部署依赖 Vercel 项目自身环境变量
- 后端部署依赖 Render 服务自身环境变量
- GitHub Actions 只是触发部署，不直接持有生产数据库凭据

### 3. 可选 GitHub Variables

当前 workflow 不依赖 GitHub Variables，所以可以不配。

如果你后续想在 workflow summary 里显示服务名，可以再加：

- `RENDER_SERVICE_NAME`
- `VERCEL_PROJECT_NAME`

## 五、GitHub Actions 行为说明

### 1. 前端 workflow

文件：`.github/workflows/frontend-ci.yml`

会执行：

- 代码检查
- 测试
- 构建检查
- Pull Request 时部署 Vercel Preview
- Push 到 `main/master` 时部署 Vercel Production

说明：

- 来自 fork 的 PR 不会拿到仓库 secrets，因此 Preview 部署会自动跳过
- Preview 部署的环境变量来自 `vercel pull --environment=preview`
- Production 部署的环境变量来自 `vercel pull --environment=production`

### 2. 后端 workflow

文件：`.github/workflows/backend-ci.yml`

会执行：

- Ruff
- MyPy
- pytest + PostgreSQL service container
- safety / bandit
- Push 到 `main/master` 时触发 Render Deploy Hook

说明：

- 真正的数据库迁移发生在 Render 的 `preDeployCommand`
- GitHub Actions 不直接跑生产迁移

## 六、推荐配置顺序

建议按下面顺序完成：

1. 先创建 Supabase 项目并拿到 Session Pooler 连接串
2. 再创建 Render Web Service 并配置：
   - `DATABASE_URL`
   - `SECRET_KEY`
   - `ALLOWED_ORIGINS`
   - `ALLOWED_ORIGIN_REGEX`
3. 确认 Render 服务可访问：
   - `https://<your-render-service>.onrender.com/health`
   - `https://<your-render-service>.onrender.com/docs`
4. 创建 Vercel 项目并配置：
   - Root Directory = `frontend`
   - `NEXT_PUBLIC_API_URL`
5. 最后再把 Vercel 和 Render 所需的 GitHub Secrets 配到仓库里
6. 推送一次到 `main` 验证自动部署

## 七、一次性检查清单

### Supabase

- [ ] 已创建项目
- [ ] 已复制 Session Pooler 连接串
- [ ] 已把连接串改成 `postgresql+asyncpg://...?...ssl=require`

### Render

- [ ] 已创建 Web Service 或 Blueprint
- [ ] 已配置 `DATABASE_URL`
- [ ] 已配置 `SECRET_KEY`
- [ ] 已配置 `ALLOWED_ORIGINS`
- [ ] 已按需配置 `ALLOWED_ORIGIN_REGEX`
- [ ] 已复制 Deploy Hook URL

### Vercel

- [ ] 已创建前端项目
- [ ] Root Directory 已指向 `frontend`
- [ ] 已配置 `NEXT_PUBLIC_API_URL`
- [ ] 已拿到 `VERCEL_TOKEN`
- [ ] 已拿到 `VERCEL_ORG_ID`
- [ ] 已拿到 `VERCEL_PROJECT_ID`

### GitHub

- [ ] 已配置 `VERCEL_TOKEN`
- [ ] 已配置 `VERCEL_ORG_ID`
- [ ] 已配置 `VERCEL_PROJECT_ID`
- [ ] 已配置 `RENDER_DEPLOY_HOOK_URL`

## 八、常见问题

### 1. 为什么推荐 Supabase Session Pooler 而不是 Transaction Pooler？

因为当前后端是长期运行的 FastAPI + SQLAlchemy + asyncpg 服务，不是 serverless 函数。Transaction pooler 对 prepared statements 有兼容限制，不适合作为主运行连接。

### 2. 为什么 GitHub Actions 里不直接部署后端代码到 Render，而是只触发 Deploy Hook？

因为 Render 已经托管了你的构建与运行环境。GitHub Actions 最适合负责“通过检查后触发部署”，而不是重复接管 Render 的构建过程。

### 3. 为什么 Vercel Preview 可能访问不到后端？

通常是 CORS 没放行预览域名。解决方法：

- 固定域名放进 `ALLOWED_ORIGINS`
- 动态 `.vercel.app` 域名放进 `ALLOWED_ORIGIN_REGEX`

### 4. Render 上第一次部署失败，提示数据库认证或连接问题怎么办？

优先检查：

1. 连接串是否改成 `postgresql+asyncpg://`
2. 是否保留了 `?ssl=require`
3. 是否误用了 transaction pooler `6543`
4. 数据库密码是否正确

## 九、部署后验证

### 前端

- 打开 Vercel Production 域名
- 打开某个 PR 的 Preview 链接

### 后端

```bash
curl https://<your-render-service>.onrender.com/health
curl -I https://<your-render-service>.onrender.com/docs
```

### 前后端联调

在浏览器里确认：

- 登录接口正常
- 带 `Authorization` 头的请求不报 CORS
- Preview 域名访问 API 不报 CORS
