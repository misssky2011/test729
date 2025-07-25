x = int(input("净利润："))

if x <= 100000:
    bonus = x * 0.1
    print(f"奖金: {bonus:.2f} 元")
elif x <= 200000:
    bonus = 10000 + (x - 100000) * 0.075
    print(f"奖金: {bonus:.2f} 元")
elif x <= 400000:
    bonus = 10000 + 7500 + (x - 200000) * 0.05
    print(f"奖金: {bonus:.2f} 元")
elif x <= 600000:
    bonus = 10000 + 7500 + 10000 + (x - 400000) * 0.03
    print(f"奖金: {bonus:.2f} 元")
elif x <= 1000000:
    bonus = 10000 + 7500 + 10000 + 6000 + (x - 600000) * 0.015
    print(f"奖金: {bonus:.2f} 元")
else:
    bonus = 10000 + 7500 + 10000 + 6000 + 6000 + (x - 1000000) * 0.01
    print(f"奖金: {bonus:.2f} 元")


for i in range(1, 85):
    if 168 % i == 0:
        j = 168 /i ;
        if i > j and (i + j) % 2 == 0 and (i - j) % 2 == 0:
            m = (i + j) / 2
            n = (i - j) / 2
            x = n * n - 100
            print(x)


f1 = 1
f2 = 1
for i in range(1, 22):
    print ('%12ld %12ld' % (f1, f2))
    if (i % 3) == 0:
        print('')
    f1 = f1 + f2
    f2 = f1 + f2


for i in range(1, 10):
    for j in range(1, i + 1):
         print(f'{i}*{j}={i*j}', end='\t')
    print()

fib = [0, 1]
for i in range(2, 10):
    fib.append(fib[i-1] + fib[i-2])
    print(fib)

num1 = int(input("请输入第一个数："))
num2 = int(input("请输入第二个数："))
num3 = int(input("请输入第三个数："))
print("三个数中的最大值为：", max(num1, num2, num3))

s = input("请输入一串字符：")
print("大写字母有：", [c for c in s if c.isupper()])


import math
for i in range(100,200):
    flag = 0
    for j in range(2, round(math.sqrt(i)) + i):
        if i%j == 0:
            flag = 1
            break
    if flag:
        continue
    print(i)
print('\nSimplify the code with "else"\n')

for i in range(100, 200):
    for j in range(2, round(math.sqrt(i)) +1):
        if i % j == 0:
           break
else:
    print(i)

