#适用于后端 API 测试
import unittest
import requests

class TestLoginFunction(unittest.TestCase):
    BASE_URL = "https://arcloud.top/Admin_UERP/Index"  # 替换为你的登录接口 URL

    def test_login_success(self):
        """测试正确的用户名和密码"""
        data = {
            "username": "admin",
            "pwd": "123456"
        }
        response = requests.post(f"{self.BASE_URL}/login", json=data)
        self.assertEqual(response.status_code, 200)
        self.assertIn("token", response.json())

    def test_login_wrong_pwd(self):
        """测试错误的密码"""
        data = {
            "username": "testuser",
            "pwd": "wrong_password"
        }
        response = requests.post(f"{self.BASE_URL}/login", json=data)
        self.assertEqual(response.status_code, 401)
        self.assertIn("error", response.json())

    def test_login_user_not_exist(self):
        """测试不存在的用户"""
        data = {
            "username": "nonexistent_user",
            "pwd": "password"
        }
        response = requests.post(f"{self.BASE_URL}/login", json=data)
        self.assertEqual(response.status_code, 404)
        self.assertIn("error", response.json())

if __name__ == "__main__":
    unittest.main()
