import asyncio
import json
from typing import Any

import redis.asyncio as redis
from loguru import logger
from config.settings import settings


# 创建 Redis 的连接对象
redis_client = redis.Redis(
    host=settings.redis_host,  # Redis 服务器的主机地址
    port=settings.redis_port,  # Redis 端口号
    db=settings.redis_db,  # Redis 数据库编号，0~15
    decode_responses=True,  # 是否将字节数据解码为字符串
    socket_connect_timeout=2,  # 连接超时（秒）
    socket_timeout=5,  # 读写超时（秒）
    retry_on_timeout=False,
)


# 设置 和 读取（字符串 和 列表或字典）"[{}]"
# 读取：字符串
async def get_cache(key: str):
    result = await _redis_call(redis_client.get, key)
    return result


# 读取：列表或字典
async def get_json_cache(key: str):
    data = await _redis_call(redis_client.get, key)
    if data:
        return json.loads(data)
    return None


# Redis 操作超时（秒）
_REDIS_TIMEOUT = 3


async def _redis_call(method, *args, **kwargs):
    """带超时的 Redis 调用，防止连接挂起"""
    try:
        return await asyncio.wait_for(
            method(*args, **kwargs),
            timeout=_REDIS_TIMEOUT
        )
    except asyncio.TimeoutError:
        logger.warning(f"Redis 操作超时: {method.__name__}")
        return None
    except Exception as e:
        logger.warning(f"Redis 操作失败: {e}")
        return None


# 设置缓存 setex(key, expire, value)
async def set_cache(key: str, value: Any, expire: int = 3600):
    if isinstance(value, (dict, list)):
        value = json.dumps(value, ensure_ascii=False)
    result = await _redis_call(redis_client.setex, key, expire, value)
    return result is not None
