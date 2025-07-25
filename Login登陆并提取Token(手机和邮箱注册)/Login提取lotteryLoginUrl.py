import time
import hashlib
import random
import json
import requests
from urllib.parse import urlparse, parse_qs

# 登录接口 URL
url = "https://sitlotteryapi.22889.club/api/webapi/Login"

# 输出 Token 的文件路径
TOKEN_FILE = "D:/figo/工具/pycharm/PycharmProjects/Login登陆并提取Token(手机和邮箱注册)/lotteryLoginUrl.txt"


def get_random_username() -> str:
    """
    随机生成8位数字字符串作为用户名
    :return: 8位数字字符串
    """
    return str(random.randint(10000000, 99999999))


def get_random_str(length: int) -> str:
    """
    随机生成指定长度的字符串，字符集为小写字母和数字
    :param length: 字符串长度
    :return: 随机字符串
    """
    chars = 'abcdefghijklmnopqrstuvwxyz1234567890'
    return ''.join(random.choice(chars) for _ in range(length))


def get_current_timestamp() -> str:
    """
    获取当前时间的10位秒级时间戳（字符串格式）
    :return: 10位时间戳字符串
    """
    # int(time.time()) 返回秒级时间戳，转换为字符串后截取后10位
    return str(int(time.time()))[-10:]


def md5_info(data, length=32) -> str:
    """
    计算 MD5 哈希，默认返回32位大写十六进制字符串
    如果传入数据是 dict，会先转为紧凑JSON字符串
    :param data: 字符串或字典
    :param length: 返回结果长度，默认32位
    :return: MD5大写摘要字符串（截断为length长度）
    """
    if isinstance(data, dict):
        data = json.dumps(data, separators=(',', ':'))
    hash_object = hashlib.md5(data.encode('utf-8'))
    hash_hex = hash_object.hexdigest().upper()
    return hash_hex if length == 32 else hash_hex[:length]


def sort_object_keys(obj: dict) -> str:
    """
    按 key 排序并转为紧凑的 JSON 字符串（无空格）
    :param obj: 字典对象
    :return: 排序后紧凑的 JSON 字符串
    """
    sorted_obj = {k: obj[k] for k in sorted(obj.keys())}
    return json.dumps(sorted_obj, separators=(',', ':'))


def get_signature(json_body: dict) -> str:
    """
    根据接口签名规则生成签名：
    - 排除 'signature' 和 'timestamp' 字段
    - 排除空值（None、空字符串、空列表）
    - 按 key 排序后转 JSON
    - 计算 MD5 大写摘要
    :param json_body: 请求体字典
    :return: 签名字符串
    """
    encoded_body = {}
    for key, value in json_body.items():
        if key not in ['signature', 'timestamp'] and value not in [None, "", []]:
            encoded_body[key] = value
    json_string = sort_object_keys(encoded_body)
    return md5_info(json_string)


def generate_login_data(username: str) -> dict:
    """
    生成登录接口请求体数据，包含随机字符串、时间戳和签名
    :param username: 用户名
    :return: 构造好的请求体字典
    """
    timestamp = get_current_timestamp()
    random_str = get_random_str(32)

    data = {
        "language": 0,
        "logintype": "mobile",
        "phonetype": 0,
        "pwd": "q123q123",
        "random": random_str,
        "signature": "",
        "timestamp": timestamp,
        "username": username
    }

    # 计算签名并赋值
    data["signature"] = get_signature(data)
    return data


def save_token_to_file(token: str):
    """
    将带 Bearer 前缀的 Token 追加保存到指定文件
    :param token: token字符串
    """
    try:
        bearer_token = f"Bearer {token}"
        with open(TOKEN_FILE, "a", encoding="utf-8") as f:
            f.write(f"{bearer_token}\n")
        print(f"✅ Token 已保存: {bearer_token[:15]}...{bearer_token[-5:]}")
    except Exception as e:
        print(f"❌ 保存 Token 到文件失败: {e}")


def login_user(username: str) -> bool:
    """
    使用指定用户名调用登录接口，成功后提取并保存 Token
    :param username: 用户名
    :return: 是否成功登录并提取到 Token
    """
    data = generate_login_data(username)
    headers = {"Content-Type": "application/json"}

    try:
        print(f"发送登录请求，用户名: {username}")
        response = requests.post(url, json=data, headers=headers)
        if response.status_code == 200:
            resp_json = response.json()
            print(f"响应数据: {json.dumps(resp_json, indent=2, ensure_ascii=False)}")

            if resp_json.get("code") == 0:
                login_url = resp_json.get("data", {}).get("lotteryLoginUrl")
                if login_url:
                    parsed = urlparse(login_url)
                    token = parse_qs(parsed.query).get("Token", [None])[0]
                    if token:
                        save_token_to_file(token)
                        return True
                    else:
                        print("⚠️ 未找到 Token 参数")
                else:
                    print("⚠️ 响应中缺少 lotteryLoginUrl")
            else:
                print(f"❌ 登录失败: {resp_json.get('msg')}")
        else:
            print(f"❌ 请求失败: 状态码 {response.status_code}, 错误: {response.text}")
    except requests.exceptions.RequestException as e:
        print(f"❌ 网络异常: {e}")

    return False


def read_usernames_from_file(filename: str) -> list:
    """
    从文件读取用户名列表，忽略空行
    :param filename: 文件路径
    :return: 用户名列表
    """
    try:
        with open(filename, 'r', encoding='utf-8') as f:
            usernames = [line.strip() for line in f.readlines() if line.strip()]
        print(f"读取 {len(usernames)} 个用户名")
        return usernames
    except FileNotFoundError:
        print(f"❌ 未找到文件 {filename}")
        return []
    except Exception as e:
        print(f"❌ 读取用户名文件失败: {e}")
        return []


def simulate_multiple_logins(usernames: list):
    """
    批量模拟登录，依次调用 login_user
    :param usernames: 用户名列表
    """
    success_count = 0
    for username in usernames:
        if login_user(username):
            success_count += 1
    print(f"\n🎯 成功登录并保存 Token 的用户数: {success_count}/{len(usernames)}")


if __name__ == "__main__":
    # 用户名文件路径
    #USER_FILE = "D:/figo/工具/pycharm/PycharmProjects/ArTest/username.txt"
    USER_FILE = "D:/figo/工具/Jmeter/Srcipt/username.txt"

    usernames = read_usernames_from_file(USER_FILE)
    TARGET_USER_COUNT = 134
    usernames = usernames[:TARGET_USER_COUNT]

    if usernames:
        simulate_multiple_logins(usernames)
    else:
        print("⚠️ 未读取到有效用户名")
