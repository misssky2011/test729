# 方法一
n = 4
sum = 1
for i in range(1,n+1):
     sum *= i
print(sum)

# 方法二:递归
def jie_chang(num):
    if num == 1:
        return 1
    else:
        return num * jie_chang(num - 1)
print(jie_chang(n))