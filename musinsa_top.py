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
options.add_argument('--headless')  # headless 모드 ON

driver = webdriver.Chrome(options=options)
driver.get("https://www.musinsa.com/category/001?gf=A")
time.sleep(2)

SCROLL_PAUSE_TIME = 5
MAX_SCROLL = 500   # 500회까지만 스크롤

# 누적 상품 링크 set
all_links = set()
scroll_count = 0
all_results = []
seen_links = set()

def get_product_cards():
    # 스크롤 직후 페이지 전체 파싱
    soup = BeautifulSoup(driver.page_source, "html.parser")
    cards = soup.select("div.sc-igtioI.eSJwIO")
    new_items = 0
    for item in cards:
        a_tag = item.select_one("a.gtm-view-item-list, a.gtm-select-item")
        img_tag = item.select_one("img")
        brand_tag = item.select_one('a[aria-label$="샵으로 이동"] span')
        name_tag = item.select_one('a[aria-label$="상품상세로 이동"] span')
        price_tag = item.select_one("div.sc-hKDTPf span.text-body_13px_semi.text-red + span.text-body_13px_semi")
        discount_tag = item.select_one("span.text-body_13px_semi.text-red")
        if a_tag and img_tag and brand_tag and name_tag:
            product_link = a_tag["href"]
            if not product_link.startswith("http"):
                product_link = "https://www.musinsa.com" + product_link
            if product_link in seen_links:
                continue
            seen_links.add(product_link)
            img_url = img_tag["src"]
            brand = brand_tag.text.strip()
            product_name = name_tag.text.strip()
            price = price_tag.text.strip() if price_tag else ""
            discount = discount_tag.text.strip() if discount_tag else ""
            all_results.append({
                "URL": img_url,
                "TEXT": f"{brand} {product_name}",
                "브랜드": brand,
                "상품명": product_name,
                "상품링크": product_link,
                "가격": price,
                "할인율": discount,
            })
            new_items += 1
    return new_items

while scroll_count < MAX_SCROLL:
    for _ in range(10):
        driver.find_element(By.TAG_NAME, 'body').send_keys(Keys.PAGE_DOWN)
        time.sleep(0.3)
    time.sleep(SCROLL_PAUSE_TIME)

    # 스크롤 후 정보 누적 파싱 & 저장
    new_count = get_product_cards()
    scroll_count += 1

    # csv 즉시 저장 (중복제거 누적)
    pd.DataFrame(all_results).to_csv("musinsa_tops_all.csv", index=False, encoding="utf-8-sig")
    print(f"{scroll_count}회 스크롤, 누적 상품 수: {len(all_results)} (신규 {new_count}개)")

    if new_count == 0:
        print("더 이상 신규 상품이 없습니다. 중단합니다.")
        break

print("최종 누적 상품 수:", len(all_results))
driver.quit()