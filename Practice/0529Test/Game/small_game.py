import randomTest
import tkinter as tk
from tkinter import ttk, font


def guess_number_game():
    def check_guess():
        try:
            user_guess = int(entry.get())
            attempts_var.set(attempts_var.get() + 1)

            # 隐藏进度条和结果标签
            progressbar.pack_forget()
            result_label.config(text="")

            # 使用 after 方法模拟加载动画
            def show_result_after_delay():
                if not root.winfo_exists():
                    return  # 如果窗口已销毁，则退出函数

                if user_guess < number_to_guess:
                    result_label.config(text="太低了！再试一次。", fg="red")
                elif user_guess > number_to_guess:
                    result_label.config(text="太高了！再试一次。", fg="red")
                else:
                    result_label.config(text=f"恭喜你，猜对了！你一共猜了 {attempts_var.get()} 次。", fg="green")
                    show_success_popup(attempts_var.get())  # 在这里显示弹窗

                if root.winfo_exists():  # 检查窗口是否存在
                    result_label.pack(pady=10)

            # 延迟显示结果
            root.after(500, show_result_after_delay)

        except ValueError:
            result_label.config(text="请输入一个有效的数字。", fg="red")

    def show_success_popup(attempts):
        if not root.winfo_exists():
            return  # 如果窗口已销毁，则退出函数

        popup = tk.Toplevel(root)
        popup.title("恭喜中奖！")
        popup.configure(bg="#ffd54f")  # 设置柔和的黄色背景颜色

        # 设置弹窗尺寸
        popup.geometry("500x300")

        # 获取屏幕的宽高
        screen_width = root.winfo_screenwidth()
        screen_height = root.winfo_screenheight()

        # 获取弹窗的宽高
        popup_width = 500
        popup_height = 300

        # 计算居中显示的位置
        x = (screen_width // 2) - (popup_width // 2)
        y = (screen_height // 2) - (popup_height // 2)

        # 设置弹窗的位置
        popup.geometry(f"{popup_width}x{popup_height}+{x}+{y}")

        # 主内容框架
        content_frame = tk.Frame(popup, bg="#ffd54f")
        content_frame.pack(expand=True, fill="both", pady=20)

        # 设置庆祝文本
        message_label = tk.Label(
            content_frame,
            text=f"恭喜你，猜对了！\n你一共猜了 {attempts} 次。",
            font=font.Font(family="Helvetica", size=20, weight="bold"),
            bg="#ffd54f",
            fg="#d32f2f",  # 红色字体，突出显示
        )
        message_label.pack(pady=20)

        # 添加庆祝图标或者表情符号
        celebration_label = tk.Label(
            content_frame,
            text="🎉🎉🎉",
            font=font.Font(family="Helvetica", size=40),
            bg="#ffd54f",
            fg="#d32f2f",
        )
        celebration_label.pack()

        # 设置模式对话框
        popup.transient(root)
        popup.grab_set()

    number_to_guess = random.randint(1, 100)

    root = tk.Tk()
    root.title("猜数字游戏")
    root.geometry("400x400")  # 调整窗口大小

    custom_font = font.Font(family="Helvetica", size=14)

    # 顶部指令标签
    instructions_label = tk.Label(
        root, text="请输入1到100之间的数字：", font=custom_font, bg="#f0f0f0", anchor="w"
    )
    instructions_label.pack(pady=20)

    # 输入框
    entry = tk.Entry(root, width=10, font=custom_font, justify="center")
    entry.pack(pady=10)

    # 提交按钮
    guess_button = tk.Button(
        root, text="提交猜测", command=check_guess, font=custom_font, bg="#d0f0ff"
    )
    guess_button.pack(pady=10)

    # 结果标签
    result_label = tk.Label(root, text="", font=custom_font, fg="black", bg="#f0f0f0")
    result_label.pack(pady=10)

    # 尝试次数显示，靠近底部
    attempts_var = tk.IntVar(value=0)
    attempts_label = tk.Label(
        root,
        textvariable=tk.StringVar(value=f"尝试次数: {attempts_var.get()}"),
        font=custom_font,
        bg="#f0f0f0",
    )
    attempts_label.pack(side="bottom", pady=20)

    # 创建进度条（用于模拟加载动画）
    progressbar_style = ttk.Style()
    progressbar_style.theme_use("default")
    progressbar_style.configure(
        "Custom.Horizontal.TProgressbar", troughcolor="#d0d0d0", background="#00ff00"
    )
    progressbar = ttk.Progressbar(
        root,
        orient="horizontal",
        length=200,
        mode="determinate",
        style="Custom.Horizontal.TProgressbar",
    )
    progressbar.pack(pady=10)
    progressbar.pack_forget()  # 初始时隐藏进度条

    # 设置窗口背景颜色
    root.configure(bg="#f0f0f0")

    # 获取屏幕的宽高
    screen_width = root.winfo_screenwidth()
    screen_height = root.winfo_screenheight()

    # 获取主窗口的宽高
    window_width = 400
    window_height = 400

    # 计算主窗口的居中位置
    x = (screen_width // 2) - (window_width // 2)
    y = (screen_height // 2) - (window_height // 2)

    # 设置主窗口位置
    root.geometry(f"{window_width}x{window_height}+{x}+{y}")

    root.mainloop()


if __name__ == "__main__":
    guess_number_game()
