"""
网络安全扫描工具 - 增强版
功能：端口扫描、漏洞检测、动态分析、报告生成
优化点：
1. 安全增强：无害化payload、法律合规检查
2. 功能完善：支持多种协议扫描、漏洞分级
3. 性能优化：会话复用、并行控制
4. 稳定性提升：资源管理、异常处理
5. 报告输出：HTML格式报告
"""

import requests
import socket
import subprocess
import platform
import logging
import shutil
import concurrent.futures
from time import time
import nmap
from concurrent.futures import ThreadPoolExecutor, as_completed
import os
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from bs4 import BeautifulSoup
import re
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import WebDriverException, TimeoutException
import sys
import json
from datetime import datetime
import urllib3

# 禁用不安全的HTTPS请求警告
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

# 配置扫描的端口和协议
PORTS = {
    80: "HTTP",
    443: "HTTPS",
    21: "FTP",
    22: "SSH",
    25: "SMTP",
    53: "DNS",
    3389: "RDP"
}

# 漏洞风险等级
RISK_LEVEL = {
    "CRITICAL": 4,
    "HIGH": 3,
    "MEDIUM": 2,
    "LOW": 1,
    "INFO": 0
}

# 漏洞知识库（包含风险等级）
VULNERABILITY_DB = {
    "SQL Injection": {
        "description": "允许攻击者执行任意SQL命令，可能导致数据泄露或破坏",
        "risk": RISK_LEVEL["CRITICAL"],
        "solution": "使用参数化查询和ORM框架，避免拼接SQL语句"
    },
    "XSS": {
        "description": "跨站脚本攻击，允许攻击者在用户浏览器执行恶意代码",
        "risk": RISK_LEVEL["HIGH"],
        "solution": "对所有用户输入进行HTML编码，使用CSP策略"
    },
    "Open Redirect": {
        "description": "开放重定向漏洞，可能用于钓鱼攻击",
        "risk": RISK_LEVEL["MEDIUM"],
        "solution": "避免使用用户提供的URL进行重定向，使用白名单验证"
    },
    "Unencrypted Service": {
        "description": "未加密的服务，数据传输可能被窃听",
        "risk": RISK_LEVEL["MEDIUM"],
        "solution": "启用TLS/SSL加密"
    },
    "Outdated Software": {
        "description": "检测到过时的软件版本，可能存在已知漏洞",
        "risk": RISK_LEVEL["HIGH"],
        "solution": "立即更新到最新版本"
    }
}

# 扫描配置
SCAN_CONFIG = {
    "timeout": 5,          # 请求超时时间(秒)
    "max_workers": 8,      # 最大并发线程数
    "browser_timeout": 15  # 浏览器超时时间(秒)
}

# 日志配置
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
    handlers=[
        logging.FileHandler("security_scan.log"),
        logging.StreamHandler()
    ]
)

class ScanResult:
    """存储扫描结果"""
    def __init__(self, target):
        self.target = target
        self.start_time = datetime.now()
        self.open_ports = []
        self.vulnerabilities = []
        self.system_info = {}
        self.network_info = ""
        self.dynamic_issues = []
        self.scan_duration = 0
        
    def add_port(self, port, protocol, status):
        """添加端口扫描结果"""
        self.open_ports.append({
            "port": port,
            "protocol": protocol,
            "status": status
        })
        
    def add_vulnerability(self, name, details):
        """添加漏洞信息"""
        self.vulnerabilities.append({
            "name": name,
            "details": details,
            "risk": VULNERABILITY_DB.get(name, {}).get("risk", RISK_LEVEL["MEDIUM"])
        })
        
    def generate_report(self):
        """生成HTML报告"""
        # 生成漏洞行HTML
        vuln_rows = []
        for v in self.vulnerabilities:
            risk_level = v["risk"]
            if risk_level == RISK_LEVEL["CRITICAL"]:
                risk_class = "critical"
                risk_text = "严重"
            elif risk_level == RISK_LEVEL["HIGH"]:
                risk_class = "high"
                risk_text = "高危"
            elif risk_level == RISK_LEVEL["MEDIUM"]:
                risk_class = "medium"
                risk_text = "中危"
            else:
                risk_class = "low"
                risk_text = "低危"
                
            vuln_rows.append(
                f'<tr><td>{v["name"]}</td><td class="{risk_class}">{risk_text}</td><td>{v["details"]}</td></tr>'
            )
        
        # 生成报告HTML
        report = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <title>安全扫描报告 - {self.target}</title>
            <style>
                body {{ font-family: Arial, sans-serif; margin: 20px; }}
                .header {{ background-color: #f0f0f0; padding: 10px; border-radius: 5px; }}
                .critical {{ color: #ff0000; font-weight: bold; }}
                .high {{ color: #ff6600; }}
                .medium {{ color: #ffcc00; }}
                .low {{ color: #3366ff; }}
                table {{ border-collapse: collapse; width: 100%; margin-bottom: 20px; }}
                th, td {{ border: 1px solid #ddd; padding: 8px; text-align: left; }}
                tr:nth-child(even) {{ background-color: #f2f2f2; }}
            </style>
        </head>
        <body>
            <div class="header">
                <h1>安全扫描报告</h1>
                <p><strong>目标地址:</strong> {self.target}</p>
                <p><strong>扫描时间:</strong> {self.start_time.strftime('%Y-%m-%d %H:%M:%S')}</p>
                <p><strong>扫描时长:</strong> {self.scan_duration:.2f} 秒</p>
            </div>
            
            <h2>开放端口</h2>
            <table>
                <tr><th>端口</th><th>协议</th><th>状态</th></tr>
                {''.join(f'<tr><td>{p["port"]}</td><td>{p["protocol"]}</td><td>{p["status"]}</td></tr>' for p in self.open_ports)}
            </table>
            
            <h2>发现漏洞</h2>
            <table>
                <tr><th>漏洞类型</th><th>风险等级</th><th>详细信息</th></tr>
                {''.join(vuln_rows)}
            </table>
            
            <h2>系统信息</h2>
            <pre>{json.dumps(self.system_info, indent=2)}</pre>
            
            <h2>动态扫描结果</h2>
            <ul>
                {''.join(f'<li>{issue}</li>' for issue in self.dynamic_issues)}
            </ul>
        </body>
        </html>
        """
        
        filename = f"scan_report_{self.target.replace('.', '_')}.html"
        with open(filename, "w", encoding="utf-8") as f:
            f.write(report)
        logging.info(f"报告已生成: {filename}")
        return filename

def get_user_consent(target):
    """获取用户扫描授权确认"""
    print(f"\n{'='*50}")
    print(f"目标扫描站点: {target}")
    print(f"注意: 未经授权的扫描可能违反法律!")
    print(f"请确保您已获得对该系统扫描的书面授权")
    print(f"{'='*50}\n")
    
    consent = input("确认扫描? (输入'y'继续): ")
    if consent.lower() != 'y':
        logging.warning("用户取消扫描操作")
        sys.exit(0)

def parse_url(url):
    """解析URL以提取域名，默认添加http://"""
    if not url.startswith(("http://", "https://")):
        url = "http://" + url
    return url.split("://")[1].split("/")[0]

def check_nmap_installed():
    """检查是否安装nmap"""
    if shutil.which("nmap") is None:
        logging.error("[错误] 'nmap' 未安装或不在PATH中")
        return False
    return True

def scan_port(host, port, protocol, result):
    """扫描端口开放情况"""
    try:
        # 对HTTP/HTTPS使用requests
        if protocol in ["HTTP", "HTTPS"]:
            scheme = "https" if port == 443 else "http"
            url = f"{scheme}://{host}:{port}"
            try:
                response = requests.get(url, timeout=SCAN_CONFIG["timeout"], verify=False)
                status = f"Open ({response.status_code})"
            except requests.exceptions.SSLError:
                status = "Open (SSL Error)"
            except requests.exceptions.RequestException as e:
                status = f"Closed ({str(e)})"
        else:
            # 非HTTP协议使用socket
            with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
                sock.settimeout(SCAN_CONFIG["timeout"])
                conn_status = sock.connect_ex((host, port))
                status = "Open" if conn_status == 0 else "Closed"
        
        logging.info(f"[端口] {protocol} 端口 {port}: {status}")
        result.add_port(port, protocol, status)
        return (port, protocol, status)
    
    except Exception as e:
        logging.error(f"[错误] 端口扫描失败: {e}")
        return (port, protocol, f"错误: {str(e)}")

def scan_sql_injection(url, session, result):
    """扫描SQL注入漏洞（使用无害payload）"""
    logging.info("\n[Web] 扫描SQL注入漏洞...")
    sql_found = False
    
    # 安全无害的检测payload
    payloads = [
        "' OR 1=1--", 
        "' UNION SELECT null,null--",
        "1' AND SLEEP(5)--"
    ]
    
    for payload in payloads:
        try:
            # 使用共享会话
            response = session.get(url, params={"q": payload}, timeout=SCAN_CONFIG["timeout"])
            
            # 检测时间延迟型注入
            if "SLEEP" in payload:
                start = time()
                session.get(url, params={"q": payload}, timeout=10)
                delay = time() - start
                if delay > 4.5:  # 检测到明显延迟
                    logging.warning(f"[Web] 检测到基于时间的SQL注入: {payload}")
                    result.add_vulnerability("SQL Injection", 
                                           f"基于时间的注入检测成功, 延迟: {delay:.2f}秒")
                    sql_found = True
            
            # 检测错误型注入
            elif "error" in response.text.lower() or "syntax" in response.text.lower():
                logging.warning(f"[Web] SQL注入漏洞: {payload}")
                result.add_vulnerability("SQL Injection", 
                                       f"错误响应检测成功, payload: {payload}")
                sql_found = True
                
        except Exception as e:
            logging.error(f"[Web] SQL注入扫描异常: {e}")

    if not sql_found:
        logging.info("[Web] 未发现SQL注入漏洞")
    return sql_found

def scan_system_vulnerabilities(result):
    """扫描系统信息"""
    try:
        os_info = platform.uname()
        result.system_info = {
            "system": os_info.system,
            "node": os_info.node,
            "release": os_info.release,
            "version": os_info.version,
            "machine": os_info.machine,
            "processor": os_info.processor
        }
        logging.info(f"[系统] 操作系统信息: {os_info.system} {os_info.release}")
        
        # 检查关键系统命令
        cmd = ['netstat', '-an'] if platform.system() == "Windows" else ['netstat', '-tuln']
        try:
            netstat_result = subprocess.run(cmd, stdout=subprocess.PIPE, text=True, timeout=10)
            logging.info(f"[系统] 活动连接数: {len(netstat_result.stdout.splitlines())}")
        except (subprocess.TimeoutExpired, FileNotFoundError):
            logging.warning("[系统] 无法获取网络连接信息")
            
        return "系统扫描完成"
    except Exception as e:
        logging.error(f"[错误] 系统扫描失败: {e}")
        return f"系统扫描错误: {str(e)}"

def scan_network_devices(host, result):
    """扫描网络设备漏洞"""
    if not check_nmap_installed():
        result.add_vulnerability("Configuration Issue", "Nmap未安装")
        return "Nmap未安装"

    logging.info("\n[网络] 扫描网络设备漏洞...")
    try:
        # 使用快速扫描避免长时间等待
        nm = nmap.PortScanner()
        nm.scan(host, arguments='-T4 -F')  # 快速扫描模式
        
        for host in nm.all_hosts():
            if nm[host].state() == 'up':
                for proto in nm[host].all_protocols():
                    ports = nm[host][proto].keys()
                    for port in ports:
                        service = nm[host][proto][port]['name']
                        state = nm[host][proto][port]['state']
                        
                        # 检查已知的脆弱服务
                        if service in ["http", "ftp"] and state == "open":
                            result.add_vulnerability("Unencrypted Service", 
                                                   f"端口 {port}/{proto} 运行未加密的 {service} 服务")
        
        logging.info(f"[网络] 发现 {len(nm.all_hosts())} 台活跃设备")
        return "网络扫描完成"
    except Exception as e:
        logging.error(f"[错误] Nmap扫描失败: {e}")
        return f"网络扫描错误: {str(e)}"

def scan_web_application(url, session, result):
    """扫描Web应用漏洞 (XSS, 开放重定向)"""
    # XSS扫描
    logging.info("\n[Web] 扫描XSS漏洞...")
    xss_found = False
    payloads = [
        "<script>console.log('XSS')</script>", 
        "<img src='invalid' onerror='console.error(1)'>",
        "\"><script>alert(1)</script>"
    ]
    
    for payload in payloads:
        try:
            response = session.get(url, params={"q": payload}, timeout=SCAN_CONFIG["timeout"])
            
            # 改进的检测逻辑
            if payload in response.text:
                # 避免误报
                if not any(ignore in response.text for ignore in ["sanitized", "filtered"]):
                    logging.warning(f"[Web] XSS漏洞: {payload}")
                    result.add_vulnerability("XSS", f"反射型XSS检测成功, payload: {payload}")
                    xss_found = True
        except Exception as e:
            logging.error(f"[Web] XSS扫描异常: {e}")
    
    # 开放重定向扫描
    logging.info("\n[Web] 检查开放重定向漏洞...")
    redirect_payloads = [
        "http://malicious.example.com",
        "https://phishing-site.com"
    ]
    
    for payload in redirect_payloads:
        try:
            response = session.get(f"{url}?redirect={payload}", allow_redirects=False)
            
            # 检查重定向响应
            if response.status_code in [301, 302, 307, 308]:
                location = response.headers.get('Location', '')
                if payload in location:
                    logging.warning(f"[Web] 开放重定向漏洞: {payload}")
                    result.add_vulnerability("Open Redirect", 
                                           f"重定向到外部域名: {location}")
        except Exception as e:
            logging.error(f"[Web] 重定向检查异常: {e}")
    
    if not xss_found:
        logging.info("[Web] 未发现XSS漏洞")
    return xss_found

def check_driver_installation():
    """检查浏览器驱动是否安装"""
    drivers = ["chromedriver", "geckodriver"]
    for driver in drivers:
        if shutil.which(driver) is None:
            logging.warning(f"[警告] {driver} 未找到，动态扫描不可用")
            return False
    return True

def dynamic_scan(url, result):
    """使用Selenium动态扫描Web页面"""
    if not check_driver_installation():
        result.add_vulnerability("Configuration Issue", "浏览器驱动未安装")
        return
    
    logging.info("\n[动态] 开始动态扫描...")
    
    # 浏览器配置
    chrome_options = Options()
    chrome_options.add_argument("--headless")
    chrome_options.add_argument("--disable-gpu")
    chrome_options.add_argument("--no-sandbox")
    chrome_options.add_argument("--disable-dev-shm-usage")
    
    driver = None
    try:
        driver = webdriver.Chrome(
            service=Service(shutil.which("chromedriver")), 
            options=chrome_options
        )
        driver.set_page_load_timeout(SCAN_CONFIG["browser_timeout"])
        
        logging.info(f"[动态] 访问URL: {url}")
        driver.get(url)
        
        # 捕获浏览器控制台日志
        logs = driver.get_log('browser')
        for log in logs:
            if log['level'] == 'SEVERE':
                result.dynamic_issues.append(f"浏览器错误: {log['message']}")
                logging.error(f"[动态] 浏览器错误: {log['message']}")
        
        # 检查HTTPS证书错误
        if "Your connection is not private" in driver.page_source:
            result.add_vulnerability("SSL/TLS Issue", "证书错误或不受信任")
        
        # 分析页面内容
        soup = BeautifulSoup(driver.page_source, "html.parser")
        
        # 检查过时的JS库
        jquery_version = None
        for script in soup.find_all("script", src=True):
            src = script["src"]
            if "jquery" in src:
                result.dynamic_issues.append(f"检测到jQuery库: {src}")
                # 提取版本号
                match = re.search(r'jquery-(\d+\.\d+\.\d+)', src)
                if match:
                    jquery_version = match.group(1)
                    if jquery_version < "3.0.0":
                        result.add_vulnerability("Outdated Software", 
                                               f"使用过时的jQuery版本: {jquery_version}")
        
        # 模拟表单提交
        forms = soup.find_all("form")
        for form in forms:
            form_action = form.get('action', '')
            logging.info(f"[动态] 发现表单: {form_action}")
            
            try:
                # 查找表单元素
                form_element = driver.find_element(By.XPATH, f"//form[@action='{form_action}']")
                inputs = form.find_all("input")
                
                if inputs:
                    # 填写第一个输入字段
                    first_input = inputs[0]
                    input_name = first_input.get('name', '')
                    if input_name:
                        input_element = form_element.find_element(By.NAME, input_name)
                        input_element.send_keys("test")
                        input_element.send_keys(Keys.RETURN)
                        
                        # 等待页面更新
                        WebDriverWait(driver, 5).until(
                            EC.staleness_of(input_element)
                        )
                        logging.info(f"[动态] 表单提交成功: {form_action}")
            except (TimeoutException, WebDriverException) as e:
                logging.warning(f"[动态] 表单提交失败: {str(e)}")
        
        # 检测不安全的内容加载
        iframes = driver.find_elements(By.TAG_NAME, "iframe")
        for iframe in iframes:
            src = iframe.get_attribute("src") or ""
            if src.startswith("http:") and url.startswith("https:"):
                result.add_vulnerability("Mixed Content", 
                                       f"HTTP内容加载到HTTPS页面: {src}")
    
    except WebDriverException as e:
        logging.error(f"[动态] 浏览器错误: {str(e)}")
        result.dynamic_issues.append(f"浏览器异常: {str(e)}")
    except Exception as e:
        logging.error(f"[动态] 未知错误: {str(e)}")
    finally:
        if driver:
            driver.quit()
    
    logging.info("[动态] 动态扫描完成")

def main():
    """主函数"""
    # 用户输入和目标解析
    input_url = input("请输入网站URL (例如: example.com): ")
    website_url = parse_url(input_url)
    
    # 法律合规确认
    get_user_consent(website_url)
    
    # 初始化扫描结果
    scan_result = ScanResult(website_url)
    logging.info(f"\n扫描目标: {website_url}\n")
    
    # 创建共享会话
    session = requests.Session()
    session.headers.update({
        "User-Agent": "SecurityScanner/1.0",
        "Accept-Language": "en-US,en;q=0.9"
    })
    
    start_time = time()
    
    try:
        # 使用线程池并行执行扫描任务
        with ThreadPoolExecutor(max_workers=SCAN_CONFIG["max_workers"]) as executor:
            futures = []
            
            # 端口扫描
            for port, protocol in PORTS.items():
                future = executor.submit(scan_port, website_url, port, protocol, scan_result)
                futures.append(future)
            
            # 系统扫描
            future = executor.submit(scan_system_vulnerabilities, scan_result)
            futures.append(future)
            
            # 网络扫描
            future = executor.submit(scan_network_devices, website_url, scan_result)
            futures.append(future)
            
            # Web应用扫描
            web_url = f"http://{website_url}"
            future = executor.submit(scan_web_application, web_url, session, scan_result)
            futures.append(future)
            
            future = executor.submit(scan_sql_injection, web_url, session, scan_result)
            futures.append(future)
            
            # 动态扫描（单独执行，因为需要浏览器）
            future = executor.submit(dynamic_scan, web_url, scan_result)
            futures.append(future)
            
            # 等待任务完成
            for future in as_completed(futures):
                try:
                    future.result(timeout=120)  # 每个任务最多2分钟
                except concurrent.futures.TimeoutError:
                    logging.warning("任务超时被终止")
                except Exception as e:
                    logging.error(f"任务执行出错: {str(e)}")
    
    except KeyboardInterrupt:
        logging.warning("用户中断扫描")
    finally:
        # 清理资源
        session.close()
        scan_result.scan_duration = time() - start_time
        logging.info(f"扫描完成，耗时: {scan_result.scan_duration:.2f} 秒")
        
        # 生成报告
        report_file = scan_result.generate_report()
        logging.info(f"请查看完整报告: {report_file}")

if __name__ == "__main__":
    main()