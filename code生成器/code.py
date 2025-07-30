import tkinter as tk
from tkinter import ttk, messagebox
import random
import string
from tronpy import Tron
from tronpy.keys import PrivateKey

# 生成 USDT 地址和私钥
def generate_address():
    try:
        Tron()  # 初始化 Tron 网络（默认主网）
        priv_key = PrivateKey.random()
        address = priv_key.public_key.to_base58check_address()
        return address, priv_key.hex()
    except Exception as e:
        return None, str(e)

# 生成印度 IFSC 代码
def generate_ifsc_code():
    letters = ''.join(random.choices(string.ascii_uppercase, k=4))
    digits = ''.join(random.choices(string.digits, k=6))
    return f"{letters}0{digits}"

# 生成印度 UPI 账号
def generate_uip_code():
    return f"{random.randint(1000, 9999)}@{random.randint(1000000, 9999999)}"

# 生成巴西 CPF 
def generate_cpf_code():
    cpf_digits = [random.randint(0, 9) for _ in range(9)]
    dv1_sum = sum([(10 - i) * cpf_digits[i] for i in range(9)])
    dv1 = 11 - (dv1_sum % 11)
    cpf_digits.append(dv1 if dv1 < 10 else 0)
    dv2_sum = sum([(11 - i) * cpf_digits[i] for i in range(10)])
    dv2 = 11 - (dv2_sum % 11)
    cpf_digits.append(dv2 if dv2 < 10 else 0)
    return ''.join(map(str, cpf_digits))

# 生成银行卡号
def generate_bank_card():
    return ''.join(random.choices(string.digits, k=16))

# 生成中国身份证号（模拟）
def generate_id_card():
    return ''.join(random.choices(string.digits, k=17)) + random.choice(['X', 'x'] + list(string.digits))

# 生成 PIX 码（巴西支付码）
def generate_pix_code():
    return ''.join(random.choices(string.digits, k=11))

# 生成护照号
def generate_passport_number():
    prefix = random.choice(['G', 'E'])
    numbers = ''.join(random.choices(string.digits, k=8))
    return f"{prefix}{numbers}"

# 生成 UTR 转账码（印度银行系统用）
def generate_utr_code():
    first_digit = random.choice(string.digits[1:])  # 不以0开头
    remaining = ''.join(random.choices(string.digits, k=11))
    return first_digit + remaining

# 窗口居中显示
def center_window(window, width, height):
    screen_width = window.winfo_screenwidth()
    screen_height = window.winfo_screenheight()
    window.geometry(f'{width}x{height}+{int((screen_width - width) / 2)}+{int((screen_height - height) / 2)}')

# 显示结果面板内容
def show_result_window(frame: tk.Frame, address=None, private_key=None, ifsc_code=None,
                       uip_code=None, cpf_code=None, bank_card=None, id_card=None,
                       pix_code=None, utr_code=None, pp_code=None):
    for widget in frame.winfo_children():
        widget.destroy()  # 清空旧内容

    # 按钮样式
    style = ttk.Style()
    style.theme_use('clam')
    # 主按钮样式（绿色主题）
    style.configure("Main.TButton",
                    background="#4CAF50",
                    foreground="white",
                    font=("微软雅黑", 12, "bold"),
                    borderwidth=0,
                    focusthickness=3,
                    focuscolor="#4CAF50")
    style.map("Main.TButton",
              background=[('active', '#45a049'), ('pressed', '#357a38')],
              relief=[('pressed', 'sunken'), ('!pressed', 'raised')])
    # 绿色复制按钮
    style.configure("Green.TButton",
                    background="#4CAF50",
                    foreground="white",
                    font=("微软雅黑", 10),
                    padding=5,
                    borderwidth=0)
    style.map("Green.TButton",
              background=[('active', '#45a049'), ('pressed', '#357a38')])
    # 下拉框样式
    style.configure("Bold.TCombobox",
                    fieldbackground="white",
                    background="white",
                    foreground="black",
                    font=("微软雅黑", 12, "bold"))
    # 标签字体颜色统一
    LABEL_FONT = ("微软雅黑", 12, "bold")
    ENTRY_FONT = ("微软雅黑", 12)
    BG_COLOR = "#E6F4EA"

    result_box = ttk.Frame(frame, padding=15)
    result_box.pack(fill="both", expand=True, padx=10, pady=10)

    # 复制到剪贴板功能
    def copy_to_clipboard(text, label):
        frame.clipboard_clear()
        frame.clipboard_append(text)
        label.config(text="已复制!", foreground="#4CAF50")
        frame.after(1500, lambda: label.config(text=""))

    # 单条结果行
    def add_result_row(title, content):
        if not content:
            return
        row_frame = ttk.Frame(result_box)
        row_frame.pack(fill="x", pady=6)

        # 标题
        label_title = ttk.Label(row_frame, text=title + ":", width=14, anchor="e", font=("微软雅黑", 12, "bold"))
        label_title.pack(side="left", padx=(0, 10))

        # 结果只读框
        entry = tk.Entry(row_frame, font=("微软雅黑", 12), bd=0, bg="white", width=40, relief="flat",
                         highlightthickness=1, highlightbackground="#4CAF50", highlightcolor="#4CAF50")
        entry.insert(0, content)
        entry.config(state="readonly")
        entry.pack(side="left", fill="x", expand=True)

        # 复制按钮
        copy_btn = ttk.Button(row_frame, text="复制", style="Green.TButton",
                              command=lambda: copy_to_clipboard(content, status_label))
        copy_btn.pack(side="left", padx=(10, 0))

        # 状态提示
        status_label = ttk.Label(row_frame, text="")
        status_label.pack(side="left", padx=5)

    # 所有可能生成的数据项
    results = [
        ("USDT地址", address),
        ("私钥", private_key),
        ("IFSC", ifsc_code),
        ("UPI", uip_code),
        ("CPF", cpf_code),
        ("银行卡", bank_card),
        ("身份证", id_card),
        ("PIX", pix_code),
        ("UTR", utr_code),
        ("护照号", pp_code)
    ]

    for title, content in results:
        if content:
            add_result_row(title, content)

# 点击按钮生成数据
def on_generate():
    selection = combo.get()
    # 根据选项调用对应的生成函数
    generators = {
        "USDT": lambda: generate_address() + (None,) * 8,
        "IFSC": lambda: (None, None, generate_ifsc_code()) + (None,) * 7,
        "UPI": lambda: (None, None, None, generate_uip_code()) + (None,) * 6,
        "CPF": lambda: (None, None, None, None, generate_cpf_code()) + (None,) * 5,
        "银行卡": lambda: (None, None, None, None, None, generate_bank_card()) + (None,) * 4,
        "身份证": lambda: (None, None, None, None, None, None, generate_id_card()) + (None,) * 3,
        "PIX": lambda: (None, None, None, None, None, None, None, generate_pix_code()) + (None,) * 2,
        "UTR": lambda: (None, None, None, None, None, None, None, None, generate_utr_code(), None),
        "护照号": lambda: (None, None, None, None, None, None, None, None, None, generate_passport_number())
    }

    if selection not in generators:
        messagebox.showerror("错误", "请选择有效的类型")
        return

    results = generators[selection]()
    show_result_window(result_frame, *results)

# 根据选择项动态更改下拉框颜色
def update_combobox_color(event):
    color_map = {
        "USDT": "darkgreen",
        "IFSC": "blue",
        "UPI": "purple",
        "CPF": "darkorange",
        "银行卡": "darkred",
        "身份证": "black",
        "PIX": "teal",
        "UTR": "brown",
        "护照号": "darkmagenta"
    }
    selected = combo.get()
    color = color_map.get(selected, "black")
    combo.configure(foreground=color)

# 创建主窗口
root = tk.Tk()
root.title("智能代码生成器")
center_window(root, 720, 500)
root.configure(bg="#E6F4EA")

# 设置样式
style = ttk.Style()
style.theme_use('clam')

style.configure("Main.TButton",
                background="#4CAF50",
                foreground="white",
                font=("微软雅黑", 12, "bold"),
                borderwidth=2)
style.map("Main.TButton", background=[('active', '#45a049'), ('pressed', '#357a38')])

style.configure("Bold.TCombobox", font=("微软雅黑", 12, "bold"))

# 主框架
main_frame = tk.Frame(root, bg="#E6F4EA")
main_frame.pack(pady=20, padx=20, fill="both", expand=True)

# 控制区（下拉和按钮）
control_frame = tk.Frame(main_frame, bg="#E6F4EA")
control_frame.pack(pady=20)

# 标签
tk.Label(control_frame, text="选择生成类型：", font=("微软雅黑", 14, "bold"),
         bg="#E6F4EA", fg="#333333").grid(row=0, column=0, padx=(0, 15))

# 下拉框
combo = ttk.Combobox(control_frame, values=[
    "USDT", "IFSC", "UPI", "CPF", "银行卡", "身份证", "PIX", "UTR", "护照号"
], font=("微软雅黑", 12, "bold"), width=18, state="readonly", style="Bold.TCombobox", justify='center')

combo.current(0)
combo.grid(row=0, column=1, padx=(0, 20))

# 绑定颜色更新事件
combo.bind("<<ComboboxSelected>>", update_combobox_color)
update_combobox_color(None)

# 生成按钮
generate_btn = ttk.Button(control_frame, text="立即生成", style="Main.TButton", command=on_generate)
generate_btn.grid(row=0, column=2, padx=10)

# 结果框架
result_frame = tk.Frame(main_frame, bg="white", relief="flat",
                        highlightthickness=1, highlightbackground="#4CAF50")
result_frame.pack(fill="both", expand=True, pady=(10, 0))

# 启动主循环
root.mainloop()
