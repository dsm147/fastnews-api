from sqlalchemy.ext.asyncio import AsyncSession

from crud import favorite as favorite_crud


class FavoriteService:
    """收藏业务逻辑层"""

    def __init__(self, db: AsyncSession):
        self.db = db

    async def check_favorite(self, user_id: int, news_id: int) -> bool:
        return await favorite_crud.is_news_favorite(self.db, user_id, news_id)

    async def add_favorite(self, user_id: int, news_id: int):
        return await favorite_crud.add_news_favorite(self.db, user_id, news_id)

    async def remove_favorite(self, user_id: int, news_id: int) -> bool:
        return await favorite_crud.remove_news_favorite(self.db, user_id, news_id)

    async def get_favorite_list(self, user_id: int, page: int, page_size: int):
        rows, total = await favorite_crud.get_favorite_list(self.db, user_id, page, page_size)
        has_more = total > page * page_size
        return rows, total, has_more

    async def clear_favorites(self, user_id: int) -> int:
        return await favorite_crud.remove_all_favorites(self.db, user_id)
