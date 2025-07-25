import os
import time
from bs4 import BeautifulSoup
import undetected_chromedriver as uc

def init_driver():
    options = uc.ChromeOptions()
    options.headless = True  # 可改为 False 调试
    options.add_argument('--disable-blink-features=AutomationControlled')
    driver = uc.Chrome(options=options)
    return driver

def get_chapter_links(driver, index_url):
    print(f"📖 正在加载目录页：{index_url}")
    driver.get(index_url)
    time.sleep(2)

    soup = BeautifulSoup(driver.page_source, 'html.parser')
    links = soup.select('div.chapterlist a')  # 章节链接容器，具体结构可调整
    chapters = []
    for link in links:
        title = link.get_text(strip=True)
        href = link['href']
        full_url = href if href.startswith('http') else os.path.join(os.path.dirname(index_url), href)
        chapters.append((title, full_url))
    print(f"✅ 共获取到 {len(chapters)} 个章节链接")
    return chapters

def get_chapter_content(driver, url):
    driver.get(url)
    time.sleep(1.5)
    soup = BeautifulSoup(driver.page_source, 'html.parser')
    content = soup.find('div', id='chaptercontent')  # 小说正文所在 div
    if content:
        return content.get_text(separator='\n', strip=True)
    else:
        return "【获取失败】"

def save_novel(chapters, driver, save_path):
    with open(save_path, 'w', encoding='utf-8') as f:
        for idx, (title, url) in enumerate(chapters, 1):
            print(f"📘 正在下载第 {idx} 章：{title}")
            content = get_chapter_content(driver, url)
            f.write(f"\n\n{title}\n{'=' * 30}\n{content}\n")
    print(f"✅ 小说下载完成，已保存至：{save_path}")

def main():
    # 示例小说目录页链接（替换成你要下载的小说目录页）
    index_url = 'https://www.shushenge.com/59/index.html'  # 这是《修罗武神》的目录页（需根据书籍修改）

    driver = init_driver()
    try:
        chapters = get_chapter_links(driver, index_url)
        book_name = '小说下载结果'
        save_path = f"{book_name}.txt"
        save_novel(chapters, driver, save_path)
    finally:
        driver.quit()

if __name__ == "__main__":
    main()
