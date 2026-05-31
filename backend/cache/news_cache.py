# 新闻相关的缓存方法：新闻分类的读取和写入
# key - value
import random
from typing import List, Dict, Any, Optional

from config.cache_conf import get_json_cache, set_cache

CATEGORIES_KEY = "news:categories"
NEWS_LIST_PREFIX = "news_list:"
NEWS_DETAIL_PREFIX = "news:detail:"
RELATED_NEWS_PREFIX = "news:related:"


# 获取新闻分类缓存
async def get_cached_categories():
    return await get_json_cache(CATEGORIES_KEY)


# 写入新闻分类缓存: 缓存的数据, 过期时间
# 分类、配置 7200；列表： 600； 详情： 1800；验证码：120 -- 数据越稳定，缓存越持久
# 避免所有key同时过期 引起缓存雪崩
async def set_cache_categories(data: List[Dict[str, Any]], expire: int = 7200):
    # 随机偏移 ±600 秒，防止缓存雪崩
    jitter = random.randint(-600, 600)
    actual_expire = max(300, expire + jitter)
    return await set_cache(CATEGORIES_KEY, data, actual_expire)


# 写入缓存-新闻列表 key = news_list:分类id:页码:每页数量:关键字  + 列表数据 + 过期时间
async def set_cache_news_list(category_id: Optional[int], page: int, size: int, news_list: List[Dict[str, Any]], expire: int = 1800, keyword: Optional[str] = None):
    # 随机偏移 ±300 秒，防止缓存雪崩
    jitter = random.randint(-300, 300)
    actual_expire = max(60, expire + jitter)
    # 调用 封装的 Redis 的设置方法，存新闻列表到缓存
    category_part = category_id if category_id is not None else "all"
    keyword_part = keyword if keyword else ""
    key = f"{NEWS_LIST_PREFIX}{category_part}:{page}:{size}:{keyword_part}"
    return await set_cache(key, news_list, actual_expire)


# 读取缓存-新闻列表
async def get_cache_news_list(category_id: Optional[int], page: int, size: int, keyword: Optional[str] = None):
    category_part = category_id if category_id is not None else "all"
    keyword_part = keyword if keyword else ""
    key = f"{NEWS_LIST_PREFIX}{category_part}:{page}:{size}:{keyword_part}"
    return await get_json_cache(key)


async def get_cached_news_detail(news_id: int) -> Optional[Dict[str, Any]]:
    """
    获取缓存的新闻详情

    Args:
        news_id: 新闻ID

    Returns:
        Optional[Dict[str, Any]]: 新闻数据，不存在则返回None
    """
    key = f"{NEWS_DETAIL_PREFIX}{news_id}"
    return await get_json_cache(key)


async def cache_news_detail(news_id: int, news_data: Dict[str, Any], expire: int = 300) -> bool:
    """
    缓存新闻详情

    Args:
        news_id: 新闻ID
        news_data: 新闻数据字典
        expire: 过期时间（秒），默认5分钟

    Returns:
        bool: 缓存成功返回True
    """
    # 随机偏移 ±60 秒，防止缓存雪崩
    jitter = random.randint(-60, 60)
    actual_expire = max(60, expire + jitter)
    key = f"{NEWS_DETAIL_PREFIX}{news_id}"
    return await set_cache(key, news_data, actual_expire)


async def cache_related_news(news_id: int, category_id: int, related_list: List[Dict[str, Any]], expire: int = 1800) -> bool:
    """
    缓存相关新闻列表

    Args:
        news_id: 当前新闻ID
        category_id: 新闻分类ID
        related_list: 相关新闻列表数据
        expire: 过期时间（秒）

    Returns:
        bool: 缓存成功返回True
    """
    # 随机偏移 ±300 秒，防止缓存雪崩
    jitter = random.randint(-300, 300)
    actual_expire = max(60, expire + jitter)
    key = f"{RELATED_NEWS_PREFIX}{news_id}:{category_id}"
    return await set_cache(key, related_list, actual_expire)


async def get_cached_related_news(news_id: int, category_id: int) -> Optional[List[Dict[str, Any]]]:
    """
    获取缓存的相关新闻列表

    Args:
        news_id: 当前新闻ID
        category_id: 新闻分类ID

    Returns:
        Optional[List[Dict[str, Any]]]: 相关新闻列表数据，不存在则返回None
    """
    key = f"{RELATED_NEWS_PREFIX}{news_id}:{category_id}"
    return await get_json_cache(key)


# ── 缓存失效函数 ──────────────────────────────────────────────

async def invalidate_categories_cache():
    """删除新闻分类缓存"""
    await _delete_key(CATEGORIES_KEY)


async def invalidate_news_list_cache(category_id: Optional[int] = None):
    """删除新闻列表缓存。指定 category_id 则只删除该分类，否则全部"""
    if category_id is not None:
        pattern = f"{NEWS_LIST_PREFIX}{category_id}:*"
    else:
        pattern = f"{NEWS_LIST_PREFIX}*"
    await _delete_pattern(pattern)


async def invalidate_news_detail_cache(news_id: int):
    """删除指定新闻的详情缓存"""
    key = f"{NEWS_DETAIL_PREFIX}{news_id}"
    await _delete_key(key)


async def invalidate_related_news_cache(news_id: int, category_id: int):
    """删除指定新闻的相关新闻缓存"""
    key = f"{RELATED_NEWS_PREFIX}{news_id}:{category_id}"
    await _delete_key(key)


async def _delete_key(key: str):
    """删除单个缓存键"""
    from config.cache_conf import redis_client
    try:
        await redis_client.delete(key)
    except Exception:
        pass


async def _delete_pattern(pattern: str):
    """按模式批量删除缓存键（使用非阻塞 scan_iter）"""
    from config.cache_conf import redis_client
    try:
        async for key in redis_client.scan_iter(match=pattern):
            await redis_client.delete(key)
    except Exception:
        pass