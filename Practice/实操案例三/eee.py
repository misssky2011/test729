from selenium import webdriver
from selenium.webdriver.chrome.options import Options

chrome_options = Options()
chrome_options.add_argument("--headless")  # 无头模式，不打开浏览器窗口
chrome_options.add_argument("--disable-gpu")
chrome_options.add_argument("--no-sandbox")
chrome_options.add_argument("user-agent=Mozilla/5.0 (Linux; Android 6.0; Nexus 5 Build/MRA58N) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/137.0.0.0 Mobile Safari/537.36")

driver = webdriver.Chrome(options=chrome_options)
driver.get('https://m.shushenge.com/59/7.html')

# 等待页面加载完成，最长等待10秒
driver.implicitly_wait(10)

page_source = driver.page_source
print(page_source)

driver.quit()