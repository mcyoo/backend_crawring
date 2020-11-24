from selenium.webdriver.chrome.options import Options
from selenium import webdriver
from bs4 import BeautifulSoup
import time
import csv
import json

loading_sec = 5
instargram_url = "https://www.instagram.com"
SCROLL_PAUSE_SEC = loading_sec
file_path = "instagram_data.json"


data = {}
data["feed_count"] = 0
data["feed_location"] = []
data["friend_profile"] = []
data["feeds_date"] = []
data["feeds_like"] = []
data["feeds_comment"] = []

options = Options()
options.add_argument("--headless")
options.add_argument("window-size=1920,1080")

driver = webdriver.Chrome(options=options)


def save_to_file(brand_name, alba_list):
    file = open(f"{brand_name}.csv", mode="w", encoding="utf-8", newline="")
    writer = csv.writer(file)
    writer.writerow(["local", "title", "data", "pay", "date"])
    for alba in alba_list:
        writer.writerow(alba)


def location_list_setting(location_list):
    new_list = []
    new_count_list = []
    for location in location_list:
        if location not in new_list:
            new_list.append(location)

    for location in new_list:
        new_count_list.append(location_list.count(location))

    return new_list, new_count_list


def friend_list_setting(friend_list):
    one_list = sum(friend_list, [])

    new_list = []
    new_count_list = []
    new_url = []
    new_img_url = []

    for tag_name in one_list:
        if tag_name not in new_list:
            new_list.append(tag_name)

    for tag_name in new_list:
        new_count_list.append(one_list.count(tag_name))
        new_url.append(instargram_url + tag_name)

    for url in new_url:
        driver.get(url)
        time.sleep(loading_sec)
        page = driver.page_source
        soup = BeautifulSoup(page, "html.parser")
        img_url = soup.find("img", {"class": "be6sR"})["src"]
        new_img_url.append(img_url)

    return new_list, new_count_list, new_url, new_img_url


time.sleep(loading_sec)
driver.get(instargram_url + "/jejucleanboysclub")
time.sleep(loading_sec)

driver.find_element_by_xpath(
    '//*[@id="loginForm"]/div/div[1]/div/label/input'
).send_keys("jejucleanboysclub")
driver.find_element_by_xpath(
    '//*[@id="loginForm"]/div/div[2]/div/label/input'
).send_keys("jcbchouse")
driver.find_element_by_xpath('//*[@id="loginForm"]/div/div[3]/button').click()

time.sleep(loading_sec)

driver.find_element_by_xpath(
    '//*[@id="react-root"]/section/main/div/div/div/div/button'
).click()

time.sleep(loading_sec)
driver.get(instargram_url + "/jejucleanboysclub")
time.sleep(loading_sec)

last_height = driver.execute_script("return document.body.scrollHeight")
while True:
    # 끝까지 스크롤 다운
    driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
    time.sleep(SCROLL_PAUSE_SEC)
    # 스크롤 다운 후 스크롤 높이 다시 가져옴
    new_height = driver.execute_script("return document.body.scrollHeight")
    if new_height == last_height:
        break
    last_height = new_height

page = driver.page_source

soup = BeautifulSoup(page, "html.parser")
feed = soup.find_all("div", {"class": "v1Nh3"})

print(len(feed))
# print(feed[0].find("a")["href"])
feed_count = len(feed)
feed_url = []
feed_location = []
feed_tag_name = []
feed_tag_url = []
feed_content = []
feed_like = []
feed_comment = []

for href in feed:
    feed_url.append(instargram_url + href.find("a")["href"])

for url in feed_url:
    driver.get(url)
    time.sleep(loading_sec)
    page = driver.page_source
    soup = BeautifulSoup(page, "html.parser")
    location = soup.find("a", {"class": "O4GlU"}).text
    tag_name = soup.find_all("span", {"class": "eg3Fv"})
    content = soup.find("div", {"class": "C4VMK"}).text
    like = soup.find("button", {"class": "sqdOP"}).find("span").text
    comment = len(soup.find_all("ul", {"class": "Mr508"}))

    temp = []
    for name in tag_name:
        name = name.text
        temp.append(name)

    feed_location.append(location)
    feed_tag_name.append(temp)
    feed_content.append(content)
    feed_like.append(like)
    feed_comment.append(comment)


print(feed_url)
print(feed_location)
print(feed_tag_name)
print(feed_content)
print(feed_like)
print(feed_comment)

# data["feed_count"] = 0
# data["feed_location"] = []
# data["friend_profile"] = []
# data["feeds_date"] = []
# data["feeds_like"] = []
# data["feeds_comment"] = []

data["feed_count"] = feed_count

for name, count in location_list_setting(feed_location):
    data["feed_location"].append({"name": name, "count": count})

for name, count, url, img_url in friend_list_setting(feed_tag_name):
    data["friend_profile"].append(
        {"name": name, "count": count, "url": url, "img_url": img_url}
    )

print(data)

with open(file_path, "w") as outfile:
    json.dump(data, outfile)


driver.quit()