# Agent 工作指南

## 重要规则
始终用中文与用户交流！

---

## 后端开发规范

当执行后端开发任务时，**必须**参考 [`project_conventions.md`](./project_conventions.md)。

### 核心原则

1. **DDD 分层架构**
   - `src/api/` → `src/application/` → `src/domain/` ← `src/infra/`
   - 依赖只能向内，不能反向

2. **充血领域模型** - 业务逻辑封装在领域对象中
   ```python
   # 正确
   skill.rename("New Name")
   
   # 错误 - 贫血模型
   skill.name = "New Name"
   ```

3. **值对象** - 构造时验证
   ```python
   slug = Slug("my-skill")
   email = Email("user@example.com")
   ```

4. **异常处理** - 使用全局异常处理器，路由中不写 try-catch

### 禁止事项
- 领域层导入 SQLAlchemy 或 FastAPI
- 路由中写业务逻辑
- 贫血模型

### 规范文档
- **默认** → [`project_conventions.md`](./project_conventions.md)
- **模板** → `docs/templates/*.py`
- **深度** → [`docs/architecture/ddd-guide.md`](./docs/architecture/ddd-guide.md)

---

## 快速启动

```bash
# 安装依赖
uv sync

# 配置环境
cp .env.example .env
# 编辑 .env 设置数据库连接

# 运行迁移
alembic upgrade head

# 启动服务
uvicorn src.main:app --reload --host 0.0.0.0 --port 8000
```

访问：http://localhost:8000/docs

---

## 技术栈

Python 3.10+ / FastAPI / SQLAlchemy 2.0 / PostgreSQL / uv

## 参考资料

- [项目规范](project_conventions.md)
- [DDD 教程](docs/architecture/ddd-guide.md)
- [代码模板](docs/templates/)
