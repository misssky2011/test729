# 5D不同类型下注
# 该脚本模拟用户登录、获取用户信息、余额查询、下注、查询下注记录等操作
# 作者：figo 
# 时间：2025-07-08
import hashlib
import json
import random
import time
import threading
from typing import Optional, List
from urllib.parse import urlencode, urlparse, parse_qs
from collections import OrderedDict, defaultdict
import requests


# === ANSI 颜色代码 ===
class Colors:
    RESET = "\033[0m"
    BOLD = "\033[1m"
    GREEN = "\033[92m"
    GRAY = "\033[90m"


# === 接口地址配置 ===
API_BASE = "https://sit-lotteryh5.wmgametransit.com/api/Lottery"
DRAW_BASE = "https://draw.tbgametransit.com/D5"

GET_USER_INFO_URL = f"{API_BASE}/GetUserInfo"
GET_BALANCE_URL = f"{API_BASE}/GetBalance"
BET_URL = f"{API_BASE}/D5Bet"
GET_BET_RECORD_URL = f"{API_BASE}/GetRecordPage"

# === 本地配置 ===
USERNAME_FILE = "D:/figo/工具/pycharm/PycharmProjects/WinGo/username.txt"  # 会员目录
MAX_TOKENS_TO_RUN = 30  # 同时运行的用户数

BET_CONTENT_OPTIONS = [ "FirstNum_0", "FirstNum_1", "FirstNum_2", "FirstNum_3", "FirstNum_4", "FirstNum_5",
                        "FirstNum_6", "FirstNum_7", "FirstNum_8", "FirstNum_9", "FirstBigSmall_Big",
                        "FirstBigSmall_Small", "FirstOddEven_Odd", "FirstOddEven_Even", "SecondNum_0", "SecondNum_1",
                        "SecondNum_2", "SecondNum_3", "SecondNum_4", "SecondNum_5", "SecondNum_6", "SecondNum_7",
                        "SecondNum_8", "SecondNum_9", "SecondBigSmall_Big", "SecondBigSmall_Small", "SecondOddEven_Odd",
                        "SecondOddEven_Even", "ThirdNum_0", "ThirdNum_1", "ThirdNum_2", "ThirdNum_3", "ThirdNum_4",
                        "ThirdNum_5", "ThirdNum_6", "ThirdNum_7", "ThirdNum_8", "ThirdNum_9", "ThirdBigSmall_Big",
                        "ThirdBigSmall_Small", "ThirdOddEven_Odd", "ThirdOddEven_Even", "FourthNum_0", "FourthNum_1",
                        "FourthNum_2", "FourthNum_3", "FourthNum_4", "FourthNum_5", "FourthNum_6", "FourthNum_7",
                        "FourthNum_8", "FourthNum_9", "FourthBigSmall_Big", "FourthBigSmall_Small", "FourthOddEven_Odd",
                        "FourthOddEven_Even", "FifthNum_0", "FifthNum_1", "FifthNum_2", "FifthNum_3", "FifthNum_4",
                        "FifthNum_5", "FifthNum_6", "FifthNum_7", "FifthNum_8", "FifthNum_9", "FifthBigSmall_Big",
                        "FifthBigSmall_Small", "FifthOddEven_Odd", "FifthOddEven_Even", "SumBigSmall_Small",
                        "SumBigSmall_Big", "SumOddEven_Even", "SumOddEven_Odd"]

SUPPORTED_GAME_CODES = ['D5_1M', 'D5_3M', 'D5_5M', 'D5_10M']

# ========== 统计 ==========
stats_lock = threading.Lock()
total_users = 0
login_failures = 0
bet_success = 0
bet_failures = 0
error_codes = defaultdict(int)

# === 全局日志锁 ===
log_lock = threading.Lock()


# === 工具函数 ===
def compute_md5_upper(s: str) -> str:
    return hashlib.md5(s.encode("utf-8")).hexdigest().upper()


def generate_random_number_str(length=12) -> str:
    return str(random.randint(1, 9)) + ''.join(str(random.randint(0, 9)) for _ in range(length - 1))


def get_current_timestamp() -> str:
    return str(int(time.time()))[-10:]


def sort_object_keys(obj):
    return json.dumps({k: obj[k] for k in sorted(obj.keys())}, separators=(',', ':'))


def get_signature(data: dict) -> str:
    sign_data = {k: v for k, v in data.items() if k not in ['signature', 'timestamp', 'betContent']}
    json_str = sort_object_keys(sign_data)
    return compute_md5_upper(json_str)


def read_usernames_from_file(filename) -> List[str]:
    try:
        with open(filename, 'r', encoding="utf-8") as file:
            usernames = [line.strip() for line in file.readlines() if line.strip()]
        return usernames
    except Exception as e:
        print(f"❌ 读取用户名文件错误: {e}")
        return []


# === 登录流程 ===
LOGIN_URL = "https://sitlotteryapi.22889.club/api/webapi/Login"


def get_random_str(length):
    return ''.join(random.choice('1234567890abcdefghijklmnopqrstuvwxyz') for _ in range(length))


def generate_login_data(username):
    timestamp = get_current_timestamp()
    random_str = get_random_str(32)
    data = {"language": 0, "logintype": "mobile", "phonetype": 0, "pwd": "q123q123", "random": random_str,
        "signature": "", "timestamp": timestamp, "username": username}
    data["signature"] = get_signature(data)
    return data


def login_user(username) -> Optional[str]:
    data = generate_login_data(username)
    try:
        response = requests.post(LOGIN_URL, json=data, timeout=10)
        if response.status_code == 200:
            res = response.json()
            if res.get("code") == 0:
                url = res.get("data", {}).get("lotteryLoginUrl")
                if url:
                    token = parse_qs(urlparse(url).query).get("Token", [None])[0]
                    return token, response.text
        return None, response.text
    except Exception as e:
        return None, f"登录异常: {e}"


# === 接口调用 ===
def get_user_info(token: str):
    random_num = generate_random_number_str()
    params = {"language": "en", "random": random_num, "timestamp": get_current_timestamp(),
        "signature": compute_md5_upper(f'{{"language":"en","random":{random_num}}}')}
    url = f"{GET_USER_INFO_URL}?{urlencode(params)}"
    headers = {"Authorization": f"Bearer {token}"}
    try:
        resp = requests.get(url, headers=headers, timeout=10)
        return resp.json(), resp.headers.get("Authorization", "").replace("Bearer ", ""), resp.text
    except Exception as e:
        return None, None, f"获取用户信息失败: {e}"


def get_balance(token: str):
    random_num = generate_random_number_str()
    params = {"language": "en", "random": random_num, "timestamp": get_current_timestamp(),
        "signature": compute_md5_upper(f'{{"language":"en","random":{random_num}}}')}
    url = f"{GET_BALANCE_URL}?{urlencode(params)}"
    headers = {"Authorization": f"Bearer {token}"}
    try:
        resp = requests.get(url, headers=headers, timeout=10)
        return resp.json(), resp.text
    except Exception as e:
        return None, f"获取余额异常: {e}"


def get_issue_number(game_code: str) -> tuple[Optional[str], str]:
    try:
        ts = int(time.time() * 1000)
        url = f"{DRAW_BASE}/{game_code}.json?ts={ts}"
        resp = requests.get(url, timeout=10)
        json_data = resp.json()
        return json_data.get("current", {}).get("issueNumber"), resp.text
    except Exception as e:
        return None, f"获取期号异常: {e}"


def get_history_issue_page(game_code: str) -> tuple[Optional[dict], str]:
    try:
        ts = int(time.time() * 1000)
        url = f"{DRAW_BASE}/{game_code}/GetHistoryIssuePage.json?ts={ts}"
        resp = requests.get(url, timeout=10)
        return resp.json(), resp.text
    except Exception as e:
        return None, f"获取开奖历史异常: {e}"


def place_bet(bearer_token: str, game_code: str, issue_number: str, amount: int, bet_multiple: int, bet_content: str,
              language: str = "en") -> tuple[Optional[dict], str]:
    random_num = generate_random_number_str()

    # 构造签名体
    sign_body = OrderedDict(
        [("amount", amount), ("betMultiple", bet_multiple), ("gameCode", game_code), ("issueNumber", issue_number),
            ("language", language), ("random", int(random_num)), ])
    signature = compute_md5_upper(json.dumps(sign_body, separators=(',', ':')))

    # 构造完整请求体
    full_body = dict(sign_body)
    full_body["betContent"] = [bet_content]
    full_body["signature"] = signature
    full_body["timestamp"] = int(time.time())

    headers = {"Authorization": f"Bearer {bearer_token}", "Content-Type": "application/json"}

    try:
        resp = requests.post(BET_URL, headers=headers, json=full_body, timeout=10)
        return resp.json(), resp.text
    except Exception as e:
        return None, f"下单异常: {e}"


# === 新增：下注记录接口 ===
from typing import Tuple

def get_bet_record_page(token: str, game_code: str, page_no: int = 1, page_size: int = 20, language: str = "en") -> Tuple[Optional[dict], str]:
    """
    获取下注记录分页数据
    """
    def generate_random_number():
        first = str(random.randint(1, 9))
        rest = ''.join(str(random.randint(0, 9)) for _ in range(11))
        return first + rest

    random_num = generate_random_number()

    params_map = {
        "gameCode": game_code,
        "language": language,
        "pageNo": page_no,
        "pageSize": page_size,
        "random": int(random_num)
    }

    json_str = json.dumps(params_map, separators=(',', ':'), sort_keys=True)
    signature = compute_md5_upper(json_str)

    query_params = {
        "gameCode": game_code,
        "language": language,
        "pageNo": page_no,
        "pageSize": page_size,
        "random": random_num,
        "signature": signature,
        "timestamp": int(time.time())
    }

    url = f"{API_BASE}/GetRecordPage?{urlencode(query_params)}"
    headers = {"Authorization": f"Bearer {token}"}

    try:
        resp = requests.get(url, headers=headers, timeout=10)
        return resp.json(), resp.text
    except Exception as e:
        return None, f"获取下注记录异常: {e}"


# === 流程主逻辑 ===
def run_flow(username: str):
    global total_users, login_failures, bet_success, bet_failures, error_codes
    game_code = random.choice(SUPPORTED_GAME_CODES)

    log_lines = []

    start_title = f"====================================================================================== 用户 {{{username}}} 流程开始 (游戏: {game_code}) =========================================================================================="
    colored_start_title = f"{Colors.BOLD}{Colors.GREEN}{start_title}{Colors.RESET}"
    log_lines.append(colored_start_title)

    with stats_lock:
        total_users += 1

    # [1] 用户登录
    log_lines.append(f"{Colors.BOLD}[1] 用户登录{Colors.RESET}")
    token, login_response = login_user(username)
    log_lines.append(f"    响应: {login_response}")
    if token:
        log_lines.append(f"    登录成功，Token: {token}")
    else:
        log_lines.append("    ❌ 登录失败")
        with stats_lock:
            login_failures += 1
        with log_lock:
            for line in log_lines:
                print(line)
        return

    # [2] 用户信息
    log_lines.append(f"{Colors.BOLD}[2] 用户信息{Colors.RESET}")
    user_info, bet_token, user_info_response = get_user_info(token)
    log_lines.append(f"    响应: {user_info_response}")
    if not user_info:
        log_lines.append("    ❌ 获取用户信息失败")
        with log_lock:
            for line in log_lines:
                print(line)
        return

    if bet_token:
        log_lines.append(f"    获取到新Token: {bet_token}")

    # [3] 获取余额
    log_lines.append(f"{Colors.BOLD}[3] 获取余额{Colors.RESET}")
    balance_info, balance_response = get_balance(token)
    log_lines.append(f"    响应: {balance_response}")
    if balance_info and balance_info.get('data'):
        balance = balance_info['data'].get('balance', 0)
        log_lines.append(f"    当前余额: {balance}")
    else:
        log_lines.append("    ⚠️ 获取余额失败")

    # [4] 获取期号
    log_lines.append(f"{Colors.BOLD}[4] 当前期号{Colors.RESET}")
    issue, issue_response = get_issue_number(game_code)
    log_lines.append(f"    响应: {issue_response}")
    if not issue:
        log_lines.append("    ❌ 获取期号失败")
        with log_lock:
            for line in log_lines:
                print(line)
        return

    bet_content = random.choice(BET_CONTENT_OPTIONS)
    amount: int = random.randint(10, 1000)
    log_lines.append(f"    当前期号: {issue}, 下注内容: {bet_content}, 金额: {amount}")

    # [5] 游戏下注
    log_lines.append(f"{Colors.BOLD}[5] 游戏下注{Colors.RESET}")
    result, bet_response = place_bet(bet_token or token, game_code, issue, amount, 1, bet_content)
    log_lines.append(f"    响应: {bet_response}")

    if result:
        if result.get("code") == 0:
            log_lines.append("    ✅ 下单成功")
            with stats_lock:
                bet_success += 1
        else:
            log_lines.append(f"    ❌ 下单失败，错误码: {result.get('code')}")
            # 详细错误信息分多行显示
            for key, val in result.items():
                log_lines.append(f"        {key}: {val}")
            with stats_lock:
                bet_failures += 1
                error_codes[result.get("code")] += 1
    else:
        log_lines.append("    ❌ 下单异常，未收到响应或请求失败")
        # 对异常情况打印更详细的原始响应
        log_lines.append(f"    响应内容: {bet_response}")
        with stats_lock:
            bet_failures += 1
            error_codes["exception"] += 1

    # [6] 开奖历史
    log_lines.append(f"{Colors.BOLD}[6] 开奖历史{Colors.RESET}")
    history_data, history_response = get_history_issue_page(game_code)
    log_lines.append(f"    响应: {history_response}")
    if history_data and history_data.get('data'):
        count = len(history_data['data'].get('list', []))
        log_lines.append(f"    开奖历史条数: {count}")
    else:
        log_lines.append("    ⚠️ 获取开奖历史失败")

    # [7] 下注记录
    log_lines.append(f"{Colors.BOLD}[7] 下注记录{Colors.RESET}")
    bet_records, bet_record_response = get_bet_record_page(bet_token or token, game_code)
    log_lines.append(f"    响应: {bet_record_response}")
    if bet_records and bet_records.get('data'):
        records_count = len(bet_records['data'].get('list', []))
        log_lines.append(f"    下注记录条数: {records_count}")
    else:
        log_lines.append("    ⚠️ 获取下注记录失败")

    end_title = f"====================================================================================== 用户 {{{username}}} 流程结束 ================================================================="
    colored_end_title = f"{Colors.BOLD}{Colors.GRAY}{end_title}{Colors.RESET}"
    log_lines.append(colored_end_title)

    with log_lock:
        for line in log_lines:
            print(line)
        print()  # 分隔空行

# === 主函数入口 ===
if __name__ == "__main__":
    usernames = read_usernames_from_file(USERNAME_FILE)
    if not usernames:
        print("❌ 未读取到有效用户名，程序退出。")
        exit(1)

    threads = []
    for username in usernames[:MAX_TOKENS_TO_RUN]:
        t = threading.Thread(target=run_flow, args=(username,))
        t.start()
        threads.append(t)
        time.sleep(0.2)

    for t in threads:
        t.join()

    print("\n" + "=" * 50)
    print("📊 ================== 数据汇总统计 =================")
    print("=" * 50)
    print(f"👥 总用户数: {total_users}")
    print(f"🔒 登录失败数: {login_failures}")
    print(f"✅ 下注成功数: {bet_success}")
    print(f"❌ 下注失败数: {bet_failures}")
    if error_codes:
        print("🧾 错误码分布:")
        for code, count in error_codes.items():
            print(f"   - 错误码 {code}: {count} 次")
