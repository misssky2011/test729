import randomTest
import string
import json
import re

# 定义正则表达式用于密码强度验证
PASSWORD_REGEX = r'^(?=.*[a-z])(?=.*[A-Z])(?=.*\d)(?=.*[@$!%*?&])[A-Za-z\d@$!%*?&]{8,}$'


def load_config(config_file="config.json"):
    """
    从配置文件加载默认设置。
    :param config_file: 配置文件路径，默认值为 "config.json"。
    :return: 返回配置字典（包含默认密码长度和是否包含特殊字符的选项）。
    """
    try:
        with open (config_file, 'r') as file:
            config = json.load (file)  # 使用 JSON 模块读取配置文件
        return config
    except FileNotFoundError:
        print (f"未找到配置文件 {config_file}，将使用默认设置。")
        # 如果找不到配置文件，则返回默认设置
        return {"default_length": 12, "include_special_chars": True}


def save_password_to_file(password, file_name="passwords.txt"):
    """
    将生成的密码保存到指定文件中。
    :param password: 要保存的密码字符串。
    :param file_name: 保存密码的文件名，默认值为 "passwords.txt"。
    """
    try:
        with open (file_name, 'a') as file:  # 以追加模式打开文件
            file.write (password + '\n')  # 每次将密码写入新行
        print (f"密码已保存到文件 {file_name}")
    except Exception as e:
        # 捕获可能的文件操作异常
        print (f"保存密码时出错: {e}")


def generate_password(length, include_special_chars=True):
    """
    生成随机密码。
    :param length: 密码长度。
    :param include_special_chars: 是否包含特殊字符，默认值为 True。
    :return: 生成的随机密码字符串。
    """
    # 定义基础字符集合（字母和数字）
    characters = string.ascii_letters + string.digits
    if include_special_chars:
        # 如果启用特殊字符，将其加入字符集合
        characters += string.punctuation
    # 使用 random.choices 随机选择指定长度的字符
    password = ''.join (random.choices (characters, k=length))
    return password


def validate_password_strength(password):
    """
    验证密码是否满足强密码要求。
    :param password: 要验证的密码字符串。
    :return: 如果密码符合强密码规则，返回 True，否则返回 False。
    """
    if re.match (PASSWORD_REGEX, password):  # 使用正则表达式匹配密码规则
        return True
    return False


def main():
    """
    主函数，负责程序的交互逻辑和功能调用。
    """
    # 从配置文件加载默认设置
    config = load_config ()

    print ("欢迎使用高级随机密码生成工具！")
    print ("模式选择：")
    print ("1. 自定义密码生成")
    print ("2. 强密码生成（系统推荐）")
    print ("3. 退出")

    while True:
        # 提示用户选择模式
        choice = input ("请选择模式（1/2/3）：").strip ()

        if choice == '1':  # 自定义密码生成模式
            while True:
                try:
                    # 提示用户输入密码长度
                    length = int (input ("请输入密码长度（正整数）："))
                    if length <= 0:
                        print ("密码长度必须大于 0，请重新输入。")
                        continue
                    break
                except ValueError:
                    # 捕获输入非整数的情况
                    print ("无效输入，请输入一个正整数！")

            # 提示用户是否包含特殊字符
            include_special_chars = input ("是否包含特殊字符？(y/n): ").strip ().lower () == 'y'
            # 调用生成密码的函数
            password = generate_password (length, include_special_chars)
            print (f"生成的自定义密码是：{password}")

            # 是否保存密码到文件
            save_option = input ("是否保存密码到文件？(y/n): ").strip ().lower ()
            if save_option == 'y':
                save_password_to_file (password)

        elif choice == '2':  # 强密码生成模式
            # 使用配置文件中的默认设置生成强密码
            length = config.get ("default_length", 12)
            include_special_chars = config.get ("include_special_chars", True)
            password = generate_password (length, include_special_chars)

            # 验证密码强度，不符合规则则重新生成
            while not validate_password_strength (password):
                password = generate_password (length, include_special_chars)

            print (f"生成的强密码是：{password}")

            # 是否保存密码到文件
            save_option = input ("是否保存密码到文件？(y/n): ").strip ().lower ()
            if save_option == 'y':
                save_password_to_file (password)

        elif choice == '3':  # 退出程序
            print ("感谢使用，程序退出。")
            break

        else:
            # 处理无效输入
            print ("无效选择，请输入 1、2 或 3！")


if __name__ == "__main__":
    main ()
