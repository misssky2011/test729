import requests
import hashlib
import json
import time
import random
import string
import os

# 注册接口地址
REGISTER_URL = "https://sitlotteryapi.22889.club/api/webapi/Register"
OUTPUT_FILE = "D:/figo/工具/pycharm/PycharmProjects/Login登陆并提取Token(手机和邮箱注册)/mobile_list.txt"

# 固定字段配置
DOMAIN_URL = "sitweb.22889.club"
DEVICE_ID = "4332d3fc05b188232f6090a062055227"
FIREBASE_TOKEN = "cAjAxpfK3wtt_UmojJy4kn:APA91bH5QkoFFRFywieIPkOHYve-yf8m7L2lulzw9NigwBT7ccKJE4T2DscBM8KhVrV90s-aCqZgD_PtvKEf2pVvNZYImlUXPDG8jaJGwAaD8UFPWz4C2jQ"
PASSWORD = "q123q123"

# 随机字符串
def get_random_str(length=32) -> str:
    return ''.join(random.choices(string.ascii_lowercase + string.digits, k=length))

# 时间戳
def get_timestamp() -> int:
    return int(time.time())

# 构建手机号，如从6695270001开始
def generate_mobile(index: int) -> str:
    return f"669527{index:04d}"

# 生成签名
def generate_signature(payload: dict) -> str:
    filtered = {k: v for k, v in payload.items() if k not in ["signature", "timestamp"] and v not in ["", None, [], {}]}
    sorted_str = json.dumps(dict(sorted(filtered.items())), separators=(',', ':'), ensure_ascii=False)
    print(f"🔏 签名字符串: {sorted_str}")
    return hashlib.md5(sorted_str.encode("utf-8")).hexdigest().upper()

# 构建注册请求体
def build_register_payload(mobile: str) -> dict:
    payload = {
        "username": mobile,
        "smsvcode": "",
        "registerType": "mobile",
        "pwd": PASSWORD,
        "invitecode": "",
        "domainurl": DOMAIN_URL,
        "phonetype": 2,
        "captchaId": "",
        "track": "",
        "deviceId": DEVICE_ID,
        "fireBaseToken": FIREBASE_TOKEN,
        "language": 0,
        "random": get_random_str(),
        "timestamp": get_timestamp()
    }
    payload["signature"] = generate_signature(payload)
    return payload

# 发送注册请求
def register_mobile(mobile: str, retry: bool = True) -> bool:
    print(f"\n📱 尝试注册手机号: {mobile}")
    payload = build_register_payload(mobile)
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
            print(f"✅ 注册成功: {mobile}")
            save_mobile(mobile)
            return True
        elif "already" in msg.lower():
            print(f"⚠️ 已注册: {mobile}，跳过")
            return False
        elif "frequently" in msg.lower() and retry:
            print("⏳ 访问频繁，等待 5 秒重试...")
            time.sleep(5)
            return register_mobile(mobile, retry=False)
        else:
            print(f"❌ 注册失败: {msg}")
            return False
    except Exception as e:
        print(f"❗ 请求异常: {str(e)}")
        return False

# 保存注册成功手机号
def save_mobile(mobile: str):
    os.makedirs(os.path.dirname(OUTPUT_FILE), exist_ok=True)
    with open(OUTPUT_FILE, "a", encoding="utf-8") as f:
        f.write(mobile + "\n")

# 批量注册
def batch_register(start_index=1, count=10):
    success = 0
    for i in range(start_index, start_index + count):
        mobile = generate_mobile(i)
        if register_mobile(mobile):
            success += 1
        time.sleep(random.uniform(1.5, 3.0))
    print(f"\n📊 批量注册完成，总数: {count}，成功: {success}，失败: {count - success}")

# 主程序入口
if __name__ == "__main__":
    batch_register(start_index=132, count=1600)  # 例如从6695270081开始，注册10个

