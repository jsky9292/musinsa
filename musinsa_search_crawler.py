from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time
import pandas as pd
from bs4 import BeautifulSoup
import argparse
from datetime import datetime

def setup_driver(headless=True):
    """웹드라이버 설정"""
    options = Options()
    options.add_argument('--disable-gpu')
    options.add_argument('--window-size=1920,1080')
    options.add_argument('--disable-blink-features=AutomationControlled')
    options.add_experimental_option("excludeSwitches", ["enable-automation"])
    options.add_experimental_option('useAutomationExtension', False)
    
    if headless:
        options.add_argument('--headless')
    
    driver = webdriver.Chrome(options=options)
    driver.execute_script("Object.defineProperty(navigator, 'webdriver', {get: () => undefined})")
    
    return driver

def search_products(driver, search_query, category="원피스", max_scroll=10):
    """무신사에서 상품 검색"""
    print(f"\n검색 시작: '{search_query}' in {category}")
    
    # 무신사 검색 페이지로 이동
    search_url = f"https://www.musinsa.com/search/musinsa/integration?q={search_query}&gf=A"
    driver.get(search_url)
    time.sleep(3)
    
    # 카테고리 필터 적용 (원피스/스커트)
    try:
        # 카테고리 버튼 찾기
        category_buttons = driver.find_elements(By.XPATH, "//button[contains(text(), '원피스') or contains(text(), '스커트')]")
        if category_buttons:
            category_buttons[0].click()
            time.sleep(2)
    except:
        print("카테고리 필터 적용 실패, 전체 검색 결과 사용")
    
    all_results = []
    seen_links = set()
    scroll_count = 0
    
    while scroll_count < max_scroll:
        # 스크롤
        for _ in range(5):
            driver.find_element(By.TAG_NAME, 'body').send_keys(Keys.PAGE_DOWN)
            time.sleep(0.5)
        
        time.sleep(2)
        
        # HTML 파싱
        soup = BeautifulSoup(driver.page_source, "html.parser")
        
        # 상품 카드 찾기
        cards = soup.select("a.gtm-view-item-list")
        
        new_items = 0
        for item in cards:
            product_link = item.get("href", "")
            if not product_link:
                continue
                
            if not product_link.startswith("http"):
                product_link = "https://www.musinsa.com" + product_link
            
            if product_link in seen_links:
                continue
            
            seen_links.add(product_link)
            
            # 이미지 URL
            img_tag = item.find("img")
            img_url = img_tag.get("src", "") if img_tag else ""
            
            # 데이터 속성에서 정보 추출
            brand = item.get("data-item-brand", "")
            price = item.get("data-price", "")
            original_price = item.get("data-original-price", "")
            discount_rate = item.get("data-discount-rate", "")
            item_id = item.get("data-item-id", "")
            item_name = item.get("aria-label", "").replace("상품상세로 이동", "").strip()
            
            all_results.append({
                "검색어": search_query,
                "상품ID": item_id,
                "브랜드": brand,
                "상품명": item_name,
                "가격": price,
                "원가": original_price,
                "할인율": discount_rate,
                "이미지URL": img_url,
                "상품링크": product_link
            })
            new_items += 1
        
        scroll_count += 1
        print(f"  {scroll_count}회 스크롤: 누적 {len(all_results)}개 상품 (신규 {new_items}개)")
        
        if new_items == 0:
            print("  더 이상 새로운 상품이 없습니다.")
            break
    
    return all_results

def apply_filters(driver, filters):
    """검색 필터 적용"""
    try:
        # 가격 필터
        if 'min_price' in filters or 'max_price' in filters:
            price_button = driver.find_element(By.XPATH, "//button[contains(text(), '가격')]")
            price_button.click()
            time.sleep(1)
            
            if 'min_price' in filters:
                min_input = driver.find_element(By.XPATH, "//input[@placeholder='최소가격']")
                min_input.clear()
                min_input.send_keys(str(filters['min_price']))
            
            if 'max_price' in filters:
                max_input = driver.find_element(By.XPATH, "//input[@placeholder='최대가격']")
                max_input.clear()
                max_input.send_keys(str(filters['max_price']))
            
            # 적용 버튼 클릭
            apply_button = driver.find_element(By.XPATH, "//button[contains(text(), '적용')]")
            apply_button.click()
            time.sleep(2)
        
        # 할인율 필터
        if 'discount' in filters:
            discount_button = driver.find_element(By.XPATH, f"//button[contains(text(), '{filters['discount']}')]")
            discount_button.click()
            time.sleep(2)
        
        # 브랜드 필터
        if 'brands' in filters:
            for brand in filters['brands']:
                try:
                    brand_checkbox = driver.find_element(By.XPATH, f"//label[contains(text(), '{brand}')]")
                    brand_checkbox.click()
                    time.sleep(0.5)
                except:
                    print(f"  브랜드 '{brand}' 필터 적용 실패")
        
        print("  필터 적용 완료")
        
    except Exception as e:
        print(f"  필터 적용 중 오류: {e}")

def interactive_search():
    """대화형 검색 모드"""
    print("="*50)
    print("무신사 원피스/스커트 검색 크롤러")
    print("="*50)
    
    # 검색어 입력
    search_query = input("\n검색어를 입력하세요: ").strip()
    if not search_query:
        print("검색어가 없습니다. 종료합니다.")
        return
    
    # 검색 옵션
    print("\n검색 옵션 설정 (Enter로 스킵 가능)")
    
    # 가격 범위
    min_price = input("최소 가격 (원): ").strip()
    max_price = input("최대 가격 (원): ").strip()
    
    # 할인율
    print("\n할인율 선택:")
    print("1. 전체")
    print("2. 10% 이상")
    print("3. 20% 이상")
    print("4. 30% 이상")
    print("5. 50% 이상")
    discount_choice = input("선택 (1-5): ").strip()
    
    discount_map = {
        '2': '10%',
        '3': '20%',
        '4': '30%',
        '5': '50%'
    }
    
    # 브랜드
    brands_input = input("\n특정 브랜드 (쉼표로 구분, 예: 자라,유니클로): ").strip()
    
    # 최대 스크롤 횟수
    max_scroll = input("\n최대 스크롤 횟수 (기본값: 10): ").strip()
    max_scroll = int(max_scroll) if max_scroll else 10
    
    # 필터 구성
    filters = {}
    if min_price:
        filters['min_price'] = int(min_price)
    if max_price:
        filters['max_price'] = int(max_price)
    if discount_choice in discount_map:
        filters['discount'] = discount_map[discount_choice]
    if brands_input:
        filters['brands'] = [b.strip() for b in brands_input.split(',')]
    
    # 드라이버 설정
    headless = input("\n백그라운드 실행? (y/n, 기본값: y): ").strip().lower()
    headless = headless != 'n'
    
    driver = setup_driver(headless)
    
    try:
        # 검색 실행
        results = search_products(driver, search_query, max_scroll=max_scroll)
        
        # 필터 적용
        if filters:
            print("\n필터 적용 중...")
            apply_filters(driver, filters)
            time.sleep(2)
            
            # 필터 적용 후 재검색
            results = search_products(driver, search_query, max_scroll=max_scroll)
        
        # 결과 저장
        if results:
            df = pd.DataFrame(results)
            filename = f"search_{search_query.replace(' ', '_')}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv"
            df.to_csv(filename, index=False, encoding='utf-8-sig')
            
            print(f"\n검색 완료!")
            print(f"총 {len(results)}개 상품 발견")
            print(f"파일 저장: {filename}")
            
            # 브랜드별 통계
            brand_counts = df['브랜드'].value_counts().head(10)
            print("\n상위 10개 브랜드:")
            for brand, count in brand_counts.items():
                print(f"  {brand}: {count}개")
            
            # 가격 통계
            df['가격'] = pd.to_numeric(df['가격'], errors='coerce')
            print(f"\n가격 통계:")
            print(f"  평균: ₩{df['가격'].mean():,.0f}")
            print(f"  최소: ₩{df['가격'].min():,.0f}")
            print(f"  최대: ₩{df['가격'].max():,.0f}")
        else:
            print("\n검색 결과가 없습니다.")
    
    finally:
        driver.quit()

def batch_search(search_queries, output_file="batch_search_results.csv"):
    """여러 검색어 일괄 처리"""
    driver = setup_driver(headless=True)
    all_results = []
    
    try:
        for query in search_queries:
            print(f"\n검색 중: {query}")
            results = search_products(driver, query, max_scroll=5)
            all_results.extend(results)
            time.sleep(2)
        
        # 결과 저장
        if all_results:
            df = pd.DataFrame(all_results)
            df.to_csv(output_file, index=False, encoding='utf-8-sig')
            print(f"\n총 {len(all_results)}개 상품 저장: {output_file}")
    
    finally:
        driver.quit()

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="무신사 검색 크롤러")
    parser.add_argument('--mode', choices=['interactive', 'batch'], default='interactive',
                       help='실행 모드 선택')
    parser.add_argument('--queries', nargs='+', help='배치 모드에서 사용할 검색어들')
    parser.add_argument('--output', default='search_results.csv', help='출력 파일명')
    
    args = parser.parse_args()
    
    if args.mode == 'interactive':
        interactive_search()
    elif args.mode == 'batch' and args.queries:
        batch_search(args.queries, args.output)
    else:
        # 기본 대화형 모드
        interactive_search()