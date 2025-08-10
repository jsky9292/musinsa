import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from wordcloud import WordCloud
import matplotlib.pyplot as plt
from datetime import datetime, timedelta
import re
import numpy as np

# 페이지 설정
st.set_page_config(
    page_title="무신사 원피스 분석 대시보드",
    page_icon="👗",
    layout="wide"
)

# 데이터 로드
@st.cache_data
def load_data():
    try:
        products_df = pd.read_csv("musinsa_onepiece_all.csv")
        reviews_df = pd.read_csv("musinsa_reviews.csv")
        
        # 가격 데이터 정리
        products_df['가격'] = pd.to_numeric(products_df['가격'], errors='coerce')
        products_df['원가'] = pd.to_numeric(products_df['원가'], errors='coerce')
        products_df['할인율'] = pd.to_numeric(products_df['할인율'], errors='coerce')
        
        return products_df, reviews_df
    except Exception as e:
        st.error(f"데이터 로딩 오류: {e}")
        return None, None

# 타이틀
st.title("👗 무신사 원피스/스커트 분석 대시보드")
st.markdown("---")

# 데이터 로드
products_df, reviews_df = load_data()

if products_df is not None and reviews_df is not None:
    
    # 사이드바 - 필터링 옵션
    st.sidebar.header("필터 옵션")
    
    # 브랜드 필터
    all_brands = products_df['브랜드'].unique()
    selected_brands = st.sidebar.multiselect(
        "브랜드 선택",
        options=all_brands,
        default=all_brands[:10] if len(all_brands) > 10 else all_brands
    )
    
    # 가격 범위 필터
    price_min = int(products_df['가격'].min()) if not products_df['가격'].isna().all() else 0
    price_max = int(products_df['가격'].max()) if not products_df['가격'].isna().all() else 1000000
    price_range = st.sidebar.slider(
        "가격 범위",
        min_value=price_min,
        max_value=price_max,
        value=(price_min, price_max),
        step=10000
    )
    
    # 할인율 필터
    discount_min = st.sidebar.number_input("최소 할인율 (%)", min_value=0, max_value=100, value=0)
    
    # 데이터 필터링
    filtered_products = products_df[
        (products_df['브랜드'].isin(selected_brands)) &
        (products_df['가격'] >= price_range[0]) &
        (products_df['가격'] <= price_range[1]) &
        (products_df['할인율'] >= discount_min)
    ]
    
    # 메인 대시보드
    # 1. 주요 지표
    st.header("📊 주요 지표")
    col1, col2, col3, col4, col5 = st.columns(5)
    
    with col1:
        st.metric("총 상품 수", f"{len(filtered_products):,}개")
    
    with col2:
        avg_price = filtered_products['가격'].mean()
        st.metric("평균 가격", f"₩{avg_price:,.0f}")
    
    with col3:
        avg_discount = filtered_products['할인율'].mean()
        st.metric("평균 할인율", f"{avg_discount:.1f}%")
    
    with col4:
        st.metric("총 리뷰 수", f"{len(reviews_df):,}개")
    
    with col5:
        unique_brands = filtered_products['브랜드'].nunique()
        st.metric("브랜드 수", f"{unique_brands}개")
    
    st.markdown("---")
    
    # 2. 브랜드별 분석
    st.header("🏷️ 브랜드별 분석")
    
    col1, col2 = st.columns(2)
    
    with col1:
        # 브랜드별 상품 수
        brand_counts = filtered_products['브랜드'].value_counts().head(15)
        fig_brand = px.bar(
            x=brand_counts.values,
            y=brand_counts.index,
            orientation='h',
            title="상위 15개 브랜드별 상품 수",
            labels={'x': '상품 수', 'y': '브랜드'}
        )
        fig_brand.update_layout(height=400)
        st.plotly_chart(fig_brand, use_container_width=True)
    
    with col2:
        # 브랜드별 평균 가격
        brand_avg_price = filtered_products.groupby('브랜드')['가격'].mean().sort_values(ascending=False).head(15)
        fig_price = px.bar(
            x=brand_avg_price.values,
            y=brand_avg_price.index,
            orientation='h',
            title="브랜드별 평균 가격 (상위 15개)",
            labels={'x': '평균 가격 (원)', 'y': '브랜드'}
        )
        fig_price.update_layout(height=400)
        st.plotly_chart(fig_price, use_container_width=True)
    
    # 3. 가격 분포 분석
    st.header("💰 가격 분포 분석")
    
    col1, col2 = st.columns(2)
    
    with col1:
        # 가격 분포 히스토그램
        fig_hist = px.histogram(
            filtered_products,
            x='가격',
            nbins=30,
            title="가격 분포",
            labels={'가격': '가격 (원)', 'count': '상품 수'}
        )
        fig_hist.update_layout(height=400)
        st.plotly_chart(fig_hist, use_container_width=True)
    
    with col2:
        # 할인율 분포
        fig_discount = px.histogram(
            filtered_products[filtered_products['할인율'] > 0],
            x='할인율',
            nbins=20,
            title="할인율 분포",
            labels={'할인율': '할인율 (%)', 'count': '상품 수'}
        )
        fig_discount.update_layout(height=400)
        st.plotly_chart(fig_discount, use_container_width=True)
    
    # 4. 할인 분석
    st.header("🎯 할인 분석")
    
    col1, col2 = st.columns(2)
    
    with col1:
        # 할인율별 상품 비율
        discount_ranges = pd.cut(
            filtered_products['할인율'],
            bins=[0, 10, 20, 30, 40, 50, 100],
            labels=['0-10%', '10-20%', '20-30%', '30-40%', '40-50%', '50% 이상']
        )
        discount_dist = discount_ranges.value_counts()
        
        fig_pie = px.pie(
            values=discount_dist.values,
            names=discount_dist.index,
            title="할인율 구간별 상품 분포"
        )
        fig_pie.update_layout(height=400)
        st.plotly_chart(fig_pie, use_container_width=True)
    
    with col2:
        # 브랜드별 평균 할인율
        brand_avg_discount = filtered_products.groupby('브랜드')['할인율'].mean().sort_values(ascending=False).head(10)
        fig_brand_discount = px.bar(
            x=brand_avg_discount.values,
            y=brand_avg_discount.index,
            orientation='h',
            title="브랜드별 평균 할인율 (상위 10개)",
            labels={'x': '평균 할인율 (%)', 'y': '브랜드'}
        )
        fig_brand_discount.update_layout(height=400)
        st.plotly_chart(fig_brand_discount, use_container_width=True)
    
    # 5. 리뷰 분석
    if len(reviews_df) > 0:
        st.header("💬 리뷰 분석")
        
        col1, col2, col3 = st.columns(3)
        
        with col1:
            # 리뷰가 많은 상품
            review_counts = reviews_df['product_id'].value_counts().head(10)
            
            # 상품 ID와 브랜드 매칭
            top_reviewed_products = []
            for pid, count in review_counts.items():
                brand = reviews_df[reviews_df['product_id'] == pid]['brand'].iloc[0] if len(reviews_df[reviews_df['product_id'] == pid]) > 0 else 'Unknown'
                top_reviewed_products.append({'상품ID': pid, '브랜드': brand, '리뷰수': count})
            
            top_reviewed_df = pd.DataFrame(top_reviewed_products)
            st.subheader("리뷰가 많은 상품 TOP 10")
            st.dataframe(top_reviewed_df, use_container_width=True)
        
        with col2:
            # 브랜드별 리뷰 수
            brand_review_counts = reviews_df['brand'].value_counts().head(10)
            fig_brand_reviews = px.bar(
                x=brand_review_counts.index,
                y=brand_review_counts.values,
                title="브랜드별 리뷰 수 (상위 10개)",
                labels={'x': '브랜드', 'y': '리뷰 수'}
            )
            fig_brand_reviews.update_layout(height=400)
            st.plotly_chart(fig_brand_reviews, use_container_width=True)
        
        with col3:
            # 리뷰 텍스트 길이 분포
            reviews_df['text_length'] = reviews_df['text'].astype(str).str.len()
            avg_review_length = reviews_df['text_length'].mean()
            
            st.metric("평균 리뷰 길이", f"{avg_review_length:.0f}자")
            
            fig_length = px.histogram(
                reviews_df,
                x='text_length',
                nbins=30,
                title="리뷰 텍스트 길이 분포",
                labels={'text_length': '텍스트 길이', 'count': '리뷰 수'}
            )
            fig_length.update_layout(height=300)
            st.plotly_chart(fig_length, use_container_width=True)
    
    # 6. 상세 데이터 테이블
    st.header("📋 상세 데이터")
    
    tab1, tab2, tab3 = st.tabs(["상품 목록", "리뷰 목록", "데이터 다운로드"])
    
    with tab1:
        st.subheader("상품 목록")
        
        # 정렬 옵션
        sort_by = st.selectbox(
            "정렬 기준",
            options=['가격 (낮은순)', '가격 (높은순)', '할인율 (높은순)', '브랜드명']
        )
        
        if sort_by == '가격 (낮은순)':
            display_products = filtered_products.sort_values('가격')
        elif sort_by == '가격 (높은순)':
            display_products = filtered_products.sort_values('가격', ascending=False)
        elif sort_by == '할인율 (높은순)':
            display_products = filtered_products.sort_values('할인율', ascending=False)
        else:
            display_products = filtered_products.sort_values('브랜드')
        
        # 표시할 컬럼 선택
        display_columns = ['브랜드', '가격', '원가', '할인율', '상품ID', '상품링크']
        st.dataframe(
            display_products[display_columns].head(100),
            use_container_width=True,
            hide_index=True
        )
    
    with tab2:
        if len(reviews_df) > 0:
            st.subheader("리뷰 목록")
            
            # 브랜드별 필터
            review_brands = reviews_df['brand'].unique()
            selected_review_brand = st.selectbox(
                "브랜드 선택",
                options=['전체'] + list(review_brands)
            )
            
            if selected_review_brand != '전체':
                display_reviews = reviews_df[reviews_df['brand'] == selected_review_brand]
            else:
                display_reviews = reviews_df
            
            # 리뷰 표시
            for idx, review in display_reviews.head(50).iterrows():
                with st.expander(f"{review['brand']} - 상품 {review['product_id']}"):
                    col1, col2 = st.columns([3, 1])
                    with col1:
                        st.write(f"**리뷰 내용:** {review['text']}")
                    with col2:
                        if pd.notna(review.get('rating')):
                            st.write(f"**평점:** {review['rating']}")
                        if pd.notna(review.get('author')):
                            st.write(f"**작성자:** {review['author']}")
                        if pd.notna(review.get('date')):
                            st.write(f"**날짜:** {review['date']}")
        else:
            st.info("리뷰 데이터가 없습니다.")
    
    with tab3:
        st.subheader("데이터 다운로드")
        
        col1, col2 = st.columns(2)
        
        with col1:
            csv = filtered_products.to_csv(index=False, encoding='utf-8-sig')
            st.download_button(
                label="📥 필터링된 상품 데이터 다운로드 (CSV)",
                data=csv,
                file_name=f"musinsa_products_filtered_{datetime.now().strftime('%Y%m%d')}.csv",
                mime="text/csv"
            )
        
        with col2:
            if len(reviews_df) > 0:
                csv_reviews = reviews_df.to_csv(index=False, encoding='utf-8-sig')
                st.download_button(
                    label="📥 리뷰 데이터 다운로드 (CSV)",
                    data=csv_reviews,
                    file_name=f"musinsa_reviews_{datetime.now().strftime('%Y%m%d')}.csv",
                    mime="text/csv"
                )

else:
    st.error("데이터 파일을 찾을 수 없습니다. 크롤링을 먼저 실행해주세요.")
    st.info("""
    필요한 파일:
    - musinsa_onepiece_all.csv (상품 데이터)
    - musinsa_reviews.csv (리뷰 데이터)
    
    크롤링 실행 방법:
    1. `python musinsa_onepiece.py` 실행 (상품 데이터 수집)
    2. `python musinsa_review_crawler.py` 실행 (리뷰 데이터 수집)
    """)

# 푸터
st.markdown("---")
st.markdown("📊 무신사 원피스/스커트 분석 대시보드 | 최종 업데이트: " + datetime.now().strftime("%Y-%m-%d %H:%M"))