"""
一提取登陆并提取Token
更新日期: 2025/07/09
作者: Figo
"""

import hashlib
import json
import random
import time
import requests
import os

# === 配置项 ===
LOGIN_URL = "https://sitlotteryapi.22889.club/api/webapi/Login"  # 登录接口地址
TOKEN_FILE = "D:/figo/工具/pycharm/PycharmProjects/WOS/saveTokens.csv"  # Token 保存路径
USERNAME_FILE = "D:/figo/工具/Jmeter/Srcipt/0716.txt"  # 用户名文件路径
TARGET_USER_COUNT = 5  # 最多处理的用户名数量

# === 工具函数 ===

def get_random_username() -> str:
    """生成12位纯数字用户名（首位不为0）"""
    return str(random.randint(1_000_000_000_000, 9_999_999_999_999))

def get_random_str(length: int) -> str:
    """生成指定长度的随机字符串（数字+小写字母）"""
    return ''.join(random.choices('abcdefghijklmnopqrstuvwxyz1234567890', k=length))

def get_current_timestamp() -> str:
    """返回当前秒级时间戳字符串"""
    return str(int(time.time()))[-10:]

def md5_info(data, length=32) -> str:
    """返回数据的MD5哈希值（大写十六进制）"""
    if isinstance(data, dict):
        data = json.dumps(data, separators=(',', ':'))
    return hashlib.md5(data.encode('utf-8')).hexdigest().upper()[:length]

def sort_object_keys(obj: dict) -> str:
    """将字典按键排序后转为JSON字符串"""
    return json.dumps({k: obj[k] for k in sorted(obj)}, separators=(',', ':'))

def get_signature(json_body: dict) -> str:
    """根据请求参数生成签名（排除signature和timestamp字段）"""
    filtered = {k: v for k, v in json_body.items() if k not in ['signature', 'timestamp'] and v not in [None, "", []]}
    return md5_info(sort_object_keys(filtered))

# === 登录逻辑 ===

def generate_login_data(username: str) -> dict:
    """生成登录请求体"""
    return {
        "language": 0,
        "logintype": "mobile",
        "phonetype": 0,
        "pwd": "q123q123",
        "random": get_random_str(32),
        "timestamp": get_current_timestamp(),
        "signature": "",
        "username": username
    }

def login_user(username: str) -> bool:
    """执行登录请求并写入Token，返回是否成功"""
    data = generate_login_data(username)
    data["signature"] = get_signature(data)

    try:
        response = requests.post(LOGIN_URL, json=data, headers={"Content-Type": "application/json"}, timeout=10)

        if response.status_code != 200:
            print(f"❌ 登录失败（HTTP错误）: {username}，状态码: {response.status_code}")
            return False

        response_data = response.json()
        print(f"📩 响应: {response_data.get('msg', '')}")

        if response_data.get("code") == 0:
            token = response_data.get("data", {}).get("token")
            if token:
                full_token = f"Bearer {token}"
                save_token_to_file(full_token)
                print(f"✅ 登录成功: {username}")
                print(f"📄 Token 写入成功: {full_token}")
                return True
            else:
                print(f"⚠️ 登录成功但未提取到token: {username}")
        else:
            print(f"❌ 登录失败: {username}, 错误: {response_data.get('msg')}")
    except Exception as e:
        print(f"🚨 异常: {username}，{e}")
    return False

# === 文件操作 ===

def save_token_to_file(token: str):
    """保存Token到文件，确保首行为空"""
    try:
        if not os.path.exists(TOKEN_FILE):
            with open(TOKEN_FILE, "w", encoding="utf-8") as f:
                f.write("\n")

        with open(TOKEN_FILE, "r+", encoding="utf-8") as f:
            lines = f.readlines()
            if not lines or (lines and lines[0].strip() != ""):
                lines.insert(0, "\n")
                f.seek(0)
                f.writelines(lines)

        with open(TOKEN_FILE, "a", encoding="utf-8") as f:
            f.write(token + "\n")
    except Exception as e:
        print(f"❌ 写入Token失败: {e}")

def read_usernames_from_file(filename: str) -> list[str]:
    """读取用户名列表"""
    try:
        with open(filename, "r", encoding="utf-8") as f:
            usernames = [line.strip() for line in f if line.strip()]
        print(f"📥 共读取 {len(usernames)} 个用户名")
        return usernames
    except Exception as e:
        print(f"❌ 无法读取用户名文件: {e}")
        return []

# === 主执行逻辑 ===

def simulate_multiple_logins(usernames: list[str]):
    """批量执行登录请求并统计成功/失败数量"""
    success_count = 0
    fail_count = 0

    for idx, username in enumerate(usernames, 1):
        print(f"\n🔁 正在登录第 {idx} 个用户: {username}")
        if login_user(username):
            success_count += 1
        else:
            fail_count += 1
        time.sleep(0.1)  # 避免过快请求被风控

    print("\n====== 📊 登录统计结果 ======")
    print(f"✅ 成功登录数: {success_count}")
    print(f"❌ 登录失败数: {fail_count}")
    print(f"📌 总计用户数: {len(usernames)}")
    print("===================================")

# === 程序入口 ===

if __name__ == "__main__":
    usernames = read_usernames_from_file(USERNAME_FILE)[:TARGET_USER_COUNT]
    if usernames:
        simulate_multiple_logins(usernames)
    else:
        print("⚠️ 用户名列表为空，程序终止")
