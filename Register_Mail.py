import requests
import hashlib
import json
import time
import random
import string
import os

# 接口地址与配置
REGISTER_URL = "https://sitlotteryapi.22889.club/api/webapi/Register"
REGISTER_LOG_FILE = "D:/figo/工具/pycharm/PycharmProjects/Login登陆并提取Token/email_list.txt"
DOMAIN_URL = "sitweb.22889.club"
PASSWORD = "q123q123"

# === 基础工具函数 ===

def generate_email(index: int) -> str:
    return f"fly{index:03d}@gmail.com"

def get_random_str(length=32) -> str:
    return ''.join(random.choices(string.ascii_lowercase + string.digits, k=length))

def get_timestamp() -> int:
    return int(time.time())

def generate_device_id() -> str:
    return ''.join(random.choices('0123456789abcdef', k=32))

def generate_firebase_token() -> str:
    return 'auto_' + ''.join(random.choices(string.ascii_letters + string.digits, k=80))

def generate_signature(payload: dict) -> str:
    filtered = {k: v for k, v in payload.items() if k not in ["signature", "timestamp"] and v not in ["", None, [], {}]}
    sorted_str = json.dumps(dict(sorted(filtered.items())), separators=(',', ':'), ensure_ascii=False)
    print(f"🔏 签名字符串: {sorted_str}")
    return hashlib.md5(sorted_str.encode("utf-8")).hexdigest().upper()

# === 构建请求体 ===

def build_register_payload(email: str) -> dict:
    payload = {
        "username": email,
        "smsvcode": "",
        "registerType": "email",
        "pwd": PASSWORD,
        "invitecode": "",
        "domainurl": DOMAIN_URL,
        "phonetype": 2,
        "captchaId": "",
        "track": "",
        "deviceId": generate_device_id(),
        "fireBaseToken": generate_firebase_token(),
        "language": 0,
        "random": get_random_str(),
        "timestamp": get_timestamp()
    }
    payload["signature"] = generate_signature(payload)
    return payload

# === 写入邮箱到日志（仅成功写入） ===

def save_email(email: str):
    os.makedirs(os.path.dirname(REGISTER_LOG_FILE), exist_ok=True)
    with open(REGISTER_LOG_FILE, "a", encoding="utf-8") as f:
        f.write(email + "\n")

# === 注册 ===

def register_user(email: str, retry: bool = True) -> bool:
    print(f"\n📧 尝试注册: {email}")
    payload = build_register_payload(email)
    headers = {"Content-Type": "application/json"}

    try:
        start = time.perf_counter()
        response = requests.post(REGISTER_URL, json=payload, headers=headers)
        elapsed = (time.perf_counter() - start) * 1000

        res_json = response.json()
        print(f"📨 响应: {json.dumps(res_json, indent=2, ensure_ascii=False)}")
        print(f"⏱ 耗时: {elapsed:.2f} ms")

        code = res_json.get("code", -1)
        msg = res_json.get("msg", "")

        if code == 0:
            print(f"✅ 注册成功: {email}")
            save_email(email)
            return True
        elif "already" in msg.lower():
            print(f"⚠️ 邮箱已注册: {email}，跳过写入")
            return False
        elif "frequently" in msg.lower() and retry:
            print("⏳ 访问频繁，等待 5 秒重试中...")
            time.sleep(5)
            return register_user(email, retry=False)
        else:
            print(f"❌ 注册失败: {msg}")
            return False
    except Exception as e:
        print(f"❗ 请求异常: {str(e)}")
        return False

# === 批量注册 ===

def batch_register(count: int = 10, start_index: int = 1):
    success = 0
    for i in range(start_index, start_index + count):
        email = generate_email(i)
        if register_user(email):
            success += 1
        time.sleep(random.uniform(1.8, 3.0))  # 延迟控制
    print(f"\n📊 注册完成，总数: {count}，成功: {success}，失败: {count - success}")

# === 程序入口 ===

if __name__ == "__main__":
    batch_register(count=10, start_index=1)  # 修改注册数量和起始序号
