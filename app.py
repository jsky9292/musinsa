"""
무신사 원피스/스커트 분석 대시보드
Streamlit Cloud 배포용 메인 애플리케이션
"""

import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime
import os

# 페이지 설정
st.set_page_config(
    page_title="무신사 패션 분석 대시보드",
    page_icon="👗",
    layout="wide"
)

# 타이틀
st.title("👗 무신사 원피스/스커트 분석 대시보드")
st.markdown("##### 💡 패션 트렌드 분석 및 마케팅 인사이트")
st.markdown("---")

# 사이드바
with st.sidebar:
    st.header("📊 대시보드 정보")
    st.info("""
    이 대시보드는 무신사의 원피스/스커트 상품을 분석합니다.
    
    **주요 기능:**
    - 🔍 키워드 검색
    - 📈 가격 분석
    - 🏷️ 브랜드 분석
    - 💬 리뷰 감성 분석
    - 🎯 마케팅 인사이트
    """)
    
    st.markdown("---")
    
    # 데이터 업로드
    st.header("📁 데이터 업로드")
    
    uploaded_products = st.file_uploader(
        "상품 데이터 (CSV)",
        type=['csv'],
        key="products",
        help="크롤링한 상품 데이터를 업로드하세요"
    )
    
    uploaded_reviews = st.file_uploader(
        "리뷰 데이터 (CSV)",
        type=['csv'],
        key="reviews",
        help="크롤링한 리뷰 데이터를 업로드하세요"
    )
    
    st.markdown("---")
    
    # 샘플 데이터 다운로드
    st.header("📥 샘플 데이터")
    
    # 샘플 데이터 생성
    sample_products = pd.DataFrame({
        '브랜드': ['Brand A', 'Brand B', 'Brand C', 'Brand D', 'Brand E'],
        '상품명': ['플로럴 원피스', '체크 스커트', '데님 원피스', '플리츠 스커트', '니트 원피스'],
        '가격': [45000, 35000, 55000, 40000, 60000],
        '원가': [60000, 50000, 70000, 50000, 80000],
        '할인율': [25, 30, 21, 20, 25],
        '상품ID': ['001', '002', '003', '004', '005']
    })
    
    csv = sample_products.to_csv(index=False, encoding='utf-8-sig')
    st.download_button(
        label="샘플 상품 데이터 다운로드",
        data=csv,
        file_name="sample_products.csv",
        mime="text/csv"
    )

# 메인 컨텐츠
# 데이터 로드
products_df = None
reviews_df = None

if uploaded_products:
    try:
        products_df = pd.read_csv(uploaded_products)
        st.success(f"✅ {len(products_df)}개 상품 데이터 로드 완료")
    except Exception as e:
        st.error(f"상품 데이터 로드 실패: {e}")

if uploaded_reviews:
    try:
        reviews_df = pd.read_csv(uploaded_reviews)
        st.success(f"✅ {len(reviews_df)}개 리뷰 데이터 로드 완료")
    except Exception as e:
        st.error(f"리뷰 데이터 로드 실패: {e}")

# 데이터가 있을 경우 분석 표시
if products_df is not None:
    # 데이터 전처리
    if '가격' in products_df.columns:
        products_df['가격'] = pd.to_numeric(products_df['가격'], errors='coerce')
    if '할인율' in products_df.columns:
        products_df['할인율'] = pd.to_numeric(products_df['할인율'], errors='coerce')
    
    # 검색 기능 추가
    st.markdown("### 🔍 상품 검색")
    col1, col2, col3 = st.columns([3, 2, 2])
    
    with col1:
        search_term = st.text_input(
            "검색어 입력", 
            placeholder="상품명, 브랜드명 검색...",
            help="상품명이나 브랜드명으로 검색할 수 있습니다"
        )
    
    with col2:
        price_range = st.select_slider(
            "가격대",
            options=['전체', '~3만원', '3-5만원', '5-10만원', '10-20만원', '20만원~'],
            value='전체'
        )
    
    with col3:
        if '브랜드' in products_df.columns:
            brand_options = ['전체'] + sorted(products_df['브랜드'].unique().tolist())
            selected_brand = st.selectbox("브랜드", brand_options)
        else:
            selected_brand = '전체'
    
    # 필터링 적용
    filtered_df = products_df.copy()
    
    # 검색어 필터링
    if search_term:
        mask = False
        if '상품명' in filtered_df.columns:
            mask = mask | filtered_df['상품명'].str.contains(search_term, case=False, na=False)
        if '브랜드' in filtered_df.columns:
            mask = mask | filtered_df['브랜드'].str.contains(search_term, case=False, na=False)
        filtered_df = filtered_df[mask]
    
    # 가격대 필터링
    if price_range != '전체' and '가격' in filtered_df.columns:
        if price_range == '~3만원':
            filtered_df = filtered_df[filtered_df['가격'] <= 30000]
        elif price_range == '3-5만원':
            filtered_df = filtered_df[(filtered_df['가격'] > 30000) & (filtered_df['가격'] <= 50000)]
        elif price_range == '5-10만원':
            filtered_df = filtered_df[(filtered_df['가격'] > 50000) & (filtered_df['가격'] <= 100000)]
        elif price_range == '10-20만원':
            filtered_df = filtered_df[(filtered_df['가격'] > 100000) & (filtered_df['가격'] <= 200000)]
        elif price_range == '20만원~':
            filtered_df = filtered_df[filtered_df['가격'] > 200000]
    
    # 브랜드 필터링
    if selected_brand != '전체' and '브랜드' in filtered_df.columns:
        filtered_df = filtered_df[filtered_df['브랜드'] == selected_brand]
    
    # 검색 결과 표시
    st.info(f"🔍 검색 결과: {len(filtered_df)}개 상품")
    
    # 정렬 옵션
    col1, col2 = st.columns([1, 5])
    with col1:
        sort_by = st.selectbox(
            "정렬",
            options=['가격 낮은순', '가격 높은순', '할인율 높은순', '브랜드명순'],
            label_visibility="collapsed"
        )
    
    # 정렬 적용
    if sort_by == '가격 낮은순' and '가격' in filtered_df.columns:
        filtered_df = filtered_df.sort_values('가격')
    elif sort_by == '가격 높은순' and '가격' in filtered_df.columns:
        filtered_df = filtered_df.sort_values('가격', ascending=False)
    elif sort_by == '할인율 높은순' and '할인율' in filtered_df.columns:
        filtered_df = filtered_df.sort_values('할인율', ascending=False)
    elif sort_by == '브랜드명순' and '브랜드' in filtered_df.columns:
        filtered_df = filtered_df.sort_values('브랜드')
    
    # 검색 결과 테이블
    if len(filtered_df) > 0:
        # 상품 카드 형식으로 표시
        st.markdown("### 📦 검색된 상품")
        
        # 페이지네이션
        items_per_page = 20
        total_pages = (len(filtered_df) - 1) // items_per_page + 1
        page = st.number_input('페이지', min_value=1, max_value=total_pages, value=1)
        
        start_idx = (page - 1) * items_per_page
        end_idx = min(start_idx + items_per_page, len(filtered_df))
        
        page_df = filtered_df.iloc[start_idx:end_idx]
        
        # 상품 표시
        for _, row in page_df.iterrows():
            with st.container():
                col1, col2, col3, col4 = st.columns([3, 2, 1, 1])
                
                with col1:
                    if '상품명' in row:
                        st.markdown(f"**{row['상품명']}**")
                    if '브랜드' in row:
                        st.caption(f"🏷️ {row['브랜드']}")
                
                with col2:
                    if '가격' in row:
                        st.metric("가격", f"₩{row['가격']:,.0f}")
                
                with col3:
                    if '할인율' in row and pd.notna(row['할인율']) and row['할인율'] > 0:
                        st.metric("할인", f"{row['할인율']:.0f}%")
                
                with col4:
                    if '상품링크' in row and pd.notna(row['상품링크']):
                        st.markdown(f"[🔗 상품보기]({row['상품링크']})")
                
                st.markdown("---")
    else:
        st.warning("검색 결과가 없습니다. 다른 검색어를 입력해주세요.")
    
    st.markdown("---")
    
    # 필터링된 데이터로 분석 진행
    products_df = filtered_df
    
    # 탭 구성
    tab1, tab2, tab3, tab4, tab5 = st.tabs([
        "📊 개요",
        "💰 가격 분석",
        "🏷️ 브랜드 분석",
        "🎨 트렌드 분석",
        "💡 인사이트"
    ])
    
    with tab1:
        st.header("📊 데이터 개요")
        
        # 주요 지표
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            st.metric("총 상품 수", f"{len(products_df):,}개")
        
        with col2:
            if '브랜드' in products_df.columns:
                unique_brands = products_df['브랜드'].nunique()
                st.metric("브랜드 수", f"{unique_brands}개")
        
        with col3:
            if '가격' in products_df.columns:
                avg_price = products_df['가격'].mean()
                st.metric("평균 가격", f"₩{avg_price:,.0f}")
        
        with col4:
            if '할인율' in products_df.columns:
                avg_discount = products_df['할인율'].mean()
                st.metric("평균 할인율", f"{avg_discount:.1f}%")
        
        # 데이터 미리보기
        st.subheader("데이터 미리보기")
        st.dataframe(products_df.head(20), use_container_width=True)
        
        # 데이터 통계
        st.subheader("기본 통계")
        st.dataframe(products_df.describe(), use_container_width=True)
    
    with tab2:
        st.header("💰 가격 분석")
        
        if '가격' in products_df.columns:
            col1, col2 = st.columns(2)
            
            with col1:
                # 가격 분포
                fig = px.histogram(
                    products_df,
                    x='가격',
                    nbins=30,
                    title="가격 분포",
                    labels={'가격': '가격 (원)', 'count': '상품 수'}
                )
                st.plotly_chart(fig, use_container_width=True)
            
            with col2:
                if '할인율' in products_df.columns:
                    # 할인율 분포
                    fig = px.histogram(
                        products_df[products_df['할인율'] > 0],
                        x='할인율',
                        nbins=20,
                        title="할인율 분포",
                        labels={'할인율': '할인율 (%)', 'count': '상품 수'}
                    )
                    st.plotly_chart(fig, use_container_width=True)
            
            # 가격대별 분포
            st.subheader("가격대별 상품 분포")
            price_ranges = pd.cut(
                products_df['가격'],
                bins=[0, 30000, 50000, 100000, 200000, float('inf')],
                labels=['~3만원', '3-5만원', '5-10만원', '10-20만원', '20만원~']
            )
            price_dist = price_ranges.value_counts().sort_index()
            
            fig = px.pie(
                values=price_dist.values,
                names=price_dist.index,
                title="가격대별 비율"
            )
            st.plotly_chart(fig, use_container_width=True)
    
    with tab3:
        st.header("🏷️ 브랜드 분석")
        
        if '브랜드' in products_df.columns:
            # 브랜드별 상품 수
            brand_counts = products_df['브랜드'].value_counts().head(15)
            
            fig = px.bar(
                x=brand_counts.values,
                y=brand_counts.index,
                orientation='h',
                title="브랜드별 상품 수 (Top 15)",
                labels={'x': '상품 수', 'y': '브랜드'}
            )
            fig.update_layout(height=500)
            st.plotly_chart(fig, use_container_width=True)
            
            if '가격' in products_df.columns:
                # 브랜드별 평균 가격
                st.subheader("브랜드별 평균 가격")
                brand_avg_price = products_df.groupby('브랜드')['가격'].mean().sort_values(ascending=False).head(15)
                
                fig = px.bar(
                    x=brand_avg_price.index,
                    y=brand_avg_price.values,
                    title="브랜드별 평균 가격 (Top 15)",
                    labels={'x': '브랜드', 'y': '평균 가격 (원)'},
                    color=brand_avg_price.values,
                    color_continuous_scale='Viridis'
                )
                st.plotly_chart(fig, use_container_width=True)
    
    with tab4:
        st.header("🎨 트렌드 분석")
        
        # 상품명에서 키워드 추출
        if '상품명' in products_df.columns:
            st.subheader("인기 키워드")
            
            # 스타일 키워드 분석
            style_keywords = {
                '플로럴': ['플로럴', '꽃', '플라워'],
                '체크': ['체크', '격자'],
                '스트라이프': ['스트라이프', '줄무늬'],
                '도트': ['도트', '물방울'],
                '레이스': ['레이스'],
                '데님': ['데님', '청']
            }
            
            style_counts = {}
            for style, keywords in style_keywords.items():
                count = 0
                for keyword in keywords:
                    count += products_df['상품명'].str.contains(keyword, na=False).sum()
                if count > 0:
                    style_counts[style] = count
            
            if style_counts:
                style_df = pd.DataFrame(list(style_counts.items()), columns=['스타일', '상품 수'])
                
                fig = px.pie(
                    style_df,
                    values='상품 수',
                    names='스타일',
                    title="스타일별 상품 분포"
                )
                st.plotly_chart(fig, use_container_width=True)
        
        # 할인 트렌드
        if '할인율' in products_df.columns and '브랜드' in products_df.columns:
            st.subheader("브랜드별 할인 전략")
            
            brand_discount = products_df.groupby('브랜드')['할인율'].mean().sort_values(ascending=False).head(10)
            
            fig = px.bar(
                x=brand_discount.index,
                y=brand_discount.values,
                title="평균 할인율 Top 10 브랜드",
                labels={'x': '브랜드', 'y': '평균 할인율 (%)'},
                color=brand_discount.values,
                color_continuous_scale='RdYlGn'
            )
            st.plotly_chart(fig, use_container_width=True)
    
    with tab5:
        st.header("💡 마케팅 인사이트")
        
        # 가격 전략 인사이트
        if '가격' in products_df.columns and '할인율' in products_df.columns:
            st.subheader("📈 가격 전략 인사이트")
            
            avg_price = products_df['가격'].mean()
            median_price = products_df['가격'].median()
            avg_discount = products_df['할인율'].mean()
            
            col1, col2 = st.columns(2)
            
            with col1:
                st.info(f"""
                **가격 포지셔닝**
                - 평균 가격: ₩{avg_price:,.0f}
                - 중간 가격: ₩{median_price:,.0f}
                - 평균 할인율: {avg_discount:.1f}%
                
                **제안사항:**
                - {'프리미엄 전략' if avg_price > 70000 else '중저가 전략'} 추천
                - {'적극적인 할인 정책' if avg_discount > 25 else '선택적 할인 정책'} 운영
                """)
            
            with col2:
                # 가성비 상품 추천
                st.success(f"""
                **가성비 상품 전략**
                
                할인율 30% 이상 상품: {len(products_df[products_df['할인율'] > 30])}개
                
                **추천 액션:**
                1. 할인 상품 큐레이션 페이지 운영
                2. 가격대별 베스트 상품 선정
                3. 시즌 오프 할인 이벤트 기획
                """)
        
        # 브랜드 전략
        if '브랜드' in products_df.columns:
            st.subheader("🏆 브랜드 전략")
            
            top_brands = products_df['브랜드'].value_counts().head(5)
            
            st.warning(f"""
            **Top 5 브랜드 집중 전략**
            
            {', '.join(top_brands.index.tolist())}
            
            **추천 액션:**
            1. 인기 브랜드 전용 기획전
            2. 브랜드별 스타일 가이드 제공
            3. 브랜드 콜라보레이션 이벤트
            """)
        
        # 다운로드 섹션
        st.markdown("---")
        st.subheader("📥 분석 결과 다운로드")
        
        if products_df is not None:
            csv = products_df.to_csv(index=False, encoding='utf-8-sig')
            st.download_button(
                label="📊 전체 데이터 다운로드",
                data=csv,
                file_name=f"musinsa_analysis_{datetime.now().strftime('%Y%m%d')}.csv",
                mime="text/csv"
            )

else:
    # 데이터가 없을 때 안내
    st.info("""
    👋 **시작하기**
    
    1. 왼쪽 사이드바에서 데이터를 업로드하세요
    2. 또는 샘플 데이터를 다운로드하여 테스트하세요
    
    **데이터 수집 방법:**
    - GitHub 저장소의 크롤러를 사용하여 데이터 수집
    - CSV 형식으로 저장 후 업로드
    
    **필요한 컬럼:**
    - 상품 데이터: 브랜드, 상품명, 가격, 할인율
    - 리뷰 데이터: product_id, text, rating
    """)
    
    # 사용 가이드
    with st.expander("📖 사용 가이드"):
        st.markdown("""
        ### 데이터 수집
        1. GitHub 저장소 클론
        2. 크롤러 실행: `python musinsa_crawler.py`
        3. 생성된 CSV 파일 업로드
        
        ### 분석 기능
        - **개요**: 전체 데이터 통계
        - **가격 분석**: 가격 분포 및 할인 현황
        - **브랜드 분석**: 브랜드별 상품 및 가격
        - **트렌드 분석**: 스타일 키워드 분석
        - **인사이트**: 마케팅 전략 제안
        """)

# 푸터
st.markdown("---")
st.markdown("""
<div style='text-align: center'>
    <p>🚀 무신사 패션 분석 대시보드 | 
    <a href='https://github.com/yourusername/musinsa-analysis'>GitHub</a> | 
    <a href='https://streamlit.io'>Powered by Streamlit</a></p>
</div>
""", unsafe_allow_html=True)