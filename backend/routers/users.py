from fastapi import APIRouter, Depends, HTTPException, Request
from sqlalchemy.ext.asyncio import AsyncSession
from starlette import status

from config.limiter import limiter
from models.users import User
from schemas.users import UserRequest, UserAuthResponse, UserInfoResponse, UserUpdateRequest, UserChangePasswordRequest

from config.db_conf import get_db
from crud import users
from utils.response import success_response
from utils.auth import get_current_user

from config.settings import settings

router = APIRouter(prefix="/api/v1/user", tags=["users"])


# 条件限流装饰器（运行时检查，测试环境自动禁用）
def rate_limit(limit_str: str):
    """如果启用了限流则应用 slowapi 限流装饰器"""
    def decorator(func):
        if settings.rate_limit_enabled:
            return limiter.limit(limit_str)(func)
        return func
    return decorator


@router.post("/register")
@rate_limit("5/minute")
async def register(request: Request, user_data: UserRequest, db: AsyncSession = Depends(get_db)):
    existing_user = await users.get_user_by_username(db, user_data.username)
    if existing_user:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="用户已存在")
    user = await users.create_user(db, user_data)
    access_token = await users.create_access_token(user.id)
    refresh_token = await users.create_refresh_token(db, user.id)
    response_data = UserAuthResponse(
        accessToken=access_token,
        refreshToken=refresh_token,
        userInfo=UserInfoResponse.model_validate(user)
    )
    return success_response(message="注册成功", data=response_data)


@router.post("/login")
@rate_limit("10/minute")
async def login(request: Request, user_data: UserRequest, db: AsyncSession = Depends(get_db)):
    user = await users.authenticate_user(db, user_data.username, user_data.password)
    if not user:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="用户名或密码错误")
    access_token = await users.create_access_token(user.id)
    refresh_token = await users.create_refresh_token(db, user.id)
    response_data = UserAuthResponse(
        accessToken=access_token,
        refreshToken=refresh_token,
        userInfo=UserInfoResponse.model_validate(user)
    )
    return success_response(message="登录成功啦", data=response_data)


@router.get("/info")
async def get_user_info(user: User = Depends(get_current_user)):
    return success_response(message="获取用户信息成功", data=UserInfoResponse.model_validate(user))


@router.put("/update")
async def update_user_info(user_data: UserUpdateRequest, user: User = Depends(get_current_user),
                           db: AsyncSession = Depends(get_db)):
    user = await users.update_user(db, user.username, user_data)
    return success_response(message="更新用户信息成功", data=UserInfoResponse.model_validate(user))


@router.put("/password")
async def update_password(
        password_data: UserChangePasswordRequest,
        user: User = Depends(get_current_user),
        db: AsyncSession = Depends(get_db)):
    res_change_pwd = await users.change_password(db, user, password_data.old_password, password_data.new_password)
    if not res_change_pwd:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="旧密码错误")

    await users.invalidate_user_tokens(db, user.id)
    return success_response(message="修改密码成功，请重新登录")
