# Vercel + Render + Supabase 部署操作手册

这篇文档不是概念说明，而是给你直接照着做的。

你的目标是把这个项目部署成下面这样：

- 前端：Vercel
- 后端：Render Web Service
- 数据库：Supabase PostgreSQL
- 自动部署：GitHub Actions

如果你只想知道最短路径，可以先看下面这 7 步：

1. 在 Supabase 拿到可用的 `DATABASE_URL`
2. 在 Render 创建后端服务，并填好环境变量
3. 在 Render 拿到两个东西：服务 URL 和 Deploy Hook URL
4. 在 Vercel 创建前端项目，并把前端根目录指到 `frontend`
5. 在 Vercel 配置 `NEXT_PUBLIC_API_URL`
6. 在 GitHub 配 4 个 Secrets
7. 推送一次 `main`，看 GitHub Actions 自动部署

下面是详细步骤。

## 0. 这份仓库里已经准备好的东西

你不用再自己写部署脚本，仓库里已经有这些文件：

- `.github/workflows/frontend-ci.yml`
  - PR 时自动部署到 Vercel Preview
  - `main/master` push 时自动部署到 Vercel Production
- `.github/workflows/backend-ci.yml`
  - 后端检查通过后自动触发 Render 部署
- `render.yaml`
  - Render Blueprint 配置

你现在要做的不是改代码，而是把三个平台的项目和环境变量配好。

## 1. 先准备你最终会拿到的 7 个值

在整套配置完成前，你最终需要手上有这 7 个值：

1. `DATABASE_URL`
2. `SECRET_KEY`
3. `RENDER_SERVICE_URL`
4. `RENDER_DEPLOY_HOOK_URL`
5. `VERCEL_PROJECT_ID`
6. `VERCEL_ORG_ID`
7. `VERCEL_TOKEN`

其中：

- `DATABASE_URL` 来自 Supabase
- `SECRET_KEY` 你自己生成
- `RENDER_SERVICE_URL` 和 `RENDER_DEPLOY_HOOK_URL` 来自 Render
- `VERCEL_PROJECT_ID`、`VERCEL_ORG_ID`、`VERCEL_TOKEN` 来自 Vercel

## 2. 先做 Supabase

这一部分结束后，你应该拿到一个最终可用的 `DATABASE_URL`。

### 2.1 在 Supabase 里做什么

1. 登录 Supabase
2. 创建一个 Project
3. 打开这个 Project
4. 点击顶部的 `Connect`
5. 在连接方式里选择 `Session pooler`
6. 复制连接串

为什么选 `Session pooler`：

- 你的后端是长期运行的 FastAPI 服务
- 它比 `transaction pooler` 更适合当前这种 Web Service
- 不建议这里用 `6543` 的 transaction pooler

### 2.2 你需要把 Supabase 给的连接串改成项目可用格式

Supabase 通常会给你类似这种：

```text
postgresql://postgres.<project-ref>:<password>@aws-0-<region>.pooler.supabase.com:5432/postgres
```

但当前项目后端用的是 `SQLAlchemy + asyncpg`，所以你最后填到 Render 的 `DATABASE_URL` 必须长这样：

```text
postgresql+asyncpg://postgres.<project-ref>:<password>@aws-0-<region>.pooler.supabase.com:5432/postgres?ssl=require
```

你需要做 2 个改动：

1. 协议头从 `postgresql://` 改成 `postgresql+asyncpg://`
2. 最后加上 `?ssl=require`

### 2.3 如果密码里有特殊字符，先做 URL 编码

如果数据库密码里包含这些字符，必须编码：

- `@`
- `:`
- `/`
- `?`
- `#`
- `%`

例如密码是：

```text
Pass@word
```

那么应该编码成：

```text
Pass%40word
```

本地终端执行：

```bash
python3 -c "import urllib.parse; print(urllib.parse.quote('你的数据库密码', safe=''))"
```

例如：

```bash
python3 -c "import urllib.parse; print(urllib.parse.quote('Pass@word', safe=''))"
```

### 2.4 这一部分结束时，你应该得到什么

你最终应该手工整理出一个完整的 `DATABASE_URL`，格式如下：

```text
postgresql+asyncpg://postgres.<project-ref>:<编码后的密码>@aws-0-<region>.pooler.supabase.com:5432/postgres?ssl=require
```

不要把密码分开存，不要写变量拼接，最终就保留这一整串。

## 3. 再做 Render 后端

这一部分结束后，你应该拿到：

- `RENDER_SERVICE_URL`
- `RENDER_DEPLOY_HOOK_URL`

### 3.1 在 Render 创建后端服务

你有两种方式：

1. 用仓库里的 `render.yaml` 自动创建
2. 在 Render 页面手动创建 Web Service

如果你现在已经在手动创建页面里了，就直接看下面的 `3.2 Render 手动创建页面怎么填`。

### 3.1.1 方式 A：使用 `render.yaml`

操作：

1. 登录 Render
2. 点击 `New +`
3. 选择 `Blueprint`
4. 连接你的 GitHub 仓库
5. 让 Render 读取仓库根目录的 `render.yaml`
6. 创建服务

为什么用 Blueprint：

- 仓库里已经写好了后端启动方式
- 不需要你手工填 build/start command
- 后续配置更容易和仓库保持一致

### 3.2 Render 手动创建页面怎么填

如果你是在 Render 的 `New Web Service` 页面手动创建，按下面填。

#### 基础字段

- `Name`
  - 建议填：
  ```text
  agent-skills-market-web-service
  ```
- `Region`
  - 建议选离 Supabase 更近的区域
  - 你现在的 Supabase 是东京区，建议优先选：
  ```text
  Singapore
  ```
  说明：Render 目前通常没有东京区可选，亚洲里优先新加坡。
- `Branch`
  - 填你的主分支：
  ```text
  main
  ```
- `Root Directory`
  - 必须填：
  ```text
  backend
  ```
- `Runtime`
  - 选择：
  ```text
  Python
  ```

#### 你截图里的两个字段

- `Build Command`
  ```bash
  uv sync --frozen
  ```

- `Start Command`
  ```bash
  uv run alembic upgrade head && uv run uvicorn src.main:app --host 0.0.0.0 --port $PORT
  ```

说明：

- 你当前页面没看到 `Pre-Deploy Command`，这通常是因为当前服务计划不支持单独的 pre-deploy 配置
- 所以这里把数据库迁移直接并到 `Start Command` 里
- `alembic upgrade head` 如果数据库已经是最新，一般会安全跳过

#### 其他建议字段

- `Instance Type`
  - 先选：
  ```text
  Free
  ```
  如果你后面需要更稳定的休眠唤醒体验，再升级。
- `Auto-Deploy`
  - 建议选：
  ```text
  Off
  ```
  因为这个仓库已经通过 GitHub Actions + Deploy Hook 来部署，避免重复部署。
- `Health Check Path`
  - 填：
  ```text
  /health
  ```

### 3.3 Render 上要填写哪些环境变量

进入你的 Render 服务：

1. 打开服务详情页
2. 找到 `Environment`
3. 添加下面这些变量

#### 必填变量

```text
PYTHON_VERSION=3.12.11
ENVIRONMENT=production
DATABASE_URL=<你在第 2 步整理好的完整连接串>
SECRET_KEY=<你自己生成的一串随机值>
ALLOWED_ORIGINS=https://你的-vercel-正式域名.vercel.app
ALLOWED_ORIGIN_REGEX=^https://.*\.vercel\.app$
```

### 3.4 `SECRET_KEY` 怎么生成

就在你本地机器终端里执行：

```bash
openssl rand -hex 32
```

或者：

```bash
python3 -c "import secrets; print(secrets.token_hex(32))"
```

把输出整串复制到 Render 的 `SECRET_KEY`。

### 3.4.1 `PYTHON_VERSION` 为什么也要填

如果你是手动创建 Render Web Service，而不是通过 `render.yaml` 导入，建议显式加上：

```text
PYTHON_VERSION=3.12.11
```

原因：

- Render 新服务默认可能用到 Python 3.14
- 当前项目我们已经统一到 Python 3.12+
- 手动固定版本可以避免运行时和本地、CI 不一致

### 3.5 `ALLOWED_ORIGINS` 和 `ALLOWED_ORIGIN_REGEX` 怎么填

这是给 CORS 用的。

建议这样理解：

- `ALLOWED_ORIGINS`：放你确定不会变的正式域名
- `ALLOWED_ORIGIN_REGEX`：放 Vercel Preview 这种会变的域名

如果你前端正式域名暂时就是默认的 Vercel 域名，可以先这样填：

```text
ALLOWED_ORIGINS=https://你的项目名.vercel.app
ALLOWED_ORIGIN_REGEX=^https://.*\.vercel\.app$
```

如果以后绑定自定义域名，比如 `https://app.example.com`，就改成：

```text
ALLOWED_ORIGINS=https://app.example.com,https://你的项目名.vercel.app
ALLOWED_ORIGIN_REGEX=^https://.*\.vercel\.app$
```

### 3.6 Render 创建完成后，你要拿到两个值

#### 1. Render 服务 URL

示例：

```text
https://agent-skills-market-web-service.onrender.com
```

这个值稍后要填到 Vercel 的 `NEXT_PUBLIC_API_URL`。

#### 2. Deploy Hook URL

获取方法：

1. 打开 Render 服务
2. 点击 `Settings`
3. 找到 `Deploy Hook`
4. 复制那条 URL

这个值稍后要填到 GitHub Secret：

```text
RENDER_DEPLOY_HOOK_URL
```

### 3.7 这一部分结束时，先做个检查

先确认后端是不是已经活了。

在浏览器打开：

- `https://你的-render-服务.onrender.com/health`
- `https://你的-render-服务.onrender.com/docs`

如果这两个地址都能打开，说明后端基本部署成功。

## 4. 再做 Vercel 前端

这一部分结束后，你应该拿到：

- Vercel 前端正式域名
- `VERCEL_PROJECT_ID`
- `VERCEL_ORG_ID`
- `VERCEL_TOKEN`

### 4.1 在 Vercel 创建项目

操作：

1. 登录 Vercel
2. 点击 `Add New...`
3. 选择 `Project`
4. 导入同一个 GitHub 仓库
5. 最关键的一步：把 `Root Directory` 设为 `frontend`
6. 创建项目

如果 `Root Directory` 没选成 `frontend`，前端项目会构建失败。

### 4.2 在 Vercel 里配置环境变量

进入：

1. 打开这个 Vercel 项目
2. 进入 `Settings`
3. 打开 `Environment Variables`
4. 添加：

```text
NEXT_PUBLIC_API_URL=https://你的-render-服务.onrender.com/api
```

注意这里必须填完整浏览器可访问地址，不能写容器地址，也不能写 `/api`。

### 4.3 建议关闭 Vercel 自己的 Git 自动部署

因为仓库已经用 GitHub Actions 来部署 Vercel 了。

如果你不关闭，通常会出现这种情况：

- GitHub Actions 部署一次
- Vercel Git Integration 再自动部署一次

不一定会坏，但会重复。

建议：

1. 打开 Vercel 项目设置
2. 找到 Git / Deployments 相关设置
3. 关闭自动 Git 部署

### 4.4 获取 `VERCEL_PROJECT_ID` 和 `VERCEL_ORG_ID`

在你本地机器终端里执行：

```bash
cd frontend
vercel login
vercel link
```

执行完成后，查看这个文件：

```text
frontend/.vercel/project.json
```

里面会有：

- `projectId`
- `orgId`

分别对应：

- `VERCEL_PROJECT_ID`
- `VERCEL_ORG_ID`

### 4.5 获取 `VERCEL_TOKEN`

操作：

1. 打开 Vercel 账号设置
2. 找到 `Tokens`
3. 创建一个新的 Token
4. 复制它

这个值稍后要放进 GitHub Secret：

```text
VERCEL_TOKEN
```

## 5. 最后做 GitHub Secrets

这一部分做完，GitHub Actions 才能真的帮你部署。

进入 GitHub 仓库：

1. `Settings`
2. `Secrets and variables`
3. `Actions`
4. 添加下面 4 个 `Repository secrets`

### 必填 Secrets

```text
VERCEL_TOKEN=<你的 Vercel Token>
VERCEL_ORG_ID=<你的 Vercel orgId>
VERCEL_PROJECT_ID=<你的 Vercel projectId>
RENDER_DEPLOY_HOOK_URL=<你的 Render Deploy Hook URL>
```

### 当前不用放进 GitHub 的值

这些不要放到 GitHub Secrets 里：

- `DATABASE_URL`
- `SECRET_KEY`
- `SUPABASE_DB_PASSWORD`

原因很简单：

- `DATABASE_URL` 和 `SECRET_KEY` 只需要存在 Render 里
- 前端运行时变量只需要存在 Vercel 里
- GitHub Actions 只负责触发部署，不直接持有生产数据库密码

## 6. 现在怎么验证整套流程

### 6.1 先验证单独平台

先分别确认：

#### 后端

- `https://你的-render-服务.onrender.com/health` 能打开
- `https://你的-render-服务.onrender.com/docs` 能打开

#### 前端

- Vercel 项目页面能成功构建
- 打开前端首页不报环境变量缺失

### 6.2 再验证 GitHub Actions 自动部署

操作：

1. 把当前改动推到 `main`
2. 打开 GitHub 仓库的 `Actions`
3. 观察两个 workflow：
   - `Frontend CI`
   - `Backend CI`

你应该看到：

- 前端 workflow 通过后部署到 Vercel Production
- 后端 workflow 通过后触发 Render Deploy Hook

### 6.3 再验证 PR Preview

操作：

1. 新建一个分支
2. 提交一点前端改动
3. 发起 PR

你应该看到：

- `Frontend CI` 跑完后会创建一个 Vercel Preview
- 这个 Preview 页面能访问后端，不报 CORS

如果 Preview 页面能打开，但接口报跨域，先检查 Render 里的：

- `ALLOWED_ORIGINS`
- `ALLOWED_ORIGIN_REGEX`

## 7. 你可以直接照抄的最终填写模板

### 7.1 Render 环境变量模板

```text
ENVIRONMENT=production
DATABASE_URL=postgresql+asyncpg://postgres.<project-ref>:<编码后的密码>@aws-0-<region>.pooler.supabase.com:5432/postgres?ssl=require
SECRET_KEY=<openssl rand -hex 32 生成的值>
ALLOWED_ORIGINS=https://<你的-vercel-正式域名>.vercel.app
ALLOWED_ORIGIN_REGEX=^https://.*\.vercel\.app$
```

### 7.2 Vercel 环境变量模板

```text
NEXT_PUBLIC_API_URL=https://<你的-render-服务>.onrender.com/api
```

### 7.3 GitHub Secrets 模板

```text
VERCEL_TOKEN=<你的 vercel token>
VERCEL_ORG_ID=<你的 vercel org id>
VERCEL_PROJECT_ID=<你的 vercel project id>
RENDER_DEPLOY_HOOK_URL=<你的 render deploy hook url>
```

## 8. 最容易出错的 5 个地方

### 1. 用错 Supabase 连接串

错误：

- 用了 transaction pooler `6543`
- 直接把 Supabase 给的 `postgresql://` 原样贴过去

正确：

- 用 `Session pooler`
- 改成 `postgresql+asyncpg://...?...ssl=require`

### 2. 密码里有 `@` 但没编码

例如密码是：

```text
Pass@word
```

那么 URL 里要写成：

```text
Pass%40word
```

### 3. Vercel Root Directory 选错

必须是：

```text
frontend
```

### 4. `NEXT_PUBLIC_API_URL` 填错

必须是完整的 Render API 地址，例如：

```text
https://你的-render-服务.onrender.com/api
```

不要写：

- `/api`
- `http://backend:8000/api`
- `localhost`

### 5. Render 没放行 Vercel Preview 域名

如果 PR Preview 调接口报跨域，通常就是没有配置：

```text
ALLOWED_ORIGIN_REGEX=^https://.*\.vercel\.app$
```

## 9. 上线前检查清单

### Supabase

- [ ] 已创建项目
- [ ] 已复制 Session pooler 连接串
- [ ] 已把协议头改成 `postgresql+asyncpg://`
- [ ] 已加上 `?ssl=require`
- [ ] 如果密码有特殊字符，已完成 URL 编码

### Render

- [ ] 已通过 Blueprint 或普通方式创建服务
- [ ] 已配置 `DATABASE_URL`
- [ ] 已配置 `SECRET_KEY`
- [ ] 已配置 `ALLOWED_ORIGINS`
- [ ] 已配置 `ALLOWED_ORIGIN_REGEX`
- [ ] 已拿到 `RENDER_SERVICE_URL`
- [ ] 已拿到 `RENDER_DEPLOY_HOOK_URL`

### Vercel

- [ ] 已创建前端项目
- [ ] Root Directory = `frontend`
- [ ] 已配置 `NEXT_PUBLIC_API_URL`
- [ ] 已拿到 `VERCEL_PROJECT_ID`
- [ ] 已拿到 `VERCEL_ORG_ID`
- [ ] 已拿到 `VERCEL_TOKEN`

### GitHub

- [ ] 已配置 `VERCEL_TOKEN`
- [ ] 已配置 `VERCEL_ORG_ID`
- [ ] 已配置 `VERCEL_PROJECT_ID`
- [ ] 已配置 `RENDER_DEPLOY_HOOK_URL`

## 10. 如果你现在就开始配，推荐顺序

你现在最省事的顺序就是：

1. 先去 Supabase 生成最终 `DATABASE_URL`
2. 再去 Render 创建服务并让 `/health` 跑通
3. 然后去 Vercel 创建前端项目并配置 `NEXT_PUBLIC_API_URL`
4. 最后再去 GitHub 把 4 个 Secrets 配上
5. 推送一次 `main` 验证自动部署

如果你不确定自己现在卡在哪一步，就不要往后跳。先把当前这一步做完，再看下一步。
