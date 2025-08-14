"""
TRXWinGo 不同类型下注 自动化投注测试脚本
该脚本模拟用户登录、获取用户信息、余额查询、下注、查询下注记录等操作
日期: 2025-08-14
"""
import hashlib
import json
import random
import time
import threading
import queue
from typing import List, Optional, Tuple, Callable
from urllib.parse import urlencode, urlparse, parse_qs
from collections import OrderedDict, defaultdict
import requests

# === ANSI颜色码 ===
GREEN_BOLD = "\033[1;32m"  # 绿色加粗
RED_BOLD = "\033[1;31m"    # 红色加粗
GRAY_BOLD = "\033[1;90m"  # 灰色加粗
RESET = "\033[0m"  # 重置样式

# === 接口地址配置 ===
API_BASE = "https://sit-lotteryh5.wmgametransit.com/api/Lottery"
DRAW_BASE = "https://draw.tbgametransit.com/TrxWinGo"

GET_USER_INFO_URL = f"{API_BASE}/GetUserInfo"
GET_BALANCE_URL = f"{API_BASE}/GetBalance"
BET_URL = f"{API_BASE}/TrxWinGoBet"
GET_BET_RECORD_URL = f"{API_BASE}/GetRecordPage"
LOGIN_URL = "https://sitlotteryapi.22889.club/api/webapi/Login"

# === 本地配置 ===
USERNAME_FILE = "D:/figo/工具/pycharm/PycharmProjects/WinGo/username.txt"  # 会员目录
MAX_TOKENS_TO_RUN = 40  # 同时运行的用户数
REQUEST_TIMEOUT = 10  # 请求超时时间（秒）

BET_CONTENT_OPTIONS = ['Num_0', 'Num_1', 'Num_2', 'Num_3', 'Num_4', 'Num_5', 'Num_6', 'Num_7', 'Num_8',
                       'Num_9', 'Color_Red', 'Color_Violet', 'Color_Green', 'BigSmall_Small', 'BigSmall_Big']

SUPPORTED_GAME_CODES = ['TrxWinGo_1M', 'TrxWinGo_3M', 'TrxWinGo_5M', 'TrxWinGo_10M']

# === 全局统计变量 ===
stats_lock = threading.Lock()
total_users = 0
login_failures = 0
bet_success = 0
bet_failures = 0

# 使用字典记录失败原因和对应的用户列表
failure_details = defaultdict(list)

# 日志队列和打印线程
log_queue = queue.Queue()
log_thread_running = True


# === 工具函数 ===

def compute_md5_upper(s: str) -> str:
    """计算字符串的 MD5 并转为大写"""
    return hashlib.md5(s.encode("utf-8")).hexdigest().upper()


def generate_random_number_str(length=12) -> str:
    """生成指定长度的随机数字字符串，首位不为0"""
    return str(random.randint(1, 9)) + ''.join(str(random.randint(0, 9)) for _ in range(length - 1))


def get_current_timestamp() -> str:
    """获取当前时间戳（10位字符串）"""
    return str(int(time.time()))[-10:]


def sort_object_keys(obj: dict) -> str:
    """按 key 排序对象并生成 JSON 字符串（用于签名）"""
    sorted_obj = {k: obj[k] for k in sorted(obj.keys())}
    return json.dumps(sorted_obj, separators=(',', ':'))


def get_signature(json_body: dict) -> str:
    """生成签名（排除 signature 和 timestamp 字段）"""
    filtered = {k: v for k, v in json_body.items() if
                k not in ['signature', 'timestamp'] and v not in [None, '', []]}
    return compute_md5_upper(sort_object_keys(filtered))


def get_random_str(length: int) -> str:
    """生成随机字符串"""
    chars = '1234567890abcdefghijklmnopqrstuvwxyz'
    return ''.join(random.choice(chars) for _ in range(length))


def read_usernames_from_file(filename: str) -> List[str]:
    """读取用户名文件"""
    try:
        with open(filename, 'r', encoding="utf-8") as f:
            usernames = [line.strip() for line in f if line.strip()]
        log_print(f"📄 成功读取 {len(usernames)} 个用户名")
        return usernames
    except Exception as e:
        log_print(f"❌ 无法读取用户名文件: {e}")
        return []


# === 日志处理 ===

def log_print(message: str):
    """添加消息到日志队列"""
    log_queue.put(message)


def log_worker():
    """日志打印线程，确保日志有序输出"""
    global log_thread_running
    while log_thread_running or not log_queue.empty():
        try:
            message = log_queue.get(timeout=0.1)
            print(message)
        except queue.Empty:
            continue


# === 登录函数 ===

def generate_login_data(username: str) -> dict:
    """生成登录请求数据"""
    timestamp = get_current_timestamp()
    random_str = get_random_str(32)
    data = {"language": 0, "logintype": "mobile", "phonetype": 0, "pwd": "q123q123", "random": random_str,
            "timestamp": timestamp, "username": username, "signature": ""}
    data["signature"] = get_signature(data)
    return data


def login_user(username: str, log_func) -> Tuple[Optional[str], Optional[str]]:
    """执行登录并返回Token和失败原因"""
    log_func(f"{GREEN_BOLD}[1] 用户登录{RESET}")
    data = generate_login_data(username)
    try:
        resp = requests.post(LOGIN_URL, json=data, headers={"Content-Type": "application/json"},
                             timeout=REQUEST_TIMEOUT)
        log_func(f"    ↳ 响应: {resp.text[:200]}{'...' if len(resp.text) > 200 else ''}")

        if resp.status_code == 200:
            json_data = resp.json()
            if json_data.get("code") == 0:
                login_url = json_data.get("data", {}).get("lotteryLoginUrl", "")
                token = parse_qs(urlparse(login_url).query).get("Token", [None])[0]
                return token, None
            else:
                error_msg = json_data.get("msg", "登录失败")
                log_func(f"    ❌ 登录失败: {error_msg}")
                return None, f"登录失败: {error_msg}"
        else:
            error_msg = f"HTTP错误: {resp.status_code}"
            log_func(f"    ❌ {error_msg}")
            return None, error_msg
    except Exception as e:
        error_msg = f"登录异常: {str(e)[:100]}"
        log_func(f"    ❌ {error_msg}")
        return None, error_msg


# === 获取用户信息 ===

def get_user_info(bearer_token: str, log_func) -> Tuple[Optional[dict], Optional[str], Optional[str]]:
    """获取用户信息及下注专用Token和失败原因"""
    log_func(f"{GREEN_BOLD}[2] 用户信息{RESET}")
    random_num = generate_random_number_str()
    params = {"language": "en", "random": random_num, "timestamp": get_current_timestamp(),
              "signature": compute_md5_upper(f'{{"language":"en","random":{random_num}}}')}
    url = f"{GET_USER_INFO_URL}?{urlencode(params)}"
    headers = {"Authorization": f"Bearer {bearer_token}"}

    try:
        resp = requests.get(url, headers=headers, timeout=REQUEST_TIMEOUT)
        log_func(f"    ↳ 响应: {resp.text[:200]}{'...' if len(resp.text) > 200 else ''}")

        bet_token = resp.headers.get("Authorization", "").replace("Bearer ", "").strip()
        return resp.json(), bet_token, None
    except Exception as e:
        error_msg = f"异常: {str(e)[:100]}"
        log_func(f"    ❌ {error_msg}")
        return None, None, error_msg


# === 获取余额 ===

def get_balance(bearer_token: str, log_func) -> Tuple[Optional[dict], float, Optional[str]]:
    """获取用户余额和失败原因"""
    log_func(f"{GREEN_BOLD}[3] 获取余额{RESET}")
    random_num = generate_random_number_str()
    params = {"language": "en", "random": random_num, "timestamp": get_current_timestamp(),
              "signature": compute_md5_upper(f'{{"language":"en","random":{random_num}}}')}
    url = f"{GET_BALANCE_URL}?{urlencode(params)}"
    headers = {"Authorization": f"Bearer {bearer_token}"}

    try:
        resp = requests.get(url, headers=headers, timeout=REQUEST_TIMEOUT)
        log_func(f"    ↳ 响应: {resp.text[:200]}{'...' if len(resp.text) > 200 else ''}")

        data = resp.json()
        balance = data.get('data', {}).get('balance', 0.0)
        log_func(f"    ↳ 当前余额: {balance}")
        return data, balance, None
    except Exception as e:
        error_msg = f"异常: {str(e)[:100]}"
        log_func(f"    ❌ {error_msg}")
        return None, 0.0, error_msg


# === 获取当前期号 ===

def get_issue_number(game_code: str, log_func) -> Tuple[Optional[str], Optional[str]]:
    """获取当前期号和失败原因"""
    log_func(f"{GREEN_BOLD}[4] 当前期号{RESET}")
    try:
        url = f"{DRAW_BASE}/{game_code}.json?ts={int(time.time() * 1000)}"
        resp = requests.get(url, timeout=REQUEST_TIMEOUT)
        log_func(f"    ↳ 响应: {resp.text[:200]}{'...' if len(resp.text) > 200 else ''}")

        issue_number = resp.json().get("current", {}).get("issueNumber")
        if issue_number:
            log_func(f"    ↳ 当前期号: {issue_number}")
            return issue_number, None
        else:
            error_msg = "未获取到期号"
            log_func(f"    ❌ {error_msg}")
            return None, error_msg
    except Exception as e:
        error_msg = f"异常: {str(e)[:100]}"
        log_func(f"    ❌ {error_msg}")
        return None, error_msg


# === 下单投注 ===

def place_bet(
    bearer_token: str,
    game_code: str,
    issue_number: str,
    amount: int,
    bet_content: str,
    log_func: Callable[[str], None]
     ) -> Tuple[Optional[dict], Optional[str]]:
    """提交下注请求并返回失败原因"""
    log_func(f"{GREEN_BOLD}[5] 游戏下注{RESET}")
    log_func(f"    ↳ 游戏: {game_code}, 期号: {issue_number}, 内容: {bet_content}, 金额: {amount}")

    random_num = generate_random_number_str()
    body = OrderedDict(
        [("amount", amount), ("betContent", bet_content), ("betMultiple", 1), ("gameCode", game_code),
         ("issueNumber", issue_number), ("language", "en"), ("random", int(random_num))])

    sign_str = json.dumps(body, separators=(',', ':'))
    body["signature"] = compute_md5_upper(sign_str)
    body["timestamp"] = int(time.time())
    headers = {"Authorization": f"Bearer {bearer_token}", "Content-Type": "application/json"}

    try:
        resp = requests.post(BET_URL, headers=headers, json=body, timeout=REQUEST_TIMEOUT)
        log_func(f"    ↳ 响应: {resp.text[:200]}{'...' if len(resp.text) > 200 else ''}")
        
        if resp.status_code == 200:
            return resp.json(), None
        else:
            error_msg = f"HTTP错误: {resp.status_code}"
            return None, error_msg
    except Exception as e:
        error_msg = f"异常: {str(e)[:100]}"
        log_func(f"    ❌ {error_msg}")
        return None, error_msg


# === 获取开奖历史 ===

def get_history_issue(game_code: str, log_func) -> Tuple[Optional[dict], Optional[str]]:
    """获取历史开奖列表和失败原因"""
    log_func(f"{GREEN_BOLD}[6] 开奖历史{RESET}")
    try:
        url = f"{DRAW_BASE}/{game_code}/GetHistoryIssuePage.json"
        params = {"ts": int(time.time() * 1000)}
        resp = requests.get(url, params=params, timeout=REQUEST_TIMEOUT)
        log_func(f"    ↳ 响应: {resp.text[:200]}{'...' if len(resp.text) > 200 else ''}")
        return resp.json(), None
    except Exception as e:
        error_msg = f"异常: {str(e)[:100]}"
        log_func(f"    ❌ {error_msg}")
        return None, error_msg

def get_bet_records(bearer_token: str, game_code: str, log_func) -> Tuple[Optional[dict], Optional[str]]:
    """获取下注记录和失败原因"""
    log_func(f"{GREEN_BOLD}[7] 获取下注记录{RESET}")

    random_num = generate_random_number_str(length=12)
    timestamp = int(time.time())

    # 构造签名用参数（排序且有序）
    sign_params = OrderedDict(sorted({
        "gameCode": game_code,
        "language": "zh",
        "pageNo": 1,
        "pageSize": 20,
        "random": int(random_num)
    }.items()))

    # 生成签名字符串：JSON序列化（紧凑格式）
    sign_str = json.dumps(sign_params, separators=(',', ':'))

    # 计算签名
    signature = compute_md5_upper(sign_str)

    # 构造最终请求参数，保持参数顺序（signature和timestamp放最后）
    params = OrderedDict(sign_params)
    params["signature"] = signature
    params["timestamp"] = timestamp

    headers = {
        "Authorization": f"Bearer {bearer_token}",
    }

    try:
        resp = requests.get(GET_BET_RECORD_URL, params=params, headers=headers, timeout=REQUEST_TIMEOUT)

        log_func(f"    ↳ HTTP状态码: {resp.status_code}")
        log_func(f"    ↳ 请求URL: {resp.url}")
        log_func(f"    ↳ 响应文本: {resp.text[:1000]}")

        resp.raise_for_status()
        return resp.json(), None
    except Exception as e:
        error_msg = f"异常: {str(e)[:100]}"
        log_func(f"    ❌ {error_msg}")
        return None, error_msg


# === 流程主逻辑 ===

def run_flow(username: str):
    """用户流程：登录 -> 获取信息 -> 下单 -> 查询余额及记录"""
    global total_users, login_failures, bet_success, bet_failures, failure_details

    # 用户日志缓冲区
    user_logs = []

    def log_local(message: str):
        """将消息添加到用户日志缓冲区"""
        user_logs.append(message)
        
    # 记录失败原因
    user_failures = []

    game_code = random.choice(SUPPORTED_GAME_CODES)

    # 流程开始
    log_local(f"{GREEN_BOLD}================================================ 用户 {username} 流程开始 (游戏: {game_code}) ================================================{RESET}")

    with stats_lock:
        total_users += 1

    # [1] 登录
    token, failure_reason = login_user(username, log_local)
    if not token:
        with stats_lock:
            login_failures += 1
            if failure_reason:
                failure_details[failure_reason].append(username)
                user_failures.append(failure_reason)
        log_local(f"{GRAY_BOLD}================================================ 用户 {username} 流程结束 (游戏: {game_code}) ================================================{RESET}")
        # 输出整个用户日志
        log_print("\n".join(user_logs))
        return

    # [2] 获取用户信息
    user_info, bet_token, failure_reason = get_user_info(token, log_local)
    if not user_info or not bet_token:
        with stats_lock:
            if failure_reason:
                failure_details[failure_reason].append(username)
                user_failures.append(failure_reason)
        log_local(f"{GRAY_BOLD}================================================ 用户 {username} 流程结束 (游戏: {game_code}) ================================================{RESET}")
        log_print("\n".join(user_logs))
        return

    # [3] 获取余额
    balance_info, old_balance, failure_reason = get_balance(token, log_local)
    if not balance_info:
        with stats_lock:
            if failure_reason:
                failure_details[failure_reason].append(username)
                user_failures.append(failure_reason)
        log_local(f"{GRAY_BOLD}================================================ 用户 {username} 流程结束 (游戏: {game_code}) ================================================{RESET}")
        log_print("\n".join(user_logs))
        return

    # [4] 获取期号
    issue, failure_reason = get_issue_number(game_code, log_local)
    if not issue:
        with stats_lock:
            if failure_reason:
                failure_details[failure_reason].append(username)
                user_failures.append(failure_reason)
        log_local(f"{GRAY_BOLD}================================================ 用户 {username} 流程结束 (游戏: {game_code}) ================================================{RESET}")
        log_print("\n".join(user_logs))
        return

    # [5] 下注
    bet_content = random.choice(BET_CONTENT_OPTIONS)
    # 金额设置为 10 ~ 200 随机
    amount: int = random.randint(10, 200) 
    # amount = random.choice([ 10, 20, 50, 100, 200, 500, 1000]) #固定金额

    bet_result, failure_reason = place_bet(
        bearer_token=bet_token, 
        game_code=game_code, 
        issue_number=issue, 
        amount=amount,
        bet_content=bet_content, 
        log_func=log_local
    )

    if bet_result:
        if bet_result.get("code") == 0:
            with stats_lock:
                bet_success += 1
            log_local("    ✅ 下注成功")
        else:
            error_code = bet_result.get("code", "exception")
            error_msg = bet_result.get("msg", "未知错误")
            reason = f"下注失败: {error_code} - {error_msg[:50]}"
            with stats_lock:
                bet_failures += 1
                failure_details[reason].append(username)
                user_failures.append(reason)
            log_local(f"    ❌ {reason}")
    else:
        reason = f"下注请求异常: {failure_reason}" if failure_reason else "下注请求异常"
        with stats_lock:
            bet_failures += 1
            failure_details[reason].append(username)
            user_failures.append(reason)
        log_local(f"    ❌ {reason}")

    # [6] 获取开奖历史
    history, failure_reason = get_history_issue(game_code, log_local)
    if not history and failure_reason:
        with stats_lock:
            failure_details[failure_reason].append(username)
            user_failures.append(failure_reason)
        log_local(f"    ❌ 获取开奖历史失败: {failure_reason}")

    # [7] 获取下注记录
    records, failure_reason = get_bet_records(bet_token, game_code, log_local)
    if not records and failure_reason:
        with stats_lock:
            failure_details[failure_reason].append(username)
            user_failures.append(failure_reason)
        log_local(f"    ❌ 获取下注记录失败: {failure_reason}")

    # 流程结束 - 添加失败原因摘要
    if user_failures:
        log_local(f"{RED_BOLD}    ⚠️ 失败原因: {', '.join(user_failures)}{RESET}")
    else:
        log_local(f"{GREEN_BOLD}    ✅ 所有操作成功完成{RESET}")
        
    log_local(f"{GRAY_BOLD}================ 用户 {username} 流程结束 (游戏: {game_code}) ================{RESET}")

    # 输出整个用户日志
    log_print("\n".join(user_logs))


# === 主程序入口 ===

if __name__ == "__main__":
    # 启动日志打印线程
    log_thread = threading.Thread(target=log_worker, daemon=True)
    log_thread.start()

    usernames = read_usernames_from_file(USERNAME_FILE)
    if not usernames:
        log_print("❌ 未读取到有效用户名，程序退出")
        exit(1)

    threads = []
    for username in usernames[:MAX_TOKENS_TO_RUN]:
        t = threading.Thread(target=run_flow, args=(username,))
        t.start()
        threads.append(t)
        time.sleep(0.1)  # 减少启动间隔

    # 等待所有线程完成
    for t in threads:
        t.join()

    # 停止日志线程
    log_thread_running = False
    log_thread.join(timeout=1.0)

    # 打印统计信息
    print("\n📊 ===== 投注流程统计汇总 =====")
    print(f"👥 总用户数: {total_users}")
    print(f"🔒 登录失败数: {login_failures}")
    print(f"🎯 下注成功数: {bet_success}")
    print(f"❌ 下注失败数: {bet_failures}")

    # 打印详细的失败原因和用户列表
    if failure_details:
        print("\n📜 失败原因详情:")
        for reason, users in failure_details.items():
            print(f"   - 原因: {reason}")
            print(f"     影响用户: {', '.join(users[:5])}{'...' if len(users) > 5 else ''}")
            print(f"     失败次数: {len(users)}")
    else:
        print("\n🎉 所有用户操作均成功完成!")