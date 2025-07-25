import requests
from bs4 import BeautifulSoup
import time

# 初始URL页面
url = 'https://movie.douban.com/top250'

# GET请求模拟浏览器发送
headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/131.0.0.0 Safari/537.36'
}

# 逐页爬行
for i in range(10):
    # 完整URL，修正为使用正确的 url 变量
    page_url = f'{url}?start={i*20}&limit=20'  # 使用页面分页的 URL

    # 发送请求获取HTML内容
    response = requests.get(page_url, headers=headers)
    if response.status_code == 200:
        soup = BeautifulSoup(response.text, 'html.parser')
        comment_list = soup.find_all('div', class_='comment')

        # 对每个影评的具体信息进行分析
        for comment_item in comment_list:
            # 得到评论者名字
            commenter = comment_item.find('a').text.strip()  # 修改为合适的选择器
            # 获取评论内容
            comment_content = comment_item.find('p', class_='comment-content').text.strip()
            # 获取评分
            rating_tag = comment_item.find('span', class_='rating')
            # 有些评论可能没有评分
            rating = rating_tag['title'] if rating_tag else '无评分'
            # 打印评论者、评分和评论内容
            print(f'评论者：{commenter}, 评分：{rating}')
            print(f'评论内容：{comment_content}\n')

    # 设置延迟时间
    time.sleep(2)
