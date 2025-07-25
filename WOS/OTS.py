"""
后台页面接口验证
1、登录
2、工单处理查询
3、待处理工单查询
4、工单配置查询
5、首页配置查询
6、查询补单记录
7、补单统计报表
8、查询代收三方转发记录
9、代收三方转发配置
10、Telegram账号配置
11、商户管理查询
12、用户管理查询
13、权限查询
14、菜单管理
2025/06/30
Figo

"""
import logging
from datetime import datetime
import requests
import hashlib
import time
import random
import json
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry

# ========== 日志配置 ==========
def setup_logger():
    """
    设置日志格式及输出位置，日志同时输出到控制台和文件。
    日志文件名包含日期，便于归档。
    """
    log_filename = f"workorder_log_{datetime.now().strftime('%Y%m%d')}.log"
    logging.basicConfig(
        level=logging.INFO,
        format='[%(asctime)s] [%(levelname)s] %(message)s',
        handlers=[
            logging.FileHandler(log_filename, encoding='utf-8'),
            logging.StreamHandler()
        ]
    )

setup_logger()

# ========== 基础配置 ==========
USERNAME = "figo"  # 登录用户名
PASSWORD = "123456"  # 登录密码
WEB_SITE = "https://sit-workorderadmin.mggametransit.com"  # 站点基础地址

# 各接口完整URL
LOGIN_URL = f"{WEB_SITE}/api/Login/Login"  # 登录
WORK_ORDER_LIST_URL = f"{WEB_SITE}/api/WorkOrder/GetPageList"  # 工单列表
PENDING_LIST_URL = f"{WEB_SITE}/api/WorkOrder/GetPageListByPending"  # 待处理工单
TENANT_FORM_LIST_URL = f"{WEB_SITE}/api/TenantForm/GetPageList"      # 工单配置
HOME_PAGE_CONFIG_URL = f"{WEB_SITE}/api/ContentSetting/GetHomePagePageList"  # 首页配置
RECHARGE_RECORD_URL = f"{WEB_SITE}/api/StatisticalReport/GetRechargeRecordPagedList"  # 查询补单记录
RECHARGE_REPORT_URL = f"{WEB_SITE}/api/StatisticalReport/GetRechargeRecordReport"  # 补单统计报表
FORWARD_RECORD_URL = f"{WEB_SITE}/api/Forward/GetRecordList"  # 查询代收三方转发记录
FORWARD_CONFIG_URL = f"{WEB_SITE}/api/Forward/GetConfigList"  # 代收三方转发配置
TELEGRAM_CONFIG_URL = f"{WEB_SITE}/api/Telegram/GetPageList"  # Telegram账号配置
TENANT_MANAGE_URL = f"{WEB_SITE}/api/Tenant/GetPageList"      # 商户管理
USER_MANAGE_URL = f"{WEB_SITE}/api/SysUser/GetPageList"       # 用户管理
ROLE_MANAGE_URL = f"{WEB_SITE}/api/Role/GetPageList"          # 权限管理
MENU_TREE_URL = f"{WEB_SITE}/api/Menu/GetMenuTree"            # 菜单管理

# ========== 当天时间处理 ==========
now = datetime.now()
START_TS_SEC = int(datetime(now.year, now.month, now.day, 0, 0, 0).timestamp())
END_TS_SEC = int(datetime(now.year, now.month, now.day, 23, 59, 59).timestamp())
START_TS_MS = START_TS_SEC * 1000
END_TS_MS = END_TS_SEC * 1000 + 999
ISO_START_4 = datetime(now.year, now.month, now.day, 0, 0, 0).isoformat() + "+04:00"
ISO_END_4 = datetime(now.year, now.month, now.day, 23, 59, 59).isoformat() + "+04:00"
ISO_START_430 = datetime(now.year, now.month, now.day, 0, 0, 0).isoformat() + "+04:30"
ISO_END_430 = datetime(now.year, now.month, now.day, 23, 59, 59).isoformat() + "+04:30"

# ========== 工具方法 ==========
def get_random_number_12() -> str:
    """生成一个12位随机数字字符串，首位非0"""
    return str(random.randint(1, 9)) + ''.join(random.choices("0123456789", k=11))

def get_timestamp() -> int:
    """获取当前Unix时间戳（秒级）"""
    return int(time.time())

def generate_signature(random_val: str, timestamp: int, web_site=WEB_SITE) -> str:
    """
    按照接口规则生成MD5签名，签名内容是 random + timestamp + 网站地址，转大写。
    """
    source = f"{random_val}{timestamp}{web_site}"
    return hashlib.md5(source.encode()).hexdigest().upper()

def create_session(token=None):
    """
    创建requests会话，自动重试机制，设置通用请求头。
    登录后传入token，自动添加Authorization头。
    """
    session = requests.Session()
    retry = Retry(total=3, backoff_factor=0.5,
                  status_forcelist=[500, 502, 503, 504],
                  allowed_methods=frozenset(['POST']))
    adapter = HTTPAdapter(max_retries=retry)
    session.mount('https://', adapter)
    session.mount('http://', adapter)

    headers = {
        "Content-Type": "application/json",
        "User-Agent": "Mozilla/5.0",
        "Connection": "close",
        "Accept-Encoding": "gzip, deflate"
    }
    if token:
        headers["Authorization"] = f"Bearer {token}"
    session.headers.update(headers)
    return session

# ========== 登录 ==========
def login_get_token():
    """
    登录接口，返回登录成功后获得的token。
    失败时返回None。
    """
    random_val = get_random_number_12()
    timestamp = get_timestamp()
    signature = generate_signature(random_val, timestamp)

    payload = {
        "userName": USERNAME,
        "pwd": PASSWORD,
        "random": random_val,
        "signature": signature,
        "timestamp": timestamp,
        "language": 1
    }

    session = create_session()
    logging.info("发起登录请求...")
    try:
        res = session.post(LOGIN_URL, json=payload, timeout=10)
        res.raise_for_status()
        data = res.json()
        logging.info(f"登录响应: {data}")

        if data.get("code") == 0 and data["data"].get("token"):
            token = data["data"]["token"]
            logging.info(f"登录成功，Token: {token}")
            return token
        else:
            logging.error(f"登录失败: {data.get('msg')} (code={data.get('code')})")
            return None
    except requests.RequestException as e:
        logging.error(f"登录请求异常: {e}")
        return None

# ========== 通用请求函数 ==========
def post_with_token(session, url, base_payload, tag="接口请求"):
    """
    发送POST请求，自动加签名、随机数、时间戳和语言参数。
    打印请求与响应日志。
    返回响应JSON，失败返回None。
    """
    random_val = get_random_number_12()
    timestamp = get_timestamp()
    signature = generate_signature(random_val, timestamp)

    payload = base_payload.copy()
    payload.update({
        "random": random_val,
        "signature": signature,
        "timestamp": timestamp,
        "language": 1
    })

    logging.info(f"[{tag}] 请求 URL: {url}")
    logging.debug(f"[{tag}] 请求体: {json.dumps(payload, ensure_ascii=False)}")

    try:
        res = session.post(url, json=payload, timeout=10)
        res.raise_for_status()
        data = res.json()
        logging.info(f"[{tag}] 响应 code: {data.get('code')} - msg: {data.get('msg')}")
        return data
    except requests.RequestException as e:
        logging.error(f"[{tag}] 请求异常: {e}")
        return None

# ========== 各页面功能查询 ==========
def query_work_order_list(session):
    logging.info("查询工单列表...")
    payload = {
        "state": 0,
        "submissionTimeBegin": ISO_START_4,
        "submissionTimeEnd": ISO_END_4,
        "pageNo": 1,
        "pageSize": 20
    }
    data = post_with_token(session, WORK_ORDER_LIST_URL, payload, tag="工单列表")
    if data and data.get("code") == 0:
        total = data.get("data", {}).get("totalCount", 0)
        logging.info(f"工单列表查询成功，记录总数: {total}")
    else:
        logging.warning("工单列表查询失败或无数据。")

def query_pending_work_orders(session):
    logging.info("查询待处理工单...")
    payload = {
        "state": 0,
        "submissionTimeBegin": ISO_START_4,
        "submissionTimeEnd": ISO_END_4,
        "pageNo": 1,
        "pageSize": 20
    }
    data = post_with_token(session, PENDING_LIST_URL, payload, tag="待处理工单")
    if data and data.get("code") == 0:
        total = data.get("data", {}).get("totalCount", 0)
        logging.info(f"待处理工单查询成功，记录总数: {total}")
    else:
        logging.warning("待处理工单查询失败或无数据。")

def query_tenant_form_list(session):
    logging.info("查询工单配置页面...")
    payload = {
        "tenantId": None,
        "workOrderTypeId": None,
        "pageNo": 1,
        "pageSize": 20
    }
    data = post_with_token(session, TENANT_FORM_LIST_URL, payload, tag="工单配置页面")
    if data and data.get("code") == 0:
        count = len(data.get("data", {}).get("list", []))
        logging.info(f"工单配置页面查询成功，配置条数: {count}")
    else:
        logging.warning("工单配置页面查询失败或无数据。")

def query_home_page_config(session):
    logging.info("查询首页配置...")
    payload = {
        "tenantId": 0,
        "pageNo": 1,
        "pageSize": 20
    }
    data = post_with_token(session, HOME_PAGE_CONFIG_URL, payload, tag="首页配置")
    if data and data.get("code") == 0:
        count = len(data.get("data", {}).get("list", []))
        logging.info(f"首页配置查询成功，配置条数: {count}")
    else:
        logging.warning("首页配置查询失败或无数据。")

def query_recharge_record_list(session):
    logging.info("查询补单记录...")
    payload = {
        "dataTimeStart": START_TS_MS,
        "dataTimeEnd": END_TS_MS,
        "pageNo": 1,
        "pageSize": 20
    }
    data = post_with_token(session, RECHARGE_RECORD_URL, payload, tag="补单记录")
    if data and data.get("code") == 0:
        total = data.get("data", {}).get("totalCount", 0)
        logging.info(f"补单记录查询成功，记录总数: {total}")
    else:
        logging.warning("补单记录查询失败或无数据。")

def query_recharge_record_report(session):
    logging.info("查询补单统计报表...")
    payload = {
        "dataTimeStart": START_TS_MS,
        "dataTimeEnd": START_TS_MS,
        "pageNo": 1,
        "pageSize": 20
    }
    data = post_with_token(session, RECHARGE_REPORT_URL, payload, tag="补单统计报表")
    if data and data.get("code") == 0:
        logging.info("补单统计报表查询成功。")
    else:
        logging.warning("补单统计报表查询失败或无数据。")

def query_forward_record_list(session):
    logging.info("查询代收三方转发记录...")
    payload = {
        "queryTimeBegin": ISO_START_430,
        "queryTimeEnd": ISO_END_430,
        "pageNo": 1,
        "pageSize": 20
    }
    data = post_with_token(session, FORWARD_RECORD_URL, payload, tag="代收三方转发记录")
    if data and data.get("code") == 0:
        total = data.get("data", {}).get("totalCount", 0)
        logging.info(f"代收三方转发记录查询成功，记录总数: {total}")
    else:
        logging.warning("代收三方转发记录查询失败或无数据。")

def query_forward_config_list(session):
    logging.info("查询代收三方转发配置...")
    payload = {
        "pageNo": 1,
        "pageSize": 20
    }
    data = post_with_token(session, FORWARD_CONFIG_URL, payload, tag="代收三方转发配置")
    if data and data.get("code") == 0:
        count = len(data.get("data", {}).get("list", []))
        logging.info(f"代收三方转发配置查询成功，配置条数: {count}")
    else:
        logging.warning("代收三方转发配置查询失败或无数据。")

def query_telegram_config_list(session):
    logging.info("查询 Telegram 账号配置...")
    payload = {
        "pageNo": 1,
        "pageSize": 20
    }
    data = post_with_token(session, TELEGRAM_CONFIG_URL, payload, tag="Telegram账号配置")
    if data and data.get("code") == 0:
        count = len(data.get("data", {}).get("list", []))
        logging.info(f"Telegram账号配置查询成功，账号数: {count}")
    else:
        logging.warning("Telegram账号配置查询失败或无数据。")

def query_tenant_manage_list(session):
    logging.info("查询商户管理列表...")
    payload = {
        "pageNo": 1,
        "pageSize": 20
    }
    data = post_with_token(session, TENANT_MANAGE_URL, payload, tag="商户管理")
    if data and data.get("code") == 0:
        total = data.get("data", {}).get("totalCount", 0)
        logging.info(f"商户管理列表查询成功，商户总数: {total}")
    else:
        logging.warning("商户管理列表查询失败或无数据。")

def query_user_manage_list(session):
    logging.info("查询用户管理列表...")
    payload = {
        "tenantId": 0,
        "pageNo": 1,
        "pageSize": 20
    }
    data = post_with_token(session, USER_MANAGE_URL, payload, tag="用户管理")
    if data and data.get("code") == 0:
        total = data.get("data", {}).get("totalCount", 0)
        logging.info(f"用户管理列表查询成功，用户总数: {total}")
    else:
        logging.warning("用户管理列表查询失败或无数据。")

def query_role_manage_list(session):
    logging.info("查询权限管理列表...")
    payload = {
        "keyword": "",
        "pageNo": 1,
        "pageSize": 20
    }
    data = post_with_token(session, ROLE_MANAGE_URL, payload, tag="权限管理")
    if data and data.get("code") == 0:
        total = data.get("data", {}).get("totalCount", 0)
        logging.info(f"权限管理列表查询成功，角色总数: {total}")
    else:
        logging.warning("权限管理列表查询失败或无数据。")

def query_menu_tree(session):
    logging.info("查询菜单管理...")
    payload = {}  # 无需额外参数
    data = post_with_token(session, MENU_TREE_URL, payload, tag="菜单管理")
    if data and data.get("code") == 0:
        menu_count = len(data.get("data", [])) if isinstance(data.get("data"), list) else 0
        logging.info(f"菜单管理查询成功，菜单项数: {menu_count}")
    else:
        logging.warning("菜单管理查询失败或无数据。")

# ========== 主入口 ==========
if __name__ == "__main__":
    token = login_get_token()
    if token:
        session = create_session(token)
        # 依次调用所有查询接口
        query_work_order_list(session)
        query_pending_work_orders(session)
        query_tenant_form_list(session)
        query_home_page_config(session)
        query_recharge_record_list(session)
        query_recharge_record_report(session)
        query_forward_record_list(session)
        query_forward_config_list(session)
        query_telegram_config_list(session)
        query_tenant_manage_list(session)
        query_user_manage_list(session)
        query_role_manage_list(session)
        query_menu_tree(session)
    else:
        logging.error("未获取到 token，终止后续请求。")
