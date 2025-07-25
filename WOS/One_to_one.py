"""
一对一客服提交流程
更新日期: 2025/07/09
作者: Figo
"""

import requests
import time
import hashlib
import uuid
import random
import re
import csv
from typing import List, Union

# ==== 配置 ====

# 保存 Token 的文件路径（csv，每行一个 token）
token_file_path = "D:/figo/工具/pycharm/PycharmProjects/WOS/saveTokens.csv"

# ==== 工具函数 ====

def get_timestamp() -> int:
    """获取当前10位秒级时间戳"""
    return int(time.time())

def get_random_string_32() -> str:
    """生成32位 UUID 随机字符串（去掉横杠）"""
    return uuid.uuid4().hex

def get_random_number_12() -> str:
    """生成12位纯数字字符串，首位非0（用于手机号等）"""
    first = str(random.randint(1, 9))
    rest = ''.join(str(random.randint(0, 9)) for _ in range(11))
    return first + rest

def generate_signature(random_value: str, timestamp: int, web_site: str = "https%3A%2F%2Fsitweb.22889.club") -> str:
    """
    按照平台规则拼接字符串并生成签名（MD5大写）
    签名规则： MD5("5" + random + timestamp + webSite)
    """
    source = f"5{random_value}{timestamp}{web_site}"
    return hashlib.md5(source.encode()).hexdigest().upper()

def read_tokens(file_path: str) -> List[str]:
    """
    从 CSV 文件中读取 token 列表
    每行一个 token
    """
    tokens = []
    try:
        with open(file_path, "r", encoding="utf-8") as file:
            reader = csv.reader(file)
            for row in reader:
                if row:
                    tokens.append(row[0])
    except Exception as e:
        print(f"❌ 读取 Token 文件失败: {e}")
    return tokens

# ==== 请求相关 ====

def get_data_block(token: str) -> Union[str, None]:
    """
    使用 token 请求客服链接，提取 URL 中的 datablock 参数
    """
    url = "https://sitlotteryapi.22889.club/api/webapi/GetSelfCustomerServiceLink"
    timestamp = get_timestamp()
    random_str = get_random_string_32()
    signature = generate_signature(random_str, timestamp)

    headers = {
        "Authorization": token,
        "Content-Type": "application/json"
    }

    payload = {
        "language": 5,
        "random": random_str,
        "signature": signature,
        "timestamp": timestamp,
        "webSite": "https%3A%2F%2Fsitweb.22889.club"
    }

    try:
        response = requests.post(url, json=payload, headers=headers, timeout=10)
        res_text = response.text

        # 正则提取 datablock=xxx
        match = re.search(r'datablock=([^&"]+)', res_text)
        if match:
            data_block = match.group(1)
            print("✅ 成功提取 dataBlock:", data_block)
            return data_block
        else:
            print("❌ 未提取到 dataBlock，响应内容：", res_text)
    except Exception as e:
        print("❌ 获取 dataBlock 异常：", str(e))
    return None

def submit_work_order(data_block: str, index: int) -> bool:
    """
    使用 dataBlock 提交一个工单
    返回是否成功提交
    """
    url = "https://sit-workorderh5.mggametransit.com/api/WorkOrder/Submit"
    timestamp = get_timestamp()
    random_num = get_random_number_12()
    signature = generate_signature(random_num, timestamp)

    headers = {
        "Content-Type": "application/json"
    }

    # 构造工单请求体
    payload = {
        "dataBlock": data_block,
        "formId": 971,
        "workOrderTypeId": 16,
        "formFields": [
            {
                "typeCode": "LongText",
                "fieldId": 4164,
                "fieldValue": f"自动问题描述内容 {index}"
            },
            {
                "typeCode": "UserName",
                "fieldId": 4136,
                "fieldValue": f"auto_user_{index}"
            },
            {
                "typeCode": "TextContent",
                "fieldId": 4137,
                "fieldValue": f"文本内容测试_{index}"
            },
            {
                "typeCode": "ImageUpload",
                "fieldId": 4152,
                "fieldValue": "https://worktracking-imgs.oss-ap-southeast-1.aliyuncs.com/Dev/User/1752232976359_7695.png?white-flower-clipart-1.png",
                "fieldName": "Dev/User/1752232976359_7695.png?white-flower-clipart-1.png"
            }
        ],
        "language": "en",
        "random": random_num,
        "tenantId": 1062,
        "signature": signature,
        "timestamp": str(timestamp)
    }

    try:
        response = requests.post(url, json=payload, headers=headers, timeout=10)
        res_text = response.text
        print(f"📨 工单提交第 {index} 次，响应：{response.status_code}, {res_text}")

        if '"code":0' in res_text:
            return True  # 提交成功
        if "请勿重复提交" in res_text or "已经提交" in res_text:
            print(f"⚠️ 用户 {index} 已提交过工单，跳过")
            return True  # 已提交视为成功
        return False  # 提交失败
    except Exception as e:
        print(f"❌ 工单提交异常（第 {index} 次）：", str(e))
        return False

# ==== 主流程 ====

def batch_submit_work_orders(max_count: int = 5):
    """
    批量提交工单入口
    会尝试从 token 文件读取并提交 max_count 条数据
    """
    tokens = read_tokens(token_file_path)
    total = min(max_count, len(tokens))
    success = 0

    if not tokens:
        print("❌ Token 文件中没有可用数据，终止执行")
        return

    for i in range(total):
        token = tokens[i]
        print(f"\n🚀 开始第 {i+1}/{total} 次工单提交，使用 Token: {token[:20]}...")

        data_block = get_data_block(token)
        if data_block:
            result = submit_work_order(data_block, i + 1)
            if result:
                success += 1
                continue  # 提交成功或重复，不等待
        time.sleep(random.uniform(1.5, 3))  # 提交失败则等待

    # 提交统计
    print(f"\n📊 工单提交完成：总尝试 {total}，成功 {success}，失败 {total - success}")

# ==== 执行入口 ====

if __name__ == "__main__":
    batch_submit_work_orders(max_count=10)
