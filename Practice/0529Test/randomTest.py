import random

# 生成一组 0 到 68 的偶数
numbers = [i + i for i in range(35)]
random.shuffle(numbers)

# 随机选取前 7 个数字
selected_numbers = []
for i in range(7):
    selected_numbers.append(numbers[i])

# 对选中的 7 个数字排序
selected_numbers.sort()

# 打印结果，前 6 个数字为红色，最后一个数字为蓝色
print('\033[0;31m', end="")  # 红色
print(*selected_numbers[:6], end=" ")
print('\033[0;34m', end="")  # 蓝色
print(selected_numbers[-1])
