# 圆的周长
import math

pi = 3.14

r = float(input('请输入半径：'))

c = 2 * pi * r

print(f'圆的周长是：{c}')

# 圆的面积

pi = 3.14

r = float(input('请输入半径：'))

S = pi * r * r
print(f'圆的面积：{S}')


# 求直角三角形斜边长
a = int(input('请输入第一个直角边长：'))
b = int(input('请输入第一个直角边长：'))

m = a * a + b * b
c = math.sqrt(m)
print(f'直角三角形斜边长为：{c}')

# 比较三个数的大小
a = int(input('请输入第一个数：'))
b = int(input('请输入第二个数：'))
c = int(input('请输入第三个数：'))

list = [a, b, c]
list1 = sorted(list)
print(list1)
print(f'三个数从小到大的顺序是：{list1}')
