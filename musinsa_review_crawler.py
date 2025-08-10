from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time
import pandas as pd
from bs4 import BeautifulSoup
import json
from datetime import datetime, timedelta
import re

# CSV 파일에서 상품 정보 읽기
products_df = pd.read_csv("musinsa_onepiece_all.csv")
print(f"총 {len(products_df)}개 상품 발견")

# 리뷰 데이터를 저장할 리스트
all_reviews = []

# Chrome 옵션 설정
options = Options()
options.add_argument('--disable-gpu')
options.add_argument('--window-size=1920,1080')
options.add_argument('--headless')  # 백그라운드 실행

driver = webdriver.Chrome(options=options)

def parse_date(date_str):
    """날짜 문자열을 datetime 객체로 변환"""
    try:
        # "2024.01.15", "24.01.15", "1일 전", "3시간 전" 등 다양한 형식 처리
        if '전' in date_str:
            if '시간' in date_str:
                hours = int(re.search(r'(\d+)', date_str).group(1))
                return datetime.now() - timedelta(hours=hours)
            elif '일' in date_str:
                days = int(re.search(r'(\d+)', date_str).group(1))
                return datetime.now() - timedelta(days=days)
            elif '주' in date_str:
                weeks = int(re.search(r'(\d+)', date_str).group(1))
                return datetime.now() - timedelta(weeks=weeks)
            elif '개월' in date_str or '달' in date_str:
                months = int(re.search(r'(\d+)', date_str).group(1))
                return datetime.now() - timedelta(days=months*30)
        else:
            # 날짜 형식 파싱
            date_str = date_str.replace('.', '-').replace('/', '-')
            if len(date_str.split('-')[0]) == 2:  # 연도가 2자리
                date_str = '20' + date_str
            return datetime.strptime(date_str.split()[0], '%Y-%m-%d')
    except:
        return datetime.now()

def get_product_reviews(product_url, product_id, brand, max_reviews=100, months_limit=3):
    """특정 상품의 리뷰를 수집하는 함수"""
    reviews = []
    
    try:
        driver.get(product_url)
        time.sleep(5)  # 페이지 로딩 대기 시간 증가
        
        # 페이지 아래로 스크롤 (리뷰 섹션 로드)
        for _ in range(3):
            driver.execute_script("window.scrollBy(0, 1000);")
            time.sleep(1)
        
        
        # 리뷰 탭 클릭 시도 - 다양한 선택자 시도
        review_clicked = False
        
        # 방법 1: 텍스트로 찾기
        try:
            buttons = driver.find_elements(By.TAG_NAME, "button")
            for button in buttons:
                if "후기" in button.text or "리뷰" in button.text or "Review" in button.text.lower():
                    button.click()
                    review_clicked = True
                    time.sleep(3)
                    break
        except:
            pass
        
        # 방법 2: 탭 리스트에서 찾기
        if not review_clicked:
            try:
                tabs = driver.find_elements(By.CSS_SELECTOR, "div[role='tab'], button[role='tab'], li[role='tab']")
                for tab in tabs:
                    if "후기" in tab.text or "리뷰" in tab.text:
                        tab.click()
                        review_clicked = True
                        time.sleep(3)
                        break
            except:
                pass
        
        if not review_clicked:
            print(f"리뷰 탭을 찾을 수 없음: {product_id}")
        
        # 3개월 전 날짜 계산
        three_months_ago = datetime.now() - timedelta(days=months_limit * 30)
        
        page_count = 0
        stop_collecting = False
        
        while not stop_collecting and len(reviews) < max_reviews:
            # 현재 페이지의 HTML 파싱
            soup = BeautifulSoup(driver.page_source, "html.parser")
            
            # 리뷰 요소 찾기 (다양한 선택자 시도)
            review_elements = []
            
            # 무신사의 일반적인 리뷰 선택자들
            selectors = [
                "div[class*='review-list-item__Container']",  # 실제 무신사 리뷰 선택자
                "div[class*='review-list']",
                "div[class*='review-item']",
                "div[class*='ReviewItem']",
                "div[class*='review_list']",
                "li[class*='review']",
                "article[class*='review']",
                "div.review",
                "div[data-testid*='review']"
            ]
            
            for selector in selectors:
                review_elements = soup.select(selector)
                if review_elements:
                    # print(f"리뷰 요소 발견: {selector} ({len(review_elements)}개)")
                    break
            
            if not review_elements:
                # 디버깅: 페이지에 어떤 요소들이 있는지 확인
                all_divs = soup.find_all("div", class_=True)
                review_related = [div for div in all_divs if 'review' in str(div.get('class', '')).lower() or '후기' in div.get_text()]
                if review_related:
                    print(f"리뷰 관련 요소 {len(review_related)}개 발견, 구조 분석 필요")
                else:
                    print(f"리뷰를 찾을 수 없음: {product_id}")
                break
            
            # 각 리뷰에서 정보 추출
            for review in review_elements:
                review_data = {
                    "product_id": product_id,
                    "brand": brand,
                    "product_url": product_url
                }
                
                # 전체 텍스트 먼저 가져오기
                review_text = review.get_text(separator=" ", strip=True)
                
                # 평점 추출 - svg 아이콘 개수나 텍스트에서 찾기
                import re
                rating_icons = review.select("svg[class*='star'], svg[class*='Star'], span[class*='star']")
                if rating_icons:
                    review_data["rating"] = str(len(rating_icons))
                else:
                    # 텍스트에서 평점 찾기
                    rating_match = re.search(r'(\d+)점|별(\d+)|★(\d+)|평점.*?(\d+)', review_text)
                    if rating_match:
                        for group in rating_match.groups():
                            if group:
                                review_data["rating"] = group
                                break
                    else:
                        review_data["rating"] = ""
                
                # 리뷰 텍스트 추출 - 더 넓은 범위로 찾기
                text_elem = review.select_one("div[class*='Content'], div[class*='content'], div[class*='Text'], div[class*='text'], p")
                if text_elem:
                    review_data["text"] = text_elem.get_text(strip=True)
                else:
                    review_data["text"] = review_text[:500]  # 전체 텍스트에서 최대 500자
                
                # 작성자 추출
                author_elem = review.select_one("span[class*='user'], span[class*='name'], div[class*='writer']")
                if author_elem:
                    review_data["author"] = author_elem.get_text(strip=True)
                else:
                    review_data["author"] = ""
                
                # 작성일 추출
                date_elem = review.select_one("span[class*='date'], span[class*='time'], time")
                if date_elem:
                    date_str = date_elem.get_text(strip=True)
                    review_data["date"] = date_str
                    
                    # 날짜 확인하여 3개월 이상 된 리뷰면 중단
                    review_date = parse_date(date_str)
                    if review_date < three_months_ago:
                        stop_collecting = True
                        break
                else:
                    review_data["date"] = ""
                
                # 옵션 정보 추출
                option_elem = review.select_one("span[class*='option'], div[class*='option']")
                if option_elem:
                    review_data["option"] = option_elem.get_text(strip=True)
                else:
                    review_data["option"] = ""
                
                if review_data["text"]:  # 텍스트가 있는 경우만 저장
                    reviews.append(review_data)
                    
                    # 최대 리뷰 수에 도달하면 중단
                    if len(reviews) >= max_reviews:
                        stop_collecting = True
                        break
            
            # 다음 페이지로 이동
            try:
                next_button = driver.find_element(By.XPATH, "//button[contains(@class, 'next') or contains(text(), '다음')]")
                if next_button.is_enabled():
                    next_button.click()
                    time.sleep(2)
                    page_count += 1
                else:
                    break
            except:
                # 다음 페이지 버튼을 찾을 수 없으면 종료
                break
        
        print(f"상품 {product_id}: {len(reviews)}개 리뷰 수집 완료")
        
    except Exception as e:
        print(f"에러 발생 (상품 {product_id}): {str(e)}")
    
    return reviews

# 상품별로 리뷰 수집 (처음 20개 상품)
test_limit = 20  # 처음 20개 상품의 리뷰 수집
for idx, row in products_df.head(test_limit).iterrows():
    print(f"\n진행중: {idx+1}/{min(test_limit, len(products_df))} - {row['브랜드']} (ID: {row['상품ID']})")
    
    reviews = get_product_reviews(
        row['상품링크'], 
        row['상품ID'],
        row['브랜드']
    )
    
    all_reviews.extend(reviews)
    
    # 중간 저장 (매 상품마다)
    if all_reviews:
        pd.DataFrame(all_reviews).to_csv("musinsa_reviews.csv", index=False, encoding="utf-8-sig")
    
    # 과도한 요청 방지
    time.sleep(2)

# 최종 저장
if all_reviews:
    reviews_df = pd.DataFrame(all_reviews)
    reviews_df.to_csv("musinsa_reviews.csv", index=False, encoding="utf-8-sig")
    print(f"\n총 {len(all_reviews)}개 리뷰 수집 완료")
    print("파일 저장: musinsa_reviews.csv")
else:
    print("\n수집된 리뷰가 없습니다.")

driver.quit()