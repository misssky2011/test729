import requests
import subprocess
import platform
import logging
import shutil
import concurrent.futures
from time import time
import nmap
from concurrent.futures import ThreadPoolExecutor
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
from selenium.webdriver.common.by import By

# 配置扫描的端口和协议
ports = {
    80: "HTTP",
    443: "HTTPS",
    21: "FTP",
    123: "NTP",
    25: "SMTP",
    110: "POP3",
    143: "IMAP",
    22: "SSH",
    23: "Telnet",
    53: "DNS",
    161: "SNMP",
    1433: "MSSQL",
    3306: "MySQL",
    5432: "PostgreSQL",
    27017: "MongoDB",
    6379: "Redis",
    3389: "RDP "
}

# 日志配置，记录INFO及以上级别的日志
logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")

# Vulnerability Analysis (for SQL injection)
vulnerability_analysis = {
    "XSS": "Cross-site scripting (XSS) vulnerabilities allow attackers to inject malicious scripts into webpages that can execute on the client's side.",
    "SQL Injection": "SQL injection vulnerabilities allow attackers to execute arbitrary SQL code on the database.",
    "Open Redirect": "Open redirect vulnerabilities allow attackers to redirect users to malicious websites.",
    "Unencrypted Traffic": "Using HTTP instead of HTTPS means data is transmitted in plaintext, which could be intercepted by attackers."
}

def parse_url(url):
    """解析URL以提取域名，默认添加http://"""
    if not url.startswith(("http://", "https://")):
        url = "http://" + url
    return url.split("://")[1].split("/")[0]

def check_nmap_installed():
    """检查是否安装nmap"""
    if shutil.which("nmap") is None:
        logging.error("[Error] 'nmap' is not installed or not in PATH.")
        return False
    return True

def scan_port(host, port, protocol):
    """扫描端口开放情况"""
    try:
        url = f"{protocol.lower()}://{host}:{port}"
        response = requests.get(url, timeout=5)
        logging.info(f"[Port] {protocol} Port {port} open: {response.status_code}")
        return (port, protocol, "Open")
    except requests.exceptions.RequestException as e:
        logging.warning(f"[Port] {protocol} Port {port} closed or unreachable. Error: {e}")
        return (port, protocol, "Closed")

def scan_sql_injection(url):
    """扫描SQL注入漏洞"""
    logging.info("\n[Web] Scanning for SQL Injection vulnerabilities...")
    sql_found = False
    payloads = ["' OR 1=1--", "' UNION SELECT null--", "'; DROP TABLE users--"]
    for payload in payloads:
        response = requests.get(url, params={"q": payload}, timeout=5)
        if "error" in response.text.lower():
            logging.warning(f"[Web] SQL Injection Vulnerability found with payload: {payload}")
            sql_found = True

    if not sql_found:
        logging.info("[Web] No SQL injection vulnerabilities found.")
    else:
        logging.info(f"[Web] SQL injection vulnerabilities found. {vulnerability_analysis['SQL Injection']}")

def scan_system_vulnerabilities():
    """扫描操作系统漏洞"""
    try:
        os_info = platform.uname()
        cmd = ['netstat', '-an'] if platform.system() == "Windows" else ['netstat', '-tuln']
        result = subprocess.run(cmd, stdout=subprocess.PIPE, text=True)
        logging.info(f"[System] Active Connections: {result.stdout[:100]}")  # Record partial result for brevity
        return "System vulnerability scan complete."
    except Exception as e:
        logging.error(f"[Error] Unable to scan system vulnerabilities: {e}")
        return "Error during system vulnerability scan."

def scan_network_devices(website_url):
    """扫描网络设备漏洞"""
    if not check_nmap_installed():
        return "Nmap is not installed."

    logging.info("\n[Network] Scanning network device vulnerabilities...")
    try:
        result = subprocess.run(['nmap', '-v', website_url], stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
        logging.info(f"[Network] Nmap output:\n{result.stdout[:300]}")  # Log a partial result for brevity
        return result.stdout
    except Exception as e:
        logging.error(f"[Error] Nmap scan failed: {e}")
        return "Error during network device scan."

def scan_web_application(url):
    """扫描Web应用漏洞 (如 XSS, SQL注入)"""
    logging.info("\n[Web] Scanning for XSS vulnerabilities...")
    xss_found = False
    payloads = ["<script>alert('XSS')</script>", "<img src='x' onerror='alert(1)'>"]
    for payload in payloads:
        response = requests.get(url, params={"q": payload}, timeout=5)
        if payload in response.text:
            logging.warning(f"[Web] XSS Vulnerability found with payload: {payload}")
            xss_found = True

    if not xss_found:
        logging.info("[Web] No XSS vulnerabilities found.")
    else:
        logging.info(f"[Web] XSS vulnerabilities found. {vulnerability_analysis['XSS']}")

def scan_ports(target):
    """使用Nmap进行全面的端口扫描"""
    if not check_nmap_installed():
        return "Nmap is not installed."

    nm = nmap.PortScanner()
    nm.scan(target, arguments='-p- -O -sV -sC')
    return nm

def check_open_redirect(url):
    """检查Open Redirect漏洞"""
    logging.info("\n[Web] Checking for Open Redirect vulnerabilities...")
    vulnerable_payloads = ["http://malicious.com", "http://evil.com"]
    for payload in vulnerable_payloads:
        response = requests.get(f"{url}?redirect={payload}")
        if "malicious" in response.text:
            logging.warning(f"Possible Open Redirect vulnerability found with payload: {payload}")
            logging.info(f"[Web] Open Redirect vulnerability detected. {vulnerability_analysis['Open Redirect']}")

def scan_multiple_sites(sites):
    """并行扫描多个站点"""
    with ThreadPoolExecutor(max_workers=10) as executor:
        results = executor.map(scan_ports, sites)
        return list(results)


def dynamic_scan(url):
    """使用Selenium动态扫描Web页面"""
    logging.info ("\n[Dynamic] Starting dynamic scan...")

    # 配置Selenium WebDriver（以Chrome为例）
    chrome_options = Options ()
    chrome_options.add_argument ("--headless")  # 无界面模式
    chrome_options.add_argument ("--disable-gpu")
    chrome_service = Service (shutil.which ("chromedriver"))

    try:
        driver = webdriver.Chrome (service=chrome_service, options=chrome_options)
        driver.get (url)
        logging.info (f"[Dynamic] Loaded URL: {url}")
        logs = driver.get_log ('browser')
        for log in logs:
            logging.error (f"[Dynamic] Browser Console Log: {log}")

        element = WebDriverWait (driver, 10).until (
            EC.presence_of_element_located ((By.NAME, "q"))
        )

        # 检查页面中的脚本和资源
        page_source = driver.page_source
        soup = BeautifulSoup (page_source, "html.parser")

        # 检查页面中加载的外部资源
        scripts = soup.find_all ("script", src=True)
        for script in scripts:
            logging.info (f"[Dynamic] External script found: {script['src']}")

        # 查找潜在的恶意资源
        for script in scripts:
            if re.search (r"(malicious|untrusted)", script["src"], re.IGNORECASE):
                logging.warning (f"[Dynamic] Potential malicious script found: {script['src']}")

        # 模拟行为（如提交表单）
        forms = soup.find_all ("form")
        for form in forms:
            logging.info (f"[Dynamic] Form found with action: {form.get ('action')}")
            inputs = form.find_all ("input")
            for input_field in inputs:
                logging.info (f"[Dynamic] Input field: {input_field.get ('name')}")

            # 示例：填写表单并提交
            if inputs:
                input_element = driver.find_element (By.NAME, inputs[0].get ("name"))
                input_element.send_keys ("test")
                input_element.send_keys (Keys.RETURN)
                logging.info (f"[Dynamic] Simulated form submission for: {form.get ('action')}")

        # 动态检查XSS
        test_payload = "<script>alert('Dynamic XSS Test')</script>"
        driver.execute_script (f"document.body.innerHTML += '{test_payload}';")
        if test_payload in driver.page_source:
            logging.warning ("[Dynamic] Potential XSS vulnerability detected.")

    except Exception as e:
        logging.error (f"[Dynamic] Error during dynamic scan: {e}")
    finally:
        driver.quit ()

    logging.info ("[Dynamic] Dynamic scan completed.")

def main():
    """主函数"""
    input_url = input("Enter the website URL (e.g., example.com): ")
    website_url = parse_url(input_url)
    logging.info(f"\nScanning website: {website_url}\n")

    # 使用线程池并行执行扫描任务
    start_time = time ()
    with ThreadPoolExecutor () as executor:
        futures = []
        for port, protocol in ports.items ():
            futures.append (executor.submit (scan_port, website_url, port, protocol))
        futures.append (executor.submit (scan_system_vulnerabilities))
        futures.append (executor.submit (scan_network_devices, website_url))
        futures.append (executor.submit (scan_web_application, f"http://{website_url}"))
        futures.append (executor.submit (check_open_redirect, f"http://{website_url}"))
        futures.append (executor.submit (scan_sql_injection, f"http://{website_url}"))

        # 动态扫描（单独执行，因为需要模拟浏览器操作）
        dynamic_scan (f"http://{website_url}")

        # 等待所有任务完成并收集结果
        for future in concurrent.futures.as_completed (futures):
            result = future.result ()
            if result:
                logging.info (result)

    logging.info (f"Scanning completed in {time () - start_time:.2f} seconds.")
    logging.info ("Detailed analysis completed. Please review the logs for further insights.")

if __name__ == "__main__":
    main()
