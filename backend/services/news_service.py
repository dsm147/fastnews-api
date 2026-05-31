from typing import Optional

from fastapi.encoders import jsonable_encoder
from sqlalchemy.ext.asyncio import AsyncSession

from cache.news_cache import (
    get_cached_categories, set_cache_categories,
    get_cache_news_list, set_cache_news_list,
    get_cached_news_detail, cache_news_detail,
    get_cached_related_news, cache_related_news,
)
from crud import news as news_crud
from models.news import News
from schemas.base import NewsItemBase
from schemas.news import NewsDetailResponse, RelatedNewsResponse


class NewsService:
    """新闻业务逻辑层，封装缓存决策和数据组装"""

    def __init__(self, db: AsyncSession):
        self.db = db

    async def get_categories(self, skip: int = 0, limit: int = 100):
        cached = await get_cached_categories()
        if cached:
            return cached

        categories = await news_crud.get_categories(self.db, skip, limit)
        if categories:
            categories = jsonable_encoder(categories)
            await set_cache_categories(categories)
        return categories

    async def get_news_list(
        self,
        category_id: int,
        page: int = 1,
        page_size: int = 10,
        keyword: Optional[str] = None,
    ):
        offset = (page - 1) * page_size

        # 尝试缓存
        cached_list = await get_cache_news_list(category_id, page, page_size, keyword)
        if cached_list:
            news_list = [News(**item) for item in cached_list]
        else:
            raw_list = await news_crud.get_news_list(self.db, category_id, offset, page_size, keyword)
            if raw_list:
                news_data = [
                    NewsItemBase.model_validate(item).model_dump(mode="json", by_alias=False)
                    for item in raw_list
                ]
                await set_cache_news_list(category_id, page, page_size, news_data, keyword=keyword)
            news_list = raw_list

        total = await news_crud.get_news_count(self.db, category_id, keyword)
        has_more = (offset + len(news_list)) < total
        return news_list, total, has_more

    async def get_news_detail(self, news_id: int):
        # 缓存命中
        cached = await get_cached_news_detail(news_id)
        if cached:
            news_obj = News(**cached)
        else:
            news_obj = await news_crud.get_news_detail(self.db, news_id)
            if news_obj:
                news_dict = NewsDetailResponse.model_validate(news_obj).model_dump(
                    by_alias=False, mode="json", exclude={"related_news"}
                )
                await cache_news_detail(news_id, news_dict)

        if not news_obj:
            return None, []

        # 增加浏览量
        await news_crud.increase_news_views(self.db, news_obj.id)

        # 相关新闻
        related = await self._get_related_news(news_obj.id, news_obj.category_id)

        return news_obj, related

    async def _get_related_news(self, news_id: int, category_id: int, limit: int = 5):
        cached = await get_cached_related_news(news_id, category_id)
        if cached:
            return cached

        related = await news_crud.get_related_news(self.db, news_id, category_id, limit)
        if related:
            related_data = [
                RelatedNewsResponse.model_validate(item).model_dump(by_alias=False, mode="json")
                for item in related
            ]
            await cache_related_news(news_id, category_id, related_data)
            return related_data
        return []

    async def get_news_count(self, category_id: int, keyword: Optional[str] = None) -> int:
        return await news_crud.get_news_count(self.db, category_id, keyword)
