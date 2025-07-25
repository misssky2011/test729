import asyncio
import random
import aiohttp
import csv
import logging
from collections import defaultdict
from common import getRandomStr
from lotteryFrameFunc import get_time, getSignature, md5_Info
import sys

# 在Windows系统上设置事件循环策略
if sys.platform == 'win32':
    asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

success_count = defaultdict(int)
failure_count = defaultdict(int)
failure_reason_count = defaultdict(int)  # 新增失败原因统计字典

# 用于跟踪已经投注过的组合
bet_combinations = {}


async def GetLoginToken(session, url, username, password, VerifyPwd):
    body = {
        "username": username,
        "pwd": password,
        "verifyPwd": "",
        "signature": "",
        "timestamp": get_time(),
        "random": getRandomStr(32),
    }
    body["verifyPwd"] = md5_Info(body["username"] + body["pwd"] + body["random"] + str(body["timestamp"]) + VerifyPwd,
                                 uppercase=False)
    body["signature"] = getSignature(body)

    async with session.post(url + "GetLoginToken", json=body) as resp:
        if resp.status == 200:
            data = await resp.json()
            token = data.get("data", {}).get("token")
            if token and data.get("msg") == "Succeed":
                logging.info(f"用户 {username} 登录成功")
                success_count['login'] += 1
                return token
            else:
                reason = data.get('msg', '未知错误')
                logging.error(f"用户 {username} 登录失败: {reason}")
                failure_count['login'] += 1
                failure_reason_count[f"登录失败: {reason}"] += 1
        else:
            reason = f"HTTP状态码: {resp.status}"
            logging.error(f"用户 {username} 登录请求失败，状态码: {resp.status}")
            failure_count['login'] += 1
            failure_reason_count[f"登录请求失败: {reason}"] += 1
        return None


async def GetAllowGameIssue(session, url, token, typeId, VerifyPwd):
    body = {
        "typeId": typeId,
        "language": 4,
        "random": getRandomStr(32),
        "signature": "",
        "timestamp": get_time(),
        "verifyPwd": ""
    }
    body["verifyPwd"] = md5_Info(str(body["typeId"]) + body["random"] + str(body["timestamp"]) + VerifyPwd,
                                 uppercase=False)
    body["signature"] = getSignature(body)
    headers = {
        "content-type": "application/json;charset=UTF-8",
        "Accept": "*/*",
        "authorization": "Bearer " + token,
    }
    async with session.post(url + "GetAllowGameIssue", json=body, headers=headers) as resp:
        if resp.status == 200:
            data = await resp.json()
            if not data or not data.get("data"):
                logging.error("获取期号失败: 返回数据为空")
                failure_count['get_issue'] += 1
                failure_reason_count["获取期号失败: 返回数据为空"] += 1
                return None
            if data["code"] == 0 and data["msg"] == "Succeed":
                issuenumber = data["data"].get("issueNumber")
                if issuenumber:
                    logging.info(f"获取期号成功(typeId={typeId}): {issuenumber}")
                    success_count['get_issue'] += 1
                    return issuenumber
                else:
                    logging.error("获取期号失败: 期号为空")
                    failure_count['get_issue'] += 1
                    failure_reason_count[f"获取期号失败: 期号为空"] += 1
            else:
                reason = data.get('msg', '未知错误')
                logging.error(f"获取期号失败: {reason}")
                failure_count['get_issue'] += 1
                failure_reason_count[f"获取期号失败: {reason}"] += 1
        else:
            reason = f"HTTP状态码: {resp.status}"
            logging.error(f"获取期号请求失败，状态码: {resp.status}")
            failure_count['get_issue'] += 1
            failure_reason_count[f"获取期号请求失败: {reason}"] += 1
        return None


async def GetAllowEmerdList(session, url, token, typeId, VerifyPwd):
    body = {
        "typeId": typeId,
        "language": 4,
        "random": getRandomStr(32),
        "signature": "",
        "timestamp": get_time(),
        "verifyPwd": ""
    }
    body["verifyPwd"] = md5_Info(str(body["typeId"]) + body["random"] + str(body["timestamp"]) + VerifyPwd,
                                 uppercase=False)
    body["signature"] = getSignature(body)
    headers = {
        "content-type": "application/json;charset=UTF-8",
        "Accept": "*/*",
        "authorization": "Bearer " + token,
    }
    async with session.post(url + "GetAllowEmerdList", json=body, headers=headers) as resp:
        if resp.status == 200:
            data = await resp.json()
            # 修正判断逻辑：只要code为0且msg为"Succeed"就视为成功
            if data.get("code") == 0 and data.get("msg") == "Succeed":
                data_count = len(data.get("data", []))
                logging.info(f"获取EmerdList成功，返回{data_count}条数据")
                success_count['get_emerd_list'] += 1
                return data.get("data", [])
            else:
                reason = data.get('msg', '未知错误')
                logging.error(f"获取EmerdList失败: {reason}, 请求体: {body}, 响应消息: {data}")
                failure_count['get_emerd_list'] += 1
                failure_reason_count[f"获取EmerdList失败: {reason}"] += 1
        else:
            reason = f"HTTP状态码: {resp.status}"
            logging.error(f"获取EmerdList请求失败，状态码: {resp.status}, 请求体: {body}")
            failure_count['get_emerd_list'] += 1
            failure_reason_count[f"获取EmerdList请求失败: {reason}"] += 1
        return None


async def GameBetting(session, url, token, typeId, issuenumber, gameType, selectType):
    # 生成随机金额（10-1000）
    amount = random.randint(10, 1000)
    body = {
        "language": 0,
        "timestamp": get_time(),
        "random": getRandomStr(32),
        "signature": "",
        "typeId": typeId,
        "issuenumber": issuenumber,
        "amount": amount,  # 使用随机金额
        "betCount": 2,
        "gameType": int(gameType),
        "selectType": int(selectType)
    }
    body["signature"] = getSignature(body)
    headers = {
        "content-type": "application/json;charset=UTF-8",
        "Accept": "*/*",
        "authorization": "Bearer " + token,
    }
    async with session.post(url + "GameBetting", json=body, headers=headers) as resp:
        if resp.status == 200:
            data = await resp.json()
            if data["code"] == 0 and data["msg"] == "Bet success":
                logging.info(f"WinGo投注成功，期号: {issuenumber}, 请求体: {body}")
                success_count['wingo'] += 1
            else:
                reason = data.get('msg', '未知错误')
                logging.error(f"WinGo投注失败，期号: {issuenumber}, 原因: {reason}, 请求body: {body}")
                failure_count['wingo'] += 1
                failure_reason_count[f"WinGo投注失败: {reason}"] += 1
        else:
            reason = f"HTTP状态码: {resp.status}"
            logging.error(f"WinGo投注请求失败，期号: {issuenumber}, 状态码: {resp.status}, 请求body: {body}")
            failure_count['wingo'] += 1
            failure_reason_count[f"WinGo投注请求失败: {reason}"] += 1


async def GetGame5DIssue(session, url, token, typeId):
    body = {
        "language": 0,
        "timestamp": get_time(),
        "random": getRandomStr(32),
        "signature": "",
        "typeId": typeId
    }
    body["signature"] = getSignature(body)
    async with session.post(url + "GetGame5DIssue", json=body, headers={
        "content-type": "application/json;charset=UTF-8",
        "authorization": "Bearer " + token,
    }) as resp:
        if resp.status == 200:
            data = await resp.json()
            if not data or not data.get("data"):
                logging.error("获取5D期号失败: 返回数据为空")
                failure_count['get_5d_issue'] += 1
                failure_reason_count["获取5D期号失败: 返回数据为空"] += 1
                return None
            if data["code"] == 0 and data["msg"] == "Succeed":
                issuenumber = data["data"].get("issueNumber")
                if issuenumber:
                    logging.info(f"获取5D期号成功(typeId={typeId}): {issuenumber}")
                    success_count['get_5d_issue'] += 1
                    return issuenumber
                else:
                    logging.error("获取5D期号失败: 期号为空")
                    failure_count['get_5d_issue'] += 1
                    failure_reason_count[f"获取5D期号失败: 期号为空"] += 1
            else:
                reason = data.get('msg', '未知错误')
                logging.error(f"获取5D期号失败: {reason}")
                failure_count['get_5d_issue'] += 1
                failure_reason_count[f"获取5D期号失败: {reason}"] += 1
        else:
            reason = f"HTTP状态码: {resp.status}"
            logging.error(f"获取5D期号请求失败，状态码: {resp.status}")
            failure_count['get_5d_issue'] += 1
            failure_reason_count[f"获取5D期号请求失败: {reason}"] += 1
        return None


async def GetGameK3Issue(session, url, token, typeId):
    body = {
        "language": 0,
        "timestamp": get_time(),
        "random": getRandomStr(32),
        "signature": "",
        "typeId": typeId
    }
    body["signature"] = getSignature(body)
    async with session.post(url + "GetGameK3Issue", json=body, headers={
        "content-type": "application/json;charset=UTF-8",
        "authorization": "Bearer " + token,
    }) as resp:
        if resp.status == 200:
            data = await resp.json()
            if not data or not data.get("data"):
                logging.error(f"获取K3期号失败: 返回数据为空, request body: {body}, response: {data}")
                failure_count['get_k3_issue'] += 1
                failure_reason_count["获取K3期号失败: 返回数据为空"] += 1
                return None
            if data["code"] == 0 and data["msg"] == "Succeed":
                issuenumber = data["data"].get("issueNumber")
                if issuenumber:
                    logging.info(f"获取K3期号成功(typeId={typeId}): {issuenumber}")
                    success_count['get_k3_issue'] += 1
                    return issuenumber
                else:
                    logging.error("获取K3期号失败: 期号为空")
                    failure_count['get_k3_issue'] += 1
                    failure_reason_count[f"获取K3期号失败: 期号为空"] += 1
            else:
                reason = data.get('msg', '未知错误')
                logging.error(f"获取K3期号失败: {reason}")
                failure_count['get_k3_issue'] += 1
                failure_reason_count[f"获取K3期号失败: {reason}"] += 1
        else:
            reason = f"HTTP状态码: {resp.status}"
            logging.error(f"获取K3期号请求失败，状态码: {resp.status}")
            failure_count['get_k3_issue'] += 1
            failure_reason_count[f"获取K3期号请求失败: {reason}"] += 1
        return None


async def Game5DBetting(session, url, token, issuenumber, typeId, gameType, selectType):
    # 生成随机金额（10-1000）
    amount = random.randint(10, 1000)

    body = {
        "issuenumber": issuenumber,
        "typeId": typeId,
        "amount": amount,  # 使用随机金额
        "betCount": 1,
        "gameType": gameType,
        "selectType": str(selectType),
        "language": 0,
        "random": getRandomStr(32),
        "signature": "",
        "timestamp": get_time()
    }
    body["signature"] = getSignature(body)
    async with session.post(url + "Game5DBetting", json=body, headers={
        "content-type": "application/json;charset=UTF-8",
        "authorization": "Bearer " + token,
    }) as resp:
        if resp.status == 200:
            data = await resp.json()
            if data["code"] == 0 and data["msg"] == "Bet success":
                logging.info(f"5D投注成功，期号: {issuenumber}, 请求体: {body}")
                success_count['betting_5d'] += 1
                success_count['betting'] += 1
            else:
                reason = data.get('msg', '未知错误')
                logging.error(f"5D投注失败，期号: {issuenumber}, 原因: {reason}, 请求body: {body}")
                failure_count['betting_5d'] += 1
                failure_reason_count[f"5D投注失败: {reason}"] += 1
        else:
            reason = f"HTTP状态码: {resp.status}"
            logging.error(f"5D投注请求失败，期号: {issuenumber}, 状态码: {resp.status}, 请求body: {body}")
            failure_count['betting_5d'] += 1
            failure_reason_count[f"5D投注请求失败: {reason}"] += 1


async def K3GameBetting(session, url, token, issuenumber, typeId, gameType, selectType):
    # 生成随机金额（10-1000）
    amount = random.randint(10, 1000)

    body = {
        "amount": amount,  # 使用随机金额
        "betCount": 1,
        "gameType": str(gameType),
        "selectType": str(selectType),
        "typeId": typeId,
        "issuenumber": issuenumber,
        "language": 0,
        "random": getRandomStr(32),
        "signature": "",
        "timestamp": get_time()
    }
    body["signature"] = getSignature(body)
    async with session.post(url + "K3GameBetting", json=body, headers={
        "content-type": "application/json;charset=UTF-8",
        "authorization": "Bearer " + token,
    }) as resp:
        if resp.status == 200:
            data = await resp.json()
            if data["code"] == 0 and data["msg"] == "Bet success":
                logging.info(f"K3投注成功，期号: {issuenumber}, 请求体: {body}")
                success_count['betting_k3'] += 1
                success_count['betting'] += 1
            else:
                reason = data.get('msg', '未知错误')
                logging.error(f"K3投注失败，期号: {issuenumber}, 原因: {reason}, 请求body: {body}")
                failure_count['betting_k3'] += 1
                failure_reason_count[f"K3投注失败: {reason}"] += 1
        else:
            reason = f"HTTP状态码: {resp.status}"
            logging.error(f"K3投注请求失败，期号: {issuenumber}, 状态码: {resp.status}, 请求body: {body}")
            failure_count['betting_k3'] += 1
            failure_reason_count[f"K3投注请求失败: {reason}"] += 1


async def GetTRXGameIssue(session, url, token, typeId):
    body = {
        "language": 0,
        "timestamp": get_time(),
        "random": getRandomStr(32),
        "signature": "",
        "typeId": typeId
    }
    body["signature"] = getSignature(body)
    async with session.post(url + "GetTRXGameIssue", json=body, headers={
        "content-type": "application/json;charset=UTF-8",
        "authorization": "Bearer " + token,
    }) as resp:
        if resp.status == 200:
            data = await resp.json()
            if data.get("code") == 0 and data.get("msg") == "Succeed":
                predraw = data.get("data", {}).get("predraw", {})
                issuenumber = predraw.get("issueNumber")
                if issuenumber:
                    logging.info(f"获取TRX期号成功(typeId={typeId}): {issuenumber}")
                    success_count['get_trx_issue'] += 1
                    return issuenumber
                else:
                    logging.error(f"获取TRX期号失败: 期号为空, request body: {body}, response: {data}")
                    failure_count['get_trx_issue'] += 1
                    failure_reason_count["TRX期号为空"] += 1
            else:
                reason = data.get("msg", "未知错误")
                logging.error(f"获取TRX期号失败: {reason}, response: {data}")
                failure_count['get_trx_issue'] += 1
                failure_reason_count[f"获取TRX期号失败: {reason}"] += 1
        else:
            reason = f"HTTP状态码: {resp.status}"
            logging.error(f"获取TRX期号请求失败，状态码: {resp.status}")
            failure_count['get_trx_issue'] += 1
            failure_reason_count[f"获取TRX期号请求失败: {reason}"] += 1
        return None


async def GetTRXNoaverageEmerdList(session, url, token, typeId):
    body = {
        "language": 0,
        "timestamp": get_time(),
        "random": getRandomStr(32),
        "signature": "",
        "pageSize": 20,
        "pageNo": 1,
        "typeId": typeId
    }
    body["signature"] = getSignature(body)
    async with session.post(url + "GetTRXNoaverageEmerdList", json=body, headers={
        "content-type": "application/json;charset=UTF-8",
        "authorization": "Bearer " + token,
    }) as resp:
        if resp.status == 200:
            data = await resp.json()
            if data.get("code") == 0 and data.get("msg") == "Succeed":
                logging.info(f"GetTRXNoaverageEmerdList接口返回, data是否为空: {not bool(data.get('data'))}")
                success_count['get_trx_noavg'] += 1
                return True
            else:
                reason = data.get("msg", "未知错误")
                logging.error(f"GetTRXNoaverageEmerdList获取失败: {reason}, 请求体: {body}, 响应消息: {data}")
                failure_count['get_trx_noavg'] += 1
                failure_reason_count[f"GetTRXNoaverageEmerdList失败: {reason}"] += 1
        else:
            reason = f"HTTP状态码: {resp.status}"
            logging.error(f"GetTRXNoaverageEmerdList请求失败，状态码: {resp.status}, 请求体: {body}")
            failure_count['get_trx_noavg'] += 1
            failure_reason_count[f"GetTRXNoaverageEmerdList请求失败: {reason}"] += 1
        return False


async def GameTRXBetting(session, url, token, issuenumber, typeId, gameType, selectType):
    # 生成随机金额（10-1000）
    amount = random.randint(10, 1000)

    body = {
        "language": 0,
        "timestamp": get_time(),
        "random": getRandomStr(32),
        "signature": "",
        "typeId": typeId,
        "issuenumber": issuenumber,
        "amount": amount,  # 使用随机金额
        "betCount": 2,
        "gameType": int(gameType),
        "selectType": int(selectType)
    }
    body["signature"] = getSignature(body)
    async with session.post(url + "GameTRXBetting", json=body, headers={
        "content-type": "application/json;charset=UTF-8",
        "authorization": "Bearer " + token,
    }) as resp:
        if resp.status == 200:
            data = await resp.json()
            if data.get("code") == 0 and data.get("msg") == "Bet success":
                logging.info(f"TRX投注成功，期号: {issuenumber}, 请求体: {body}")
                success_count['betting'] += 1
            else:
                reason = data.get("msg", "未知错误")
                logging.error(f"TRX投注失败，期号: {issuenumber}, 原因: {reason}, 请求body: {body}")
                failure_count['betting'] += 1
                failure_reason_count[f"TRX投注失败: {reason}"] += 1
        else:
            reason = f"HTTP状态码: {resp.status}"
            logging.error(f"TRX投注请求失败，期号: {issuenumber}, 状态码: {resp.status}, 请求body: {body}")
            failure_count['betting'] += 1
            failure_reason_count[f"TRX投注请求失败: {reason}"] += 1


async def GetNoaverageEmerdList(session, url, token, typeId):
    body = {
        "language": 0,
        "timestamp": get_time(),
        "random": getRandomStr(32),
        "signature": "",
        "pageSize": 20,
        "pageNo": 1,
        "typeId": typeId
    }
    body["signature"] = getSignature(body)
    async with session.post(url + "GetNoaverageEmerdList", json=body, headers={
        "content-type": "application/json;charset=UTF-8",
        "authorization": "Bearer " + token,
    }) as resp:
        if resp.status == 200:
            data = await resp.json()
            if data.get("code") == 0 and data.get("msg") == "Succeed":
                logging.info(f"GetNoaverageEmerdList接口返回, data是否为空: {not bool(data.get('data'))}")
                success_count['get_noavg_emerd'] += 1
                return True
            else:
                reason = data.get("msg", "未知错误")
                logging.error(f"GetNoaverageEmerdList获取失败: {reason}, 请求体: {body}, 响应消息: {data}")
                failure_count['get_noavg_emerd'] += 1
                failure_reason_count[f"GetNoaverageEmerdList失败: {reason}"] += 1
        else:
            reason = f"HTTP状态码: {resp.status}"
            logging.error(f"GetNoaverageEmerdList请求失败，状态码: {resp.status}, 请求体: {body}")
            failure_count['get_noavg_emerd'] += 1
            failure_reason_count[f"GetNoaverageEmerdList请求失败: {reason}"] += 1
        return False


async def GetK3NoaverageEmerdList(session, url, token, typeId):
    body = {
        "language": 0,
        "timestamp": get_time(),
        "random": getRandomStr(32),
        "signature": "",
        "pageSize": 20,
        "pageNo": 1,
        "typeId": typeId
    }
    body["signature"] = getSignature(body)
    async with session.post(url + "GetK3NoaverageEmerdList", json=body, headers={
        "content-type": "application/json;charset=UTF-8",
        "authorization": "Bearer " + token,
    }) as resp:
        if resp.status == 200:
            data = await resp.json()
            if data.get("code") == 0 and data.get("msg") == "Succeed":
                logging.info(f"GetK3NoaverageEmerdList接口返回, data是否为空: {not bool(data.get('data'))}")
                success_count['get_k3_noavg_emerd'] += 1
                return True
            else:
                reason = data.get("msg", "未知错误")
                logging.error(f"GetK3NoaverageEmerdList获取失败: {reason}, 请求体: {body}, 响应消息: {data}")
                failure_count['get_k3_noavg_emerd'] += 1
                failure_reason_count[f"GetK3NoaverageEmerdList失败: {reason}"] += 1
        else:
            reason = f"HTTP状态码: {resp.status}"
            logging.error(f"GetK3NoaverageEmerdList请求失败，状态码: {resp.status}, 请求体: {body}")
            failure_count['get_k3_noavg_emerd'] += 1
            failure_reason_count[f"GetK3NoaverageEmerdList请求失败: {reason}"] += 1
        return False


async def GetNoaverage5DEmerdList(session, url, token, typeId):
    body = {
        "language": 0,
        "timestamp": get_time(),
        "random": getRandomStr(32),
        "signature": "",
        "pageSize": 20,
        "pageNo": 1,
        "typeId": typeId
    }
    body["signature"] = getSignature(body)
    async with session.post(url + "GetNoaverage5DEmerdList", json=body, headers={
        "content-type": "application/json;charset=UTF-8",
        "authorization": "Bearer " + token,
    }) as resp:
        if resp.status == 200:
            data = await resp.json()
            if data.get("code") == 0 and data.get("msg") == "Succeed":
                logging.info(f"GetNoaverage5DEmerdList接口返回, data是否为空: {not bool(data.get('data'))}")
                success_count['get_5d_noavg_emerd'] += 1
                return True
            else:
                reason = data.get("msg", "未知错误")
                logging.error(f"GetNoaverage5DEmerdList获取失败: {reason}, 请求体: {body}, 响应消息: {data}")
                failure_count['get_5d_noavg_emerd'] += 1
                failure_reason_count[f"GetNoaverage5DEmerdList失败: {reason}"] += 1
        else:
            reason = f"HTTP状态码: {resp.status}"
            logging.error(f"GetNoaverage5DEmerdList请求失败，状态码: {resp.status}, 请求体: {body}")
            failure_count['get_5d_noavg_emerd'] += 1
            failure_reason_count[f"GetNoaverage5DEmerdList请求失败: {reason}"] += 1
        return False


async def GetBalance(session, url, token):
    body = {
        "language": 0,
        "timestamp": get_time(),
        "random": getRandomStr(32),
        "signature": ""
    }

    body["signature"] = getSignature(body)

    headers = {
        "content-type": "application/json;charset=UTF-8",
        "authorization": "Bearer " + token,
    }
    try:
        async with session.post(url + "GetBalance", json=body, headers=headers) as resp:
            if resp.status == 200:
                data = await resp.json()
                # 检查返回数据格式是否正确
                if data.get("code") == 0:
                    # 尝试从data中获取balance字段，如果没有则尝试获取amount字段
                    balance_data = data.get("data", {})
                    balance = balance_data.get("balance")
                    if balance is None:
                        balance = balance_data.get("amount")
                    if balance is not None:
                        logging.info(f"获取余额成功: {balance}")
                        return balance
                    else:
                        # 添加更详细的错误日志
                        logging.error(f"获取余额失败: 响应数据中未找到余额字段, 响应: {data}")
                else:
                    reason = data.get('msg', '未知错误')
                    logging.error(f"获取余额失败，错误信息: {reason}")
            else:
                logging.error(f"获取余额请求失败，状态码: {resp.status}")
    except Exception as e:
        logging.error(f"获取余额过程中发生异常: {str(e)}")
    return None


def get_game_category(typeId):
    """根据typeId返回游戏类别"""
    if typeId in [1, 2, 3, 30]:
        return 'wingo'
    elif typeId in [5, 6, 7, 8]:
        return '5d'
    elif typeId in [9, 10, 11, 12]:
        return 'k3'
    elif typeId in [13, 14, 15, 16]:
        return 'trx'
    return 'wingo'  # 默认


def generate_game_and_select_type(typeId, used_combinations):
    """生成不重复的gameType和selectType组合"""
    if typeId in [1, 2, 3, 30, 13, 14, 15, 16]:  # WinGo和TRX
        # 所有可能的组合
        all_combinations = []

        # 生成所有可能的num类型 (gameType=1, selectType=0-9)
        for num in range(10):
            all_combinations.append((1, str(num)))

        # 大小类型 (gameType=0, selectType=10-12)
        for size in range(10, 13):
            all_combinations.append((0, str(size)))

        # 奇偶类型 (gameType=2, selectType=13-14)
        for parity in range(13, 15):
            all_combinations.append((2, str(parity)))

        # 过滤掉已经使用过的组合
        available_combinations = [combo for combo in all_combinations if combo not in used_combinations]

        if not available_combinations:
            return None, None  # 所有组合都已经使用过

        # 随机选择一个未使用的组合
        gameType, selectType = random.choice(available_combinations)
        return gameType, selectType

    elif typeId in [5, 6, 7, 8]:  # 5D
        all_combinations = []

        # 对于每个位置 (gameType 1-5)
        for gameType in range(1, 6):
            # 数字0-9
            for num in range(10):
                all_combinations.append((gameType, str(num)))
            # 大小
            all_combinations.append((gameType, 'H'))
            all_combinations.append((gameType, 'L'))
            # 奇偶
            all_combinations.append((gameType, 'O'))
            all_combinations.append((gameType, 'E'))

        # 和值 (gameType 6)
        for selectType in ['H', 'L', 'O', 'E']:
            all_combinations.append((6, selectType))

        # 过滤掉已使用的组合
        available_combinations = [combo for combo in all_combinations if combo not in used_combinations]

        if not available_combinations:
            return None, None

        gameType, selectType = random.choice(available_combinations)
        return gameType, selectType

    elif typeId in [9, 10, 11, 12]:  # K3
        all_combinations = []

        # 点数和 (gameType=1)
        for sum_value in range(3, 19):
            all_combinations.append((1, str(sum_value)))

        # 大小 (gameType=2)
        all_combinations.append((2, 'H'))
        all_combinations.append((2, 'L'))

        # 奇偶 (gameType=3)
        all_combinations.append((3, 'O'))
        all_combinations.append((3, 'E'))

        # 过滤掉已使用的组合
        available_combinations = [combo for combo in all_combinations if combo not in used_combinations]

        if not available_combinations:
            return None, None

        gameType, selectType = random.choice(available_combinations)
        return gameType, selectType

    else:  # 默认情况
        if (0, '0') not in used_combinations:
            return 0, '0'
        return None, None


async def user_flow(session, url, username, password, VerifyPwd, loop):
    global bet_combinations

    # 初始化用户的投注组合跟踪
    user_key = f"{username}"
    if user_key not in bet_combinations:
        bet_combinations[user_key] = {
            'wingo': set(),  # typeId: 1, 2, 3, 30
            '5d': set(),  # typeId: 5, 6, 7, 8
            'k3': set(),  # typeId: 9, 10, 11, 12
            'trx': set()  # typeId: 13, 14, 15, 16
        }

    iteration = 0
    all_combinations_used = False

    # 修改为 while 循环，当没有可用的投注组合时停止
    while not all_combinations_used and (loop == 0 or iteration < loop):
        iteration += 1
        # 在每次循环开始时随机选择游戏类型
        typeId = random.choice([1, 2, 3, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 30])
        logging.info(f"用户 {username} 第 {iteration} 次业务链路, 随机选择 typeId: {typeId}")

        # 确定当前游戏类别
        game_category = get_game_category(typeId)

        # 在每次登录前生成不重复的gameType和selectType组合
        gameType, selectType = generate_game_and_select_type(typeId, bet_combinations[user_key][game_category])

        if gameType is None or selectType is None:
            logging.info(f"用户 {username} 已经投注了所有可能的组合，跳过 typeId: {typeId}")

            # 检查所有游戏类型是否都没有可用组合
            all_used = True
            for check_typeId in [1, 2, 3, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 30]:
                check_category = get_game_category(check_typeId)
                check_gameType, check_selectType = generate_game_and_select_type(check_typeId,
                                                                                 bet_combinations[user_key][
                                                                                     check_category])
                if check_gameType is not None:
                    all_used = False
                    break

            if all_used:
                logging.info(f"用户 {username} 已经投注了所有可能的组合，结束循环")
                all_combinations_used = True
                break

            continue

        # 记录这个组合已经被使用
        bet_combinations[user_key][game_category].add((gameType, str(selectType)))
        logging.info(f"用户 {username} 投注组合: typeId={typeId}, gameType={gameType}, selectType={selectType}")

        # 登录获取token
        token = await GetLoginToken(session, url, username, password, VerifyPwd)
        if not token:
            logging.error(f"用户 {username} 登录失败，跳过本次业务链路")
            continue

        # 获取初始余额
        initial_balance = await GetBalance(session, url, token)
        if initial_balance is not None:
            logging.info(f"用户 {username} 初始余额: {initial_balance}")
        else:
            logging.warning(f"用户 {username} 获取初始余额失败")

        if typeId in [5, 6, 7, 8]:
            noavg_flag = await GetNoaverage5DEmerdList(session, url, token, typeId)
            if noavg_flag:
                issuenumber = await GetGame5DIssue(session, url, token, typeId)
                if issuenumber:
                    await Game5DBetting(session, url, token, issuenumber, typeId, gameType, selectType)
                else:
                    logging.error(f"用户 {username} 第 {iteration} 次获取5D期号失败，跳过本次投注")
            else:
                logging.error(f"用户 {username} 第 {iteration} 次GetNoaverage5DEmerdList失败，跳过本次投注")
        elif typeId in [9, 10, 11, 12]:
            noavg_flag = await GetK3NoaverageEmerdList(session, url, token, typeId)
            if noavg_flag:
                issuenumber = await GetGameK3Issue(session, url, token, typeId)
                if issuenumber:
                    await K3GameBetting(session, url, token, issuenumber, typeId, gameType, selectType)
                else:
                    logging.error(f"用户 {username} 第 {iteration} 次获取K3期号失败，跳过本次投注")
            else:
                logging.error(f"用户 {username} 第 {iteration} 次GetK3NoaverageEmerdList失败，跳过本次投注")
        elif typeId in [13, 14, 15, 16]:
            issuenumber = await GetTRXGameIssue(session, url, token, typeId)
            if issuenumber:
                await GameTRXBetting(session, url, token, issuenumber, typeId, gameType, selectType)
            else:
                logging.error(f"用户 {username} 第 {iteration} 次获取TRX期号失败，跳过本次投注")
        else:
            noavg_flag = await GetNoaverageEmerdList(session, url, token, typeId)
            if noavg_flag:
                # 这里不再检查GetAllowEmerdList的返回值，因为空列表也是有效响应
                await GetAllowEmerdList(session, url, token, typeId, VerifyPwd)
                issuenumber = await GetAllowGameIssue(session, url, token, typeId, VerifyPwd)
                if issuenumber:
                    await GameBetting(session, url, token, typeId, issuenumber, gameType, selectType)
                else:
                    logging.error(f"用户 {username} 第 {iteration} 次获取期号失败，跳过本次投注")
            else:
                logging.error(f"用户 {username} 第 {iteration} 次GetNoaverageEmerdList失败，跳过本次投注")

        # 获取投注后余额
        new_balance = await GetBalance(session, url, token)
        if new_balance is not None:
            logging.info(f"用户 {username} 当前余额: {new_balance}")
            # 计算余额变化 - 只记录非零变化
            if initial_balance is not None:
                try:
                    initial_balance_float = float(initial_balance)
                    new_balance_float = float(new_balance)
                    amount_change = initial_balance_float - new_balance_float

                    # 只有当余额变化不为0时才记录变化
                    if amount_change != 0:
                        logging.info(f"用户 {username} 余额变化: -{amount_change}")
                except ValueError:
                    logging.warning(f"用户 {username} 余额转换失败: 初始={initial_balance}, 当前={new_balance}")
        else:
            logging.error("获取余额失败")

        await asyncio.sleep(3)  # 每次业务链路执行完毕后等待3秒


async def main():
    url = "https://sitlotteryapi.22889.club/api/webapi/"
    VerifyPwd = "Lottery9527"
    loop = 0  # 设置为0表示没有固定循环次数限制，会一直循环直到所有投注类型都被使用

    # 清空全局跟踪字典
    global bet_combinations
    bet_combinations = {}

    tasks = []
    async with aiohttp.ClientSession() as session:
        with open('users.csv', 'r', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            for row in reader:
                logging.info(f"开始执行用户 {row['username']} 的业务链路流程")
                tasks.append(user_flow(session, url, row['username'], row['password'], VerifyPwd, loop))
            await asyncio.gather(*tasks)

    # 统计投注情况
    logging.info("================== 投注组合统计 ==================")
    for user, categories in bet_combinations.items():
        for category, combinations in categories.items():
            logging.info(f"用户 {user} - {category} 游戏类型总共投注了 {len(combinations)} 种组合")

    # 增强统计信息输出
    logging.info("======================== 成功统计 ========================")
    logging.info(f"总投注成功次数: {success_count['betting']}")
    logging.info(f"5D投注成功次数: {success_count['betting_5d']}")
    logging.info(f"K3投注成功次数: {success_count['betting_k3']}")
    logging.info(f"WINGO投注成功次数: {success_count['wingo']}")
    logging.info(f"其他成功统计: {dict(success_count)}")

    logging.info("======================== 失败统计 ========================")
    logging.info(f"失败统计: {dict(failure_count)}")

    logging.info("=================== 失败原因详细统计 ===================")
    logging.info(f"{dict(failure_reason_count)}")

    # 显式关闭事件循环（可选）
    try:
        loop = asyncio.get_running_loop()
        loop.run_until_complete(loop.shutdown_asyncgens())
    except RuntimeError:
        pass


if __name__ == "__main__":
    # 使用asyncio.run()的安全调用方式
    try:
        asyncio.run(main())
    except RuntimeError as e:
        if "Event loop is closed" not in str(e):
            raise