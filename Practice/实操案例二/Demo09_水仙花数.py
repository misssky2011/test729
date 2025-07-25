# n = 567
# a = n % 10
# b = (n % 100) // 10
# c = n // 100
# print(a, b, c)
for i in range(100, 10000):
    a = i % 10
    b = (i % 100) // 10
    c = i // 100
    if a*a*a + b*b*b + c*c*c == i:
        print(f'{i}是水仙花')