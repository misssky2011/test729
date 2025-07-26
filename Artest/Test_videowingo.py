# VideoWinGo同一期下注所有类型
# 该脚本模拟用户登录、获取用户信息、余额查询、下注、查询下注记录等操作
import hashlib
import json
import random
import time
import threading
from typing import Tuple, Dict, Union, Optional, List
from urllib.parse import urlencode, urlparse, parse_qs
from collections import OrderedDict, defaultdict
import requests

# 颜色和样式常量
GREEN_BOLD = "\033[1;32m"
GRAY_BOLD = "\033[1;90m"
RESET = "\033[0m"

# === 接口地址配置 ===
API_BASE = "https://sit-lotteryh5.wmgametransit.com/api/Lottery"
DRAW_BASE = "https://draw.wmgametransit.com/VideoWinGo"
LOGIN_URL = "https://sitlotteryapi.22889.club/api/webapi/Login"
BET_URL = "https://api.wmgametransit.com/api/Lottery/VideoWinGoBet"

# === 接口路径 ===
GET_USER_INFO_URL = f"{API_BASE}/GetUserInfo"
GET_BALANCE_URL = f"{API_BASE}/GetBalance"

CALL_INTERVAL = 1
MAX_CALLS_PER_TOKEN = 1
MAX_TOKENS_TO_RUN = 1  # 改成3个线程同时跑

# 固定账号和密码
FIXED_USERS = [
    ("6695270002", "q123q123"),
]

BET_CONTENT_OPTIONS = [
    'Num_0', 'Num_1', 'Num_2', 'Num_3', 'Num_4',
    'Num_5', 'Num_6', 'Num_7', 'Num_8', 'Num_9',
    'Color_Red', 'Color_Violet', 'Color_Green',
    'BigSmall_Small', 'BigSmall_Big'
]
SUPPORTED_GAME_CODES = ['VideoWinGo_3M']

stats_lock = threading.Lock()
total_users = 0
login_failures = 0
bet_success = 0
bet_failures = 0
error_codes = defaultdict(int)
error_details = defaultdict(list)
login_fail_detail = []
log_lock = threading.Lock()


def compute_md5_upper(s: str) -> str:
    return hashlib.md5(s.encode("utf-8")).hexdigest().upper()


def generate_random_number_str(length=12) -> str:
    return str(random.randint(1, 9)) + ''.join(str(random.randint(0, 9)) for _ in range(length - 1))


def get_current_timestamp() -> str:
    return str(int(time.time()))[-10:]


def sort_object_keys(obj: Dict) -> str:
    sorted_obj = {key: obj[key] for key in sorted(obj.keys())}
    return json.dumps(sorted_obj, separators=(',', ':'))


def get_signature(json_body: Dict) -> str:
    encoded = {k: v for k, v in json_body.items() if k not in ['signature', 'timestamp'] and v not in [None, '', []]}
    return compute_md5_upper(sort_object_keys(encoded))


def get_random_str(length: int) -> str:
    return ''.join(random.choice('1234567890abcdefghijklmnopqrstuvwxyz') for _ in range(length))


def generate_login_data(username: str, password: str) -> Dict:
    timestamp = get_current_timestamp()
    random_str = get_random_str(32)
    data = {
        "language": 0, "logintype": "mobile", "phonetype": 0,
        "pwd": password, "random": random_str,
        "signature": "", "timestamp": timestamp, "username": username
    }
    data["signature"] = get_signature(data)
    return data


def login_user(username: str, password: str) -> Optional[str]:
    print(f"{GREEN_BOLD}[1] 用户登录 - {username}{RESET}")
    data = generate_login_data(username, password)
    headers = {"Content-Type": "application/json"}
    try:
        response = requests.post(LOGIN_URL, json=data, headers=headers, timeout=10)
        print(f"    ↳ 响应: {response.text}")
        if response.status_code == 200:
            res = response.json()
            if res.get("code") == 0:
                login_url = res.get("data", {}).get("lotteryLoginUrl")
                return parse_qs(urlparse(login_url).query).get("Token", [None])[0]
            else:
                login_fail_detail.append((username, res.get("msg", "登录失败")))
                return None
        else:
            login_fail_detail.append((username, f"HTTP错误: {response.status_code}"))
            return None
    except Exception as e:
        login_fail_detail.append((username, str(e)))
        print(f"    ↳ 异常: {e}")
        return None


def get_user_info(bearer_token: str, username: str):
    print(f"{GREEN_BOLD}[2] 用户信息 - {username}{RESET}")
    random_num = generate_random_number_str()
    params = {
        "language": "en", "random": random_num, "timestamp": get_current_timestamp(),
        "signature": compute_md5_upper(f'{{"language":"en","random":{random_num}}}')
    }
    url = f"{GET_USER_INFO_URL}?{urlencode(params)}"
    headers = {"Authorization": f"Bearer {bearer_token}"}
    try:
        resp = requests.get(url, headers=headers, timeout=10)
        print(f"    ↳ 响应: {resp.text}")
        return resp.json(), resp.headers.get("Authorization", "").replace("Bearer ", "").strip()
    except Exception as e:
        print(f"    ↳ 异常: {e}")
        return None, None


def get_balance(bearer_token: str, username: str) -> Tuple[Optional[Dict], Union[str, float]]:
    print(f"{GREEN_BOLD}[3] 获取余额 - {username}{RESET}")
    random_num = generate_random_number_str()
    params = {
        "language": "en", "random": random_num, "timestamp": get_current_timestamp(),
        "signature": compute_md5_upper(f'{{"language":"en","random":{random_num}}}')
    }
    url = f"{GET_BALANCE_URL}?{urlencode(params)}"
    headers = {"Authorization": f"Bearer {bearer_token}"}
    try:
        resp = requests.get(url, headers=headers, timeout=10)
        data = resp.json()
        balance = data.get('data', {}).get('balance', "N/A")
        print(f"    ↳ 响应: {resp.text}")
        print(f"    ↳ 当前余额: {balance}")
        return data, balance
    except Exception as e:
        print(f"    ↳ 异常: {e}")
        return None, "N/A"


def get_issue_number(game_code: str) -> Optional[str]:
    print(f"{GREEN_BOLD}[4] 当前期号{RESET}")
    try:
        url = f"{DRAW_BASE}/{game_code}.json?ts={int(time.time() * 1000)}"
        response = requests.get(url, timeout=10)
        issue_number = response.json().get("current", {}).get("issueNumber")
        print(f"    ↳ 响应: {response.text}")
        print(f"    ↳ 当前期号: {issue_number}")
        return issue_number
    except Exception as e:
        print(f"    ↳ 异常: {e}")
        return None


def place_bet(bearer_token: str, game_code: str, issue_number: str, amount: int, bet_multiple: int, bet_content: str,
              username: str):
    print(f"{GREEN_BOLD}[5] 游戏下注 - {username}{RESET}")
    print(f"    ↳ 游戏: {game_code}, 期号: {issue_number}, 内容: {bet_content}, 金额: {amount}")
    random_num = generate_random_number_str()
    body = OrderedDict([
        ("amount", amount),
        ("betContent", bet_content),
        ("betMultiple", bet_multiple),
        ("gameCode", game_code),
        ("issueNumber", issue_number),
        ("language", "en"),
        ("random", int(random_num))
    ])
    sign_str = json.dumps(body, separators=(',', ':'))
    body["signature"] = compute_md5_upper(sign_str)
    body["timestamp"] = int(time.time())
    headers = {"Authorization": f"Bearer {bearer_token}", "Content-Type": "application/json"}

    try:
        resp = requests.post(BET_URL, headers=headers, json=body, timeout=10)
        print(f"    ↳ 响应: {resp.text}")
        return resp.json()
    except Exception as e:
        print(f"    ↳ 异常: {e}")
        return None


def get_bet_record(game_code: str):
    print(f"{GREEN_BOLD}[6] 开奖历史{RESET}")
    ts = int(time.time() * 1000)
    url = f"{DRAW_BASE}/{game_code}/GetHistoryIssuePage.json?ts={ts}"
    try:
        resp = requests.get(url, timeout=10)
        print(f"    ↳ 请求URL: {url}")
        print(f"    ↳ 响应: {resp.text}")
    except Exception as e:
        print(f"    ↳ 异常: {e}")


def get_bet_record_list(bearer_token: str, game_code: str, page_no: int = 1, page_size: int = 10):
    print(f"{GREEN_BOLD}[7] 查询下注记录{RESET}")
    random_number = generate_random_number_str()

    params = {
        "gameCode": game_code,
        "language": "zh",
        "pageNo": page_no,
        "pageSize": page_size,
        "random": int(random_number)
    }

    json_string = json.dumps(params, separators=(',', ':'), ensure_ascii=False)
    signature = compute_md5_upper(json_string)

    params["signature"] = signature
    params["timestamp"] = int(time.time())

    url = f"https://api.wmgametransit.com/api/Lottery/GetRecordPage?{urlencode(params)}"
    headers = {
        "Authorization": f"Bearer {bearer_token}",
        "Content-Type": "application/json"
    }

    try:
        response = requests.get(url, headers=headers, timeout=10)
        print(f"    ↳ 请求URL: {url}")
        print(f"    ↳ 响应: {response.text}")
        return response.json()
    except Exception as e:
        print(f"    ↳ 异常: {e}")
        return None


def run_flow(username: str, password: str):
    global total_users, login_failures, bet_success, bet_failures, error_codes, error_details

    game_code = random.choice(SUPPORTED_GAME_CODES)
    print(f"{GREEN_BOLD}====================== 用户 {username} 流程开始 (游戏: {game_code}) ======================{RESET}")

    with stats_lock:
        total_users += 1

    token = login_user(username, password)
    if not token:
        with stats_lock:
            login_failures += 1
        return

    user_info, bet_token = get_user_info(token, username)
    if not user_info:
        return

    _, old_balance = get_balance(token, username)

    issue = get_issue_number(game_code)
    if not issue:
        return

    amount = random.choice([10, 20, 50, 100, 200, 500, 1000]) # 固定金额
    # amount: int=random.randint(10, 1000)  # 随机金额

    # === 🔁 同一期下注所有类型 ===
    for bet_content in BET_CONTENT_OPTIONS:
        bet_result = place_bet(
            bearer_token=bet_token, game_code=game_code, issue_number=issue,
            amount=amount, bet_multiple=1, bet_content=bet_content, username=username
        )

        if bet_result and bet_result.get("code") == 0:
            with stats_lock:
                bet_success += 1
        else:
            with stats_lock:
                bet_failures += 1
                error_code = bet_result.get("code") if bet_result else "exception"
                error_msg = bet_result.get("msg") if bet_result else "request error"
                error_codes[error_code] += 1
                error_details[error_code].append((username, error_msg))

        time.sleep(0.3)  # 控制下注频率，避免风控

    # === 查询记录 ===
    get_bet_record(game_code)
    get_bet_record_list(bearer_token=bet_token, game_code=game_code)
    print(f"{GRAY_BOLD}====================== 用户 {username} 流程结束 ======================{RESET}")



if __name__ == "__main__":
    threads = []
    for i, (username, password) in enumerate(FIXED_USERS[:MAX_TOKENS_TO_RUN]):
        t = threading.Thread(target=run_flow, args=(username, password))
        t.start()
        threads.append(t)
        time.sleep(0.5)

    for t in threads:
        t.join()

    print("\n✅ 全部流程执行完毕。")
    print("📊 投注统计:\n--------------------------")
    print(f"👥 总用户: {total_users}")
    print(f"🔐 登录失败: {login_failures}")
    print(f"🎯 投注成功: {bet_success}")
    print(f"❌ 投注失败: {bet_failures}")

    total_attempts = bet_success + bet_failures
    if total_attempts:
        print(f"📈 成功率: {bet_success / total_attempts * 100:.2f}%")

    if login_fail_detail:
        print("\n🧾 登录失败用户明细:")
        for uname, reason in login_fail_detail:
            print(f"   - 用户: {uname}, 原因: {reason}")

    if error_codes:
        print("\n📜 失败错误码:")
        for code, count in error_codes.items():
            print(f"   - 错误码 {code}: {count} 次")
            for uname, msg in error_details[code]:
                print(f"     · 用户: {uname}, 错误信息: {msg}")
