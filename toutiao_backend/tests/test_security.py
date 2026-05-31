from utils.security import get_hash_password, verify_password


class TestPasswordSecurity:
    """密码加密和验证的单元测试"""

    def test_hash_password_returns_string(self):
        """加密后的密码应该是字符串"""
        hashed = get_hash_password("123456")
        assert isinstance(hashed, str)
        assert len(hashed) > 10

    def test_hash_password_is_different_each_time(self):
        """每次加密结果应该不同（因为有随机 salt）"""
        hash1 = get_hash_password("123456")
        hash2 = get_hash_password("123456")
        assert hash1 != hash2

    def test_verify_password_correct(self):
        """正确密码应该验证通过"""
        hashed = get_hash_password("123456")
        assert verify_password("123456", hashed) is True

    def test_verify_password_wrong(self):
        """错误密码应该验证失败"""
        hashed = get_hash_password("123456")
        assert verify_password("wrong", hashed) is False

    def test_verify_password_empty(self):
        """空密码应该验证失败"""
        hashed = get_hash_password("123456")
        assert verify_password("", hashed) is False
