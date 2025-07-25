def simple_calculator():
    print("欢迎使用简单计算器！")
    print("请输入你想计算的表达式（例如：88*22）：")

    while True:
        expression = input("输入表达式（或输入'exit'退出）：")
        if expression.lower() == 'exit':
            print("感谢适用简单计算器！")
            break
        try:
            result = eval(expression)
            print(f"结果：{result}")
        except Exception as e:
            print("输入错误，请重新输入有效的表达式！")

simple_calculator()