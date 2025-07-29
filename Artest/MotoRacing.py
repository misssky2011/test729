# MotoRacing下注所有类型
# 该脚本模拟用户登录、获取用户信息、余额查询、下注、查询下注记录等操作
# 作者：Figo 
# 时间：2025-07-08
import hashlib
import json
import random
import time
import threading
from typing import Optional, List, Tuple, Dict, Any
from urllib.parse import urlencode, urlparse, parse_qs
from collections import defaultdict
import requests
from colorama import Fore, Style, init

init(autoreset=True)

API_BASE = "https://sit-lotteryh5.wmgametransit.com/api/Lottery"
DRAW_BASE = "https://draw.wmgametransit.com/MotoRace"
GET_USER_INFO_URL = f"{API_BASE}/GetUserInfo"
GET_BALANCE_URL = f"{API_BASE}/GetBalance"
BET_URL = f"{API_BASE}/MotoRaceBet"
LOGIN_URL = "https://sitlotteryapi.22889.club/api/webapi/Login"
GET_RECORD_URL = f"{API_BASE}/GetRecordPage"  # 新增下注记录接口

USERNAME_FILE = "D:/figo/工具/VScode/Artest/username.txt"  # 会员目录
MAX_TOKENS_TO_RUN = 30  # 同时运行的用户数
SUPPORTED_GAME_CODES = [ 'MotoRace_1M' ]

stats_lock = threading.Lock()
total_users = 0
login_failures = 0
bet_success = 0
bet_failure = 0
bet_failure_reasons = defaultdict(lambda: { "count": 0, "users": set() })

BET_CONTENT_OPTIONS = [ 'FirstNum_1', 'FirstNum_2', 'FirstNum_3', 'FirstNum_4', 'FirstNum_5', 'FirstNum_6',
                        'FirstNum_7', 'FirstNum_8', 'FirstNum_9', 'SecondNum_2', 'SecondNum_3', 'SecondNum_4',
                        'SecondNum_5', 'SecondNum_6', 'SecondNum_7', 'SecondNum_8', 'SecondNum_9', 'ThirdNum_1',
                        'ThirdNum_2', 'ThirdNum_3', 'ThirdNum_4', 'ThirdNum_5', 'ThirdNum_6', 'ThirdNum_7',
                        'ThirdNum_8', 'ThirdNum_9', 'FirstOddEven_Odd', 'FirstOddEven_Even', 'SecondOddEven_Odd',
                        'SecondOddEven_Even', 'ThirdOddEven_Odd', 'ThirdOddEven_Even', 'FirstBigSmall_Big',
                        'FirstBigSmall_Small', 'SecondBigSmall_Big', 'SecondBigSmall_Small', 'ThirdBigSmall_Big',
                        'ThirdBigSmall_Small' ]


def shorten_token(token: str, head=6, tail=4) -> str:
    if not token or len(token) <= head + tail:
        return token
    return f"{token[ :head ]}...{token[ -tail: ]} (共 {len(token)} 字符)"


def compute_md5_upper(s: str) -> str:
    return hashlib.md5(s.encode("utf-8")).hexdigest().upper()


def generate_random_number_str(length=12) -> str:
    return str(random.randint(1, 9)) + ''.join(str(random.randint(0, 9)) for _ in range(length - 1))


def get_current_timestamp() -> str:
    return str(int(time.time()))[ -10: ]


def sort_object_keys(obj: Dict[ str, Any ]) -> str:
    return json.dumps({ k: obj[ k ] for k in sorted(obj.keys()) }, separators=(',', ':'))


def get_signature(data: dict) -> str:
    sign_data = { k: v for k, v in data.items() if k not in [ 'signature', 'timestamp', 'betContent' ] }
    return compute_md5_upper(sort_object_keys(sign_data))


def read_usernames_from_file(filename: str) -> List[ str ]:
    try:
        with open(filename, 'r', encoding="utf-8") as file:
            return [ line.strip() for line in file if line.strip() ]
    except Exception as e:
        print(f"    读取用户名文件错误: {e}")
        return [ ]


def get_random_str(length: int) -> str:
    return ''.join(random.choice('1234567890abcdefghijklmnopqrstuvwxyz') for _ in range(length))


def generate_login_data(username: str) -> Dict[ str, Any ]:
    timestamp = get_current_timestamp()
    random_str = get_random_str(32)
    data = { "language": 0, "logintype": "mobile", "phonetype": 0, "pwd": "q123q123", "random": random_str,
             "signature": "", "timestamp": timestamp, "username": username }
    data[ "signature" ] = get_signature(data)
    return data


def login_user(username: str) -> Tuple[ Optional[ str ], Dict ]:
    data = generate_login_data(username)
    try:
        response = requests.post(LOGIN_URL, json=data, timeout=10)
        if response.status_code == 200:
            res = response.json()
            if res.get("code") == 0:
                url = res.get("data", { }).get("lotteryLoginUrl")
                if url:
                    token = parse_qs(urlparse(url).query).get("Token", [ None ])[ 0 ]
                    return token, res
            return None, res
        return None, { "status": response.status_code, "text": response.text }
    except Exception as e:
        return None, { "error": str(e) }


def get_user_info(token: str) -> Tuple[ Optional[ Dict[ str, Any ] ], Optional[ str ] ]:
    random_num = random.randint(100000000000, 999999999999)
    signature = compute_md5_upper(f'{{"language":"en","random":{random_num}}}')
    params = { "language": "en", "random": str(random_num), "timestamp": get_current_timestamp(),
               "signature": signature }
    url = f"{GET_USER_INFO_URL}?{urlencode(params)}"
    headers = { "Authorization": f"Bearer {token}" }
    try:
        resp = requests.get(url, headers=headers, timeout=10)
        return resp.json(), resp.headers.get("Authorization", "").replace("Bearer ", "")
    except Exception as e:
        return { "error": str(e) }, None


def get_balance(token: str) -> Dict:
    random_num = generate_random_number_str()
    signature = compute_md5_upper(f'{{"language":"en","random":{random_num}}}')
    params = { "language": "en", "random": random_num, "timestamp": get_current_timestamp(), "signature": signature }
    url = f"{GET_BALANCE_URL}?{urlencode(params)}"
    headers = { "Authorization": f"Bearer {token}" }
    try:
        resp = requests.get(url, headers=headers, timeout=10)
        return resp.json()
    except Exception as e:
        return { "error": str(e) }


def get_issue_number(game_code: str) -> Tuple[ Optional[ str ], Dict ]:
    try:
        ts = int(time.time() * 1000)
        url = f"{DRAW_BASE}/{game_code}.json?ts={ts}"
        resp = requests.get(url, timeout=10)
        data = resp.json()
        return data.get("current", { }).get("issueNumber"), data
    except Exception as e:
        return None, { "error": str(e) }


def get_draw_history(game_code: str) -> Dict:
    ts = int(time.time() * 1000)
    url = f"{DRAW_BASE}/{game_code}.json?ts={ts}"
    try:
        resp = requests.get(url, timeout=10)
        return resp.json()
    except Exception as e:
        return { "error": str(e) }


def place_bet(token: str, game_code: str, issue_number: str, amount: int, bet_multiple: int, bet_content: str) -> Tuple[
    bool, Dict ]:
    random_str = generate_random_number_str()
    timestamp = int(time.time())
    sign_map = { "amount": amount, "betMultiple": bet_multiple, "betContent": bet_content, "gameCode": game_code,
                 "issueNumber": issue_number, "language": "en", "random": int(random_str) }
    sign_json = json.dumps({ k: sign_map[ k ] for k in sorted(sign_map) }, separators=(',', ':'))
    signature = compute_md5_upper(sign_json)
    data = { **sign_map, "signature": signature, "timestamp": timestamp }
    headers = { "Authorization": f"Bearer {token}", "Content-Type": "application/json" }
    try:
        resp = requests.post(BET_URL, headers=headers, json=data, timeout=10)
        if resp.status_code == 200:
            resp_json = resp.json()
            return resp_json.get("code") == 0, resp_json
        return False, { "status": resp.status_code, "text": resp.text }
    except Exception as e:
        return False, { "error": str(e) }


# 新增函数：获取下注记录
def get_bet_records(token: str, game_code: str) -> Dict:
    # 构造请求参数
    params = { "pageSize": 10, "pageNo": 1, "gameCode": game_code, "language": "en",
        "random": int(generate_random_number_str()),  # 转换为整数类型
        "timestamp": get_current_timestamp() }

    # 创建签名参数（不包含signature和timestamp）
    sign_params = { k: v for k, v in params.items() if k not in [ "signature", "timestamp" ] }

    # 对参数按key排序并转换为JSON字符串
    sign_str = json.dumps(sign_params, sort_keys=True, separators=(',', ':'))

    # 计算MD5签名
    signature = compute_md5_upper(sign_str)
    params[ "signature" ] = signature

    # 添加Authorization头
    headers = { "Authorization": f"Bearer {token}" }

    try:
        # 发送GET请求
        resp = requests.get(GET_RECORD_URL, params=params, headers=headers, timeout=10)
        if resp.status_code == 200:
            return resp.json()
        return { "error": f"HTTP状态码: {resp.status_code}", "response": resp.text }
    except Exception as e:
        return { "error": str(e) }


def print_step(step_num: int, step_name: str, response: Dict, additional_info: str = None,
               log_buffer: List[ str ] = None):
    # 标题加粗
    log_entry = f"{Style.BRIGHT}[{step_num}] {step_name}{Style.RESET_ALL}"
    log_buffer.append(log_entry)
    log_buffer.append(f"    ↳ 响应: {json.dumps(response, ensure_ascii=False)}")
    if additional_info:
        log_buffer.append(f"    ↳ {additional_info}")


def run_flow(username: str):
    global total_users, login_failures, bet_success, bet_failure
    game_code = 'MotoRace_1M'

    log_buffer = [ ]

    with stats_lock:
        total_users += 1

    log_buffer.append(f"\n================ 用户 {username} 流程开始 (游戏: {game_code}) ================")

    # [1] 登录信息
    token, login_res = login_user(username)
    print_step(1, "用户登录", login_res, f"Token: {shorten_token(token)}" if token else "登录失败", log_buffer)
    if not token:
        with stats_lock:
            login_failures += 1

    # [2] 用户信息
    user_info, bet_token = get_user_info(token) if token else ({ }, None)
    final_token = bet_token or token
    print_step(2, "用户信息", user_info, log_buffer=log_buffer)

    # [3] 获取余额
    balance_data = get_balance(final_token) if final_token else { "error": "无有效token" }
    current_balance = balance_data.get("data", { }).get("balance") if balance_data.get("code") == 0 else None
    print_step(3, "获取余额", balance_data, f"当前余额: {current_balance}" if current_balance is not None else None,
               log_buffer)

    # [4] 当前期号
    issue, issue_data = get_issue_number(game_code)
    print_step(4, "当前期号", issue_data, f"当前期号: {issue}" if issue else "获取期号失败", log_buffer)

    # [5] 游戏下注
    log_buffer.append("[5] 游戏下注")
    if issue and final_token:
        # 金额设置为 10 ~ 1000 随机
        amount: int = random.randint(10, 1000)
        bet_content = random.choice(BET_CONTENT_OPTIONS)
        log_buffer.append(f"    ↳ 下注: {game_code}, 期号: {issue}, 内容: {bet_content}, 金额: {amount}")
        success, bet_res = place_bet(final_token, game_code, issue, amount, 1, bet_content)
        log_buffer.append(f"    ↳ 响应: {json.dumps(bet_res, ensure_ascii=False)}")
        if success:
            log_buffer.append(f"    ↳ 下注成功")
            with stats_lock:
                bet_success += 1
        else:
            reason = bet_res.get("msg", "未知错误")
            log_buffer.append(f"    ↳ 下注失败: {reason}")
            with stats_lock:
                bet_failure += 1
                bet_failure_reasons[ reason ][ "count" ] += 1
                bet_failure_reasons[ reason ][ "users" ].add(username)
    else:
        skip_reason = "未获取到期号" if not issue else "无有效token" if not final_token else "未知原因"
        log_buffer.append(f"    ↳ 跳过下注 - {skip_reason}")
        with stats_lock:
            bet_failure += 1
            bet_failure_reasons[ skip_reason ][ "count" ] += 1
            bet_failure_reasons[ skip_reason ][ "users" ].add(username)

    # [6] 开奖历史
    history = get_draw_history(game_code)
    print_step(6, "开奖历史", history, log_buffer=log_buffer)

    # [7] 新增：获取下注记录
    if final_token:
        bet_records = get_bet_records(final_token, game_code)
        if "data" in bet_records and "records" in bet_records[ "data" ]:
            record_count = len(bet_records[ "data" ][ "records" ])
            print_step(7, "获取下注记录", bet_records, f"获取到 {record_count} 条下注记录", log_buffer)
        else:
            print_step(7, "获取下注记录", bet_records, "未获取到下注记录", log_buffer)
    else:
        log_buffer.append("[7] 获取下注记录 - 跳过，无有效token")

    log_buffer.append(f"================ 用户 {username} 流程结束 (游戏: {game_code}) =================\n")
    for line in log_buffer:
        print(line)


if __name__ == "__main__":
    usernames = read_usernames_from_file(USERNAME_FILE)
    if not usernames:
        print(f"{Fore.RED}没有读取到用户名，程序退出{Style.RESET_ALL}")
        exit(1)

    threads = [ ]
    for username in usernames[ :MAX_TOKENS_TO_RUN ]:
        t = threading.Thread(target=run_flow, args=(username,))
        t.start()
        threads.append(t)
        time.sleep(0.2)

    for t in threads:
        t.join()

    success_rate = (bet_success / (bet_success + bet_failure)) * 100 if (bet_success + bet_failure) > 0 else 0

    print(f"\n{Fore.BLUE}📊 相关数据统计:{Style.RESET_ALL}")
    print("--------------------------")
    print(f"👥 总用户: {total_users}")
    print(f"🔐 登录失败: {login_failures}")
    print(f"🎯 投注成功: {bet_success}")
    print(f"❌ 投注失败: {bet_failure}")
    print(f"📈 成功率: {success_rate:.2f}%")

    print(f"\n{Fore.RED}📉 下注失败原因统计：{Style.RESET_ALL}")
    if bet_failure_reasons:
        for reason, info in bet_failure_reasons.items():
            users_list = ", ".join(sorted(info[ "users" ]))
            print(f"  - {reason}: {info[ 'count' ]} 次，对应用户: {users_list}")
    else:
        print("  无")