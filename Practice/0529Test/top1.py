# #数字组合
# num = 0
# for an in range (1, 5):
#     for b in range (1, 5):
#         for c in range (1, 5):
#             if (a != b) and (a != c) and (b != c):
#                 print (a, b, c)
#                 num += 1
# print (num)

# #个税计算
# profit = int (input 'Show me the money: ')
# bonus = 0
# thresholds = [100000, 100000, 200000, 200000, 200000, 200000, 1000000]  # 调整阶梯区间
# rates = [0.1, 0.075, 0.05, 0.03, 0.015, 0.01, 0.005]  # 对应税率
#
# for i in range (len (thresholds)):
#     if profit <= thresholds[i]:  # 若利润在当前区间内，直接计算
#         bonus += profit * rates[i]
#         profit = 0
#         break
#     else:  # 否则，计算该区间的奖金，并扣除该部分利润
#         bonus += thresholds[i] * rates[i]
#         profit -= thresholds[i]
#
# bonus += profit * rates[-1]  # 计算超出100万部分的奖金
# print (f'奖金总额: {bonus:.2f}')  # 格式化输出，保留两位小数

# #完全平方数
# n = 0
# while (n + 1) ** 2 - n * n <= 168:
#     n += 1
#
# print (n + 1)
#
# n = 0
# while (n + 1) ** 2 - n * n <= 168:
#     n += 1
#
# for i in range ((n + 1) ** 2):
#     if i ** 0.5 == int (i ** 0.5) and (i + 168) ** 0.5 == int ((i + 168) ** 0.5):
#         print (i - 100)


# #这天第几天
# def isleapyear(y):
#     return y % 400 == 0 or (y % 4 == 0 and y % 100 != 0)
#
# DofM = [0, 31, 28, 31, 30, 31, 30, 31, 31, 30, 31, 30]
# res = 0
# year = int (input ('Year:'))
# month = int (input ('Month:'))
# day = int (input ('day:'))
# if isleapyear (year):
#     DofM[2] += 1
# for i in range (month):
#     res += DofM[i]
# print (res + day)

# #三数排序
# raw = []
# for i in range (3):
#     x = int (input ('int%d: ' % i))
#     raw.append (x)
#
# for i in range (len (raw)):
#     for j in range (i, len (raw)):
#         if raw[i] > raw[j]:
#             raw[i], raw[j] = raw[j], raw[i]
# print (raw)
#
# raw2 = []
# for i in range (3):
#     x = int (input ('int%d: ' % i))
#     raw2.append (x)
# print (sorted (raw2))

# #九九乘法表
# for i in range(1, 10):
#     for j in range(1, i+1):
#         print('%d*%d=%2ld ' % (i, j, i*j), end='')
#     print()

# #暂停一秒
# import time
# for i in range(4):
#     print(str(int(time.time()))[-2:])
#     time.sleep(1)

#给人看的时间
# import time
#
# for i in range(4):
#     print(time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(time.time())))
#     time.sleep(1)


# #养兔子
# month = int(input('繁殖几个月？： '))
# month_1 = 1
# month_2 = 0
# month_3 = 0
# month_elder = 0
# for i in range(month):
#     month_1, month_2, month_3, month_elder = month_elder+month_3, month_1, month_2, month_elder+month_3
#     print('第%d个月共' % (i+1), month_1+month_2+month_3+month_elder, '对兔子')
#     print('其中1月兔：', month_1)
#     print('其中2月兔：', month_2)
#     print('其中3月兔：', month_3)
#     print('其中成年兔：', month_elder)

# #颜色
# class bcolors:
#     HEADER = '\033[95m'
#     OKBLUE = '\033[94m'
#     OKGREEN = '\033[92m'
#     WARNING = '\033[93m'
#     FAIL = '\033[91m'
#     ENDC = '\033[0m'
#     BOLD = '\033[1m'
#     UNDERLINE = '\033[4m'
# print(bcolors.WARNING + "警告的颜色字体?" + bcolors.ENDC)

# #矩阵
# X = [[12, 7, 3],
#      [4, 5, 6],
#      [7, 8, 9]]
#
# Y = [[5, 8, 1],
#      [6, 7, 3],
#      [4, 5, 9]]
#
# res = [[0, 0, 0],
#        [0, 0, 0],
#        [0, 0, 0]]
# for i in range (len (res)):
#     for j in range (len (res[0])):
#         res[i][j] = X[i][j] + Y[i][j]
# print (res)

# #求和
# res = 0
# for i in range(1, 101):
#     res += i
# print(res)
#
# #画圈
# from tkinter import *
# canvas = Canvas(width=800, height=600, bg='yellow')
# canvas.pack(expand=YES, fill=BOTH)
# k = 1
# j = 1
# for i in range(26):
#     canvas.create_oval(310-k, 250-k, 310+k, 250+k, width=1)
#     k += j
#     j += 0.3
# mainloop()

# #画线
# if __name__ == '__main__':
#     from tkinter import *
#
#     canvas = Canvas (width=300, height=300, bg='green')
#     canvas.pack (expand=YES, fill=BOTH)
#     x0 = 263
#     y0 = 263
#     y1 = 275
#     x1 = 275
#     for i in range (19):
#         canvas.create_line (x0, y0, x0, y1, width=1, fill='red')
#         x0 = x0 - 5
#         y0 = y0 - 5
#         x1 = x1 + 5
#         y1 = y1 + 5
#
#     x0 = 263
#     y1 = 275
#     y0 = 263
#     for i in range (21):
#         canvas.create_line (x0, y0, x0, y1, fill='red')
#         x0 += 5
#         y0 += 5
#         y1 += 5

# mainloop ()

#画矩形
# if __name__ == '__main__':
#     from tkinter import *
#
#     root = Tk ()
#     root.title ('Canvas')
#     canvas = Canvas (root, width=400, height=400, bg='yellow')
#     x0 = 263
#     y0 = 263
#     y1 = 275
#     x1 = 275
#     for i in range (19):
#         canvas.create_rectangle (x0, y0, x1, y1)
#         x0 -= 5
#         y0 -= 5
#         x1 += 5
#         y1 += 5
#
#     canvas.pack ()
#     root.mainloop ()

# #画图
# if __name__ == '__main__':
#     from tkinter import *
#
#     canvas = Canvas (width=300, height=300, bg='green')
#     canvas.pack (expand=YES, fill=BOTH)
#     x0 = 150
#     y0 = 100
#     canvas.create_oval (x0 - 10, y0 - 10, x0 + 10, y0 + 10)
#     canvas.create_oval (x0 - 20, y0 - 20, x0 + 20, y0 + 20)
#     canvas.create_oval (x0 - 50, y0 - 50, x0 + 50, y0 + 50)
#     import math
#
#     B = 0.809
#     for i in range (16):
#         a = 2 * math.pi / 16 * i
#         x = math.ceil (x0 + 48 * math.cos (a))
#         y = math.ceil (y0 + 48 * math.sin (a) * B)
#         canvas.create_line (x0, y0, x, y, fill='red')
#     canvas.create_oval (x0 - 60, y0 - 60, x0 + 60, y0 + 60)
#
#     for k in range (501):
#         for i in range (17):
#             a = (2 * math.pi / 16) * i + (2 * math.pi / 180) * k
#             x = math.ceil (x0 + 48 * math.cos (a))
#             y = math.ceil (y0 + 48 + math.sin (a) * B)
#             canvas.create_line (x0, y0, x, y, fill='red')
#         for j in range (51):
#             a = (2 * math.pi / 16) * i + (2 * math.pi / 180) * k - 1
#             x = math.ceil (x0 + 48 * math.cos (a))
#             y = math.ceil (y0 + 48 * math.sin (a) * B)
#             canvas.create_line (x0, y0, x, y, fill='red')
#     mainloop ()

# #三角形
# def generate(numRows):
#     r = [[1]]
#     for i in range(1, numRows):
#         r.append(list(map(lambda x, y: x+y, [0]+r[-1], r[-1]+[0])))
#     return r[:numRows]
# a = generate(10)
# for i in a:
#     print(i)

# #椭圆
# if __name__ == '__main__':
#     from tkinter import *
#
#     x = 360
#     y = 160
#     top = y - 30
#     bottom = y - 30
#
#     canvas = Canvas (width=400, height=600, bg='white')
#     for i in range (20):
#         canvas.create_oval (250 - top, 250 - bottom, 250 + top, 250 + bottom)
#         top -= 5
#         bottom += 5
#     canvas.pack ()
#     mainloop ()

# #
# l = ['moyu', 'niupi', 'xuecaibichi', 'shengfaji', '42']
# for i in range(len(l)):
#     print(l[i])

# RUNOOB = [6, 0, 4, 1]
# print('清空前:', RUNOOB)
# RUNOOB.clear()
# print('清空后:', RUNOOB)

# # 引入日历模块
# import calendar
#
# # 输入指定年月
# yy = int(input("输入年份: "))
# mm = int(input("输入月份: "))
#
# # 显示日历
# print(calendar.month(yy, mm))

# import numpy as np
# import matplotlib.pyplot as plt
# from mpl_toolkits.mplot3d import Axes3D
# #matplotlib inline
# from sklearn.datasets import make_blobs
# ## X为样本特征，Y为样本簇类别， 共1000个样本，每个样本3个特征，共4个簇
# X, y = make_blobs(n_samples=10000, n_features=3, centers=[[3,3, 3], [0,0,0], [1,1,1], [2,2,2]], cluster_std=[0.2, 0.1, 0.2, 0.2],
#                   random_state =9)
# fig = plt.figure()
# ax = Axes3D(fig, rect=[0, 0, 1, 1], elev=30, azim=20)
# plt.scatter(X[:, 0], X[:, 1], X[:, 2],marker='x')
#
# from sklearn.decomposition import PCA
# pca = PCA(n_components=3)
# pca.fit(X)
# print(pca.explained_variance_ratio_)
# print(pca.explained_variance_)
# pca = PCA(n_components=2)
# pca.fit(X)
# print(pca.explained_variance_ratio_)
# print(pca.explained_variance_)
#
# pca = PCA(n_components=0.9)
# pca.fit(X)
# print(pca.explained_variance_ratio_)
# print(pca.explained_variance_)
# print(pca.n_components_)

# a = 30
# b = 10
# c = 0
# if a == b:
#     print ("a 等于 b")
# else:
#     print ("a 不等于 b")
# if a != b:
#     print ("a 不等于 b")
# else:
#     print ("a 等于 b")
# if a < b:
#     print ("a 小于 b")
# else:
#     print ("a 大于等于 b")
# if a > b:
#     print ("a 大于 b")
# else:
#     print ("a 小于等于 b")
# # 修改变量 a 和 b 的值
# a = 5
# b = 20
# if a <= b:
#     print ("a 小于等于 b")
# else:
#     print ("a 大于  b")
# if b >= a:
#     print ("b 大于等于 a")
# else:
#     print ("b 小于 a")


# a = 30
# b = 10
# c = 0
#
# c = a + b
# print("第1次运算后，c的值为：", c)
# c += a
# print("第2次运算后，c的值为：", c)
# c *= a
# print("第3次运算后，c的值为：", c)
# c /= a
# print("第4次运算后，c的值为：", c)
# c = 2
# c %= a
# print("第5次运算后，c的值为：", c)
# c **= a
# print("第6次运算后，c的值为：", c)
# c //= a
# print("第7次运算后，c的值为：", c)

# a = 60            # 60 = 0011 1100
# b = 13            # 13 = 0000 1101
# c = 0
# c = a & b  # 12 = 0000 1100
# print("第1次运算后，c的值为：", c)
# c = a | b  # 61 = 0011 1101
# print("第2次运算后，c的值为：", c)
# c = a ^ b  # 49 = 0011 0001
# print("第3次运算后，c的值为：", c)
# c = ~a  # -61 = 1100 0011
# print("第4次运算后，c的值为：", c)
# c = a << 2  # 240 = 1111 0000
# print("第5次运算后，c的值为：", c)
# c = a >> 2  # 15 = 0000 1111
# print("第6次运算后，c的值为：", c)

# num = 9
# if 0 <= num <= 10:    # 判断值是否在0~10之间
#     print('hello')

# num = 10
# if num < 0 or num > 10:    # 判断值是否在小于0或大于10
#     print('hello')
# else:
#     print('undefine')

# num = 6
# # 判断值是否在0~5或者10~15之间
# if (num >= 0 and num <= 5) or (num >= 10 and num <= 15):
#     print('hello')
# else:
#     print('undefine')

# show = 100
# if ( show  == 100 ) : print("变量 show 的值为100")
# print("Good bye!")

# for letter in 'ShowMeAI':  # 第一个实例
#     print ("当前字母: %s" % letter)
# fruits = ['banana', 'apple', 'mango']
# for fruit in fruits:  # 第二个实例
#     print ('当前水果: %s' % fruit)
# print ("完成!")

# for num in range (20, 30):  # 迭代 10 到 20 之间的数字
#     for i in range (2, num):  # 根据因子迭代
#         if num % i == 0:  # 确定第一个因子
#             j = num / i  # 计算第二个因子
#             print ('%d 等于 %d * %d' % (num, i, j))
#             break  # 跳出当前循环
#     else:  # 循环的 else 部分
#         print ('%d 是一个质数' % num)


# #空心三角形
# rows = int(input('输入列数： '))
# print("打印空心等边三角形，这里去掉if-else条件判断就是实心的")
# for i in range(0, rows + 1):#变量i控制行数
#     for j in range(0, rows - i):#(1,rows-i)
#         print(" ", end='')
#         j += 1
#     for k in range(0, 2 * i - 1):#(1,2*i)
#         if k == 0 or k == 2 * i - 2 or i == rows:
#             if i == rows:
#                 if k % 2 == 0:#因为第一个数是从0开始的，所以要是偶数打印*，奇数打印空格
#                     print("*", end='')
#                 else:
#                     print(" ", end='')#注意这里的", end='' "，一定不能省略，可以起到不换行的作用
#             else:
#                print("*", end='')
#         else:
#             print(" ", end='')
#         k += 1
#     print("\
# ")
#     i += 1


# #菱形
# rows = int(input('输入列数： '))
# print("打印空心等菱形，这里去掉if-else条件判断就是实心的")
# rows = int(input('输入列数： '))
# for i in range(rows):#变量i控制行数
#     for j in range(rows - i):#(1,rows-i)
#         print(" ", end='')
#         j += 1
#     for k in range(2 * i - 1):#(1,2*i)
#         if k == 0 or k == 2 * i - 2:
#             print("*", end='')
#         else:
#             print(" ", end='')
#         k += 1
#     print("\
# ")
#     i += 1
#     #菱形的下半部分
# for i in range(rows):
#     for j in range(i):#(1,rows-i)
#         print(" ", end='')
#         j += 1
#     for k in range(2 * (rows - i) - 1):#(1,2*i)
#         if k == 0 or k == 2 * (rows - i) - 2:
#             print("*", end='')
#         else:
#             print(" ", end='')
#         k += 1
#     print("\
# ")
#     i += 1


# #continue语句
# for letter in 'ItIsShowMeAI':  # 第一个实例
#     if letter == 'h':
#         continue
#     print ('当前字母 :', letter)
# var = 10  # 第二个实例
# while var > 0:
#     var = var - 1
#     if var == 5:
#         continue
#     print ('当前变量值 :', var)
# print ("完成!")

# #PASS语句
# for letter in 'ItIsShowMeAI':
#     if letter == 'h':
#         pass
#         print ('这是 pass 块')
#         print ('当前字母 :', letter)
#     print ("完成!")

# import sys
# print('命令行参数如下:')
# for i in sys.argv:
#    print(i)
# print('\
# \
# Python 路径为：', sys.path, '\
# ')


# my_love = "13766666666"
# my_ex = my_love
# my_love = "15688888888"
# print("拨打的电话：" + my_love)
# print("拨打的电话：" + my_ex)
# print("===")

# import math
# math.sin(1)
# print('sin')

# s = "Hello world!"
# print(len(s))
#
# #通过索引获取单个字符
# print(s[0])
#
# #布尔类型
# b1 = True
# b2 = False
#
# #空值类型
# n = None
#
# #tpye函数
# print(type(s))
# print(type(b1))
# print(type(n))
# print(type(1.5))


# #BMI = 体重/身高*2
# user_weight = float(input("请输入你的体重（单位：kg）："))
# user_height = float(input("请输入您的身高（单位：m）："))
# user_BMI = user_weight / user_height ** 2
# print("您的BMI值为：" + str(user_BMI))
# if user_BMI <= 18.5:
#     print("BMI值属于正常范围")
# elif 18.5 < user_BMI <= 30:
#     print("BMI值属于偏瘦范围")
# else:
#     print("BMI值属于偏胖范围")
# def calculate_BMI(weight, height):
#     BMI = weight/height **2
#     if BMI <= 18.5:
#         category = "偏瘦"
#     elif BMI <= 25:
#         category = "正常"
#     else:
#         category = '偏胖'
#     print(f"你的BMI分类：{category}")
#     return BMI
# result = calculate_BMI(1.8, 70)
# print(result)

# mood_index = int(input("对象的心情指数是："))
# if mood_index >= 60:
#     print("恭喜，今晚应该可以打游戏，去吧皮卡丘！")
#     print(":saluting_face:")
# else:
#     print("为了自个儿小命，还是别打了！")
#     print(":joy")

# #打印大写字母
# s = "hello"
# print(s.upper())
# print(s）

# shopping_list = []
# shopping_list.append("键盘")
# shopping_list.append("帽子")
# shopping_list.remove("帽子")
# shopping_list.append("音响")
# shopping_list.append("电竞椅")
# shopping_list[1] = "硬盘"
#
# print(shopping_list)
# print(len(shopping_list))
# print(shopping_list[2])
# # print(max(shopping_list))  # 打印列表最大值
# # print(min(shopping_list))  # 打印列表最小值
# # print(sorted(shopping_list))  # 打印列表排序
# price = [799, 1024, 200, 800, 2099]
# max_price = max(price)
# min_price = min(price)
# sorted_price = sorted(price)
# print(sorted_price)

# #字典、元组
# contacts = {}
# slang_dict = {"觉醒时代": "特色它",
#               "yyds": "test"}
# query = input("请输入你查询的流行语：")
# if query in slang_dict:
#     print('你的查询' + query + "含义如下")
#     print(slang_dict[query])
# else:
#     print("你当前的流行语未找到")
#     print("当前的词典收录词条数为:" + str(len(slang_dict)) + "条.")

# #for &range
# total = 0
# for i in range(1, 101):
#     total = total + i
# print(total)

# #for & while循环未知次数
# total = 0
# count = 0
# print("我是一个求平均值的程序")
# user_input = input("请输入数字：")
# while user_input != "q":
#     num = float(user_input)
#     total += num
#     count += 1
#     user_input = input("请输入数字：")
# if count == 0:
#     result = 0
# else:
#     result = total/count
# print("你输入的数字平方值为：" + str(result))

# #发送祝福短信
# import datetime
# def send_message(name, message):
#     """模拟发送消息的函数，可替换为实际发送逻辑"""
#     print(f"发送给 {name}：\n{message}\n")
#
# def get_chinese_zodiac(year):
#     """根据年份计算对应的生肖"""
#     zodiacs = ["鼠", "牛", "虎", "兔", "龙", "蛇", "马", "羊", "猴", "鸡", "狗", "猪"]
#     return zodiacs[(year - 4) % 12]  # 以 4 年（甲子年）为基准计算生肖
#
# # 获取当前年份并计算生肖
# current_year = datetime.datetime.now().year
# year_zodiac = get_chinese_zodiac(current_year)
#
# contacts = ["老余", "老林", "老陈", "老曾", "老李", "老张"]
#
# for name in contacts:
#     message_content = f"""
# 律回春渐，新元肇启。
# 新岁甫至，福气东来。
# 金{year_zodiac}贺岁，欢乐祥瑞。
# 给{name}及家人拜年啦！
# 新春快乐，{year_zodiac}年大吉！
# """
#     send_message(name, message_content)

# import socket
# server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
# server_address = ('localhost', 8888)
# server_socket.bind(server_address)
# server_socket.listen(1)
# print("服务器正在监听端口8888...")

# first_name = "John"
# last_name = "Doe"
# full_name = first_name + " " + last_name
# print(full_name)
#
# text = "Python is great"
# sub_text = text[0:8]
# print(sub_text)

# #列表元素的添加和删除
# numbers = [1, 2, 3]
# numbers.append(4)
# print(numbers)
# numbers.remove(2)
# print(numbers)
# #列表的排序
# unsorted_list = [3, 1, 4, 1, 5, 9, 2, 6, 5, 3, 5]
# unsorted_list.sort()
# print(unsorted_list)

# #for 循环遍历列表
# colors = ["red", "green", "blue"]
# for color in colors:
#     print(color)

# student = {"name": "Tom", "age": 20, "major": "Computer Science"}
# print("name", "age")

#热力图
# import pandas
# from sklearn import datasets
# import seaborn as sns
# import matplotlib.pyplot as plt
# import numpy
# data = datasets.load_wine().data
# print(type(data))
# df1 = pandas.DataFrame(data, columns=["x%d"%(i+1) for i in range(numpy.shape(data)[1])]).iloc[:, :7]
# cor1 = df1.corr()
# sns.heatmap(cor1, cmap='Blues', annot=True)
# plt.show()

# #散点图
# import seaborn as sns
# import matplotlib.pyplot as plt
# import pandas
# df3=pandas.DataFrame({"english":[4,6,7,9,6,4,9,11],"math":[1,2,3,4,5,2,7,8]})
# sns.scatterplot(x=df3['english'],y=df3['math'],marker='o',label='c',c=["blue"])
# plt.show()

# #折线图
# import numpy as np
# import matplotlib.pyplot as plt
# a=np.arange(-20,20,0.01)
# b=a**2
# c=-a**2
# plt.plot(a,b,color="black",linestyle='-.')
# plt.plot(a,c,color="black",linestyle='--')   		#在同一坐标系中绘制多张图
# plt.show()

# #饼图
# import matplotlib.pyplot as  plt
# x=[2,3,4,1]
# xlabel=['a','b','c','d']
# odistance=[0,0,0.1,0]
# plt.pie(x=x,labels=xlabel,explode=odistance,radius=0.8)
# plt.show()

# #热力图
# import numpy as np
# import matplotlib.pyplot as plt
# import seaborn as sns
# #数据准备
# flights = sns.load_dataset("flights")
# data = flights.pivot('year', 'month', 'passengers')
# #S
# sns.heatmap(data)
# plt.show()

#
# #蜘蛛图
# import numpy as np
# import matplotlib.pyplot as plt
# import seaborn as sns
# ## 数据准备
# labels=np.array([u" 推进 ","KDA",u" 生存 ",u" 团战 ",u" 发育 ",u" 输出 "])
# stats = [83,61,95,67,76,88]
# angles=np.linspace(0, 2*np.pi, len(labels), endpoint=False)
# stats=np.concatenate((stats,[stats[0]]))  # 与第一个组合才能闭环
# angles=np.concatenate((angles,[angles[0]]))
# # Matplotlib
# fig = plt.figure()
# ax = fig.add_subplot(111, polar=True)
# ax.plot(angles, stats, 'o-', linewidth=2)
# ax.fill(angles, stats, alpha=0.25)
# ax.set_thetagrids(angles * 180/np.pi, labels)
# plt.show()

# import numpy
# speed = [99, 86, 87, 88, 111, 86, 103, 87, 94, 78, 77, 85, 86]
# speed.sort()  # 排序
# x = numpy.mean(speed)  # 平均值
# y = numpy.median(speed)  # 中值
# print(speed, x, y)

# from scipy import stats
# speed = [99, 86, 87, 88, 111, 86, 103, 87, 94, 78, 77, 85, 86]
# x = stats.mode(speed)  # 众数
# print(x)

# import numpy
# speed = [99, 86, 87, 88, 111, 86, 103, 87, 94, 78, 77, 85, 86]
# x = numpy.std(speed)  # 标准差 --标准差通常用 Sigma 符号表示：σ
# y = numpy.var(speed)  # 方差 --方差通常由 Sigma Square 符号 σ2 表示
# print(round(x, 2), round(y, 2))  # 保留2位小数  -- print(f"{x:.2f} {y:.2f}")

# import numpy
# ages = [5, 31, 43, 48, 50, 41, 7, 11, 15, 39, 80, 82, 32, 2, 8, 6, 25, 36, 27, 61, 31]
# x = numpy.percentile(ages, 90)  # 百分位数
# print(x)

# import numpy
# import matplotlib.pyplot as plt
# x = numpy.random.uniform(0.0, 5.0, 250)
# plt.hist(x, 5)  # 直方图
# plt.show()

# import datetime
# x = datetime.datetime.now()
# print(x.year)  # 年
# print(x)       # 年/月/日
# print(x.strftime("%A"))    # 星期

# %A/%a：短板、完整版本
# %w	Weekday，数字 0-6，0 为周日
# %d	日，数字 01-31
# %b/%B	月名称，短版本
# %m	月，数字01-12
# %H	小时，00-23
# %I	小时，00-12
# %p	AM/PM
# %M	分，00-59
# %S	秒，00-59
# %Z	时区
# 时区%j	天数，001-366

# import datetime
# x = datetime.datetime(2019, 10, 1)
# print(x.strftime("%H"))

# !/usr/bin/python3

# a = 21
# b = 10
# c = 0
#
# c = a + b
# print ("1 - c 的值为：", c)
#
# c += a
# print ("2 - c 的值为：", c)
#
# c *= a
# print ("3 - c 的值为：", c)
#
# c /= a
# print ("4 - c 的值为：", c)
#
# c = 2
# c %= a
# print ("5 - c 的值为：", c)
#
# c **= a
# print ("6 - c 的值为：", c)
#
# c //= a
# print ("7 - c 的值为：", c)

# # 传统写法
# n = 10
# if n > 5:
#     print(n)
#
# # 使用海象运算符
# if (n := 10) > 5:
#     print(n)

