import asyncio

import pytest
from httpx import AsyncClient, ASGITransport
from sqlalchemy import MetaData
from sqlalchemy.ext.asyncio import async_sessionmaker, AsyncSession, create_async_engine

# 必须在导入 main 之前禁用 Rate Limiting（因为路由装饰器在 import 时执行）
from config.settings import settings
settings.rate_limit_enabled = False

from main import app
from config.db_conf import get_db
from models.news import Base as NewsBase
from models.users import Base as UsersBase
from models.favorite import Base as FavoriteBase
from models.history import Base as HistoryBase

# 创建 SQLite 内存引擎
TEST_DATABASE_URL = "sqlite+aiosqlite:///:memory:"

test_engine = create_async_engine(TEST_DATABASE_URL, echo=False)
TestSessionLocal = async_sessionmaker(
    bind=test_engine,
    class_=AsyncSession,
    expire_on_commit=False
)


@pytest.fixture(scope="session")
def event_loop():
    """整个会话共用一个事件循环"""
    loop = asyncio.new_event_loop()
    yield loop
    loop.close()


@pytest.fixture(autouse=True)
async def setup_database():
    """自动创建所有表，每个测试函数前创建，测试后清理"""
    # 合并所有模型的 metadata
    combined_metadata = MetaData()
    for base in [NewsBase, UsersBase, FavoriteBase, HistoryBase]:
        for table_name, table in base.metadata.tables.items():
            table.to_metadata(combined_metadata)

    # 创建所有表
    async with test_engine.begin() as conn:
        await conn.run_sync(combined_metadata.create_all)

    # 覆盖 get_db 依赖
    async def _get_test_db():
        async with TestSessionLocal() as session:
            try:
                yield session
                await session.commit()
            except Exception:
                await session.rollback()
                raise
            finally:
                await session.close()

    app.dependency_overrides[get_db] = _get_test_db

    yield

    # 清理
    app.dependency_overrides.clear()
    async with test_engine.begin() as conn:
        await conn.run_sync(combined_metadata.drop_all)


@pytest.fixture
async def async_client():
    """提供异步 HTTP 测试客户端"""
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        yield client
