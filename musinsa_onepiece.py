from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.chrome.options import Options
import time
import pandas as pd
from bs4 import BeautifulSoup

options = Options()
options.add_argument('--disable-gpu')
options.add_argument('--window-size=1920,1080')
# options.add_argument('--headless')  # 창 안 띄움

driver = webdriver.Chrome(options=options)
driver.get("https://www.musinsa.com/category/100?gf=A")
time.sleep(10)  # 페이지 로딩 대기 시간 증가

SCROLL_PAUSE_TIME = 5
MAX_SCROLL = 5   # 5회까지만 스크롤 (테스트용)

all_results = []
seen_links = set()
scroll_count = 0

def parse_and_add_new_items():
    soup = BeautifulSoup(driver.page_source, "html.parser")
    
    # 무신사 페이지의 상품 링크 찾기
    cards = soup.select("a.gtm-view-item-list")
    
    print(f"Found {len(cards)} product cards")
    
    new_items = 0
    for idx, item in enumerate(cards):
        # item 자체가 a 태그임
        product_link = item.get("href", "")
        if not product_link:
            continue
        
        if product_link in seen_links:
            continue
        seen_links.add(product_link)
        
        # 이미지 찾기
        img_tag = item.find("img")
        img_url = ""
        if img_tag:
            img_url = img_tag.get("src", "")
            if not img_url:
                img_url = img_tag.get("data-src", "")
        
        # 데이터 속성에서 정보 추출
        brand = item.get("data-item-brand", "")
        price = item.get("data-price", "")
        original_price = item.get("data-original-price", "")
        discount_rate = item.get("data-discount-rate", "")
        item_id = item.get("data-item-id", "")
        
        # 결과 저장
        all_results.append({
            "URL": img_url,
            "브랜드": brand,
            "가격": price,
            "원가": original_price,
            "할인율": discount_rate,
            "상품ID": item_id,
            "상품링크": product_link,
        })
        new_items += 1
    return new_items

while scroll_count < MAX_SCROLL:
    for _ in range(10):
        driver.find_element(By.TAG_NAME, 'body').send_keys(Keys.PAGE_DOWN)
        time.sleep(0.3)
    time.sleep(SCROLL_PAUSE_TIME)
    new_count = parse_and_add_new_items()
    scroll_count += 1
    if all_results:
        pd.DataFrame(all_results).to_csv("musinsa_onepiece_all.csv", index=False, encoding="utf-8-sig")
    print(f"{scroll_count}회 스크롤, 누적 상품 수: {len(all_results)} (신규 {new_count}개)")
    if new_count == 0:
        print("더 이상 신규 상품이 없습니다. 중단합니다.")
        break

print("최종 누적 상품 수:", len(all_results))
driver.quit()