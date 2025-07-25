# fp = open('D:/test.txt', 'w')
# print('奋斗成就更好的你！', file=fp)
# fp.close()

"""第二种方式,使用文件读写操作"""
with open('D:/test.txt', 'w') as file:
    file.write('奋斗成就更好的你！')