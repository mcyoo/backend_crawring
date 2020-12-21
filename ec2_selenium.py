# -*- coding: utf-8 -*-
from selenium.webdriver.chrome.options import Options
from selenium import webdriver
from bs4 import BeautifulSoup
import time
import json


loading_sec = 3
instargram_url = "https://www.instagram.com"
SCROLL_PAUSE_SEC = loading_sec
file_path = "/home/ec2-user/frontend/build/instagram_data.json"


now = time.localtime()
date = "%04d-%02d-%02d %02d:%02d:%02d" % (
    now.tm_year,
    now.tm_mon,
    now.tm_mday,
    now.tm_hour,
    now.tm_min,
    now.tm_sec,
)

data = {}
data["update_time"] = date
data["feed_count"] = 0
data["feed_location"] = []
data["friend_profile"] = []
data["feeds_date"] = []
data["feeds_like"] = []
data["feeds_comment"] = []

options = Options()
options.add_argument("--headless")
options.add_argument("window-size=1920,1080")
options.add_argument(
    "user-agent=Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/87.0.4280.88 Safari/537.36"
)


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
        new_url.append(instargram_url + "/" + tag_name)

    for url in new_url:
        driver.get(url)
        time.sleep(loading_sec)
        page = driver.page_source
        soup = BeautifulSoup(page, "html.parser")
        img_url = soup.find("div", {"class": "XjzKX"}).find("img")["src"]
        new_img_url.append(img_url)

    return new_list, new_count_list, new_url, new_img_url


# main
driver = webdriver.Chrome(options=options)
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

feed_list = []
last_height = driver.execute_script("return document.body.scrollHeight")
while True:

    driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
    time.sleep(SCROLL_PAUSE_SEC)

    page = driver.page_source
    soup = BeautifulSoup(page, "html.parser")
    feed = soup.find_all("div", {"class": "v1Nh3"})

    feed_list += feed
    print(" %02d건 수집함 >> 누적 데이터수: %05d" % (len(feed), len(feed_list)))

    new_height = driver.execute_script("return document.body.scrollHeight")
    if new_height == last_height:
        break
    last_height = new_height

new_list = []
for v in feed_list:
    if v not in new_list:
        new_list.append(v)

print(len(new_list))

feed = new_list

# print(feed[0].find("a")["href"])
feed_count = len(feed)
feed_url = []
feed_img = []
feed_location = []
feed_tag_name = []
feed_content = []
feed_like = []
feed_comment = []

for href in feed:
    feed_url.append(instargram_url + href.find("a")["href"])
    feed_img.append(href.find("img")["src"])

for url in feed_url:
    driver.get(url)
    time.sleep(loading_sec)
    page = driver.page_source
    soup = BeautifulSoup(page, "html.parser")
    location = soup.find("a", {"class": "O4GlU"}).text
    tag_name = soup.find_all("span", {"class": "eg3Fv"})
    content = soup.find("div", {"class": "C4VMK"}).text
    like = int(soup.find("div", {"class": "Nm9Fw"}).find("button").find("span").text)
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

# data
data["feed_count"] = feed_count

name, count = location_list_setting(feed_location)
for i in range(0, len(name)):
    data["feed_location"].append({"name": name[i], "count": count[i]})

name, count, url, img_url = friend_list_setting(feed_tag_name)
for i in range(0, len(name)):
    data["friend_profile"].append(
        {
            "name": name[i],
            "count": count[i],
            "url": url[i],
            "img_url": img_url[i],
        }
    )

for i in range(0, feed_count):
    data["feeds_date"].append(
        {
            "content": feed_content[i],
            "url": feed_url[i],
            "img_url": feed_img[i],
            "location": feed_location[i],
            "like_count": feed_like[i],
            "comment_count": feed_comment[i],
        }
    )

data["feeds_like"] = sorted(
    data["feeds_date"], key=lambda x: x["like_count"], reverse=True
)
data["feeds_comment"] = sorted(
    data["feeds_date"], key=lambda x: x["comment_count"], reverse=True
)
data["friend_profile"] = sorted(
    data["friend_profile"], key=lambda x: x["count"], reverse=True
)

with open(file_path, "w") as outfile:
    json.dump(data, outfile)


driver.quit()