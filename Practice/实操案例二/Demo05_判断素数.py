# 判断素数
a = 15
for i in range(2,a):
    if a % i ==0:
        flag = True
        break
if flag:
    print('是合数')
else:
    print('是素数')
