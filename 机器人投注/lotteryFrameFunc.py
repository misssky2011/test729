# -*- coding: utf-8 -*-
# -------------------------------
# @Project：PerformanceZone
# -------------------------------
# @file：lotteryFrameFunc 
# @date：2024/10/28 下午3:59
# @Author：Micheal
# @Email：Micheal190215@gmail.com
# @Case Description: 
# -------------------------------
# -*- coding: utf-8 -*-
# -------------------------------
# @Project：Performance-Zone
# -------------------------------
import string
import itertools
import json
import random
import subprocess
import time

def md5_Info(data, uppercase=True):
    import hashlib
    md5 = hashlib.md5()
    md5.update(data.encode('utf-8'))
    result = md5.hexdigest()
    return result.upper() if uppercase else result.lower()


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


def getSignature(Body, VerifyPwd = None):
    """
    获取签名前置算法
    """
    # 过滤字段
    filtered_obj = {}
    for key in sorted(Body.keys()):
        value = Body[key]
        if value not in [None, ""] and key not in ["timestamp", "signature", "track"] and not isinstance(value,
                                                                                                         list):
            filtered_obj[key] = value

    # 转换为 JSON 字符串
    encoder = json.dumps(filtered_obj, separators = (',', ':'))
    if VerifyPwd:
        encoder = encoder + VerifyPwd
    # print(f"加密前置数据为：{encoder}")
    return md5_Info(encoder)


def get_time() -> int:
    """

    :return: 获取的时间戳
    """
    return int(time.time())

def generate_random_email(exampleMail = 'example.com'):
    length = random.randint(2, 9)
    chars = ''.join(random.choices(string.ascii_lowercase + string.digits, k = length))
    return f'{chars}@{exampleMail}'

def generate_ifsc_code():
    letters = ''.join(random.choices(string.ascii_uppercase, k=4))
    digits = ''.join(random.choices(string.digits, k=6))
    return f"{letters}0{digits}"


def generate_cpf():
    import random

    # 生成9位随机数字
    digits = [random.randint(0, 9) for _ in range(9)]

    # 计算第一个校验位
    first_sum = sum(x * y for x, y in zip(digits, range(10, 1, -1)))
    first_check = (first_sum * 10) % 11
    if first_check == 10:
        first_check = 0
    digits.append(first_check)

    # 计算第二个校验位
    second_sum = sum(x * y for x, y in zip(digits, range(11, 1, -1)))
    second_check = (second_sum * 10) % 11
    if second_check == 10:
        second_check = 0
    digits.append(second_check)

    return ''.join(map(str, digits))

def generate_random_ip():
    import random
    return '.'.join(str(random.randint(0, 255)) for _ in range(4))

def get_timestamp_range(range_type="day"):
    import datetime
    from datetime import timedelta
    now = datetime.datetime.now()

    if range_type == "week":
        # 从当前周一至当前周日
        start = now - timedelta(days=now.weekday())
        start = start.replace(hour=0, minute=0, second=0, microsecond=0)
        end = start + timedelta(days=6, hours=23, minutes=59, seconds=59, microseconds=999999)
    elif range_type == "month":
        # 从当月1号至月末
        start = now.replace(day=1, hour=0, minute=0, second=0, microsecond=0)
        next_month = (start.replace(day=28) + timedelta(days=4)).replace(day=1)
        end = next_month - timedelta(seconds=1)
        end = end.replace(hour=23, minute=59, second=59, microsecond=999999)
    else:
        # 默认当天
        start = now.replace(hour=0, minute=0, second=0, microsecond=0)
        end = now.replace(hour=23, minute=59, second=59, microsecond=999999)

    return int(start.timestamp()), int(end.timestamp())

def getRandomNumber(k=32, onlyNum=False):
    if onlyNum:
        if k < 2:
            return '9'
        first = random.choice('123456789')
        last = random.choice('123456789')
        middle = ''.join(random.choices('0123456789', k=k-2))
        return first + middle + last
    else:
        return ''.join(random.choices('0123456789abcdefghijklmnopqrstuvwxyz', k=k))



def choicesUser(usernameData):
    """
    随机选取username并进行构造
    :return:
    """

    # TODO:需要做用户名去重
    prepare_time = time.strftime("%a %b %d %H:%M:%S %Y", time.localtime())
    usernameSingle = random.choice(usernameData).replace('\n', '')

    print('当前登录的username is：{} [{}]'.format(usernameSingle, prepare_time))
    return usernameSingle


def get_K3_2and1_get_all_valid_combinations(select_dict):
    """
    获取K3游戏中，2+1游戏玩法的所有组合类型
    :return:
    """
    combinations = [(a, b) for a, b in itertools.product(select_dict['2'], select_dict['1']) if
                    ''.join(b.split(':')) not in ''.join(a.split(':'))]
    combinations_result = [f"{a},{b}" for a, b in combinations]
    return combinations_result


def get_K3_3_not_same_combinations(select_list):
    """
    获取K3游戏中，三个不相同游戏玩法的所有组合类型
    :param select_list:
    :return:
    """
    # 生成长度为3到列表长度的所有组合
    all_combinations = []
    for i in range(3, len(select_list) + 1):
        all_combinations.extend(itertools.combinations(select_list, i))
    combinations_result = [','.join(map(str, combination)) for combination in all_combinations]
    return combinations_result


def get_K3_2_not_same_combinations(select_list):
    """
    获取K3游戏中，三各不相同游戏玩法的所有组合类型
    :param select_list:
    :return:
    """
    ABC = False
    # 如果有顺子选项，将它单独剔除
    if "|ABC|" in select_list:
        select_list.remove("|ABC|")
        ABC = True
    # 生成长度为2到列表长度的所有组合
    all_combinations = []
    all_combinations.extend(itertools.combinations(select_list, 2))
    combinations_result = [','.join(map(str, combination)) for combination in all_combinations]
    if ABC:
        combinations_result.append('|ABC|')
    return combinations_result


#
# def randomGameType(body, **kwargs):
#     """
#
#     :param kwargs:
#     :return:
#     """
#     if len(kwargs) > 0:
#         for key, value in kwargs.items():
#             body[key] = value


def preDataSet(data, apiName = '', methodTuple = ('signature'), isUsers = None, **kwargs):
    """
    :param data:    Json预配置数据
    :param apiName:
    :param methodTuple: 此参数必传，否则将默认不计算random或timestamp
    :param isUsers:是否是多用户？如果为多用户，username将被传参进来. 如果没有，username将使用默认值
    :return:
    """

    method = data['api_Template'][apiName]['method']
    url = data['api_Template'][apiName]['url']
    headers = data['headersTemplate']
    # 这里的preData指的是前置body数据
    preData = data['api_Template'][apiName]['body']
    # 这里模糊传参的意义在于，某些接口中的某些body属性需要在脚本中被临时修改
    for k, v in kwargs.items():
        preData[k] = v
    if isUsers:
        preData['username'] = isUsers

    # TODO：后续完善筛选逻辑
    # 2024年4月16日 增加登录接口login_web的参数配置筛选.这里为了防止后续版本迭代的过程中，对算法进行更新，因此使用tuple的形式传参
    # 仅在methodTuple中传入该值，才会被自动生成
    for item in methodTuple:
        if item == 'random':
            preData['random'] = getRandomNumber()
        elif item == 'timestamp':
            preData['timestamp'] = get_time()

    preData['signature'] = getSignature(preData)
    return {
        "method": method,
        "url": url,
        "headers": headers,
        "preData": preData}


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


if __name__ == '__main__':
    import json

    demo_dict = {"charlie": 3, "alpha": 1, "beta": 2}
    encoder = json.dumps(demo_dict, sort_keys=True)
    print(encoder)  # 输出 {"alpha":1,"beta":2,"charlie":3}
    print(0)
