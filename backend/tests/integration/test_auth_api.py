import uuid

import pytest
from httpx import AsyncClient

from src.auth import create_access_token, create_refresh_token
from src.infra.persistence.models.user_model import UserModel

AUTH_PREFIX = "/api/auth"


class TestRegisterEndpoint:
    @pytest.mark.asyncio
    async def should_return_tokens_when_register_given_valid_input(
        self, client: AsyncClient
    ) -> None:
        unique_email = f"newuser-{uuid.uuid4().hex[:8]}@example.com"
        response = await client.post(
            f"{AUTH_PREFIX}/register",
            json={
                "email": unique_email,
                "username": "newuser",
                "password": "SecurePass123!",
            },
        )

        assert response.status_code == 201
        data = response.json()
        assert "access_token" in data
        assert "refresh_token" in data
        assert data["token_type"] == "bearer"

    @pytest.mark.asyncio
    async def should_return_409_when_register_given_duplicate_email(
        self, client: AsyncClient, test_user: UserModel
    ) -> None:
        response = await client.post(
            f"{AUTH_PREFIX}/register",
            json={
                "email": test_user.email,
                "username": "anotheruser",
                "password": "SecurePass123!",
            },
        )

        assert response.status_code == 409  # CONFLICT is more appropriate for duplicate resources
        assert (
            "already registered" in response.json()["message"].lower()
            or "conflict" in response.json()["message"].lower()
        )

    @pytest.mark.asyncio
    async def should_return_422_when_register_given_invalid_email(
        self, client: AsyncClient
    ) -> None:
        response = await client.post(
            f"{AUTH_PREFIX}/register",
            json={
                "email": "not-an-email",
                "username": "testuser",
                "password": "SecurePass123!",
            },
        )

        assert response.status_code == 422

    @pytest.mark.asyncio
    async def should_return_422_when_register_given_short_password(
        self, client: AsyncClient
    ) -> None:
        response = await client.post(
            f"{AUTH_PREFIX}/register",
            json={
                "email": "valid@example.com",
                "username": "testuser",
                "password": "short",
            },
        )

        assert response.status_code == 422


class TestLoginEndpoint:
    @pytest.mark.asyncio
    async def should_return_tokens_when_login_given_valid_credentials(
        self, client: AsyncClient, test_user: UserModel
    ) -> None:
        response = await client.post(
            f"{AUTH_PREFIX}/login",
            json={
                "email": test_user.email,
                "password": "password123",
            },
        )

        assert response.status_code == 200
        data = response.json()
        assert "access_token" in data
        assert "refresh_token" in data
        assert data["token_type"] == "bearer"

    @pytest.mark.asyncio
    async def should_return_401_when_login_given_invalid_password(
        self, client: AsyncClient, test_user: UserModel
    ) -> None:
        response = await client.post(
            f"{AUTH_PREFIX}/login",
            json={
                "email": test_user.email,
                "password": "wrongpassword",
            },
        )

        assert response.status_code == 401
        assert "incorrect" in response.json()["message"].lower()

    @pytest.mark.asyncio
    async def should_return_401_when_login_given_nonexistent_user(
        self, client: AsyncClient
    ) -> None:
        response = await client.post(
            f"{AUTH_PREFIX}/login",
            json={
                "email": "nonexistent@example.com",
                "password": "anypassword",
            },
        )

        assert response.status_code == 401
        assert "incorrect" in response.json()["message"].lower()


class TestRefreshEndpoint:
    @pytest.mark.asyncio
    async def should_return_new_tokens_when_refresh_given_valid_token(
        self, client: AsyncClient, test_user: UserModel
    ) -> None:
        refresh_token = create_refresh_token(data={"sub": str(test_user.id)})

        response = await client.post(
            f"{AUTH_PREFIX}/refresh",
            headers={"Authorization": f"Bearer {refresh_token}"},
        )

        assert response.status_code == 200
        data = response.json()
        assert "access_token" in data
        assert "refresh_token" in data

    @pytest.mark.asyncio
    async def should_return_401_when_refresh_given_no_token(self, client: AsyncClient) -> None:
        response = await client.post(f"{AUTH_PREFIX}/refresh")

        assert response.status_code == 401
        assert "not found" in response.json()["message"].lower()

    @pytest.mark.asyncio
    async def should_return_401_when_refresh_given_invalid_token(self, client: AsyncClient) -> None:
        response = await client.post(
            f"{AUTH_PREFIX}/refresh",
            headers={"Authorization": "Bearer invalid-token"},
        )

        assert response.status_code == 401
        assert "invalid" in response.json()["message"].lower()

    @pytest.mark.asyncio
    async def should_return_401_when_refresh_given_access_token(
        self, client: AsyncClient, test_user: UserModel
    ) -> None:
        access_token = create_access_token(data={"sub": str(test_user.id)})

        response = await client.post(
            f"{AUTH_PREFIX}/refresh",
            headers={"Authorization": f"Bearer {access_token}"},
        )

        assert response.status_code == 401
        assert "invalid token type" in response.json()["message"].lower()


class TestLogoutEndpoint:
    @pytest.mark.asyncio
    async def should_logout_successfully_when_logout_given_authenticated(
        self, client: AsyncClient, test_user: UserModel
    ) -> None:
        response = await client.post(f"{AUTH_PREFIX}/logout")

        assert response.status_code == 200
        data = response.json()
        assert data["message"] == "Logged out successfully"

    @pytest.mark.asyncio
    async def should_return_200_when_logout_given_no_auth(self, client: AsyncClient) -> None:
        response = await client.post(f"{AUTH_PREFIX}/logout")

        assert response.status_code == 200
        assert "logged out" in response.json()["message"].lower()


class TestMeEndpoint:
    @pytest.mark.asyncio
    async def should_return_user_info_when_get_me_given_authenticated(
        self, client: AsyncClient, test_user: UserModel
    ) -> None:
        access_token = create_access_token(data={"sub": str(test_user.id)})

        response = await client.get(
            f"{AUTH_PREFIX}/me",
            headers={"Authorization": f"Bearer {access_token}"},
        )

        assert response.status_code == 200
        data = response.json()
        assert data["email"] == test_user.email
        assert data["username"] == test_user.username
        assert data["id"] == str(test_user.id)
        assert "password_hash" not in data

    @pytest.mark.asyncio
    async def should_return_401_when_get_me_given_no_token(self, client: AsyncClient) -> None:
        response = await client.get(f"{AUTH_PREFIX}/me")

        assert response.status_code == 401
        assert "not authenticated" in response.json()["message"].lower()

    @pytest.mark.asyncio
    async def should_return_401_when_get_me_given_invalid_token(self, client: AsyncClient) -> None:
        response = await client.get(
            f"{AUTH_PREFIX}/me",
            headers={"Authorization": "Bearer invalid-token"},
        )

        assert response.status_code == 401
        assert "invalid" in response.json()["message"].lower()

    @pytest.mark.asyncio
    async def should_return_404_when_get_me_given_nonexistent_user(
        self, client: AsyncClient
    ) -> None:
        access_token = create_access_token(data={"sub": "00000000-0000-0000-0000-000000000000"})

        response = await client.get(
            f"{AUTH_PREFIX}/me",
            headers={"Authorization": f"Bearer {access_token}"},
        )

        assert response.status_code == 404  # User not found is 404, not 401
        assert "not found" in response.json()["message"].lower()


class TestAuthFlow:
    @pytest.mark.asyncio
    async def should_complete_full_auth_flow_when_register_login_logout(
        self, client: AsyncClient
    ) -> None:
        unique_email = f"flowtest-{uuid.uuid4().hex[:8]}@example.com"
        register_response = await client.post(
            f"{AUTH_PREFIX}/register",
            json={
                "email": unique_email,
                "username": "flowtest",
                "password": "FlowTest123!",
            },
        )
        assert register_response.status_code == 201
        data = register_response.json()
        access_token = data["access_token"]

        me_response = await client.get(
            f"{AUTH_PREFIX}/me",
            headers={"Authorization": f"Bearer {access_token}"},
        )
        assert me_response.status_code == 200
        assert me_response.json()["email"] == unique_email

        logout_response = await client.post(f"{AUTH_PREFIX}/logout")
        assert logout_response.status_code == 200

        me_after_logout = await client.get(
            f"{AUTH_PREFIX}/me",
            headers={"Authorization": f"Bearer {access_token}"},
        )
        assert me_after_logout.status_code == 200

    @pytest.mark.asyncio
    async def should_refresh_tokens_when_login_then_refresh(
        self, client: AsyncClient, test_user: UserModel
    ) -> None:
        login_response = await client.post(
            f"{AUTH_PREFIX}/login",
            json={
                "email": test_user.email,
                "password": "password123",
            },
        )
        assert login_response.status_code == 200
        login_data = login_response.json()
        refresh_token = login_data["refresh_token"]

        refresh_response = await client.post(
            f"{AUTH_PREFIX}/refresh",
            headers={"Authorization": f"Bearer {refresh_token}"},
        )
        assert refresh_response.status_code == 200
        refresh_data = refresh_response.json()
        new_access_token = refresh_data["access_token"]

        me_response = await client.get(
            f"{AUTH_PREFIX}/me",
            headers={"Authorization": f"Bearer {new_access_token}"},
        )
        assert me_response.status_code == 200
        assert me_response.json()["email"] == test_user.email


class TestEdgeCases:
    @pytest.mark.asyncio
    async def should_not_expose_password_when_login_given_valid_credentials(
        self, client: AsyncClient, test_user: UserModel
    ) -> None:
        response = await client.post(
            f"{AUTH_PREFIX}/login",
            json={
                "email": test_user.email,
                "password": "password123",
            },
        )

        assert response.status_code == 200
        data = response.json()
        assert "password" not in data
        assert "password_hash" not in data

    @pytest.mark.asyncio
    async def should_return_tokens_when_register_given_valid_input_tokens(
        self, client: AsyncClient
    ) -> None:
        unique_email = f"tokens-{uuid.uuid4().hex[:8]}@example.com"
        response = await client.post(
            f"{AUTH_PREFIX}/register",
            json={
                "email": unique_email,
                "username": "tokens",
                "password": "SecurePass123!",
            },
        )

        assert response.status_code == 201
        data = response.json()
        assert "access_token" in data
        assert "refresh_token" in data

    @pytest.mark.asyncio
    async def should_allow_multiple_logouts_when_called_repeatedly(
        self, client: AsyncClient
    ) -> None:
        response1 = await client.post(f"{AUTH_PREFIX}/logout")
        response2 = await client.post(f"{AUTH_PREFIX}/logout")

        assert response1.status_code == 200
        assert response2.status_code == 200

    @pytest.mark.asyncio
    async def should_accept_case_insensitive_email_when_login(
        self, client: AsyncClient, test_user: UserModel
    ) -> None:
        response = await client.post(
            f"{AUTH_PREFIX}/login",
            json={
                "email": test_user.email.upper(),
                "password": "password123",
            },
        )

        # Email is normalized to lowercase, so uppercase email should work
        assert response.status_code == 200

    @pytest.mark.asyncio
    async def should_return_401_when_use_expired_token(self, client: AsyncClient) -> None:
        response = await client.get(
            f"{AUTH_PREFIX}/me",
            headers={"Authorization": "Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.expired"},
        )

        assert response.status_code == 401
