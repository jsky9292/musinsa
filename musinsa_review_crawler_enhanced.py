from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, NoSuchElementException
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
options.add_argument('--disable-blink-features=AutomationControlled')
options.add_experimental_option("excludeSwitches", ["enable-automation"])
options.add_experimental_option('useAutomationExtension', False)
options.add_argument('--headless')  # 백그라운드 실행

driver = webdriver.Chrome(options=options)
driver.execute_script("Object.defineProperty(navigator, 'webdriver', {get: () => undefined})")

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

def wait_for_element(driver, selector, timeout=10):
    """요소가 나타날 때까지 대기"""
    try:
        element = WebDriverWait(driver, timeout).until(
            EC.presence_of_element_located((By.CSS_SELECTOR, selector))
        )
        return element
    except TimeoutException:
        return None

def scroll_to_reviews(driver):
    """리뷰 섹션까지 스크롤"""
    try:
        # 여러 방법으로 리뷰 섹션 찾기
        review_section = None
        
        # 방법 1: 리뷰 탭 버튼 찾기
        for selector in ["button[class*='review']", "button[class*='Review']", 
                        "div[class*='review-tab']", "li[class*='review-tab']"]:
            elements = driver.find_elements(By.CSS_SELECTOR, selector)
            if elements:
                review_section = elements[0]
                break
        
        # 방법 2: 텍스트로 찾기
        if not review_section:
            buttons = driver.find_elements(By.TAG_NAME, "button")
            for button in buttons:
                if '후기' in button.text or '리뷰' in button.text:
                    review_section = button
                    break
        
        if review_section:
            driver.execute_script("arguments[0].scrollIntoView(true);", review_section)
            time.sleep(1)
            return review_section
        
        # 페이지 중간으로 스크롤
        driver.execute_script("window.scrollTo(0, document.body.scrollHeight * 0.6);")
        time.sleep(1)
        
    except Exception as e:
        print(f"스크롤 에러: {e}")
    
    return None

def click_review_tab(driver):
    """리뷰 탭 클릭"""
    try:
        # 리뷰 섹션으로 스크롤
        review_section = scroll_to_reviews(driver)
        
        if review_section:
            try:
                review_section.click()
                time.sleep(2)
                return True
            except:
                driver.execute_script("arguments[0].click();", review_section)
                time.sleep(2)
                return True
        
        # 다른 방법으로 리뷰 탭 찾기
        for text in ['후기', '리뷰', 'Review', 'REVIEW']:
            elements = driver.find_elements(By.XPATH, f"//*[contains(text(), '{text}')]")
            for elem in elements:
                if elem.tag_name in ['button', 'a', 'li', 'div']:
                    try:
                        elem.click()
                        time.sleep(2)
                        return True
                    except:
                        continue
        
        return False
        
    except Exception as e:
        print(f"리뷰 탭 클릭 에러: {e}")
        return False

def get_review_pages(driver):
    """리뷰 페이지 수 확인"""
    try:
        # 페이지네이션 찾기
        pagination_selectors = [
            "div[class*='pagination']",
            "ul[class*='pagination']",
            "div[class*='paging']",
            "div[class*='page-list']"
        ]
        
        for selector in pagination_selectors:
            elements = driver.find_elements(By.CSS_SELECTOR, selector)
            if elements:
                # 페이지 번호 추출
                page_numbers = re.findall(r'\d+', elements[0].text)
                if page_numbers:
                    return max(map(int, page_numbers))
        
        return 1
        
    except Exception as e:
        print(f"페이지 수 확인 에러: {e}")
        return 1

def click_next_page(driver, page_num):
    """다음 페이지로 이동"""
    try:
        # 방법 1: 페이지 번호 직접 클릭
        page_buttons = driver.find_elements(By.XPATH, f"//button[text()='{page_num}'] | //a[text()='{page_num}']")
        if page_buttons:
            page_buttons[0].click()
            time.sleep(2)
            return True
        
        # 방법 2: 다음 버튼 클릭
        next_selectors = [
            "button[class*='next']",
            "a[class*='next']",
            "button[aria-label*='다음']",
            "button[title*='다음']"
        ]
        
        for selector in next_selectors:
            elements = driver.find_elements(By.CSS_SELECTOR, selector)
            if elements and elements[0].is_enabled():
                elements[0].click()
                time.sleep(2)
                return True
        
        # 방법 3: 화살표 아이콘 찾기
        arrow_buttons = driver.find_elements(By.XPATH, "//button[contains(@class, 'arrow')] | //a[contains(@class, 'arrow')]")
        for button in arrow_buttons:
            if '>' in button.text or '→' in button.text:
                button.click()
                time.sleep(2)
                return True
        
        return False
        
    except Exception as e:
        print(f"페이지 이동 에러: {e}")
        return False

def extract_review_data(review_elem, product_id, brand):
    """리뷰 요소에서 데이터 추출"""
    review_data = {
        "product_id": product_id,
        "brand": brand
    }
    
    try:
        # 전체 텍스트
        review_text = review_elem.get_text(separator=" ", strip=True)
        
        # 리뷰 내용 추출 - 더 다양한 선택자
        content_selectors = [
            "div[class*='content']",
            "div[class*='Content']",
            "div[class*='text']",
            "div[class*='Text']",
            "p[class*='review']",
            "span[class*='review']",
            "div[class*='body']"
        ]
        
        content = ""
        for selector in content_selectors:
            elem = review_elem.select_one(selector)
            if elem:
                content = elem.get_text(strip=True)
                if len(content) > 10:  # 의미있는 내용인지 확인
                    break
        
        review_data["text"] = content if content else review_text[:500]
        
        # 평점 추출
        rating = ""
        # 별점 아이콘 개수
        star_icons = review_elem.select("svg[class*='star'], svg[class*='Star'], span[class*='star-fill']")
        if star_icons:
            rating = str(len([s for s in star_icons if 'fill' in str(s.get('class', ''))]))
        
        # 숫자로 된 평점
        if not rating:
            rating_elem = review_elem.select_one("span[class*='rating'], div[class*='score']")
            if rating_elem:
                rating_match = re.search(r'(\d+)', rating_elem.get_text())
                if rating_match:
                    rating = rating_match.group(1)
        
        review_data["rating"] = rating
        
        # 작성자 추출
        author_selectors = [
            "span[class*='user']",
            "span[class*='name']",
            "div[class*='writer']",
            "span[class*='author']",
            "div[class*='nickname']"
        ]
        
        author = ""
        for selector in author_selectors:
            elem = review_elem.select_one(selector)
            if elem:
                author = elem.get_text(strip=True)
                if author and len(author) > 1:
                    break
        
        review_data["author"] = author
        
        # 작성일 추출
        date_selectors = [
            "span[class*='date']",
            "span[class*='time']",
            "time",
            "div[class*='date']",
            "span[class*='created']"
        ]
        
        date = ""
        for selector in date_selectors:
            elem = review_elem.select_one(selector)
            if elem:
                date = elem.get_text(strip=True)
                if date:
                    break
        
        review_data["date"] = date
        
        # 구매 옵션 추출
        option_selectors = [
            "span[class*='option']",
            "div[class*='option']",
            "span[class*='variant']",
            "div[class*='purchase']"
        ]
        
        option = ""
        for selector in option_selectors:
            elem = review_elem.select_one(selector)
            if elem:
                option = elem.get_text(strip=True)
                if option:
                    break
        
        review_data["option"] = option
        
        # 도움이 됨 수
        helpful_elem = review_elem.select_one("span[class*='helpful'], button[class*='like']")
        if helpful_elem:
            helpful_match = re.search(r'(\d+)', helpful_elem.get_text())
            if helpful_match:
                review_data["helpful_count"] = helpful_match.group(1)
        else:
            review_data["helpful_count"] = "0"
        
        # 이미지 유무
        has_image = len(review_elem.select("img[class*='review'], img[alt*='리뷰']")) > 0
        review_data["has_image"] = "Y" if has_image else "N"
        
    except Exception as e:
        print(f"리뷰 데이터 추출 에러: {e}")
    
    return review_data

def get_product_reviews_enhanced(product_url, product_id, brand, max_pages=5, max_reviews=100):
    """개선된 리뷰 수집 함수"""
    reviews = []
    
    try:
        # 페이지 로드
        driver.get(product_url)
        time.sleep(5)
        
        print(f"  상품 페이지 로드 완료: {product_id}")
        
        # 리뷰 탭 클릭
        review_tab_clicked = click_review_tab(driver)
        if not review_tab_clicked:
            print(f"  리뷰 탭을 찾을 수 없음: {product_id}")
        
        # 총 페이지 수 확인
        total_pages = get_review_pages(driver)
        pages_to_collect = min(max_pages, total_pages)
        print(f"  총 {total_pages}페이지 중 {pages_to_collect}페이지 수집 예정")
        
        # 페이지별로 리뷰 수집
        for page_num in range(1, pages_to_collect + 1):
            print(f"    {page_num}/{pages_to_collect} 페이지 수집 중...")
            
            # 현재 페이지 HTML 파싱
            soup = BeautifulSoup(driver.page_source, "html.parser")
            
            # 리뷰 요소 찾기
            review_selectors = [
                "div[class*='review-list-item']",
                "div[class*='review-item']",
                "li[class*='review']",
                "article[class*='review']",
                "div[class*='ReviewItem']"
            ]
            
            review_elements = []
            for selector in review_selectors:
                elements = soup.select(selector)
                if elements:
                    review_elements = elements
                    print(f"      {len(elements)}개 리뷰 발견")
                    break
            
            # 각 리뷰 데이터 추출
            for review_elem in review_elements:
                review_data = extract_review_data(review_elem, product_id, brand)
                
                # 유효한 리뷰인지 확인
                if review_data.get("text") and len(review_data["text"]) > 10:
                    review_data["page_number"] = page_num
                    review_data["product_url"] = product_url
                    reviews.append(review_data)
                    
                    if len(reviews) >= max_reviews:
                        print(f"    최대 리뷰 수({max_reviews})에 도달")
                        break
            
            # 최대 리뷰 수에 도달하면 중단
            if len(reviews) >= max_reviews:
                break
            
            # 다음 페이지로 이동
            if page_num < pages_to_collect:
                if not click_next_page(driver, page_num + 1):
                    print(f"    {page_num + 1}페이지로 이동 실패")
                    break
                
                # 페이지 로딩 대기
                time.sleep(3)
        
        print(f"  상품 {product_id}: 총 {len(reviews)}개 리뷰 수집 완료")
        
    except Exception as e:
        print(f"  에러 발생 (상품 {product_id}): {str(e)}")
    
    return reviews

# 브랜드별 우선순위 설정 (리뷰가 많은 브랜드 우선)
brand_priority = products_df['브랜드'].value_counts().head(30).index.tolist()

# 우선순위 브랜드의 상품만 선택 (테스트를 위해 5개만)
priority_products = products_df[products_df['브랜드'].isin(brand_priority)].head(5)

print(f"\n우선순위 브랜드 {len(brand_priority)}개의 상품 {len(priority_products)}개 리뷰 수집 시작")
print(f"수집 브랜드: {', '.join(brand_priority[:10])}...")

# 상품별로 리뷰 수집
for idx, row in priority_products.iterrows():
    print(f"\n[{idx+1}/{len(priority_products)}] {row['브랜드']} (ID: {row['상품ID']})")
    
    reviews = get_product_reviews_enhanced(
        row['상품링크'], 
        row['상품ID'],
        row['브랜드'],
        max_pages=5,
        max_reviews=100
    )
    
    all_reviews.extend(reviews)
    
    # 중간 저장 (10개 상품마다)
    if (idx + 1) % 10 == 0:
        if all_reviews:
            pd.DataFrame(all_reviews).to_csv("musinsa_reviews_enhanced.csv", index=False, encoding="utf-8-sig")
            print(f"\n중간 저장 완료: {len(all_reviews)}개 리뷰")
    
    # 과도한 요청 방지
    time.sleep(3)

# 최종 저장
if all_reviews:
    reviews_df = pd.DataFrame(all_reviews)
    reviews_df.to_csv("musinsa_reviews_enhanced.csv", index=False, encoding="utf-8-sig")
    
    # 브랜드별 통계
    brand_stats = reviews_df.groupby('brand').agg({
        'product_id': 'nunique',
        'text': 'count'
    }).rename(columns={'product_id': '상품수', 'text': '리뷰수'})
    
    print("\n" + "="*50)
    print("수집 완료!")
    print(f"총 {len(all_reviews)}개 리뷰 수집")
    print(f"총 {reviews_df['product_id'].nunique()}개 상품")
    print(f"총 {reviews_df['brand'].nunique()}개 브랜드")
    print("\n브랜드별 리뷰 수집 현황:")
    print(brand_stats.sort_values('리뷰수', ascending=False).head(10))
    print("\n파일 저장: musinsa_reviews_enhanced.csv")
else:
    print("\n수집된 리뷰가 없습니다.")

driver.quit()