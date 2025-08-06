# K3不同类型下注
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

# === 接口地址配置 ===
API_BASE = "https://sit-lotteryh5.wmgametransit.com/api/Lottery"
DRAW_BASE = "https://draw.tbgametransit.com/K3"

GET_USER_INFO_URL = f"{API_BASE}/GetUserInfo"
GET_BALANCE_URL = f"{API_BASE}/GetBalance"
BET_URL = f"{API_BASE}/K3Bet"

# === 下注记录接口 ===
GET_BET_RECORD_URL = "https://api.wmgametransit.com/api/Lottery/GetRecordPage"

# === 本地配置 ===
USERNAME_FILE = "D:/figo/工具/VScode/Artest/username8005.txt"  # 会员目录
MAX_TOKENS_TO_RUN = 20  # 同时运行的用户数
SUPPORTED_GAME_CODES = [ 'K3_1M', 'K3_3M', 'K3_5M', 'K3_10M']

# === 统计数据结构 ===
stats_lock = threading.Lock()
total_users = 0
login_failures = 0
bet_success = 0
bet_failure = 0
# 使用字典记录失败原因和对应的用户列表
bet_failure_details = defaultdict(list)

# === 全局日志锁 ===
log_lock = threading.Lock()


# === 工具函数 ===
def compute_md5_upper(s: str) -> str:
    """返回大写MD5摘要"""
    return hashlib.md5(s.encode("utf-8")).hexdigest().upper()


def generate_random_number_str(length=12) -> str:
    """生成指定位数的随机数字字符串，首位不为0"""
    return str(random.randint(1, 9)) + ''.join(str(random.randint(0, 9)) for _ in range(length - 1))


def get_current_timestamp() -> str:
    """获取当前10位时间戳"""
    return str(int(time.time()))[ -10:]


def sort_object_keys(obj: Dict[ str, Any]) -> str:
    """对对象键排序并转换为JSON字符串"""
    return json.dumps({ k: obj[ k] for k in sorted(obj.keys()) }, separators=(',', ':'))


def get_signature(data: dict) -> str:
    """计算签名，排除特定字段"""
    sign_data = { k: v for k, v in data.items() if k not in [ 'signature', 'timestamp', 'betContent']}
    json_str = sort_object_keys(sign_data)
    return compute_md5_upper(json_str)


def read_usernames_from_file(filename: str) -> List[ str]:
    """读取用户名文件"""
    try:
        with open(filename, 'r', encoding="utf-8") as file:
            usernames = [ line.strip() for line in file.readlines() if line.strip()]
        print(f"读取到 {len(usernames)} 个用户名")
        return usernames
    except Exception as e:
        print(f"读取用户名文件错误: {e}")
        return [ ]


# === 登录流程 ===
LOGIN_URL = "https://sitlotteryapi.22889.club/api/webapi/Login"


def get_random_str(length: int) -> str:
    """生成随机字符串"""
    chars = '1234567890abcdefghijklmnopqrstuvwxyz'
    return ''.join(random.choice(chars) for _ in range(length))


def generate_login_data(username: str) -> Dict[ str, Any ]:
    """构造登录参数"""
    timestamp = get_current_timestamp()
    random_str = get_random_str(32)
    data = { "language": 0, "logintype": "mobile", "phonetype": 0, "pwd": "q123q123", "random": random_str,
             "signature": "", "timestamp": timestamp, "username": username}
    # 计算签名并添加到数据
    data[ "signature"] = get_signature(data)
    return data


def login_user(username: str) -> Tuple[ Optional[ str], str ]:
    """执行登录操作并返回token和响应内容"""
    data = generate_login_data(username)
    try:
        response = requests.post(LOGIN_URL, json=data, timeout=10)
        if response.status_code == 200:
            res = response.json()
            if res.get("code") == 0:
                url = res.get("data", { }).get("lotteryLoginUrl")
                if url:
                    token = parse_qs(urlparse(url).query).get("Token", [ None ])[ 0 ]
                    return token, response.text
        return None, response.text
    except Exception as e:
        return None, f"登录异常: {e}"


# === 获取用户信息 ===
def get_user_info(token: str) -> Tuple[ Optional[ Dict[ str, Any]], Optional[ str], str]:
    """获取用户信息并返回新的认证token和响应内容"""
    random_num = random.randint(100000000000, 999999999999)
    params = { "language": "en", "random": str(random_num), "timestamp": get_current_timestamp(),
               "signature": compute_md5_upper(f'{{"language":"en","random":{random_num}}}')}
    url = f"{GET_USER_INFO_URL}?{urlencode(params)}"
    headers = { "Authorization": f"Bearer {token}"}
    try:
        resp = requests.get(url, headers=headers, timeout=10)
        return resp.json(), resp.headers.get("Authorization", "").replace("Bearer ", ""), resp.text
    except Exception as e:
        return None, None, f"获取用户信息失败: {e}"


# === 获取用户余额 ===
def get_balance(token: str) -> Tuple[ Optional[ Dict[ str, Any]], str]:
    """获取用户余额信息和响应内容"""
    random_num = generate_random_number_str()
    params = { "language": "en", "random": random_num, "timestamp": get_current_timestamp(),
               "signature": compute_md5_upper(f'{{"language":"en","random":{random_num}}}')}
    url = f"{GET_BALANCE_URL}?{urlencode(params)}"
    headers = { "Authorization": f"Bearer {token}"}
    try:
        resp = requests.get(url, headers=headers, timeout=10)
        return resp.json(), resp.text
    except Exception as e:
        return None, f"获取余额异常: {e}"


# === 获取当前期号 ===
def get_issue_number(game_code: str) -> Tuple[ Optional[ str], str]:
    """获取指定游戏的当前期号和响应内容"""
    try:
        ts = int(time.time() * 1000)
        url = f"{DRAW_BASE}/{game_code}.json?ts={ts}"
        resp = requests.get(url, timeout=10)
        resp.raise_for_status()
        json_data = resp.json()
        return json_data.get("current", { }).get("issueNumber"), resp.text
    except Exception as e:
        return None, f"获取期号异常: {e}"


# === 获取开奖历史 ===
def get_history_issue_page(game_code: str) -> Tuple[ Optional[ Dict[ str, Any]], str]:
    """获取开奖历史数据和响应内容"""
    try:
        ts = int(time.time() * 1000)
        url = f"{DRAW_BASE}/{game_code}/GetHistoryIssuePage.json?ts={ts}"
        resp = requests.get(url, timeout=10)
        return resp.json(), resp.text
    except Exception as e:
        return None, f"获取开奖历史异常: {e}"


# === 下注接口 ===
def place_bet(token: str, game_code: str, issue_number: str, amount: int, bet_multiple: int,
              bet_content: List[ str]) -> Tuple[ bool, Optional[ str], str]:
    """执行下注操作并返回响应内容"""
    random_str = generate_random_number_str()
    timestamp = int(time.time())

    # 构造签名数据
    sign_map = { "amount": amount, "betMultiple": bet_multiple, "gameCode": game_code, "issueNumber": issue_number,
                 "language": "en", "random": int(random_str) }
    sign_json = json.dumps({ k: sign_map[ k] for k in sorted(sign_map)}, separators=(',', ':'))
    signature = compute_md5_upper(sign_json)

    # 构造请求数据
    data = { "gameCode": game_code, "issueNumber": issue_number, "amount": str(amount),
             "betMultiple": str(bet_multiple), "betContent": bet_content, "language": "en", "random": random_str,
             "signature": signature, "timestamp": timestamp}

    headers = { "Authorization": f"Bearer {token}", "Content-Type": "application/json"}

    try:
        resp = requests.post(BET_URL, headers=headers, json=data, timeout=10)
        if resp.status_code == 200:
            res_json = resp.json()
            if res_json.get("code") == 0:
                return True, None, resp.text
            else:
                return False, f"{res_json.get('code')}_{res_json.get('msg')}", resp.text
        else:
            return False, f"HTTP_{resp.status_code}", resp.text
    except Exception as e:
        return False, f"EXCEPTION_{str(e)}", str(e)


def get_bet_record_page(game_code: str, page_size: int, page_no: int, language: str, token: str) -> Tuple[
    Optional[ Dict[ str, Any ] ], str ]:
    """获取下注记录页面，返回数据和响应文本"""
    random_num_str = generate_random_number_str()
    random_num = int(random_num_str)
    params = { "pageSize": page_size, "pageNo": page_no, "gameCode": game_code, "language": language,
        "random": random_num }

    # 修复签名计算：包含所有参数
    sign_json = json.dumps({ k: params[ k ] for k in sorted(params) }, separators=(',', ':'))
    signature = compute_md5_upper(sign_json)

    params[ "signature" ] = signature
    params[ "timestamp" ] = int(time.time())

    headers = { "Authorization": f"Bearer {token}" }
    try:
        resp = requests.get(GET_BET_RECORD_URL, params=params, headers=headers, timeout=10)
        return resp.json(), resp.text
    except Exception as e:
        return None, f"获取下注记录异常: {e}"


# === 执行流程 ===
def run_flow(username: str):
    """单个用户的完整执行流程"""
    global total_users, login_failures, bet_success, bet_failure, bet_failure_details

    # 随机选择一个游戏类型
    game_code = random.choice(SUPPORTED_GAME_CODES)

    # 收集所有日志行
    log_lines = [ ]

    # 添加流程开始标题
    title = f"================================================================ 用户 {{{username}}} 流程开始 (游戏: {game_code})================================================================="
    log_lines.append(title)

    # 更新总用户数统计
    with stats_lock:
        total_users += 1

    # 1. 登录获取token
    log_lines.append("\033[1m[1] 用户登录\033[0m")
    token, login_response = login_user(username)
    log_lines.append(f"    响应: {login_response}")
    if token:
        log_lines.append(f"    登录成功，Token: {token}")
    else:
        log_lines.append("    ❌ 登录失败")
        with stats_lock:
            login_failures += 1
        # 输出当前用户的所有日志
        with log_lock:
            for line in log_lines:
                print(line)
        return

    # 2. 获取用户信息
    log_lines.append("\033[1m[2] 用户信息\033[0m")
    user_info, bet_token, user_info_response = get_user_info(token)
    log_lines.append(f"    响应: {user_info_response}")
    if not user_info:
        log_lines.append("    ❌ 获取用户信息失败")
        # 输出当前用户的所有日志
        with log_lock:
            for line in log_lines:
                print(line)
        return

    # 使用新token（如果存在）
    final_token = bet_token or token
    if bet_token:
        log_lines.append(f"    获取到新Token: {bet_token}")

    # 3. 获取余额
    log_lines.append("\033[1m[3] 获取余额\033[0m")
    balance_info, balance_response = get_balance(final_token)
    log_lines.append(f"    响应: {balance_response}")
    if balance_info and balance_info.get('data'):
        balance = balance_info[ 'data' ].get('balance', 0)
        log_lines.append(f"    当前余额: {balance}")
    else:
        log_lines.append("    ⚠️ 获取余额失败")

    # 4. 获取当前期号
    log_lines.append("\033[1m[4] 当前期号\033[0m")
    issue, issue_response = get_issue_number(game_code)
    log_lines.append(f"    响应: {issue_response}")
    if not issue:
        log_lines.append("    ❌ 获取期号失败")
        # 输出当前用户的所有日志
        with log_lock:
            for line in log_lines:
                print(line)
        return

    # 金额设置为 10 ~ 1000 随机
    amount = random.randint(1, 1000)  # 随机金额
    log_lines.append(f"    当前期号: {issue}, 下注金额: {amount}")

    # 下注类型
    bet_options = (
        'SumNum_3', 'SumNum_4', 'SumNum_5', 'SumNum_6', 'SumNum_7', 'SumNum_8', 'SumNum_9', 'SumNum_10', 'SumNum_11',
        'SumNum_12', 'SumNum_13', 'SumNum_14', 'SumNum_15', 'SumNum_16', 'SumNum_17', 'SumNum_18', 'NumSame2_11',
        'NumSame2_22', 'NumSame2_33', 'NumSame2_44', 'NumSame2_55', 'NumSame2_66', 'NumSame2Mult_11_2',
        'NumSame2Mult_11_3', 'NumSame2Mult_11_4', 'NumSame2Mult_11_5', 'NumSame2Mult_11_6', 'NumSame2Mult_11_2_3',
        'NumSame2Mult_11_2_4', 'NumSame2Mult_11_2_5', 'NumSame2Mult_11_2_6', 'NumSame2Mult_11_3_4',
        'NumSame2Mult_11_3_5', 'NumSame2Mult_11_3_6', 'NumSame2Mult_11_4_5', 'NumSame2Mult_11_4_6',
        'NumSame2Mult_11_5_6', 'NumSame2Mult_11_2_3_4', 'NumSame2Mult_11_3_4_5', 'NumSame2Mult_11_3_4_6',
        'NumSame2Mult_11_3_5_6', 'NumSame2Mult_11_4_5_6', 'NumSame2Mult_11_2_3_4_5', 'NumSame2Mult_11_2_3_4_6',
        'NumSame2Mult_11_2_3_5_6', 'NumSame2Mult_11_2_4_5_6', 'NumSame2Mult_11_3_4_5_6', 'NumSame2Mult_22_1',
        'NumSame2Mult_22_3', 'NumSame2Mult_22_4', 'NumSame2Mult_22_5', 'NumSame2Mult_22_6', 'NumSame2Mult_22_1_3',
        'NumSame2Mult_22_1_4', 'NumSame2Mult_22_1_5', 'NumSame2Mult_22_1_6', 'NumSame2Mult_22_3_4',
        'NumSame2Mult_22_3_5', 'NumSame2Mult_22_3_6', 'NumSame2Mult_22_4_5', 'NumSame2Mult_22_4_6',
        'NumSame2Mult_22_5_6', 'NumSame2Mult_22_1_3_4', 'NumSame2Mult_22_1_3_5', 'NumSame2Mult_22_1_3_6',
        'NumSame2Mult_22_3_4_5', 'NumSame2Mult_22_3_4_6', 'NumSame2Mult_22_3_5_6', 'NumSame2Mult_22_4_5_6',
        'NumSame2Mult_22_1_3_4_5', 'NumSame2Mult_22_1_3_4_6', 'NumSame2Mult_22_1_3_5_6', 'NumSame2Mult_22_3_4_5_6',
        'NumSame2Mult_33_1', 'NumSame2Mult_33_2', 'NumSame2Mult_33_4', 'NumSame2Mult_33_5', 'NumSame2Mult_33_6',
        'NumSame2Mult_33_1_2', 'NumSame2Mult_33_1_4', 'NumSame2Mult_33_1_5', 'NumSame2Mult_33_1_6',
        'NumSame2Mult_33_2_4', 'NumSame2Mult_33_2_5', 'NumSame2Mult_33_2_6', 'NumSame2Mult_33_4_5',
        'NumSame2Mult_33_4_6', 'NumSame2Mult_33_5_6', 'NumSame2Mult_33_1_2_4', 'NumSame2Mult_33_1_2_5',
        'NumSame2Mult_33_1_2_6', 'NumSame2Mult_33_2_4_5', 'NumSame2Mult_33_2_4_6', 'NumSame2Mult_33_2_5_6',
        'NumSame2Mult_33_4_5_6', 'NumSame2Mult_33_1_2_4_5', 'NumSame2Mult_33_1_2_4_6', 'NumSame2Mult_33_1_2_5_6',
        'NumSame2Mult_33_2_4_5_6', 'NumSame2Mult_44_1', 'NumSame2Mult_44_2', 'NumSame2Mult_44_3', 'NumSame2Mult_44_5',
        'NumSame2Mult_44_6', 'NumSame2Mult_44_1_2', 'NumSame2Mult_44_1_3', 'NumSame2Mult_44_1_5', 'NumSame2Mult_44_1_6',
        'NumSame2Mult_44_2_3', 'NumSame2Mult_44_2_5', 'NumSame2Mult_44_2_6', 'NumSame2Mult_44_3_5',
        'NumSame2Mult_44_3_6', 'NumSame2Mult_44_5_6', 'NumSame2Mult_44_1_2_3', 'NumSame2Mult_44_1_2_5',
        'NumSame2Mult_44_1_2_6', 'NumSame2Mult_44_2_3_5', 'NumSame2Mult_44_2_3_6', 'NumSame2Mult_44_2_5_6',
        'NumSame2Mult_44_3_5_6', 'NumSame2Mult_44_1_2_3_5', 'NumSame2Mult_44_1_2_3_6', 'NumSame2Mult_44_1_2_5_6',
        'NumSame2Mult_44_2_3_5_6', 'NumSame2Mult_44_1_2_3_5_6', 'NumSame2Mult_55_1', 'NumSame2Mult_55_2',
        'NumSame2Mult_55_3', 'NumSame2Mult_55_4', 'NumSame2Mult_55_6', 'NumSame2Mult_55_1_2', 'NumSame2Mult_55_1_3',
        'NumSame2Mult_55_1_4', 'NumSame2Mult_55_1_6', 'NumSame2Mult_55_2_3', 'NumSame2Mult_55_2_4',
        'NumSame2Mult_55_2_6', 'NumSame2Mult_55_3_4', 'NumSame2Mult_55_3_6', 'NumSame2Mult_55_4_6',
        'NumSame2Mult_55_1_2_3', 'NumSame2Mult_55_1_2_4', 'NumSame2Mult_55_1_2_6', 'NumSame2Mult_55_1_3_4',
        'NumSame2Mult_55_1_3_6', 'NumSame2Mult_55_1_4_6', 'NumSame2Mult_55_2_3_4', 'NumSame2Mult_55_2_3_6',
        'NumSame2Mult_55_2_4_6', 'NumSame2Mult_55_3_4_6', 'NumSame2Mult_55_1_2_3_4', 'NumSame2Mult_55_1_2_3_6',
        'NumSame2Mult_55_1_2_4_6', 'NumSame2Mult_55_1_3_4_6', 'NumSame2Mult_55_2_3_4_6', 'NumSame2Mult_55_1_2_3_4_6',
        'NumSame2Mult_66_1', 'NumSame2Mult_66_2', 'NumSame2Mult_66_3', 'NumSame2Mult_66_4', 'NumSame2Mult_66_5',
        'NumSame2Mult_66_1_2', 'NumSame2Mult_66_1_3', 'NumSame2Mult_66_1_4', 'NumSame2Mult_66_1_5',
        'NumSame2Mult_66_2_3', 'NumSame2Mult_66_2_4', 'NumSame2Mult_66_2_5', 'NumSame2Mult_66_3_4',
        'NumSame2Mult_66_3_5', 'NumSame2Mult_66_4_5', 'NumSame2Mult_66_1_2_3', 'NumSame2Mult_66_1_2_4',
        'NumSame2Mult_66_1_2_5', 'NumSame2Mult_66_1_3_4,', 'NumSame2Mult_66_1_3_5', 'NumSame2Mult_66_1_4_5',
        'NumSame2Mult_66_2_3_4', 'NumSame2Mult_66_2_3_5', 'NumSame2Mult_66_2_4_5', 'NumSame2Mult_66_3_4_5',
        'NumSame2Mult_66_1_2_3_4', 'NumSame2Mult_66_1_2_3_5', 'NumSame2Mult_66_1_2_4_5', 'NumSame2Mult_66_1_3_4_5',
        'NumSame2Mult_66_2_3_4_5', 'NumSame2Mult_66_1_2_3_4_5', 'NumSame3_111', 'NumSame3_222', 'NumSame3_333',
        'NumSame3_444', 'NumSame3_555', 'NumSame3_666', 'NumSame3All_AAA', 'NumDiff3_1_2_3', 'NumDiff3_1_2_4',
        'NumDiff3_1_2_5', 'NumDiff3_1_2_6', 'NumDiff3_1_3_4', 'NumDiff3_1_3_5', 'NumDiff3_1_3_6', 'NumDiff3_1_4_5',
        'NumDiff3_1_4_6', 'NumDiff3_1_5_6', 'NumDiff3_2_3_4', 'NumDiff3_2_3_5', 'NumDiff3_2_3_6', 'NumDiff3_2_4_5',
        'NumDiff3_2_4_6', 'NumDiff3_2_5_6', 'NumDiff3_3_4_5', 'NumDiff3_3_4_6', 'NumDiff3_3_5_6', 'NumDiff3_4_5_6',
        'NumDiff3_1_2_3_4', 'NumDiff3_1_2_3_5', 'NumDiff3_1_2_3_6', 'NumDiff3_1_2_4_5', 'NumDiff3_1_2_4_6',
        'NumDiff3_1_2_5_6', 'NumDiff3_1_3_4_5', 'NumDiff3_1_3_4_6', 'NumDiff3_1_3_5_6', 'NumDiff3_1_4_5_6',
        'NumDiff3_2_3_4_5', 'NumDiff3_2_3_4_6', 'NumDiff3_2_3_5_6', 'NumDiff3_2_4_5_6', 'NumDiff3_3_4_5_6',
        'NumDiff3_1_2_3_4_5', 'NumDiff3_1_2_3_4_6', 'NumDiff3_1_2_3_5_6', 'NumDiff3_1_2_4_5_6', 'NumDiff3_1_3_4_5_6',
        'NumDiff3_2_3_4_5_6', 'NumNear3All_ABC', 'NumDiff2_1_2', 'NumDiff2_1_3', 'NumDiff2_1_4', 'NumDiff2_1_5',
        'NumDiff2_1_6', 'NumDiff2_2_3', 'NumDiff2_2_4', 'NumDiff2_2_5', 'NumDiff2_2_6', 'NumDiff2_3_4', 'NumDiff2_3_5',
        'NumDiff2_3_6', 'NumDiff2_4_5', 'NumDiff2_4_6', 'NumDiff2_5_6', 'NumDiff2_1_2_3', 'NumDiff2_1_2_4',
        'NumDiff2_1_2_5', 'NumDiff2_1_2_6', 'NumDiff2_1_3_4', 'NumDiff2_1_3_5', 'NumDiff2_1_3_6', 'NumDiff2_1_4_5',
        'NumDiff2_1_4_6', 'NumDiff2_1_5_6', 'NumDiff2_2_3_4', 'NumDiff2_2_3_5', 'NumDiff2_2_3_6', 'NumDiff2_2_4_5',
        'NumDiff2_2_4_6', 'NumDiff2_2_5_6', 'NumDiff2_3_4_5', 'NumDiff2_3_4_6', 'NumDiff2_3_5_6', 'NumDiff2_4_5_6',
        'NumDiff2_1_2_3_4', 'NumDiff2_1_2_3_5', 'NumDiff2_1_2_3_6', 'NumDiff2_1_2_4_5', 'NumDiff2_1_2_4_6',
        'NumDiff2_1_2_5_6', 'NumDiff2_1_3_4_5', 'NumDiff2_1_3_4_6', 'NumDiff2_1_3_5_6', 'NumDiff2_1_4_5_6',
        'NumDiff2_2_3_4_5', 'NumDiff2_2_3_4_6', 'NumDiff2_2_3_5_6', 'NumDiff2_2_4_5_6', 'NumDiff2_3_4_5_6',
        'NumDiff2_1_2_3_4_5', 'NumDiff2_1_2_3_4_6', 'NumDiff2_1_2_3_5_6', 'NumDiff2_1_2_4_5_6', 'NumDiff2_1_3_4_5_6',
        'NumDiff2_2_3_4_5_6', 'NumDiff2_1_2_3_4_5_6')
    selected_bet_content = [ random.choice(bet_options) ]

    # 5. 执行下注
    log_lines.append("\033[1m[5] 游戏下注\033[0m")
    success, reason, bet_response = place_bet(final_token, game_code, issue, amount, 1, selected_bet_content)
    log_lines.append(f"    响应: {bet_response}")
    if success:
        log_lines.append("    ✅ 下注成功!")
        with stats_lock:
            bet_success += 1
    else:
        log_lines.append(f"    ❌ 下注失败! 原因: {reason}")
        with stats_lock:
            bet_failure += 1
            bet_failure_details[ reason ].append(username)

    # 6. 获取开奖历史
    log_lines.append("\033[1m[6] 开奖历史\033[0m")
    history_data, history_response = get_history_issue_page(game_code)
    log_lines.append(f"    响应: {history_response}")
    if history_data and history_data.get('data'):
        count = len(history_data[ 'data' ].get('list', [ ]))
        log_lines.append(f"    开奖历史条数: {count}")
    else:
        log_lines.append("    ⚠️ 获取开奖历史失败")

    # 7. 获取下注记录
    log_lines.append("\033[1m[7] 下注记录\033[0m")
    bet_records, bet_records_resp = get_bet_record_page(game_code, page_size=10, page_no=1, language="en",
                                                        token=final_token)
    log_lines.append(f"    响应: {bet_records_resp}")
    if bet_records and bet_records.get("data"):
        records_list = bet_records[ "data" ].get("list", [ ])
        log_lines.append(f"    下注记录条数: {len(records_list)}")
    else:
        log_lines.append("    ⚠️ 获取下注记录失败")

    # 流程结束
    log_lines.append(
        f"================================================================ 用户 {{{username}}}流程结束 =================================================================")

    # 输出当前用户的所有日志（确保不会被其他用户日志打断）
    with log_lock:
        for line in log_lines:
            print(line)
        print()  # 添加空行分隔用户


# === 主函数入口 ===
if __name__ == "__main__":
    # 读取用户名列表
    usernames = read_usernames_from_file(USERNAME_FILE)
    if not usernames:
        print("❌ 未读取到有效用户名，程序退出")
        exit(1)

    # 创建并启动线程
    threads = [ ]
    for username in usernames[ :MAX_TOKENS_TO_RUN ]:
        t = threading.Thread(target=run_flow, args=(username,))
        t.start()
        threads.append(t)
        time.sleep(0.2)  # 避免并发冲突

    # 等待所有线程完成
    for t in threads:
        t.join()

    # 打印统计汇总
    print("\n" + "=" * 50)
    print("📊 ===== 流程统计汇总 =====")
    print("=" * 50)
    print(f"👥 总用户数: {total_users}")
    print(f"🔒 登录失败数: {login_failures}")
    print(f"✅ 下注成功数: {bet_success}")
    print(f"❌ 下注失败数: {bet_failure}")

    # 打印详细的失败原因和用户
    if bet_failure_details:
        print("\n📉 下注失败原因详情:")
        for reason, users in bet_failure_details.items():
            print(f"  - 原因: {reason}")
            print(f"    影响用户: {', '.join(users)}")
            print(f"    失败次数: {len(users)}")
    else:
        print("\n🎉 所有用户下注均成功!")