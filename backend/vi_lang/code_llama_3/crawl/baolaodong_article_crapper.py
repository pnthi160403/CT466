import subprocess
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from bs4 import BeautifulSoup
import csv
import re
import pandas as pd
import os
import time
import random

# Constants
# tags = ["xa-hoi", "cong-nghe", "giao-duc"]
# tags = ["xa-hoi", "kinh-doanh", "the-gioi", "thoi-su", "the-thao", "van-hoa-giai-tri", "bat-dong-san", "cong-nghe", "viec-lam", "giao-duc"]
# tags = ["kinh-doanh", "the-gioi", "thoi-su", "the-thao", "van-hoa-giai-tri", "bat-dong-san"]
# tags = ["giao-thong", "moi-truong", "the-gioi-so", "chuyen-nha-minh"]
# tags = ["thi-truong", "doanh-nghiep-doanh-nhan", "tu-lieu", "dinh-duong-am-thuc", "lam-dep", "cac-loai-benh"]
tags = ["tlv-tin-hoat-dong", "the-gioi", "gia-dinh-hon-nhan"]
pattern_url = "https://laodong.vn/{tag}?page={page}"
pattern_prefix = "https://laodong.vn/{tag}/"
file_results = 'baolaodong_articles.csv'  # link,tag,content,summary
file_articles_links_not_found = 'baolaodong_articles_links_not_found.csv'
file_pages_links_not_found = 'baolaodong_pages_links_not_found.csv'
class_summary = 'chappeau'  # div tag
id_content = 'gallery-ctt'  # div tag
file_epoch = "epoch.txt" # epoch: [page, tag_index]
total_links_collected = 0
wait_time = 2
time_out = 5
used_page_links = []

if not os.path.exists(file_results):
    with open(file_results, mode='w', newline='', encoding='utf-8') as file:
        writer = csv.writer(file)
        writer.writerow(["link", "tag", "content", "summary"])
else:
    df = pd.read_csv(file_results)
    total_links_collected = df.shape[0]
    for i in range(df.shape[0]):
        used_page_links.append(df.iloc[i]['link'])
    
if not os.path.exists(file_articles_links_not_found):
    with open(file_articles_links_not_found, mode='w', encoding='utf-8') as file:
        writer = csv.writer(file)
        writer.writerow(['tag', 'url'])

if not os.path.exists(file_pages_links_not_found):
    with open(file_pages_links_not_found, mode='w', encoding='utf-8') as file:
        writer = csv.writer(file)
        writer.writerow(['tag', 'url'])

def update_epoch(page, tag_index):
    if tag_index == len(tags) - 1:
        tag_index = 0
        page += 1
    else:
        tag_index += 1
        
    with open(file_epoch, 'w') as file:
        file.write(f"{page} {tag_index}")
        
    return page, tag_index

def restart_script(page, tag_index):
    update_epoch(page, tag_index)
    print("Đã hoàn thành quá trình thu thập dữ liệu, sẽ khởi động lại script sau 1 giây...")
    time.sleep(1)
    os.system('clear')
    print("Đang khởi động lại script...")
    subprocess.Popen(['python3', 'baolaodong_article_crapper.py'])
    exit()

def process_html_content(tag_content):
    desired_tags = [
        "h1", "h2", "h3", "h4", "h5", "h6",
        "p", "a" , "strong", "em",
        "b", "i", "small", "mark", "sub",
        "sup", "ul", "ol", "li", "span", 'div'
    ]

    soup = BeautifulSoup(tag_content, "html.parser")

    for element in soup.find_all(True):
        if element.name not in desired_tags:
            element.decompose()

    text = soup.get_text(separator=" ")
    text = re.sub(r'[^\w\s,.ÀÁÂÃÈÉÊÌÍÒÓÔÕÙÚĂĐĨŨƠàáâãèéêìíòóôõùúăđĩũơƯăạảấầẩẫậắằẳẵặẹẻẽềểếễệỉịọỏốồổỗộớờởỡợụủứừửữựỳỵỷỹ]', '', text)
    text = re.sub(
        r'[\U0001F600-\U0001F64F'
        r'\U0001F300-\U0001F5FF'
        r'\U0001F680-\U0001F6FF'
        r'\U0001F700-\U0001F77F'
        r'\U0001F780-\U0001F7FF'
        r'\U0001F800-\U0001F8FF'
        r'\U0001F900-\U0001F9FF'
        r'\U0001FA00-\U0001FA6F'
        r'\U00002700-\U000027BF'
        r'\U00002000-\U0000201F'
        r'\U00002500-\U0000257F'
        r'\U00002760-\U0000277F'
        r'\U0001F1E6-\U0001F1FF'
        r'\U0001F9C0-\U0001F9FF'
        r']+', '', text)

    text = re.sub(r'\s+', ' ', text).strip()

    for h_tag in desired_tags[:6]:
        for element in soup.find_all(h_tag):
            if not element.get_text().strip().endswith('.'):
                element.string = element.get_text().strip() + '.'

    return text

try:
    print('Đang cài đặt ChromeDriver...')
    service = Service('/usr/bin/chromedriver')
    options = webdriver.ChromeOptions()
    options.add_argument("--headless")
    options.add_argument("--disable-gpu")
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")
    options.add_argument("--incognito")
    driver = webdriver.Chrome(service=service, options=options)
except Exception as e:
    print(f'Có lỗi xảy ra khi cài đặt ChromeDriver: {e}')
    print("Đang khởi động lại script sau 3 giây...")
    time.sleep(3)
    os.system('clear')
    print("Đang khởi động lại script...")
    subprocess.Popen(['python3', 'baolaodong_article_crapper.py'])
        
def try_get_links(page, tag):
    url = pattern_url.format(tag=tag, page=page)
    print(f'Đang lấy link từ trang {url}...')
    try:
        driver.set_page_load_timeout(time_out)
        driver.get(url)
        WebDriverWait(driver, wait_time).until(EC.presence_of_element_located((By.CLASS_NAME, 'link-title')))
        html_content = driver.page_source
        soup = BeautifulSoup(html_content, 'html.parser')
        links = soup.find_all('a', class_='link-title')
        filtered_links = [link['href'] for link in links if link['href'].startswith(pattern_prefix.format(tag=tag))]
        print(f'Đã lấy được {len(filtered_links)} link từ trang {url}')
        return filtered_links
    except Exception as e:
        print(f'Có lỗi xảy ra khi lấy trang {url}: {e}')
        return None
    
def try_get_content(link):
    print('Đang tải', link)
    try:
        driver.set_page_load_timeout(time_out)
        driver.get(link)
        WebDriverWait(driver, wait_time).until(EC.presence_of_element_located((By.ID, id_content)))

        html_content = driver.page_source
        soup = BeautifulSoup(html_content, 'html.parser')

        content_element = soup.find("div", id=id_content)
        summary_element = soup.find("div", class_=class_summary)

        if content_element is None or summary_element is None:
            print(f'Không tìm thấy nội dung hoặc tóm tắt cho link {link}')
            return None, None

        content = process_html_content(str(content_element))
        summary = process_html_content(str(summary_element))

        print('Đã tải xong', link)
        return content, summary
    except Exception as e:
        print(f'Có lỗi xảy ra khi lấy trang {link}: {e}')
        return None, None
    
start_time = time.time()
    
def get_time():
    elapsed_time = time.time() - start_time
    
    hours = int(elapsed_time // 3600)
    minutes = int((elapsed_time % 3600) // 60)
    seconds = int(elapsed_time % 60)

    return f"{hours}:{minutes}:{seconds}"

if not os.path.exists(file_epoch):
    with open(file_epoch, 'w') as file:
        file.write("2 0")

with open(file_epoch, 'r') as file:
    epoch = file.read().split()
    page = int(epoch[0])
    tag_index = int(epoch[1])      

cnt = 0

while total_links_collected <= 200000:
    # get page content
    tag = tags[tag_index]
    url = pattern_url.format(tag=tag, page=page)
    
    filtered_links = try_get_links(page, tag)
    if filtered_links is None:
        with open(file_pages_links_not_found, mode='a', encoding='utf-8') as file:
            writer = csv.writer(file)
            writer.writerow([tag, url])
        restart_script(page, tag_index)    
    # get article content
    for i in range(len(filtered_links)):
        link = filtered_links[i]
        if link in used_page_links:
            continue
        content, summary = try_get_content(link)
        if content is None or summary is None or content == '' or summary == '':
            if i < 2:
                with open(file_articles_links_not_found, mode='a', encoding='utf-8') as file:
                    writer = csv.writer(file)
                    writer.writerow([tag, link])
            else:
                for j in range(i, len(filtered_links)):
                    with open(file_articles_links_not_found, mode='a', encoding='utf-8') as file:
                        writer = csv.writer(file)
                        writer.writerow([tag, filtered_links[j]])
                restart_script(page, tag_index)
        else:
            with open(file_results, mode='a', newline='', encoding='utf-8') as file:
                writer = csv.writer(file)
                writer.writerow([link, tag, content, summary])
                total_links_collected += 1
                used_page_links.append(link)
                cnt += 1
                print("======================================================================")
                print("SỐ BÀI BÁO ĐÃ THU THẬP: ", total_links_collected)
                print("TIME ELAPSED: ", get_time())
            print()

    page, tag_index = update_epoch(page, tag_index)