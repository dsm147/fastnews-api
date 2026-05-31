import uuid
from datetime import datetime, timedelta

from fastapi import HTTPException
from sqlalchemy import select, update, delete
from sqlalchemy.ext.asyncio import AsyncSession

from config.settings import settings
from models.users import User, UserToken
from schemas.users import UserRequest, UserUpdateRequest
from utils import security, jwt as jwt_utils


# 根据用户名查询数据库
async def get_user_by_username(db: AsyncSession, username: str):
    query = select(User).where(User.username == username)
    result = await db.execute(query)
    return result.scalar_one_or_none()


# 根据 ID 查询用户
async def get_user_by_id(db: AsyncSession, user_id: int):
    query = select(User).where(User.id == user_id)
    result = await db.execute(query)
    return result.scalar_one_or_none()


# 创建用户
async def create_user(db: AsyncSession, user_data: UserRequest):
    hashed_password = security.get_hash_password(user_data.password)
    user = User(username=user_data.username, password=hashed_password)
    db.add(user)
    await db.commit()
    await db.refresh(user)
    return user


# 生成 Access Token（JWT，无状态）
async def create_access_token(user_id: int) -> str:
    return jwt_utils.create_access_token({"user_id": user_id})


# 生成 Refresh Token（JWT，存入 DB 用于撤销）
async def create_refresh_token(db: AsyncSession, user_id: int) -> str:
    token = jwt_utils.create_refresh_token({"user_id": user_id})
    expires_at = datetime.now() + timedelta(days=settings.refresh_token_expire_days)
    query = select(UserToken).where(UserToken.user_id == user_id)
    result = await db.execute(query)
    user_token = result.scalar_one_or_none()

    if user_token:
        user_token.token = token
        user_token.expires_at = expires_at
    else:
        user_token = UserToken(user_id=user_id, token=token, expires_at=expires_at)
        db.add(user_token)
    await db.commit()
    return token


async def authenticate_user(db: AsyncSession, username: str, password: str):
    user = await get_user_by_username(db, username)
    if not user:
        return None
    if not security.verify_password(password, user.password):
        return None
    return user


# 更新用户信息
async def update_user(db: AsyncSession, username: str, user_data: UserUpdateRequest):
    query = update(User).where(User.username == username).values(**user_data.model_dump(
        exclude_unset=True
    ))
    result = await db.execute(query)
    await db.commit()

    if result.rowcount == 0:
        raise HTTPException(status_code=404, detail="用户不存在")

    updated_user = await get_user_by_username(db, username)
    return updated_user


# 修改密码
async def change_password(db: AsyncSession, user: User, old_password: str, new_password: str):
    if not security.verify_password(old_password, user.password):
        return False

    hashed_new_pwd = security.get_hash_password(new_password)
    user.password = hashed_new_pwd
    db.add(user)
    await db.commit()
    await db.refresh(user)
    return True


async def invalidate_user_tokens(db: AsyncSession, user_id: int):
    """使指定用户的所有 Token 失效（删除所有 Token 记录）"""
    stmt = delete(UserToken).where(UserToken.user_id == user_id)
    result = await db.execute(stmt)
    await db.commit()
    return result.rowcount
