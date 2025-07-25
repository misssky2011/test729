import requests
import hashlib
import json
import time
import os

# 接口地址
LOGIN_URL = "https://sitlotteryapi.22889.club/api/webapi/Login"

# 用户名文件路径
USERNAME_FILE = "D:/figo/工具/Jmeter/Srcipt/WOS/sit/username8005.txt"

# 输出文件路径
LOGIN_TOKEN_FILE = "D:/figo/工具/pycharm/PycharmProjects/0624Test/login_tokens.txt"
LOTTERY_URL_FILE = "D:/figo/工具/pycharm/PycharmProjects/0624Test/lotteryLoginUrl.txt"

# 是否使用图形验证码
USE_CAPTCHA = False


def get_signature(data: dict) -> str:
    filtered = {
        k: v for k, v in data.items()
        if k not in ['signature', 'timestamp'] and v not in [None, "", []]
    }
    sorted_json = json.dumps(dict(sorted(filtered.items())), separators=(',', ':'), ensure_ascii=False)
    print(f"🔏 签名字符串: {sorted_json}")
    return hashlib.md5(sorted_json.encode("utf-8")).hexdigest().upper()


def generate_payload(username: str) -> dict:
    payload = {
        "username": username,
        "pwd": "q123q123",
        "phonetype": 2,
        "logintype": "mobile",
        "fireBaseToken": "cAjAxpfK3wtt_UmojJy4kn:APA91bH5QkoFFRFywieIPkOHYve-yf8m7L2lulzw9NigwBT7ccKJE4T2DscBM8KhVrV90s-aCqZgD_PtvKEf2pVvNZYImlUXPDG8jaJGwAaD8UFPWz4C2jQ",
        "language": 0,
        "random": "da9b08eb77854710b80d690d3a38dfc6",
        "timestamp": int(time.time())
    }

    if USE_CAPTCHA:
        payload["captchaId"] = "xxx"
        payload["track"] = {
            "backgroundImageWidth": 340,
            "backgroundImageHeight": 212,
            "sliderImageWidth": 68,
            "sliderImageHeight": 212,
            "startTime": "2025-06-23T09:00:23.661Z",
            "endTime": "2025-06-23T09:00:25.763Z",
            "tracks": [{"x": 10, "y": 1, "t": 100}]
        }

    payload["signature"] = get_signature(payload)
    return payload


def save_to_file(path: str, content: str):
    try:
        os.makedirs(os.path.dirname(path), exist_ok=True)
        with open(path, 'a', encoding='utf-8') as f:
            f.write(content + '\n')
        print(f"💾 内容已保存到 {path}")
    except Exception as e:
        print(f"❌ 写入文件失败: {e}")



def login_user(username: str):
    print(f"\n🔐 登录用户: {username}")
    payload = generate_payload(username)
    headers = {"Content-Type": "application/json"}

    try:
        start = time.perf_counter()
        response = requests.post(LOGIN_URL, headers=headers, json=payload)
        duration = (time.perf_counter() - start) * 1000

        res_json = response.json()

        print(f"📨 状态码: {response.status_code}")
        print(f"📨 响应内容: {json.dumps(res_json, indent=2, ensure_ascii=False)}")
        print(f"⏱ 耗时: {duration:.2f} ms")

        if res_json.get("code") == 0:
            token = res_json.get("data", {}).get("token", "")
            lottery_url = res_json.get("data", {}).get("lotteryLoginUrl", "")

            # 写入 login_tokens.txt
            if token:
                save_to_file(LOGIN_TOKEN_FILE, f"Bearer {token}")
            else:
                print("⚠️ 登录成功但未返回 token")

            # 写入 lotteryLoginUrl.txt（只取 token 部分）
            if lottery_url and "Token=" in lottery_url:
                lottery_token = lottery_url.split("Token=")[-1].strip()
                save_to_file(LOTTERY_URL_FILE, lottery_token)
            else:
                print("⚠️ 登录成功但未返回 lotteryLoginUrl")

            print(f"✅ 登录成功: {username}")
            return True, duration
        else:
            print(f"❌ 登录失败: {res_json.get('msg')}")
            return False, duration
    except Exception as e:
        print(f"🚨 请求异常: {e}")
        return False, 0


def read_usernames(file_path: str):
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            usernames = [line.strip() for line in f if line.strip()]
        print(f"📘 成功读取 {len(usernames)} 个用户名")
        return usernames
    except Exception as e:
        print(f"❌ 无法读取用户名文件: {e}")
        return []


def batch_login(usernames):
    success = 0
    total_time = 0
    for username in usernames:
        ok, duration = login_user(username)
        total_time += duration
        if ok:
            success += 1

    count = len(usernames)
    print(f"\n📊 登录完毕：共 {count}，成功 {success}，失败 {count - success}")
    if count > 0:
        print(f"⏱ 总耗时: {total_time:.2f} ms，平均: {total_time / count:.2f} ms")


if __name__ == "__main__":
    users = read_usernames(USERNAME_FILE)
    batch_login(users[:5])  # 可修改 [:10] 调整数量
