from fastapi import HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from starlette import status

from crud import users as users_crud
from models.users import User
from schemas.users import UserRequest, UserUpdateRequest


class UserService:
    """用户业务逻辑层"""

    def __init__(self, db: AsyncSession):
        self.db = db

    async def register(self, user_data: UserRequest):
        existing = await users_crud.get_user_by_username(self.db, user_data.username)
        if existing:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="用户已存在")
        user = await users_crud.create_user(self.db, user_data)
        access_token = await users_crud.create_access_token(user.id)
        refresh_token = await users_crud.create_refresh_token(self.db, user.id)
        return user, access_token, refresh_token

    async def login(self, user_data: UserRequest):
        user = await users_crud.authenticate_user(self.db, user_data.username, user_data.password)
        if not user:
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="用户名或密码错误")
        access_token = await users_crud.create_access_token(user.id)
        refresh_token = await users_crud.create_refresh_token(self.db, user.id)
        return user, access_token, refresh_token

    async def update_user_info(self, user: User, user_data: UserUpdateRequest):
        return await users_crud.update_user(self.db, user.username, user_data)

    async def change_password(self, user: User, old_password: str, new_password: str):
        success = await users_crud.change_password(self.db, user, old_password, new_password)
        if not success:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="旧密码错误")
        await users_crud.invalidate_user_tokens(self.db, user.id)
