# 求100以内的奇数
# 第一种方法
list1 = []
for i in range(1, 100):
    if i % 2 != 0:
        list1.append(i)
print(list1)

# 第二种方法
list2 = []
for i in range(1, 100,2):
    list2.append(i)
print(list2)