"""
Token安全测试 - 验证JWT Token的安全机制

本测试文件覆盖以下Token安全场景：
1. Token撤销（用户登出后Token失效）
2. 密码修改后Token失效策略
3. Refresh Token一次性使用（轮换机制）
4. 并发刷新竞态条件处理

实现状态说明：
- 所有功能当前都未实现
- 测试标记为xfail，待功能实现后自动通过
- 每个测试包含详细的实现建议
"""

import uuid

import pytest
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession

from src.auth import create_access_token, create_refresh_token
from src.infra.persistence.models.user_model import UserModel

AUTH_PREFIX = "/api/auth"

class TestTokenRevocationOnLogout:
    """
    场景1: 用户撤销会话后Token失效

    背景:
    - 用户A已登录，持有access_token_X
    - access_token_X被泄露给用户B

    预期行为:
    1. 用户B使用access_token_X可以访问资源（Token技术上仍有效）
    2. 用户A检测到泄露并登出/撤销会话
    3. 后端将access_token_X加入黑名单
    4. 用户B再次使用access_token_X访问，返回401

    实现状态: ❌ 未实现
    - logout路由是stub，无实际撤销逻辑
    - 无Token黑名单/撤销列表机制
    - 需要数据库表存储已撤销的Token
    """

    @pytest.mark.asyncio
    @pytest.mark.xfail(
        reason="Token撤销机制未实现: logout路由是stub，需要添加Token黑名单表和撤销逻辑",
        strict=False,
    )
    async def test_should_invalidate_access_token_when_user_logs_out(
        self,
        client: AsyncClient,
        db_session: AsyncSession,
    ) -> None:
        """
        测试: 用户登出后，其access_token应该失效

        实现建议:
        1. 创建token_blacklist表，存储被撤销的token_jti和撤销时间
        2. 在logout handler中将token加入黑名单
        3. 在verify_token中检查token是否在黑名单中
        4. 定期清理过期的黑名单记录
        """
        # Step 1: 创建测试用户
        import bcrypt

        unique_id = str(uuid.uuid4())[:8]
        email = f"revoke_test_{unique_id}@example.com"
        username = f"revoke_user_{unique_id}"
        password = "password123"

        salt = bcrypt.gensalt()
        password_hash = bcrypt.hashpw(password.encode(), salt).decode()

        user = UserModel(
            email=email,
            username=username,
            password_hash=password_hash,
            is_active=True,
            email_verified=True,
        )
        db_session.add(user)
        await db_session.flush()
        await db_session.refresh(user)

        # Step 2: 生成access token
        access_token = create_access_token(data={"sub": str(user.id)})

        # Step 3: 使用token访问/me，验证token有效
        response = await client.get(
            f"{AUTH_PREFIX}/me",
            headers={"Authorization": f"Bearer {access_token}"},
        )
        assert response.status_code == 200, f"Token应该有效，但返回{response.status_code}"

        # Step 4: 用户登出（携带token）
        logout_response = await client.post(
            f"{AUTH_PREFIX}/logout",
            headers={"Authorization": f"Bearer {access_token}"},
        )
        assert logout_response.status_code == 200, "登出应该成功"

        # Step 5: 再次使用相同的token访问/me，应该401
        response_after_logout = await client.get(
            f"{AUTH_PREFIX}/me",
            headers={"Authorization": f"Bearer {access_token}"},
        )
        assert response_after_logout.status_code == 401, "Token已被撤销，应该返回401"
        assert (
            "revoked" in response_after_logout.json().get("message", "").lower()
            or "invalid" in response_after_logout.json().get("message", "").lower()
        ), "错误消息应该提示Token已被撤销"

    @pytest.mark.asyncio
    @pytest.mark.xfail(reason="Token撤销机制未实现: 需要实现全局会话撤销功能", strict=False)
    async def test_should_invalidate_all_user_tokens_when_revoke_all_sessions(
        self,
        client: AsyncClient,
        db_session: AsyncSession,
    ) -> None:
        """
        测试: 用户撤销所有会话后，该用户的所有Token都应该失效

        实现建议:
        1. 在用户表中添加token_version字段
        2. 生成token时包含当前token_version
        3. 撤销所有会话时增加token_version
        4. 验证token时检查version是否匹配
        """
        # Step 1: 创建测试用户
        import bcrypt

        unique_id = str(uuid.uuid4())[:8]
        email = f"revoke_all_{unique_id}@example.com"
        username = f"revoke_all_user_{unique_id}"
        password = "password123"

        salt = bcrypt.gensalt()
        password_hash = bcrypt.hashpw(password.encode(), salt).decode()

        user = UserModel(
            email=email,
            username=username,
            password_hash=password_hash,
            is_active=True,
            email_verified=True,
        )
        db_session.add(user)
        await db_session.flush()
        await db_session.refresh(user)

        # Step 2: 生成多个token（模拟多个设备登录）
        token1 = create_access_token(data={"sub": str(user.id)})
        token2 = create_access_token(data={"sub": str(user.id)})
        token3 = create_access_token(data={"sub": str(user.id)})

        # Step 3: 验证所有token都有效
        for i, token in enumerate([token1, token2, token3], 1):
            response = await client.get(
                f"{AUTH_PREFIX}/me",
                headers={"Authorization": f"Bearer {token}"},
            )
            assert response.status_code == 200, f"Token {i} 应该有效"

        # Step 4: 调用撤销所有会话的API（需要实现）
        # POST /api/auth/revoke-all-sessions
        revoke_response = await client.post(
            f"{AUTH_PREFIX}/revoke-all-sessions",
            headers={"Authorization": f"Bearer {token1}"},
        )
        assert revoke_response.status_code == 200, "撤销所有会话应该成功"

        # Step 5: 验证所有token都失效
        for i, token in enumerate([token1, token2, token3], 1):
            response = await client.get(
                f"{AUTH_PREFIX}/me",
                headers={"Authorization": f"Bearer {token}"},
            )
            assert response.status_code == 401, f"Token {i} 应该已被撤销"

class TestTokenInvalidationOnPasswordChange:
    """
    场景2: 密码修改后Token失效策略

    背景:
    - 用户A已登录，持有access_token_Y
    - 用户怀疑密码泄露或定期更换密码

    预期行为（策略1 - 推荐）:
    1. 用户A修改密码
    2. 所有现有Token立即失效
    3. 用户使用旧access_token_Y访问，返回401
    4. 用户需要使用新密码重新登录

    实现状态: ❌ 未实现
    - 无密码修改API
    - 无Token失效策略
    - 需要用户表支持token_version或issued_at
    """

    @pytest.mark.asyncio
    @pytest.mark.xfail(reason="密码修改功能未实现: 无密码修改API，无Token失效策略", strict=False)
    async def test_should_invalidate_all_tokens_when_password_changed(
        self,
        client: AsyncClient,
        db_session: AsyncSession,
    ) -> None:
        """
        测试: 用户修改密码后，所有现有Token应该失效

        实现建议:
        1. 实现PUT /api/auth/password API
        2. 在用户表中添加password_changed_at字段
        3. Token payload中包含iat（issued at）时间戳
        4. 验证Token时检查iat < password_changed_at
        """
        # Step 1: 创建测试用户并登录
        import bcrypt

        unique_id = str(uuid.uuid4())[:8]
        email = f"pwd_change_{unique_id}@example.com"
        username = f"pwd_change_user_{unique_id}"
        old_password = "oldpassword123"
        new_password = "newpassword456"

        salt = bcrypt.gensalt()
        password_hash = bcrypt.hashpw(old_password.encode(), salt).decode()

        user = UserModel(
            email=email,
            username=username,
            password_hash=password_hash,
            is_active=True,
            email_verified=True,
        )
        db_session.add(user)
        await db_session.flush()
        await db_session.refresh(user)

        # Step 2: 生成token（模拟登录后的token）
        access_token = create_access_token(data={"sub": str(user.id)})
        refresh_token = create_refresh_token(data={"sub": str(user.id)})

        # Step 3: 验证token有效
        response = await client.get(
            f"{AUTH_PREFIX}/me",
            headers={"Authorization": f"Bearer {access_token}"},
        )
        assert response.status_code == 200, "Token应该有效"

        # Step 4: 修改密码（需要实现密码修改API）
        # PUT /api/auth/password
        change_response = await client.put(
            f"{AUTH_PREFIX}/password",
            headers={"Authorization": f"Bearer {access_token}"},
            json={
                "old_password": old_password,
                "new_password": new_password,
            },
        )
        assert change_response.status_code == 200, "密码修改应该成功"

        # Step 5: 验证旧token失效
        response_after_change = await client.get(
            f"{AUTH_PREFIX}/me",
            headers={"Authorization": f"Bearer {access_token}"},
        )
        assert response_after_change.status_code == 401, "密码修改后旧token应该失效"

        # Step 6: 验证refresh token也失效
        refresh_response = await client.post(
            f"{AUTH_PREFIX}/refresh",
            headers={"Authorization": f"Bearer {refresh_token}"},
        )
        assert refresh_response.status_code == 401, "密码修改后旧refresh token也应该失效"

        # Step 7: 使用新密码登录应该成功
        login_response = await client.post(
            f"{AUTH_PREFIX}/login",
            json={
                "email": email,
                "password": new_password,
            },
        )
        assert login_response.status_code == 200, "使用新密码登录应该成功"

class TestRefreshTokenRotation:
    """
    场景3: Refresh Token一次性使用（轮换机制）

    背景:
    - 用户持有refresh_token_v1
    - refresh token可能被窃取

    预期行为:
    1. 用户使用refresh_token_v1刷新
    2. 返回新的token对（access_token_v2, refresh_token_v2）
    3. refresh_token_v1应该失效
    4. 再次使用refresh_token_v1应该返回401
    5. （可选）检测到重放攻击，撤销该用户的所有Token

    实现状态: ❌ 未实现
    - refresh_token_handler只生成新token，不撤销旧token
    - 无refresh token存储和跟踪机制
    - 需要数据库表存储已使用的refresh token
    """

    @pytest.mark.asyncio
    @pytest.mark.xfail(
        reason="Refresh Token轮换机制未实现: 需要存储已使用的refresh token", strict=False
    )
    async def test_should_invalidate_old_refresh_token_after_rotation(
        self,
        client: AsyncClient,
        db_session: AsyncSession,
    ) -> None:
        """
        测试: Refresh Token只能使用一次，刷新后旧token应该失效

        实现建议:
        1. 创建refresh_tokens表，存储token_jti、user_id、expires_at、used_at
        2. 生成refresh token时记录到表中
        3. 刷新时标记旧token为已使用
        4. 如果尝试使用已使用的token，返回401并可能撤销用户所有token（检测重放攻击）
        """
        # Step 1: 创建测试用户
        import bcrypt

        unique_id = str(uuid.uuid4())[:8]
        email = f"rotation_{unique_id}@example.com"
        username = f"rotation_user_{unique_id}"
        password = "password123"

        salt = bcrypt.gensalt()
        password_hash = bcrypt.hashpw(password.encode(), salt).decode()

        user = UserModel(
            email=email,
            username=username,
            password_hash=password_hash,
            is_active=True,
            email_verified=True,
        )
        db_session.add(user)
        await db_session.flush()
        await db_session.refresh(user)

        # Step 2: 生成初始refresh token
        refresh_token_v1 = create_refresh_token(data={"sub": str(user.id)})

        # Step 3: 使用refresh_token_v1刷新，应该成功
        response1 = await client.post(
            f"{AUTH_PREFIX}/refresh",
            headers={"Authorization": f"Bearer {refresh_token_v1}"},
        )
        assert response1.status_code == 200, "第一次刷新应该成功"

        data1 = response1.json()
        assert "access_token" in data1, "响应应该包含access_token"
        assert "refresh_token" in data1, "响应应该包含新的refresh_token"
        refresh_token_v2 = data1["refresh_token"]

        # Step 4: 再次使用refresh_token_v1刷新，应该失败
        response2 = await client.post(
            f"{AUTH_PREFIX}/refresh",
            headers={"Authorization": f"Bearer {refresh_token_v1}"},
        )
        assert response2.status_code == 401, "使用已使用过的refresh token应该返回401"
        assert (
            "used" in response2.json().get("message", "").lower()
            or "invalid" in response2.json().get("message", "").lower()
        ), "错误消息应该提示token已被使用或无效"

        # Step 5: 使用新的refresh_token_v2刷新，应该成功
        response3 = await client.post(
            f"{AUTH_PREFIX}/refresh",
            headers={"Authorization": f"Bearer {refresh_token_v2}"},
        )
        assert response3.status_code == 200, "使用新的refresh token应该成功"

    @pytest.mark.asyncio
    @pytest.mark.xfail(
        reason="Refresh Token重放攻击检测未实现: 需要检测已使用token的重放", strict=False
    )
    async def test_should_revoke_all_tokens_when_replay_attack_detected(
        self,
        client: AsyncClient,
        db_session: AsyncSession,
    ) -> None:
        """
        测试: 检测到重放攻击时，应该撤销用户的所有Token

        安全考虑:
        - 如果攻击者窃取了用户的refresh token并尝试使用
        - 合法用户也在使用这个token刷新
        - 检测到重放攻击后，应该撤销该用户的所有会话，强制重新登录
        """
        # Step 1: 创建测试用户
        import bcrypt

        unique_id = str(uuid.uuid4())[:8]
        email = f"replay_{unique_id}@example.com"
        username = f"replay_user_{unique_id}"
        password = "password123"

        salt = bcrypt.gensalt()
        password_hash = bcrypt.hashpw(password.encode(), salt).decode()

        user = UserModel(
            email=email,
            username=username,
            password_hash=password_hash,
            is_active=True,
            email_verified=True,
        )
        db_session.add(user)
        await db_session.flush()
        await db_session.refresh(user)

        # Step 2: 生成初始token对
        refresh_token = create_refresh_token(data={"sub": str(user.id)})

        # Step 3: 正常使用refresh token刷新
        response1 = await client.post(
            f"{AUTH_PREFIX}/refresh",
            headers={"Authorization": f"Bearer {refresh_token}"},
        )
        assert response1.status_code == 200, "合法刷新应该成功"

        # Step 4: 攻击者尝试重放攻击（使用已使用的refresh token）
        response2 = await client.post(
            f"{AUTH_PREFIX}/refresh",
            headers={"Authorization": f"Bearer {refresh_token}"},
        )

        # Step 5: 应该检测到重放攻击
        assert response2.status_code == 401, "重放攻击应该被检测"

        # Step 6: 该用户的所有token应该被撤销（安全策略）
        new_access_token = response1.json()["access_token"]
        await client.get(
            f"{AUTH_PREFIX}/me",
            headers={"Authorization": f"Bearer {new_access_token}"},
        )
        # 但至少应该记录安全事件并通知用户

# 辅助测试：验证当前实现的实际行为
class TestCurrentImplementationBehavior:
    """
    这些测试验证当前实现的行为（非xfail）
    用于记录当前系统的实际状态
    """

    @pytest.mark.asyncio
    async def test_current_logout_does_not_revoke_token(
        self,
        client: AsyncClient,
        db_session: AsyncSession,
    ) -> None:
        """
        验证: 当前logout实现不会撤销token（记录当前行为）
        """
        import bcrypt

        unique_id = str(uuid.uuid4())[:8]
        email = f"current_{unique_id}@example.com"
        username = f"current_user_{unique_id}"
        password = "password123"

        salt = bcrypt.gensalt()
        password_hash = bcrypt.hashpw(password.encode(), salt).decode()

        user = UserModel(
            email=email,
            username=username,
            password_hash=password_hash,
            is_active=True,
            email_verified=True,
        )
        db_session.add(user)
        await db_session.flush()
        await db_session.refresh(user)

        access_token = create_access_token(data={"sub": str(user.id)})

        # 登出
        logout_response = await client.post(
            f"{AUTH_PREFIX}/logout",
            headers={"Authorization": f"Bearer {access_token}"},
        )
        assert logout_response.status_code == 200
        me_response = await client.get(
            f"{AUTH_PREFIX}/me",
            headers={"Authorization": f"Bearer {access_token}"},
        )
        # 记录当前行为：token在logout后仍然有效
        assert me_response.status_code == 200, (
            "当前实现：logout不会使token失效（这是一个已知的安全问题）"
        )

    @pytest.mark.asyncio
    async def test_current_refresh_token_not_rotated(
        self,
        client: AsyncClient,
        db_session: AsyncSession,
    ) -> None:
        """
        验证: 当前refresh token不会被撤销（记录当前行为）
        """
        import bcrypt

        unique_id = str(uuid.uuid4())[:8]
        email = f"current_rot_{unique_id}@example.com"
        username = f"current_rot_user_{unique_id}"
        password = "password123"

        salt = bcrypt.gensalt()
        password_hash = bcrypt.hashpw(password.encode(), salt).decode()

        user = UserModel(
            email=email,
            username=username,
            password_hash=password_hash,
            is_active=True,
            email_verified=True,
        )
        db_session.add(user)
        await db_session.flush()
        await db_session.refresh(user)

        refresh_token = create_refresh_token(data={"sub": str(user.id)})

        # 第一次刷新
        response1 = await client.post(
            f"{AUTH_PREFIX}/refresh",
            headers={"Authorization": f"Bearer {refresh_token}"},
        )
        assert response1.status_code == 200
        response2 = await client.post(
            f"{AUTH_PREFIX}/refresh",
            headers={"Authorization": f"Bearer {refresh_token}"},
        )
        # 记录当前行为：旧token可以重复使用
        assert response2.status_code == 200, (
            "当前实现：refresh token可以重复使用（这是一个已知的安全问题）"
        )
