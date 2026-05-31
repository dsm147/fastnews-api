class TestAuth:

    async def test_no_auth_header(self, async_client):
        """无请求头返回 422"""
        response = await async_client.get("/api/user/info")
        assert response.status_code == 422

    async def test_invalid_format(self, async_client):
        """请求头格式错误（缺少 Bearer）返回 401"""
        response = await async_client.get(
            "/api/user/info",
            headers={"Authorization": "invalid-token"}
        )
        assert response.status_code == 401

    async def test_empty_token(self, async_client):
        """空 Token 返回 401"""
        response = await async_client.get(
            "/api/user/info",
            headers={"Authorization": "Bearer "}
        )
        assert response.status_code == 401

    async def test_fake_token(self, async_client):
        """伪造 Token 返回 401"""
        response = await async_client.get(
            "/api/user/info",
            headers={"Authorization": "Bearer fake_token_12345"}
        )
        assert response.status_code == 401
