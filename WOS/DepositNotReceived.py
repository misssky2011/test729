"""
该脚本用于自动化处理“存款未到账”提交流程，包括：
1. 读取用户token
2. 创建充值订单（使用动态签名）
3. 获取充值记录
4. 提取工单入口数据块 (datablock)
5. 提交支付工单
6. 生成签名和随机数
日期：2025/06/30
作者：Figo
"""

import csv
import re
import random
import requests
import json
import time
import os
import sys
import hashlib
import string

# 创建日志目录和文件
def setup_logging():
    if not os.path.exists("logs"):
        os.makedirs("logs")
    log_filename = f"logs/payment_log_{time.strftime('%Y%m%d_%H%M%S')}.txt"
    return log_filename

log_file = setup_logging()

# 日志记录函数
def log_message(message):
    timestamp = time.strftime("%Y-%m-%d %H:%M:%S")
    log_entry = f"[{timestamp}] {message}"
    print(log_entry)
    with open(log_file, "a", encoding="utf-8") as f:
        f.write(log_entry + "\n")

# 读取 CSV 文件中的所有 token
def read_tokens(file_path):
    tokens = []
    try:
        with open(file_path, "r", encoding="utf-8") as file:
            reader = csv.reader(file)
            for row in reader:
                if row and row[0]:
                    tokens.append(row[0])
        log_message(f"成功读取 {len(tokens)} 个 token")
    except Exception as e:
        log_message(f"读取 CSV 文件时发生错误: {e}")
    return tokens

# 生成32位随机字符串（首位不能为0）
def generate_random_32():
    first_char = random.choice(string.ascii_lowercase + '123456789')
    rest_chars = ''.join(random.choices(string.ascii_lowercase + string.digits, k=31))
    return first_char + rest_chars

# 生成12位纯数字 UTR
def generate_utr():
    utr = ''.join(random.choices('0123456789', k=12))
    log_message(f"生成的 UTR: {utr}")
    return utr

# 生成12位纯数字随机数（首位不为0）
def generate_random_12():
    first_digit = random.randint(1, 9)
    other_digits = ''.join([str(random.randint(0, 9)) for _ in range(11)])
    return f"{first_digit}{other_digits}"

# 生成MD5值
def md5_info(data):
    return hashlib.md5(data.encode('utf-8')).hexdigest()

# 按JMeter一致规则生成签名
def calculate_signature(data: dict) -> str:
    filtered_obj = {}
    for key in sorted(data.keys()):
        value = data[key]
        if value not in [None, "", []] and key not in ["signature", "timestamp", "track"] and not isinstance(value, list):
            filtered_obj[key] = value

    json_str = json.dumps(filtered_obj, separators=(',', ':'))
    log_message(f"签名前参数: {json_str}")
    return md5_info(json_str).upper()

# 创建充值订单
def create_recharge_order(token: str) -> bool:
    headers = {"Authorization": token, "Content-Type": "application/json"}
    url = "https://sitlotteryapi.22889.club/api/webapi/ThirdPay"

    random_str = generate_random_32()
    timestamp = int(time.time())

    post_data = {
        "payTypeId": 10161,
        "bankCode": "",
        "urlInfo": "https://sitweb.22889.club,status/rechargeStatus",
        "amount": 888,
        "pixelId": "",
        "vendorId": 1,
        "fbcId": "",
        "fbc": "",
        "fbp": "",
        "adId": "",
        "language": 5,
        "random": random_str,
        "timestamp": timestamp,
        "signature": "",
    }

    post_data["signature"] = calculate_signature(post_data)
    log_message(f"生成动态签名: random={random_str}, timestamp={timestamp}, signature={post_data['signature']}")

    try:
        response = requests.post(url, headers=headers, data=json.dumps(post_data), timeout=10)
        log_message(f"创建订单响应状态码: {response.status_code}")

        if response.status_code == 200:
            response_data = response.json()
            if response_data.get("code") == 0:
                log_message("✅ 订单创建成功")
                return True
            log_message(f"❌ 订单创建失败: {response_data.get('msg', '未知错误')}")
        else:
            log_message(f"❌ 订单创建请求失败: HTTP {response.status_code}")
    except Exception as e:
        log_message(f"❌ 订单创建异常: {str(e)}")

    return False

# 获取充值记录
def get_recharge_record(token: str):
    headers = {"Authorization": token, "Content-Type": "application/json"}
    url = "https://sitlotteryapi.22889.club/api/webapi/GetRechargeRecord"

    random_str = generate_random_32()
    timestamp = int(time.time())

    post_data = {
        "pageNo": 1,
        "pageSize": 10,
        "startDate": "",
        "endDate": "",
        "state": -1,
        "payId": -1,
        "payTypeId": -1,
        "language": 0,
        "random": random_str,
        "timestamp": timestamp,
        "signature": "",
    }

    post_data["signature"] = calculate_signature(post_data)

    try:
        response = requests.post(url, headers=headers, data=json.dumps(post_data), timeout=10)
        log_message(f"获取记录响应状态码: {response.status_code}")

        if response.status_code == 200:
            response_data = response.json()
            if response_data.get("code") == 0:
                records = response_data.get("data", {}).get("list", [])
                for record in records:
                    if record.get("state") in [0, 1]:
                        recharge_number = record.get("rechargeNumber")
                        price = record.get("price")
                        if recharge_number and price:
                            log_message(f"✅ 获取到充值记录: 单号={recharge_number}, 金额={price}")
                            return recharge_number, price
                log_message("❌ 未找到待处理的充值订单")
            else:
                log_message(f"❌ 获取记录失败: {response_data.get('msg', '未知错误')}")
        else:
            log_message(f"❌ 获取记录请求失败: HTTP {response.status_code}")
    except Exception as e:
        log_message(f"❌ 获取记录异常: {str(e)}")

    return None, None

# 提取工单入口中的 datablock
def get_self_customer_service_link(token: str):
    headers = {"Authorization": token, "Content-Type": "application/json"}
    url = "https://sitlotteryapi.22889.club/api/webapi/GetSelfCustomerServiceLink"

    random_str = generate_random_32()
    timestamp = int(time.time())

    post_data = {
        "language": 5,
        "random": random_str,
        "timestamp": timestamp,
        "webSite": "https%3A%2F%2Fsitweb.22889.club",
        "signature": "",
    }

    post_data["signature"] = calculate_signature(post_data)

    try:
        response = requests.post(url, headers=headers, data=json.dumps(post_data), timeout=10)
        log_message(f"工单入口响应状态码: {response.status_code}")

        if response.status_code == 200:
            response_data = response.json()
            if response_data.get("code") == 0:
                match = re.search(r"datablock=([^&\"]+)", response_data.get("data", ""))
                if match:
                    datablock = match.group(1)
                    log_message(f"✅ 提取到 datablock: {datablock}")
                    return datablock
                log_message("❌ 未找到 datablock 参数")
            else:
                log_message(f"❌ 工单入口失败: {response_data.get('msg', '未知错误')}")
        else:
            log_message(f"❌ 工单入口请求失败: HTTP {response.status_code}")
    except Exception as e:
        log_message(f"❌ 工单入口异常: {str(e)}")

    return None

# 提交工单
def submit_work_order(datablock, recharge_number, price, token):
    headers = {"Authorization": token, "Content-Type": "application/json"}
    url = "https://sit-workorderh5.mggametransit.com/api/WorkOrder/Submit"

    utr = generate_utr()
    random_str = generate_random_12()
    timestamp = int(time.time())

    post_data = {
        "dataBlock": datablock,
        "formFields": [
            {"typeCode": "DepositOrderNo", "fieldId": 798, "fieldValue": recharge_number},
            {"typeCode": "OrderAmount", "fieldId": 795, "fieldValue": str(price)},
            {"typeCode": "UTR", "fieldId": 796, "fieldValue": utr},
            {
                "typeCode": "ImageUpload",
                "fieldId": 4052,
                "fieldValue": "https://worktracking-imgs.oss-ap-southeast-1.aliyuncs.com/Dev/User/1751947531676_726.png?a50f4bfbfbedab6418b9bf5de536afc378311e67.png",
                "fieldName": "Dev/User/1751265594804_6486.png?AR008_video wingo 2.png"
            }
        ],
        "payTypeId": 10161,
        "code": 10161,
        "payName": "S7DaysPayINR-UPI",
        "formId": 86,
        "language": 0,
        "random": random_str,
        "signature": "",
        "tenantId": 1062,
        "timestamp": timestamp,
        "workOrderTypeId": 6,
    }

    post_data["signature"] = calculate_signature(post_data)
    log_message(f"提交工单参数: random={random_str}, timestamp={timestamp}, signature={post_data['signature']}")

    try:
        response = requests.post(url, headers=headers, data=json.dumps(post_data), timeout=15)
        log_message(f"提交工单响应状态码: {response.status_code}")
        log_message(f"工单提交响应内容: {json.dumps(response.json(), indent=2)}")

        if response.status_code == 200 and response.json().get("code") == 0:
            log_message("✅ 工单提交成功！")
            return True
        log_message(f"❌ 工单提交失败: {response.json().get('msg', '未知错误')}")
    except Exception as e:
        log_message(f"❌ 工单提交异常: {str(e)}")

    return False

# 处理单个 token
def process_single_token(token, index, total):
    log_message(f"\n{'=' * 50}")
    log_message(f"开始处理 token [{index}/{total}]: {token[:15]}...")

    if not create_recharge_order(token):
        log_message("❌ 订单创建失败，跳过后续步骤")
        return False

    # 重试获取充值记录
    wait_times = [2, 3, 5, 8, 10]
    for attempt in range(len(wait_times)):
        time.sleep(wait_times[attempt])
        log_message(f"尝试获取充值记录 [{attempt + 1}/{len(wait_times)}]")
        recharge_number, price = get_recharge_record(token)
        if recharge_number and price:
            break
    else:
        log_message("❌ 无法获取充值记录，跳过后续步骤")
        return False

    datablock = get_self_customer_service_link(token)
    if not datablock:
        log_message("❌ 未提取到 datablock，无法继续提交工单")
        return False

    return submit_work_order(datablock, recharge_number, price, token)

# 批量执行处理流程
def run_batch_process(tokens, run_count=None):
    run_count = run_count or len(tokens)
    run_count = min(run_count, len(tokens))
    success_count = 0
    for i in range(run_count):
        if process_single_token(tokens[i], i + 1, run_count):
            success_count += 1

    print("===============================================================\n")
    # 统计提交总数
    log_message(f"提交工单统计 - 成功: {success_count}, 失败: {run_count - success_count}, 总计: {run_count}")

    return success_count



# 主程序入口
if __name__ == "__main__":
    token_file_path = "saveTokens.csv"
    log_message(f"开始执行提交流程, 读取文件: {token_file_path}")

    tokens = read_tokens(token_file_path)
    if not tokens:
        log_message("❌ 未找到有效 token，请检查 CSV 文件")
        sys.exit(1)

    run_count = min(5, len(tokens))  # 可调整并发处理数量
    success_count = run_batch_process(tokens, run_count)

