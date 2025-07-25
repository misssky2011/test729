from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from webdriver_manager.chrome import ChromeDriverManager
from lxml import etree
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time
import os

# 设置无头浏览器选项
chrome_options = Options()
chrome_options.add_argument('--headless')
chrome_options.add_argument('--disable-gpu')
chrome_options.add_argument('--no-sandbox')
chrome_options.add_argument("--disable-blink-features=AutomationControlled")

# 初始化 WebDriver
service = Service(ChromeDriverManager().install())
driver = webdriver.Chrome(service=service, options=chrome_options)

# 目标小说 ID（例如 59 是《斗罗大陆》）
book_id = "59"

# 目录页 URL
catalog_url = f'https://m.shushenge.com/{book_id}/'

print("正在访问小说目录页:", catalog_url)
driver.get(catalog_url)

# 等待章节列表加载完成
try:
    WebDriverWait(driver, 10).until(
        EC.presence_of_element_located((By.XPATH, '//div[@class="listmain"]/dl/dd/a'))
    )
except Exception as e:
    print("❌ 等待超时或发生异常：", e)
    driver.quit()
    exit()

# 获取页面源码并关闭浏览器
html_str = driver.page_source
driver.quit()

# 解析目录页 HTML
html = etree.HTML(html_str)

# 提取所有章节链接
chapter_links = html.xpath('//div[@class="listmain"]/dl/dd/a/@href')
chapter_titles = html.xpath('//div[@class="listmain"]/dl/dd/a/text()')

print(f"共找到 {len(chapter_links)} 章节")

# 创建文件夹保存章节
output_dir = f"{book_id}_小说内容"
os.makedirs(output_dir, exist_ok=True)

# 合并后的完整小说内容
full_content = []

# 遍历每个章节
for i, (title, link) in enumerate(zip(chapter_titles, chapter_links), start=1):
    chapter_url = f'https://m.shushenge.com{link}'
    print(f"第 {i}/{len(chapter_links)} 章：{title} —— {chapter_url}")

    # 重新启动浏览器（防止长时间运行出错）
    driver = webdriver.Chrome(service=service, options=chrome_options)

    try:
        driver.get(chapter_url)
        WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.XPATH, '//div[@id="chaptercontent"]'))
        )

        html_str = driver.page_source
        html = etree.HTML(html_str)

        # 提取标题和正文
        content_title = html.xpath('//h1[@class="title"]/text()')[0].strip()
        paragraphs = html.xpath('//div[@id="chaptercontent"]/p/text()')

        # 添加到完整内容中
        full_content.append(f"== {content_title} ==\n")
        full_content.extend(paragraphs)
        full_content.append("\n\n")

        # 可选：单独保存每一章
        with open(os.path.join(output_dir, f"{i:04d}_{content_title}.txt"), "w", encoding="utf-8") as f:
            f.write("\n".join(paragraphs))

    except Exception as e:
        print(f"⚠️ 无法读取章节：{e}")
    finally:
        driver.quit()

    time.sleep(1)  # 防止请求过快被封 IP

# 保存完整小说文件
with open(f"{book_id}_完整小说.txt", "w", encoding="utf-8") as f:
    f.write("\n".join(full_content))

print("✅ 所有章节已采集完成，并合并为完整小说文件！")