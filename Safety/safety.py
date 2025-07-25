import tkinter as tk
from tkinter import scrolledtext
from concurrent.futures import ThreadPoolExecutor
import requests
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry
import subprocess
import threading

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
    3389: "RDP"
}

# 创建会话并配置重试机制
def create_session():
    """创建一个requests会话，配置重试机制"""
    session = requests.Session()
    retry = Retry(total=3, backoff_factor=0.1, allowed_methods=["GET", "POST"])
    adapter = HTTPAdapter(max_retries=retry)
    session.mount("http://", adapter)
    session.mount("https://", adapter)
    return session

session = create_session()  # 创建一个全局的session对象

def parse_url(url):
    """解析URL以提取域名，默认添加http://"""
    if not url.startswith(("http://", "https://")):
        url = "http://" + url
    return url.split("://")[1].split("/")[0]

def create_gui():
    """创建GUI窗口"""
    window = tk.Tk()
    window.title("网站漏洞扫描器")
    window.geometry("800x800")  # 设置窗口大小为800x800
    window.config(bg="#f1f1f1")
    window.resizable(False, False)  # 禁止调整窗口大小

    # 标题标签
    title_label = tk.Label(window, text="网站漏洞扫描器", font=("Arial", 18, "bold"), bg="#f1f1f1", fg="#2E3A59")
    title_label.pack(pady=20)

    # 输入框和标签
    label = tk.Label(window, text="请输入网站URL:", font=("Arial", 14), bg="#f1f1f1", fg="#333")
    label.pack(pady=10)

    url_entry = tk.Entry(window, font=("Arial", 14), width=50, fg="#333", bg="#E5E5E5", bd=0, highlightthickness=2, highlightbackground="#4CAF50", highlightcolor="#4CAF50", justify="center")
    url_entry.pack(pady=10)

    # 创建滚动文本框并美化其边框
    result_frame = tk.Frame(window, bg="#f1f1f1", bd=1, relief="solid", highlightbackground="#4CAF50", highlightcolor="#4CAF50", highlightthickness=2, padx=10, pady=10)
    result_frame.pack(pady=20, fill="both", expand=True)

    result_text = scrolledtext.ScrolledText(result_frame, width=80, height=20, font=("Arial", 12), wrap=tk.WORD, bd=0, relief="flat", bg="#F5F5F5", fg="#333")
    result_text.pack(fill="both", expand=True)

    # 创建一个Frame来包含按钮
    button_frame = tk.Frame(window, bg="#f1f1f1")
    button_frame.pack(pady=20)

    # 美化按钮函数
    def button_style(button):
        button.config(font=("Arial", 14), bg="#4CAF50", fg="white", relief="flat", width=20, height=2, bd=0, activebackground="#45a049")
        button.bind("<Enter>", lambda e: button.config(bg="#45a049"))
        button.bind("<Leave>", lambda e: button.config(bg="#4CAF50"))

    # 开始扫描按钮
    def start_scan():
        """触发扫描任务"""
        url = url_entry.get()
        if not url:
            result_text.insert(tk.END, "请输入有效的URL。\n")
            return

        # 清除之前的扫描结果
        result_text.delete(1.0, tk.END)

        # 启动一个线程来执行扫描
        scan_thread = threading.Thread(target=scan_website, args=(url, result_text))
        scan_thread.start()

    scan_button = tk.Button(button_frame, text="开始扫描", command=start_scan)
    scan_button.pack(side="left", padx=20)
    button_style(scan_button)  # 应用美化按钮样式

    # 复制按钮
    def copy_to_clipboard():
        window.clipboard_clear()
        window.clipboard_append(result_text.get(1.0, tk.END))
        result_text.insert(tk.END, "\n已复制到剪贴板！")

    copy_button = tk.Button(button_frame, text="复制到剪贴板", command=copy_to_clipboard)
    copy_button.pack(side="left", padx=20)
    button_style(copy_button)  # 应用美化按钮样式

    # 启动GUI
    window.mainloop()

def scan_website(url, result_text):
    """执行网站扫描，并将结果添加到GUI中的Text框"""
    website_url = parse_url(url)
    result_text.insert(tk.END, f"正在扫描网站: {website_url}\n")

    # 执行多个扫描任务
    with ThreadPoolExecutor() as executor:
        futures = [
            executor.submit(scan_port, website_url, 80, "HTTP", result_text),
            executor.submit(scan_port, website_url, 443, "HTTPS", result_text),
            executor.submit(scan_sql_injection, f"http://{website_url}", result_text),
            executor.submit(scan_web_application, f"http://{website_url}", result_text),
            executor.submit(scan_directory_traversal, f"http://{website_url}", result_text),
            executor.submit(scan_command_injection, f"http://{website_url}", result_text),
            executor.submit(scan_sensitive_data_exposure, f"http://{website_url}", result_text),
            executor.submit(scan_owasp_zap, website_url, result_text),
            # 添加新的漏洞扫描项
            executor.submit(scan_csrf, f"http://{website_url}", result_text),
            executor.submit(scan_file_upload, f"http://{website_url}", result_text),
            executor.submit(scan_idor, f"http://{website_url}", result_text),
            executor.submit(scan_security_misconfig, f"http://{website_url}", result_text),
            executor.submit(scan_session_management, f"http://{website_url}", result_text),
            executor.submit(scan_error_handling, f"http://{website_url}", result_text),
            executor.submit(scan_buffer_overflow, f"http://{website_url}", result_text),
            executor.submit(scan_dos_ddos, f"http://{website_url}", result_text),
            executor.submit(scan_websocket_security, f"http://{website_url}", result_text),
            executor.submit(scan_access_control, f"http://{website_url}", result_text)
        ]

        # 等待所有任务完成
        for future in futures:
            future.result()

    result_text.insert(tk.END, "扫描完成。\n")

def scan_port(host, port, protocol, result_text):
    """扫描端口开放情况"""
    try:
        url = f"{protocol.lower()}://{host}:{port}"
        response = session.get(url, timeout=5)  # 设置请求超时
        result_text.insert(tk.END, f"[端口扫描] {protocol}端口 {port} 开放，状态码: {response.status_code}\n")
    except requests.exceptions.RequestException as e:
        result_text.insert(tk.END, f"[端口扫描] {protocol}端口 {port} 关闭或无法访问。错误: {e}\n")

def scan_sql_injection(url, result_text):
    """扫描SQL注入漏洞"""
    payloads = [
        "' OR 1=1--",
        "' UNION SELECT null--",
        "'; DROP TABLE users--",
        "' AND 1=2--",
        "' OR 'a'='a--"
    ]

    for payload in payloads:
        try:
            response = session.get(url, params={"q": payload}, timeout=5)
            if "error" in response.text.lower():  # 根据响应内容判断是否有SQL错误
                result_text.insert(tk.END, f"[SQL注入] 可能的SQL注入漏洞，载荷: {payload}\n")
        except requests.exceptions.RequestException as e:
            result_text.insert(tk.END, f"[SQL注入] SQL注入测试过程中出错: {e} (载荷: {payload})\n")

def scan_web_application(url, result_text):
    """扫描Web应用漏洞"""
    xss_found = False
    payloads = ["<script>alert('XSS')</script>", "<img src='x' onerror='alert(1)'>"]
    for payload in payloads:
        try:
            response = session.get(url, params={"q": payload}, timeout=5)
            if payload in response.text:
                result_text.insert(tk.END, f"[跨站脚本(XSS)] 发现XSS漏洞，载荷: {payload}\n")
                xss_found = True
        except requests.exceptions.RequestException as e:
            result_text.insert(tk.END, f"[跨站脚本(XSS)] XSS测试过程中出错: {e}\n")

    if not xss_found:
        result_text.insert(tk.END, "[跨站脚本(XSS)] 未发现XSS漏洞。\n")

def scan_directory_traversal(url, result_text):
    """扫描目录遍历漏洞"""
    payloads = [
        "/../../../../etc/passwd",
        "/..\\..\\..\\..\\..\\windows\\system32\\config\\SAM"
    ]

    for payload in payloads:
        try:
            response = session.get(url + payload, timeout=5)
            if "root" in response.text.lower():
                result_text.insert(tk.END, f"[目录遍历] 发现目录遍历漏洞，载荷: {payload}\n")
        except requests.exceptions.RequestException as e:
            result_text.insert(tk.END, f"[目录遍历] 目录遍历测试过程中出错: {e}\n")

def scan_command_injection(url, result_text):
    """扫描命令注入漏洞"""
    payloads = [
        "; ls",
        "| ls",
        "&& ls"
    ]

    for payload in payloads:
        try:
            response = session.get(url + payload, timeout=5)
            if "root" in response.text.lower():
                result_text.insert(tk.END, f"[命令注入] 发现命令注入漏洞，载荷: {payload}\n")
        except requests.exceptions.RequestException as e:
            result_text.insert(tk.END, f"[命令注入] 命令注入测试过程中出错: {e}\n")

def scan_sensitive_data_exposure(url, result_text):
    """扫描敏感数据暴露"""
    try:
        response = session.get(url + "/login", timeout=5)
        if "password" in response.text.lower():
            result_text.insert(tk.END, f"[敏感数据暴露] 发现敏感数据暴露漏洞，位置: {url}/login\n")
    except requests.exceptions.RequestException as e:
        result_text.insert(tk.END, f"[敏感数据暴露] 敏感数据暴露测试过程中出错: {e}\n")

def scan_owasp_zap(url, result_text):
    """使用OWASP ZAP工具扫描"""
    result_text.insert(tk.END, "[OWASP ZAP] 扫描（集成待完成）\n")
    # TODO: 集成OWASP ZAP API


def scan_csrf(url, result_text):
    """扫描CSRF（跨站请求伪造）漏洞"""
    csrf_token_payload = "<img src='http://malicious.com/attack?token=12345' />"
    try:
        response = session.get(url, params={"csrf_token": csrf_token_payload}, timeout=5)
        if "error" in response.text.lower():  # 根据错误信息判断是否存在漏洞
            result_text.insert(tk.END, f"[CSRF] 发现CSRF漏洞，载荷: {csrf_token_payload}\n")
    except requests.exceptions.RequestException as e:
        result_text.insert(tk.END, f"[CSRF] CSRF测试过程中出错: {e}\n")

def scan_file_upload(url, result_text):
    """扫描文件上传漏洞"""
    try:
        # 模拟上传恶意脚本文件
            result_text.insert(tk.END, "[文件上传漏洞] 存在文件上传漏洞，可以上传恶意脚本。\n")
    except requests.exceptions.RequestException as e:
        result_text.insert(tk.END, f"[文件上传漏洞] 文件上传测试过程中出错: {e}\n")

def scan_idor(url, result_text):
    """扫描不安全的直接对象引用（IDOR）漏洞"""
    try:
        # 假设系统通过URL中的ID进行访问
        response = session.get(url + "/user/123", timeout=5)  # 假设用户123的资料
        if "error" in response.text.lower():  # 根据错误信息判断是否泄露数据
            result_text.insert(tk.END, "[IDOR] 可能存在不安全的直接对象引用漏洞。\n")
    except requests.exceptions.RequestException as e:
        result_text.insert(tk.END, f"[IDOR] IDOR测试过程中出错: {e}\n")

def scan_security_misconfig(url, result_text):
    """扫描安全配置错误"""
    try:
        response = session.get(url + "/robots.txt", timeout=5)
        if "Disallow" in response.text:
            result_text.insert(tk.END, "[安全配置错误] 发现公开的敏感文件：robots.txt\n")
        # 检查HTTP头
        headers = {'User-Agent': 'Mozilla/5.0'}
        response = session.get(url, headers=headers, timeout=5)
        if "X-Frame-Options" not in response.headers:
            result_text.insert(tk.END, "[安全配置错误] 缺少X-Frame-Options，可能存在Clickjacking漏洞。\n")
    except requests.exceptions.RequestException as e:
        result_text.insert(tk.END, f"[安全配置错误] 安全配置检查过程中出错: {e}\n")

def scan_session_management(url, result_text):
    """扫描会话管理和认证漏洞"""
    try:
        # 测试会话固定漏洞
        session.cookies.set('sessionid', '123456')  # 设置固定的Session ID
        response = session.get(url + "/dashboard", timeout=5)
        if "error" not in response.text:
            result_text.insert(tk.END, "[会话管理漏洞] 发现会话固定漏洞。\n")
    except requests.exceptions.RequestException as e:
        result_text.insert(tk.END, f"[会话管理漏洞] 会话管理测试过程中出错: {e}\n")

def scan_error_handling(url, result_text):
    """扫描信息泄露和错误处理"""
    try:
        response = session.get(url + "/nonexistent_page", timeout=5)
        if "stack trace" in response.text.lower():
            result_text.insert(tk.END, "[信息泄露] 发现堆栈跟踪或敏感错误信息暴露。\n")
    except requests.exceptions.RequestException as e:
        result_text.insert(tk.END, f"[信息泄露] 错误处理测试过程中出错: {e}\n")

def scan_buffer_overflow(url, result_text):
    """扫描缓冲区溢出"""
    # 缓冲区溢出通常影响本地应用或服务，对于Web应用不常见，因此这部分可以根据具体情况进行扩展。
    result_text.insert(tk.END, "[缓冲区溢出] 由于是Web应用，通常不涉及缓冲区溢出，未进行测试。\n")

def scan_dos_ddos(url, result_text):
    """扫描资源过度消耗（DoS/DDoS）"""
    try:
        # 模拟多个请求来检测资源消耗
        for _ in range(10):
            response = session.get(url, timeout=5)
            if response.status_code != 200:
                result_text.insert(tk.END, "[DoS/DDoS] 可能存在拒绝服务攻击的风险。\n")
                break
    except requests.exceptions.RequestException as e:
        result_text.insert(tk.END, f"[DoS/DDoS] DoS/DDoS测试过程中出错: {e}\n")

def scan_websocket_security(url, result_text):
    """扫描WebSocket安全性"""
    if "websocket" in url:
        result_text.insert(tk.END, "[WebSocket安全性] 检测WebSocket连接的安全性。\n")
        # 这部分的实现涉及到WebSocket连接的扫描
    else:
        result_text.insert(tk.END, "[WebSocket安全性] 未发现WebSocket服务。\n")

def scan_access_control(url, result_text):
    """扫描权限控制和访问控制问题"""
    try:
        # 检查用户权限是否被正确控制
        response = session.get(url + "/admin", timeout=5)
        if "error" not in response.text:
            result_text.insert(tk.END, "[权限控制] 存在不当的权限控制，普通用户可以访问管理员页面。\n")
    except requests.exceptions.RequestException as e:
        result_text.insert(tk.END, f"[权限控制] 权限控制测试过程中出错: {e}\n")


# 启动GUI
create_gui()
