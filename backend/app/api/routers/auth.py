from typing import Annotated
from uuid import UUID

from fastapi import APIRouter, Depends, Header, status
from jwt.exceptions import InvalidTokenError

from app.api.dependencies.repositories import get_user_repo
from app.api.schemas.user import (
    GetUserResp,
    LoginReq,
    LoginResp,
    RegisterUserReq,
    RegisterUserResp,
)
from app.application.handlers.get_current_user_handler import handle_get_current_user
from app.application.handlers.login_handler import handle_login
from app.application.handlers.refresh_token_handler import handle_refresh_token
from app.application.handlers.register_user_handler import handle_register_user
from app.auth import verify_token
from app.domain.exceptions import UnauthorizedError
from app.domain.repositories.user_repository import UserRepository

router = APIRouter(prefix="/auth", tags=["auth"])


@router.post("/register", response_model=RegisterUserResp, status_code=status.HTTP_201_CREATED)
async def register(
    request: RegisterUserReq,
    user_repo: UserRepository = Depends(get_user_repo),
) -> RegisterUserResp:
    user, access_token, refresh_token = await handle_register_user(
        email=request.email,
        username=request.username,
        password=request.password,
        user_repo=user_repo,
    )
    return RegisterUserResp.from_domain(user, access_token, refresh_token)


@router.post("/login", response_model=LoginResp)
async def login(
    request: LoginReq,
    user_repo: UserRepository = Depends(get_user_repo),
) -> LoginResp:
    user, access_token, refresh_token = await handle_login(
        email=request.email,
        password=request.password,
        user_repo=user_repo,
    )
    return LoginResp(
        access_token=access_token,
        refresh_token=refresh_token,
        token_type="bearer",
    )


@router.post("/refresh", response_model=LoginResp)
async def refresh_token(
    authorization: Annotated[str | None, Header()] = None,
    user_repo: UserRepository = Depends(get_user_repo),
) -> LoginResp:
    if not authorization:
        raise UnauthorizedError("Refresh token not found")
    if authorization.startswith("Bearer "):
        refresh_token_str = authorization[7:]
    else:
        refresh_token_str = authorization
    user, access_token, new_refresh_token = await handle_refresh_token(
        refresh_token=refresh_token_str,
        user_repo=user_repo,
    )
    return LoginResp(
        access_token=access_token,
        refresh_token=new_refresh_token,
        token_type="bearer",
    )


@router.get("/me", response_model=GetUserResp)
async def get_current_user_endpoint(
    authorization: Annotated[str | None, Header()] = None,
    user_repo: UserRepository = Depends(get_user_repo),
) -> GetUserResp:
    if not authorization:
        raise UnauthorizedError("Not authenticated")
    if authorization.startswith("Bearer "):
        token = authorization[7:]
    else:
        token = authorization
    try:
        payload = verify_token(token)
    except InvalidTokenError:
        raise UnauthorizedError("Invalid authentication credentials")
    user_id_str = payload.get("sub")
    if not user_id_str:
        raise UnauthorizedError("Invalid token payload")
    user_id = UUID(user_id_str)
    user = await handle_get_current_user(
        user_id=user_id,
        user_repo=user_repo,
    )
    return GetUserResp.from_domain(user)


@router.post("/logout")
async def logout() -> dict:
    return {"message": "Logged out successfully"}
