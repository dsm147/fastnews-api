"""浏览历史模块测试"""
from datetime import datetime

import pytest

from models.news import Category, News
from tests.conftest import TestSessionLocal


@pytest.fixture(autouse=True)
async def setup_news_data():
    """每个测试前插入测试新闻数据"""
    async with TestSessionLocal() as session:
        category = Category(name="测试分类", sort_order=1)
        session.add(category)
        await session.flush()

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
    username = "histtestuser"
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


class TestHistory:
    """浏览历史接口测试"""

    async def test_add_history(self, async_client, auth_header):
        """添加浏览记录"""
        resp = await async_client.post(
            "/api/v1/history/add",
            json={"newsId": 1},
            headers=auth_header
        )
        assert resp.status_code == 200
        assert resp.json()["code"] == 200

    async def test_add_history_duplicate(self, async_client, auth_header):
        """重复添加同一条新闻（应更新浏览时间，不报错）"""
        await async_client.post(
            "/api/v1/history/add",
            json={"newsId": 1},
            headers=auth_header
        )
        resp = await async_client.post(
            "/api/v1/history/add",
            json={"newsId": 1},
            headers=auth_header
        )
        assert resp.status_code == 200

    async def test_history_list(self, async_client, auth_header):
        """获取浏览历史列表"""
        await async_client.post(
            "/api/v1/history/add",
            json={"newsId": 1},
            headers=auth_header
        )
        resp = await async_client.get(
            "/api/v1/history/list",
            headers=auth_header
        )
        assert resp.status_code == 200
        data = resp.json()
        assert data["code"] == 200
        assert len(data["data"]["list"]) > 0
        assert data["data"]["total"] > 0

    async def test_history_list_pagination(self, async_client, auth_header):
        """浏览历史分页"""
        for news_id in range(1, 5):
            await async_client.post(
                "/api/v1/history/add",
                json={"newsId": news_id},
                headers=auth_header
            )
        # 第一页 2 条
        resp = await async_client.get(
            "/api/v1/history/list?page=1&pageSize=2",
            headers=auth_header
        )
        data = resp.json()
        assert len(data["data"]["list"]) == 2
        assert data["data"]["total"] == 4
        assert data["data"]["hasMore"] is True

        # 第二页
        resp = await async_client.get(
            "/api/v1/history/list?page=2&pageSize=2",
            headers=auth_header
        )
        data = resp.json()
        assert len(data["data"]["list"]) == 2
        assert data["data"]["hasMore"] is False

    async def test_delete_history(self, async_client, auth_header):
        """删除单条浏览记录"""
        await async_client.post(
            "/api/v1/history/add",
            json={"newsId": 1},
            headers=auth_header
        )
        resp = await async_client.delete(
            "/api/v1/history/delete/1",
            headers=auth_header
        )
        assert resp.status_code == 200

    async def test_delete_nonexistent(self, async_client, auth_header):
        """删除不存在的记录应返回 404"""
        resp = await async_client.delete(
            "/api/v1/history/delete/999",
            headers=auth_header
        )
        assert resp.status_code == 404

    async def test_clear_history(self, async_client, auth_header):
        """清空浏览历史"""
        for news_id in range(1, 4):
            await async_client.post(
                "/api/v1/history/add",
                json={"newsId": news_id},
                headers=auth_header
            )
        resp = await async_client.delete(
            "/api/v1/history/clear",
            headers=auth_header
        )
        assert resp.status_code == 200

        # 验证列表为空
        resp = await async_client.get(
            "/api/v1/history/list",
            headers=auth_header
        )
        assert resp.json()["data"]["total"] == 0
