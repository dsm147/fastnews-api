from typing import Optional

from fastapi import APIRouter, Depends, Query, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from config.db_conf import get_db
from services.news_service import NewsService
from utils.response import success_response

router = APIRouter(prefix="/api/v1/news", tags=["news"])


@router.get("/categories")
async def get_categories(skip: int = 0, limit: int = 100, db: AsyncSession = Depends(get_db)):
    service = NewsService(db)
    categories = await service.get_categories(skip, limit)
    return success_response(message="获取新闻分类成功", data=categories)


@router.get("/list")
async def get_news_list(
        category_id: int = Query(..., alias="categoryId"),
        page: int = Query(1, ge=1),
        page_size: int = Query(10, alias="pageSize", ge=1, le=100),
        keyword: Optional[str] = None,
        db: AsyncSession = Depends(get_db)
):
    service = NewsService(db)
    news_list, total, has_more = await service.get_news_list(category_id, page, page_size, keyword)
    return success_response(message="获取新闻列表成功", data={
        "list": news_list,
        "total": total,
        "hasMore": has_more
    })


@router.get("/detail")
async def get_news_detail(news_id: int = Query(..., alias="id"), db: AsyncSession = Depends(get_db)):
    service = NewsService(db)
    news_detail, related_news = await service.get_news_detail(news_id)
    if not news_detail:
        raise HTTPException(status_code=404, detail="新闻不存在")

    return success_response(message="success", data={
        "id": news_detail.id,
        "title": news_detail.title,
        "content": news_detail.content,
        "image": news_detail.image,
        "author": news_detail.author,
        "publishTime": news_detail.publish_time,
        "categoryId": news_detail.category_id,
        "views": news_detail.views,
        "relatedNews": related_news
    })
