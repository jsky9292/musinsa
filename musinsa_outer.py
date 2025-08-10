from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.chrome.options import Options
import time
from bs4 import BeautifulSoup
import pandas as pd

options = Options()
options.add_argument('--disable-gpu')
options.add_argument('--window-size=1920,1080')
options.add_argument('--headless')

driver = webdriver.Chrome(options=options)
driver.get("https://www.musinsa.com/category/002?gf=A")
time.sleep(2)

SCROLL_PAUSE_TIME = 3
MAX_SCROLL = 500

seen_links = set()
results = []
scroll_count = 0

def parse_and_add_new_items():
    soup = BeautifulSoup(driver.page_source, "html.parser")
    added = 0
    for card in soup.select("div.sc-igtioI.eSJwIO"):
        # 메인 링크와 썸네일
        a_tag = card.select_one("a.gtm-view-item-list, a.gtm-select-item")
        link = a_tag['href'] if a_tag else ""
        if link and not link.startswith("http"):
            link = "https://www.musinsa.com" + link
        if not link or link in seen_links:
            continue
        seen_links.add(link)

        img_tag = card.select_one("img")
        img_url = img_tag["src"] if img_tag else ""

        # 브랜드명
        brand_tag = card.select_one('a[aria-label$="샵으로 이동"] span, span.text-etc_11px_semibold')
        brand = brand_tag.text.strip() if brand_tag else ""

        # 상품명
        name_tag = card.select_one('a[aria-label$="상품상세로 이동"] span, span.text-body_13px_reg')
        product_name = name_tag.text.strip() if name_tag else ""

        # 할인/가격 (최신 무신사 스타일 대응)
        discount_tag = card.select_one('span.text-body_13px_semi.text-red, span.text-body_13px_semi.sc-gwsNht.text-red')
        discount = discount_tag.text.strip() if discount_tag else ""
        price_tag = card.select_one('span[aria-label], span.text-body_13px_semi.sc-gwsNht')
        price = price_tag['aria-label'] if price_tag and price_tag.has_attr('aria-label') else (price_tag.text.strip() if price_tag else "")

        # 평점
        rating_tag = card.select_one('span.text-etc_11px_reg.text-yellow')
        rating = rating_tag.text.strip() if rating_tag else ""

        # 리뷰수
        review_tag = card.select_one('span.text-etc_11px_reg.text-yellow+span')
        review = review_tag.text.strip() if review_tag else ""

        results.append({
            "상품링크": link,
            "이미지": img_url,
            "브랜드": brand,
            "상품명": product_name,
            "할인율": discount,
            "가격": price,
            "평점": rating,
            "리뷰수": review
        })
        added += 1
    return added

for i in range(MAX_SCROLL):
    for _ in range(10):
        driver.find_element(By.TAG_NAME, 'body').send_keys(Keys.PAGE_DOWN)
        time.sleep(0.2)
    time.sleep(SCROLL_PAUSE_TIME)
    new_count = parse_and_add_new_items()
    scroll_count += 1
    print(f"{scroll_count}회 스크롤, 누적 상품 개수: {len(results)} (새로 추가: {new_count})")

    # ⬇️ 매번 저장! (중복 덮어쓰기)
    df = pd.DataFrame(results)
    df.to_csv("musinsa_outer_all.csv", index=False, encoding="utf-8-sig")

    if new_count == 0 and i > 3:
        print("더 이상 로드되는 상품이 없습니다.")
        break

print("최종 누적 상품 수:", len(df))
driver.quit()