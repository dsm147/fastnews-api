"""收藏模块测试"""
from datetime import datetime

import pytest

from models.news import Category, News
from tests.conftest import TestSessionLocal


@pytest.fixture(autouse=True)
async def setup_news_data():
    """每个测试前插入测试新闻数据"""
    async with TestSessionLocal() as session:
        # 添加测试分类
        category = Category(name="测试分类", sort_order=1)
        session.add(category)
        await session.flush()

        # 添加测试新闻
        for i in range(1, 6):
            news = News(
                category_id=category.id,
                title=f"测试新闻{i}",
                content=f"测试新闻内容{i}",
                author="测试作者",
                views=0,
                publish_time=datetime.now()
            )
            session.add(news)
        await session.commit()


@pytest.fixture
async def auth_header(async_client):
    """注册并登录测试用户，返回认证请求头"""
    username = "favtestuser"
    await async_client.post(
        "/api/v1/user/register",
        json={"username": username, "password": "123456"}
    )
    resp = await async_client.post(
        "/api/v1/user/login",
        json={"username": username, "password": "123456"}
    )
    token = resp.json()["data"]["accessToken"]
    return {"Authorization": f"Bearer {token}"}


class TestFavorite:
    """收藏接口测试"""

    async def test_check_not_logged_in(self, async_client):
        """未登录时检查收藏应返回 422"""
        resp = await async_client.get("/api/v1/favorite/check?newsId=1")
        assert resp.status_code == 422

    async def test_check_not_favorited(self, async_client, auth_header):
        """检查未收藏的新闻"""
        resp = await async_client.get(
            "/api/v1/favorite/check?newsId=999",
            headers=auth_header
        )
        assert resp.status_code == 200
        data = resp.json()
        assert data["code"] == 200
        assert data["data"]["isFavorite"] is False

    async def test_add_favorite(self, async_client, auth_header):
        """添加收藏"""
        resp = await async_client.post(
            "/api/v1/favorite/add",
            json={"newsId": 1},
            headers=auth_header
        )
        assert resp.status_code == 200
        data = resp.json()
        assert data["code"] == 200

    async def test_add_favorite_twice(self, async_client, auth_header):
        """重复添加收藏应返回 400"""
        await async_client.post(
            "/api/v1/favorite/add",
            json={"newsId": 1},
            headers=auth_header
        )
        resp = await async_client.post(
            "/api/v1/favorite/add",
            json={"newsId": 1},
            headers=auth_header
        )
        assert resp.status_code == 400

    async def test_check_favorited(self, async_client, auth_header):
        """添加后检查收藏状态应为 true"""
        await async_client.post(
            "/api/v1/favorite/add",
            json={"newsId": 1},
            headers=auth_header
        )
        resp = await async_client.get(
            "/api/v1/favorite/check?newsId=1",
            headers=auth_header
        )
        assert resp.status_code == 200
        assert resp.json()["data"]["isFavorite"] is True

    async def test_remove_favorite(self, async_client, auth_header):
        """取消收藏"""
        await async_client.post(
            "/api/v1/favorite/add",
            json={"newsId": 1},
            headers=auth_header
        )
        resp = await async_client.delete(
            "/api/v1/favorite/remove?newsId=1",
            headers=auth_header
        )
        assert resp.status_code == 200
        # 验证已取消
        resp = await async_client.get(
            "/api/v1/favorite/check?newsId=1",
            headers=auth_header
        )
        assert resp.json()["data"]["isFavorite"] is False

    async def test_remove_nonexistent(self, async_client, auth_header):
        """取消不存在的收藏应返回 404"""
        resp = await async_client.delete(
            "/api/v1/favorite/remove?newsId=999",
            headers=auth_header
        )
        assert resp.status_code == 404

    async def test_favorite_list(self, async_client, auth_header):
        """收藏列表"""
        await async_client.post(
            "/api/v1/favorite/add",
            json={"newsId": 1},
            headers=auth_header
        )
        resp = await async_client.get(
            "/api/v1/favorite/list",
            headers=auth_header
        )
        assert resp.status_code == 200
        data = resp.json()
        assert data["code"] == 200
        assert len(data["data"]["list"]) > 0
        assert data["data"]["total"] > 0

    async def test_clear_favorites(self, async_client, auth_header):
        """清空收藏"""
        await async_client.post(
            "/api/v1/favorite/add",
            json={"newsId": 1},
            headers=auth_header
        )
        resp = await async_client.delete(
            "/api/v1/favorite/clear",
            headers=auth_header
        )
        assert resp.status_code == 200
        # 验证列表为空
        resp = await async_client.get(
            "/api/v1/favorite/list",
            headers=auth_header
        )
        assert resp.json()["data"]["total"] == 0
