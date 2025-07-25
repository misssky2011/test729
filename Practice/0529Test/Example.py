with open ("output.txt", "w") as f:
    print ("Hello world", file=f)

#分隔符
print ("Hello world", "python", sep="-")
x = 10
print (x)

#格式化输出
name = "test"
print ("hello,{}!".format (name))

#文件输出
name = input ("请输入名字：")
print ("你的名字为：", name)

#算术运算符
a = 5 + 3
print (a)

b = 10 - 4
print (b)

c = 2 * 3
print (c)

d = 10 / 2
print (d)

e = 10 // 3
print (e)

f = 10 % 3
print (f)

g = 2 ** 3
print (g)

#比较运算符
x = 5
y = 5
#等于
print (x == y)
# 不等于
print (x != 6)
#大于
print (x > 3)
#小于
print (x < 6)
#大于等于
print (x >= 5)
#小于等于
print (x <= 5)

#赋值运算符
h = 10
print (h)

h += 5
print (h)

h *= 2
print (h)

#逻辑运算符
print (True and True)
print (True and False)

print (True and False)
print (False and False)

print (not True)
print (not False)

#身份运算符
a = [1, 2, 3]
b = a
c = [1, 2, 3]
print (a is b)
print (a is c)
print (a is not c)

#成员运算符
my_list = [1, 2, 3, 4, 5]
print (3 in my_list)
print (6 not in my_list)

#位运算符
a = 60
b = 13
print (a & b)
print (a | b)
print (a ^ b)
print (~ a)
print (a << 2)
print (a >> 2)

#条件判断
age = 20

if age < 13:
    print ("你是个小孩")
elif 13 <= age < 20:
    print ("你是个青年人")
elif 20 < age < 65:
    print ("你是个成年人")
else:
    print ("你是个老人")

# If语句
if x > 10:
    print ("x is greater than 10")
elif x == 10:
    print ("x is equal to 10")
else:
    print ("x is less than 10")

# For循环
for i in range (5):
    print (i)

# While循环
while x > 0:
    print (x)
    x -= 1

#!/usr/bin/python
import json

data = [{'a': 1, 'b': 2, 'c': 3, 'd': 4, 'e': 5}]

data2 = json.dumps (data)
print (data2)

# continue 和 break 用法

i = 1
while i < 10:
    i += 1
    if i % 2 > 0:  # 非双数时跳过输出
        continue
    print (i)  # 输出双数2、4、6、8、10

i = 1
while 1:  # 循环条件为1必定成立
    print (i)  # 输出1~10
    i += 1
    if i > 10:  # 当i大于10时跳出循环
        break

# !/usr/bin/python
count = 0
while count < 5:
    print (count, " is  less than 5")
    count = count + 1
else:
    print (count, " is not less than 5")

# 初始化变量
total_sum = 0
current_value = 1

# 计算30天的总和，每天的值是前一天的2倍
for day in range (1, 31):
    total_sum += current_value
    current_value *= 2  # 第二天的值是前一天的2倍

print (total_sum)

for letter in 'python':
    print ("当前字母: %s" % letter)

fruits = ['banana', 'apple', 'mango']
for fruit in fruits:
    print ('当前水果： %s' % fruit)
print ("Good bye!")

a = ['banana', 'apple', 'mango']
print ('当前水果： %s' % a)

i = 2
while i < 100:
    j = 2
    while j <= (i / j):
        if not (i % j): break
        j = j + 1
    if j > i / j: print (i, "是素数")
    i = i + 1

print ("Good bye!")

for letter in 'python':
    if letter == 'h':
        break
    print('当前变量值：', letter)

var = 10
while var > 0:
    print('当前变量值：', var)
    var = var - 1
    if var == 5:
        break

print("good bye!")

from bs4 import BeautifulSoup
import requests

# 指定你想要获取标题的网站
url = 'https://www.baidu.com/' # 抓取bing搜索引擎的网页内容

# 发送HTTP请求获取网页内容
response = requests.get(url)
# 中文乱码问题
response.encoding = 'utf-8'

soup = BeautifulSoup(response.text, 'lxml')

# 查找第一个 <a> 标签
first_link = soup.find('a')
print(first_link)
print("----------------------------")

# 获取第一个 <a> 标签的 href 属性
first_link_url = first_link.get('href')
print(first_link_url)
print("----------------------------")

# 查找所有 <a> 标签
all_links = soup.find_all('a')
print(all_links)



# 四叶玫瑰数
for number in range(1000, 10000):  # 四位数范围
    # 将数字分解为每一位
    digits = [int(d) for d in str(number)]
    # 计算每一位的四次方之和
    sum_of_powers = sum(d ** 4 for d in digits)
    # 检查是否是四叶玫瑰数
    if sum_of_powers == number:
        print(number)


# 三叶玫瑰数
def find_armstrong_numbers():
    result = []
    for num in range(100, 1000):  # 限定为三位数范围
        hundreds = num // 100  # 百位
        tens = (num // 10) % 10  # 十位
        units = num % 10  # 个位
        if num == hundreds**3 + tens**3 + units**3:  # 判断是否满足条件
            result.append(num)
    return result

# 打印所有三叶玫瑰数
armstrong_numbers = find_armstrong_numbers()
print("三叶玫瑰数:", armstrong_numbers)


year = int(input("请输入年份"))
month = int(input("请输入月份"))
day = int(input("请输入日期"))

date_list = [31, 29, 31, 30, 31, 30, 31, 31, 30, 31, 30, 31]
count_day = day
if year % 4 == 0 and year % 100 != 0 or year % 400 == 0:
    print(f'{year}年是闰年')
    date_list[1] = 29
else:
    print(f'{year}年是平年')
    date_list[1] = 28

for i in range(month-1):
    count_day += date_list[i]

print(f'{year}年{month}月{day}日是当年的第{count_day}天')

L = ["Jams", "Meng", "Xin"]
for i in range(len(L)):
    print("Hello, %s" %L [i])