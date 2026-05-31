from sqlalchemy.ext.asyncio import AsyncSession

from crud import history as history_crud


class HistoryService:
    """浏览历史业务逻辑层"""

    def __init__(self, db: AsyncSession):
        self.db = db

    async def add_history(self, user_id: int, news_id: int):
        return await history_crud.add_history(self.db, user_id, news_id)

    async def get_history_list(self, user_id: int, page: int, page_size: int):
        rows, total = await history_crud.get_history_list(self.db, user_id, page, page_size)
        has_more = total > page * page_size
        return rows, total, has_more

    async def delete_history(self, user_id: int, news_id: int) -> bool:
        return await history_crud.delete_history(self.db, user_id, news_id)

    async def clear_history(self, user_id: int) -> int:
        return await history_crud.clear_history(self.db, user_id)
