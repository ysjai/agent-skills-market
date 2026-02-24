# Token安全测试实现路线图

## 当前状态

| 功能 | 实现状态 | 测试状态 |
|------|----------|----------|
| Token撤销（logout） | ❌ 未实现 | ✅ xfail测试已编写 |
| 密码修改后Token失效 | ❌ 未实现 | ✅ xfail测试已编写 |
| Refresh Token轮换 | ❌ 未实现 | ✅ xfail测试已编写 |
| 并发刷新竞态条件 | ❌ 未实现 | ✅ xfail测试已编写 |

## 未实现功能详情

### 1. Token撤销机制
**当前问题**: logout路由是stub，无实际撤销逻辑

**实现建议**:
```python
# 1. 创建token_blacklist表
class TokenBlacklist(Base):
    token_jti = Column(String, primary_key=True)
    user_id = Column(UUID, ForeignKey("users.id"))
    revoked_at = Column(DateTime)
    expires_at = Column(DateTime)

# 2. 在logout handler中添加撤销逻辑
async def logout(token: str):
    payload = verify_token(token)
    await add_to_blacklist(payload["jti"], payload["sub"])

# 3. 在verify_token中检查黑名单
async def verify_token(token: str):
    payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
    if await is_blacklisted(payload["jti"]):
        raise UnauthorizedError("Token has been revoked")
    return payload
```

### 2. 密码修改后Token失效
**当前问题**: 无密码修改API，无Token失效策略

**实现建议**:
```python
# 1. 在用户表中添加password_changed_at字段
class User(Base):
    password_changed_at = Column(DateTime, default=datetime.utcnow)

# 2. Token中包含iat（issued at）
def create_access_token(data: dict):
    to_encode = data.copy()
    to_encode.update({"iat": datetime.utcnow(), "type": "access"})
    return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)

# 3. 验证时检查iat < password_changed_at
async def verify_token(token: str, user: User):
    payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
    token_iat = datetime.fromtimestamp(payload["iat"])
    if token_iat < user.password_changed_at:
        raise UnauthorizedError("Token invalidated due to password change")
```

### 3. Refresh Token轮换
**当前问题**: refresh_token_handler只生成新token，不撤销旧token

**实现建议**:
```python
# 1. 创建refresh_tokens表
class RefreshToken(Base):
    token_jti = Column(String, primary_key=True)
    user_id = Column(UUID, ForeignKey("users.id"))
    used_at = Column(DateTime, nullable=True)
    expires_at = Column(DateTime)

# 2. 刷新时标记旧token为已使用
async def handle_refresh_token(refresh_token: str):
    payload = verify_token(refresh_token)
    
    # 检查token是否已被使用
    token_record = await get_refresh_token(payload["jti"])
    if token_record.used_at:
        # 检测到重放攻击，撤销用户所有token
        await revoke_all_user_tokens(payload["sub"])
        raise UnauthorizedError("Token reuse detected, all sessions revoked")
    
    # 标记为已使用
    await mark_token_as_used(payload["jti"])
    
    # 生成新token对
    new_access = create_access_token({"sub": payload["sub"]})
    new_refresh = create_refresh_token({"sub": payload["sub"]})
    await save_refresh_token(new_refresh.jti, payload["sub"])
    
    return new_access, new_refresh
```

### 4. 并发刷新竞态条件
**当前问题**: 无并发控制机制

**实现建议（宽松策略）**:
```python
# 使用数据库事务和唯一约束处理竞态条件
async def handle_refresh_token_with_concurrency(refresh_token: str):
    async with db.transaction():
        # 尝试标记token为已使用
        updated = await mark_token_as_used_if_not_used(refresh_token_jti)
        
        if not updated:
            # Token已被使用，检查是否已经生成了新token
            existing_new_tokens = await get_new_tokens_for_old(refresh_token_jti)
            if existing_new_tokens:
                # 返回相同的token对（幂等性）
                return existing_new_tokens
            else:
                raise UnauthorizedError("Token already used")
        
        # 生成新token对
        new_tokens = generate_new_tokens()
        await save_token_mapping(refresh_token_jti, new_tokens)
        return new_tokens
```

## 测试运行命令

```bash
# 运行所有Token安全测试
cd backend && pytest tests/integration/journey/auth/test_token_security.py -v

# 只运行xfail测试（验证未实现功能）
cd backend && pytest tests/integration/journey/auth/test_token_security.py -v --runxfail

# 只运行当前行为测试
cd backend && pytest tests/integration/journey/auth/test_token_security.py::TestCurrentImplementationBehavior -v
```

## 优先级建议

1. **P0 - Refresh Token轮换**: 防止长期有效的refresh token被滥用
2. **P1 - Token撤销机制**: 允许用户主动登出和撤销泄露的token
3. **P1 - 密码修改后Token失效**: 密码安全策略的基础
4. **P2 - 并发刷新处理**: 改善用户体验，防止竞态条件
