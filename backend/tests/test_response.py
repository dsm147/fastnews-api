import json

from pydantic import BaseModel
from utils.response import success_response


class SampleModel(BaseModel):
    id: int
    name: str


class TestSuccessResponse:

    async def test_response_with_dict(self):
        """测试返回字典数据"""
        resp = success_response(data={"id": 1, "name": "测试"})
        data = json.loads(resp.body)

        assert resp.status_code == 200
        assert data["code"] == 200
        assert data["message"] == "success"
        assert data["data"]["name"] == "测试"

    async def test_response_with_pydantic(self):
        """测试返回 Pydantic 对象"""
        model = SampleModel(id=1, name="Pydantic测试")
        resp = success_response(data=model)
        data = json.loads(resp.body)

        assert data["data"]["id"] == 1
        assert data["data"]["name"] == "Pydantic测试"

    async def test_response_with_none(self):
        """测试返回 None"""
        resp = success_response(data=None)
        data = json.loads(resp.body)

        assert data["data"] is None

    async def test_response_custom_message(self):
        """测试自定义消息"""
        resp = success_response(message="操作成功", data="ok")
        data = json.loads(resp.body)

        assert data["message"] == "操作成功"
