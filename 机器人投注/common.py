# -*- coding: utf-8 -*-
# -------------------------------
# @Project：lotteryWeb
# -------------------------------
# @file：common
# @date：2024/6/19 下午5:41
# @Author：Micheal
# @Email：Micheal190215@gmail.com
# @Case Description:
# -------------------------------
import functools
import base64
import hashlib
import random
import subprocess
import time
from datetime import datetime, timezone
# import pyotp
import pytz
# from Crypto.Cipher import AES
# from numpy import pad


def capture_screenshot_on_error(func):
    """
    Capture screenshot on error
    :param func:
    :return:
    """

    @functools.wraps(func)
    def wrapper(device_o, *args, **kwargs):
        try:
            return func(device_o, *args, **kwargs)
        except Exception as e:
            # 出错时获取页面截图并保存到文件
            page = device_o.contexts[0].pages[0]
            screenshot_data = page.screenshot()
            with open('screenshot.png', 'wb') as f:
                f.write(screenshot_data)
            # 抛出AssertionError继续让pytest报告错误
            raise e

    return wrapper

def md5_Info(data):
    # 创建 MD5 对象
    md5 = hashlib.md5()
    # 更新 MD5 对象的内容
    md5.update(data.encode('utf-8'))
    # 获取加密后的摘要
    encrypted_data = md5.hexdigest().upper()
    return encrypted_data

def value_is_not_empty(value):
    return value not in ['', None, {}, []]


def remove_empty_values(data):
    if isinstance(data, dict):
        return {k: remove_empty_values(v) for k, v in data.items() if v}
    elif isinstance(data, list):
        return [remove_empty_values(item) for item in data if item]
    elif isinstance(data, str):
        return data.strip() or None
    else:
        return data


def get_time() -> int:
    """

    :return: 获取的时间戳
    """
    return int(time.time())


def get_time_12():
    """
    生成12位的时间戳
    :return:
    """
    return int(time.time() * 100)


def get_us_zone_time(timestamp):
    """
    获取美东格式时间：2024-08-05T00:15:44.048-04:00
    """
    # 将时间戳转换为 UTC 时间
    utc_time = datetime.fromtimestamp(timestamp, tz = timezone.utc)

    # 转换为美东时间
    eastern = pytz.timezone('US/Eastern')
    eastern_time = utc_time.astimezone(eastern)

    # 格式化时间
    formatted_time = eastern_time.strftime('%Y-%m-%dT%H:%M:%S.%f')[:-3] + eastern_time.strftime('%z')

    # 手动添加冒号到时区部分
    return f"{formatted_time[:-2]}:{formatted_time[-2:]}"


def getRandomNumber(k: int = 32, seed: int = None) -> str:
    """
    获取随机数字串，可选根据 seed 固定结果
    :param k: 生成长度
    :param seed: 随机种子，默认为 None
    :return: 指定长度的随机数字字符串
    """
    chars = '0123456789'
    rng = random.Random(seed) if seed is not None else random
    return ''.join(rng.choices(chars, k=k))


def getRandomStr(k = 24):
    """
    获取一个随机字符串
    """
    randomStr = '0123456789abcdef'
    return ''.join(random.choices(randomStr, k = k))


def getRandomNum(k = 12):
    """
    获取随机数字
    :return:
    """
    randomNum = '123456789'  # Exclude '0' from the first position
    first_digit = random.choice(randomNum)
    rest_digits = ''.join(random.choices('0123456789', k = k - 1))
    return first_digit + rest_digits

def get_uuid():
    import uuid
    return str(uuid.uuid4())

def aes_encrypt(data, key):
    if not data:
        return None

    # Ensure key length is correct (16, 24, or 32 bytes for AES)
    # key = key.encode('utf-8')
    # if len(key) not in (16, 24, 32):
    #     raise ValueError("Key length must be 16, 24, or 32 bytes")
    #
    # # Create AES cipher object
    # cipher = AES.new(key, AES.MODE_ECB)
    #
    # # Pad and encrypt the data
    # data_bytes = data.encode('utf-8')
    # padded_data = pad(data_bytes, AES.block_size)
    # encrypted_data = cipher.encrypt(padded_data)
    #
    # # Convert to base64 string
    # encrypted_base64 = base64.b64encode(encrypted_data).decode('utf-8')
    #
    # return encrypted_base64

def getIntervalNumber(lower_bound, upper_bound):
    """
    随机区间数字
    """
    # 生成一个在指定范围内的随机数
    return str(random.randint(lower_bound, upper_bound))


def choicesUser(usernameData):
    """
    随机选取username并进行构造
    :return:
    """

    prepare_time = time.strftime("%a %b %d %H:%M:%S %Y", time.localtime())
    usernameSingle = random.choice(usernameData).replace('\n', '')

    print('当前登录的username is：{} [{}]'.format(usernameSingle, prepare_time))
    return usernameSingle


def find_process_by_port(port):
    # 执行 netstat 命令，并通过管道连接到 findstr 命令
    netstat_cmd = ['netstat', '-ano']
    findstr_cmd = ['findstr', ':' + str(port)]
    netstat_process = subprocess.Popen(netstat_cmd, stdout = subprocess.PIPE)
    findstr_process = subprocess.Popen(findstr_cmd, stdin = netstat_process.stdout, stdout = subprocess.PIPE)

    # 读取 findstr 命令的输出，并解析出进程 PID
    output, _ = findstr_process.communicate()
    lines = output.decode().split('\n')
    pid_list = []
    for line in lines:
        if ':' + str(port) in line:
            parts = line.split()
            if len(parts) >= 5:
                pid_list.append(parts[-1])
    return pid_list


def kill_process_by_pid(pid):
    # 执行 taskkill 命令终止指定 PID 的进程
    taskkill_cmd = ['taskkill', '/F', '/PID', str(pid)]
    subprocess.run(taskkill_cmd)


def encode_base64_img(file_path):
    """
    将本地图片转换为base64格式的字符串
    :param file_path:
    :return:
    """
    # 读取本地的图片文件
    with open(file_path, 'rb') as f:
        image_data = f.read()

    # 将图片数据转换为 Base64 编码
    return base64.b64encode(image_data).decode('utf-8')


import requests


def GoogleVerify(secret_key):
    """

    :param secret_key:
    :return:
    """
    totp = pyotp.TOTP(secret_key)
    return totp.now()


if __name__ == '__main__':
    # Example usage
    secret_key = "GAZDAMRUGA4TCMJQHE2DAMRQGQYDQZ3INB4A"

    result = GoogleVerify(secret_key)
    print(result)
