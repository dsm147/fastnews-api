import pytest
from httpx import AsyncClient


class TestUserRegister:
    """用户注册接口测试"""

    async def test_register_success(self, async_client):
        """正常注册应该成功"""
        response = await async_client.post(
            "/api/v1/user/register",
            json={"username": "newuser", "password": "123456"}
        )
        assert response.status_code == 200
        data = response.json()
        assert data["code"] == 200
        assert isinstance(data["data"]["accessToken"], str)
        assert len(data["data"]["accessToken"]) > 0
        assert isinstance(data["data"]["refreshToken"], str)
        assert len(data["data"]["refreshToken"]) > 0
        assert data["data"]["userInfo"]["username"] == "newuser"

    async def test_register_short_password(self, async_client):
        """密码太短应该返回 422"""
        response = await async_client.post(
            "/api/v1/user/register",
            json={"username": "newuser", "password": "123"}
        )
        assert response.status_code == 422

    async def test_register_invalid_username(self, async_client):
        """用户名含特殊字符应该返回 422"""
        response = await async_client.post(
            "/api/v1/user/register",
            json={"username": "hello world!", "password": "123456"}
        )
        assert response.status_code == 422

    async def test_register_duplicate_username(self, async_client):
        """重复用户名应该返回 400"""
        await async_client.post(
            "/api/v1/user/register",
            json={"username": "dupuser", "password": "123456"}
        )
        response = await async_client.post(
            "/api/v1/user/register",
            json={"username": "dupuser", "password": "123456"}
        )
        assert response.status_code == 400
        assert "已存在" in response.json()["message"]


class TestUserLogin:
    """用户登录接口测试"""

    async def test_login_success(self, async_client):
        """正常登录应该成功"""
        # 先注册
        await async_client.post(
            "/api/v1/user/register",
            json={"username": "loginuser", "password": "123456"}
        )
        # 再登录
        response = await async_client.post(
            "/api/v1/user/login",
            json={"username": "loginuser", "password": "123456"}
        )
        assert response.status_code == 200
        data = response.json()
        assert data["code"] == 200
        assert isinstance(data["data"]["accessToken"], str)
        assert len(data["data"]["accessToken"]) > 0
        assert isinstance(data["data"]["refreshToken"], str)
        assert len(data["data"]["refreshToken"]) > 0

    async def test_login_wrong_password(self, async_client):
        """错误密码应该返回 401"""
        await async_client.post(
            "/api/v1/user/register",
            json={"username": "loginuser2", "password": "123456"}
        )
        response = await async_client.post(
            "/api/v1/user/login",
            json={"username": "loginuser2", "password": "wrong1"}
        )
        assert response.status_code == 401

    async def test_login_nonexistent_user(self, async_client):
        """不存在的用户应该返回 401"""
        response = await async_client.post(
            "/api/v1/user/login",
            json={"username": "nobody", "password": "123456"}
        )
        assert response.status_code == 401


@pytest.mark.parametrize("username,password,expected_status", [
    ("validuser", "123456", 200),
    ("a", "123456", 422),
    ("validuser", "123", 422),
    ("", "123456", 422),
    ("validuser", "", 422),
])
async def test_register_validation(async_client, username, password, expected_status):
    """参数化测试：注册校验"""
    response = await async_client.post(
        "/api/v1/user/register",
        json={"username": username, "password": password}
    )
    assert response.status_code == expected_status
