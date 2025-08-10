"""
무신사 크롤러 - GitHub Actions용 간소화 버전
"""

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.chrome.options import Options
import time
import pandas as pd
from bs4 import BeautifulSoup
import argparse
import os
from datetime import datetime

def setup_driver(headless=True):
    """웹드라이버 설정"""
    options = Options()
    options.add_argument('--no-sandbox')
    options.add_argument('--disable-dev-shm-usage')
    options.add_argument('--disable-gpu')
    options.add_argument('--window-size=1920,1080')
    
    if headless:
        options.add_argument('--headless')
    
    driver = webdriver.Chrome(options=options)
    return driver

def crawl_products(category_url, max_scroll=10, max_products=500):
    """무신사 상품 크롤링"""
    driver = setup_driver(headless=True)
    
    try:
        driver.get(category_url)
        time.sleep(3)
        
        all_results = []
        seen_links = set()
        scroll_count = 0
        
        while scroll_count < max_scroll and len(all_results) < max_products:
            # 스크롤
            for _ in range(5):
                driver.find_element(By.TAG_NAME, 'body').send_keys(Keys.PAGE_DOWN)
                time.sleep(0.3)
            
            time.sleep(2)
            
            # HTML 파싱
            soup = BeautifulSoup(driver.page_source, "html.parser")
            
            # 상품 카드 찾기
            cards = soup.select("a.gtm-view-item-list")
            
            for item in cards:
                if len(all_results) >= max_products:
                    break
                    
                product_link = item.get("href", "")
                if not product_link:
                    continue
                    
                if not product_link.startswith("http"):
                    product_link = "https://www.musinsa.com" + product_link
                
                if product_link in seen_links:
                    continue
                
                seen_links.add(product_link)
                
                # 데이터 추출
                img_tag = item.find("img")
                img_url = img_tag.get("src", "") if img_tag else ""
                
                all_results.append({
                    "상품ID": item.get("data-item-id", ""),
                    "브랜드": item.get("data-item-brand", ""),
                    "가격": item.get("data-price", ""),
                    "원가": item.get("data-original-price", ""),
                    "할인율": item.get("data-discount-rate", ""),
                    "이미지URL": img_url,
                    "상품링크": product_link,
                    "수집일시": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                })
            
            scroll_count += 1
            print(f"스크롤 {scroll_count}: {len(all_results)}개 상품 수집")
            
            if len(cards) == 0:
                break
        
        return all_results
        
    finally:
        driver.quit()

def main():
    parser = argparse.ArgumentParser(description="무신사 크롤러")
    parser.add_argument('--category', default='onepiece', choices=['onepiece', 'skirt', 'all'],
                       help='카테고리 선택')
    parser.add_argument('--max-products', type=int, default=100,
                       help='최대 수집 상품 수')
    parser.add_argument('--max-scroll', type=int, default=20,
                       help='최대 스크롤 횟수')
    parser.add_argument('--headless', action='store_true',
                       help='헤드리스 모드')
    parser.add_argument('--output', default='data',
                       help='출력 디렉토리')
    
    args = parser.parse_args()
    
    # 카테고리 URL
    category_urls = {
        'onepiece': 'https://www.musinsa.com/category/100?gf=A',
        'skirt': 'https://www.musinsa.com/category/101?gf=A',
        'all': 'https://www.musinsa.com/category/100?gf=A'
    }
    
    url = category_urls[args.category]
    
    print(f"크롤링 시작: {args.category}")
    print(f"최대 상품 수: {args.max_products}")
    
    # 크롤링 실행
    results = crawl_products(url, args.max_scroll, args.max_products)
    
    # 결과 저장
    if results:
        # 출력 디렉토리 생성
        os.makedirs(args.output, exist_ok=True)
        
        # 파일명
        timestamp = datetime.now().strftime("%Y%m%d")
        filename = f"{args.output}/musinsa_{args.category}_{timestamp}.csv"
        
        # DataFrame 생성 및 저장
        df = pd.DataFrame(results)
        df.to_csv(filename, index=False, encoding='utf-8-sig')
        
        print(f"\n크롤링 완료!")
        print(f"수집된 상품: {len(results)}개")
        print(f"저장 위치: {filename}")
        
        # 통계 출력
        df['가격'] = pd.to_numeric(df['가격'], errors='coerce')
        df['할인율'] = pd.to_numeric(df['할인율'], errors='coerce')
        
        print(f"\n=== 수집 통계 ===")
        print(f"브랜드 수: {df['브랜드'].nunique()}개")
        print(f"평균 가격: ₩{df['가격'].mean():,.0f}")
        print(f"평균 할인율: {df['할인율'].mean():.1f}%")
    else:
        print("수집된 데이터가 없습니다.")

if __name__ == "__main__":
    main()