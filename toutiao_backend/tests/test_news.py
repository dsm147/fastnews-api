import pytest


class TestNewsCategories:

    async def test_get_categories(self, async_client):
        """获取新闻分类列表"""
        response = await async_client.get("/api/v1/news/categories")
        assert response.status_code == 200
        data = response.json()
        assert data["code"] == 200
        assert isinstance(data["data"], list)


class TestNewsListPagination:

    @pytest.mark.parametrize("page,page_size,expected_status", [
        (1, 10, 200),
        (-1, 10, 422),
        (1, 200, 422),
        (0, 10, 422),
    ])
    async def test_pagination_validation(
        self, async_client, page, page_size, expected_status
    ):
        """测试分页参数的校验"""
        response = await async_client.get(
            f"/api/v1/news/list?categoryId=1&page={page}&pageSize={page_size}"
        )
        assert response.status_code == expected_status
