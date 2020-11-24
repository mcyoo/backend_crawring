from selenium import webdriver
from selenium.webdriver.chrome.options import Options
import time

chrome_options = Options()
chrome_options.add_argument("--headless")
chrome_options.add_argument("--no-sandbox")
chrome_options.add_argument("--disable-dev-shm-usage")

driver = webdriver.Chrome(
    "/usr/lib/chromium-browser/chromedriver", chrome_options=chrome_options
)
time.sleep(3)

driver.get("https://pionex.zendesk.com/hc/ko-kr/")

page = driver.page_source

print(page)

driver.quit()