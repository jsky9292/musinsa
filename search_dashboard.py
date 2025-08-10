import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime
import subprocess
import os
import time
from review_analyzer import ReviewAnalyzer
from brand_analyzer import BrandAnalyzer

# 페이지 설정
st.set_page_config(
    page_title="무신사 검색 & 분석 대시보드",
    page_icon="🔍",
    layout="wide"
)

# 세션 상태 초기화
if 'search_results' not in st.session_state:
    st.session_state.search_results = None
if 'current_search' not in st.session_state:
    st.session_state.current_search = ""

# 타이틀
st.title("🔍 무신사 원피스/스커트 검색 & 분석 대시보드")
st.markdown("##### 💡 키워드 검색 및 필터링 기능")
st.markdown("---")

# 사이드바 - 검색 설정
with st.sidebar:
    st.header("🔍 검색 설정")
    
    # 검색 모드 선택
    search_mode = st.radio(
        "검색 모드",
        ["간단 검색", "상세 검색", "일괄 검색"]
    )
    
    if search_mode == "간단 검색":
        # 검색어 입력
        search_query = st.text_input(
            "검색어",
            placeholder="예: 플로럴 원피스, 체크 스커트",
            help="검색하고 싶은 키워드를 입력하세요"
        )
        
        # 빠른 필터
        st.subheader("빠른 필터")
        
        col1, col2 = st.columns(2)
        with col1:
            price_range = st.select_slider(
                "가격대",
                options=["전체", "~3만원", "3~5만원", "5~10만원", "10만원~"],
                value="전체"
            )
        
        with col2:
            discount_filter = st.selectbox(
                "할인율",
                ["전체", "10% 이상", "20% 이상", "30% 이상", "50% 이상"]
            )
        
        # 스크롤 횟수
        max_scroll = st.slider("검색 깊이 (스크롤 횟수)", 1, 20, 5)
    
    elif search_mode == "상세 검색":
        st.subheader("상세 검색 조건")
        
        # 검색어
        search_query = st.text_input("검색어 (필수)", placeholder="검색 키워드")
        
        # 가격 범위
        col1, col2 = st.columns(2)
        with col1:
            min_price = st.number_input("최소 가격", min_value=0, step=10000)
        with col2:
            max_price = st.number_input("최대 가격", min_value=0, step=10000)
        
        # 브랜드 선택
        brand_input = st.text_area(
            "브랜드 필터",
            placeholder="브랜드명을 입력하세요 (한 줄에 하나씩)",
            height=100
        )
        
        # 카테고리
        category = st.multiselect(
            "카테고리",
            ["원피스", "스커트", "미니원피스", "롱원피스", "미디원피스"],
            default=["원피스", "스커트"]
        )
        
        # 색상 필터
        colors = st.multiselect(
            "색상",
            ["블랙", "화이트", "베이지", "네이비", "그레이", "브라운", "핑크", "블루", "그린", "레드"],
            help="원하는 색상을 선택하세요"
        )
        
        # 패턴/스타일
        patterns = st.multiselect(
            "패턴/스타일",
            ["무지", "체크", "스트라이프", "플로럴", "도트", "레이스", "프릴", "플리츠"],
            help="원하는 패턴이나 스타일을 선택하세요"
        )
        
        max_scroll = st.slider("검색 깊이", 1, 30, 10)
    
    else:  # 일괄 검색
        st.subheader("일괄 검색")
        
        batch_queries = st.text_area(
            "검색어 목록",
            placeholder="검색어를 한 줄에 하나씩 입력\n예:\n플로럴 원피스\n체크 스커트\n데님 원피스",
            height=150
        )
        
        max_scroll = st.slider("검색 깊이 (검색어당)", 1, 10, 3)
    
    # 검색 실행 버튼
    st.markdown("---")
    search_button = st.button("🔍 검색 실행", type="primary", use_container_width=True)
    
    # 데이터 로드 옵션
    st.markdown("---")
    st.subheader("📁 기존 데이터 로드")
    uploaded_file = st.file_uploader(
        "CSV 파일 업로드",
        type=['csv'],
        help="이전에 검색한 결과 파일을 업로드하세요"
    )

# 메인 영역
# 검색 실행
if search_button:
    if search_mode == "간단 검색" and search_query:
        with st.spinner(f"'{search_query}' 검색 중..."):
            # 검색 파라미터 구성
            search_params = {
                'query': search_query,
                'max_scroll': max_scroll,
                'price_range': price_range,
                'discount': discount_filter
            }
            
            # 실제 검색 실행 (여기서는 시뮬레이션)
            st.info("검색을 실행하려면 터미널에서 다음 명령을 실행하세요:")
            st.code(f"python musinsa_search_crawler.py")
            st.success(f"검색어 '{search_query}'로 검색을 시작합니다.")
            
            # 세션에 저장
            st.session_state.current_search = search_query
    
    elif search_mode == "상세 검색" and search_query:
        with st.spinner("상세 검색 실행 중..."):
            st.info("상세 검색 조건:")
            search_conditions = {
                "검색어": search_query,
                "가격": f"{min_price:,}원 ~ {max_price:,}원" if max_price > 0 else "전체",
                "브랜드": brand_input.split('\n') if brand_input else "전체",
                "카테고리": category,
                "색상": colors if colors else "전체",
                "패턴": patterns if patterns else "전체"
            }
            st.json(search_conditions)
    
    elif search_mode == "일괄 검색" and batch_queries:
        queries = [q.strip() for q in batch_queries.split('\n') if q.strip()]
        st.info(f"{len(queries)}개 검색어로 일괄 검색을 시작합니다:")
        for q in queries:
            st.write(f"• {q}")
    
    else:
        st.warning("검색어를 입력해주세요.")

# 업로드된 파일 처리
if uploaded_file:
    try:
        df = pd.read_csv(uploaded_file)
        st.session_state.search_results = df
        st.success(f"✅ {len(df)}개 상품 데이터를 로드했습니다.")
    except Exception as e:
        st.error(f"파일 로드 실패: {e}")

# 탭 구성
if st.session_state.search_results is not None or os.path.exists("musinsa_onepiece_all.csv"):
    tabs = st.tabs([
        "📊 검색 결과",
        "📈 가격 분석",
        "🏷️ 브랜드 분석",
        "🎨 스타일 분석",
        "💬 리뷰 분석",
        "🛒 추천 상품"
    ])
    
    # 데이터 로드
    if st.session_state.search_results is not None:
        data = st.session_state.search_results
    else:
        try:
            data = pd.read_csv("musinsa_onepiece_all.csv")
        except:
            data = None
    
    if data is not None:
        # 데이터 전처리
        if '가격' in data.columns:
            data['가격'] = pd.to_numeric(data['가격'], errors='coerce')
        if '할인율' in data.columns:
            data['할인율'] = pd.to_numeric(data['할인율'], errors='coerce')
        
        with tabs[0]:  # 검색 결과
            st.header("📊 검색 결과")
            
            # 필터링 옵션
            col1, col2, col3, col4 = st.columns(4)
            
            with col1:
                if '브랜드' in data.columns:
                    selected_brands = st.multiselect(
                        "브랜드 필터",
                        options=data['브랜드'].unique(),
                        default=[]
                    )
            
            with col2:
                if '가격' in data.columns:
                    price_min = int(data['가격'].min()) if not data['가격'].isna().all() else 0
                    price_max = int(data['가격'].max()) if not data['가격'].isna().all() else 1000000
                    price_filter = st.slider(
                        "가격 범위",
                        min_value=price_min,
                        max_value=price_max,
                        value=(price_min, price_max)
                    )
            
            with col3:
                if '할인율' in data.columns:
                    min_discount = st.number_input(
                        "최소 할인율 (%)",
                        min_value=0,
                        max_value=100,
                        value=0
                    )
            
            with col4:
                sort_by = st.selectbox(
                    "정렬 기준",
                    ["가격 낮은순", "가격 높은순", "할인율 높은순", "브랜드명"]
                )
            
            # 데이터 필터링
            filtered_data = data.copy()
            
            if selected_brands and '브랜드' in filtered_data.columns:
                filtered_data = filtered_data[filtered_data['브랜드'].isin(selected_brands)]
            
            if '가격' in filtered_data.columns:
                filtered_data = filtered_data[
                    (filtered_data['가격'] >= price_filter[0]) &
                    (filtered_data['가격'] <= price_filter[1])
                ]
            
            if '할인율' in filtered_data.columns:
                filtered_data = filtered_data[filtered_data['할인율'] >= min_discount]
            
            # 정렬
            if sort_by == "가격 낮은순" and '가격' in filtered_data.columns:
                filtered_data = filtered_data.sort_values('가격')
            elif sort_by == "가격 높은순" and '가격' in filtered_data.columns:
                filtered_data = filtered_data.sort_values('가격', ascending=False)
            elif sort_by == "할인율 높은순" and '할인율' in filtered_data.columns:
                filtered_data = filtered_data.sort_values('할인율', ascending=False)
            elif sort_by == "브랜드명" and '브랜드' in filtered_data.columns:
                filtered_data = filtered_data.sort_values('브랜드')
            
            # 결과 표시
            col1, col2, col3 = st.columns(3)
            with col1:
                st.metric("검색 결과", f"{len(filtered_data):,}개")
            with col2:
                if '가격' in filtered_data.columns:
                    avg_price = filtered_data['가격'].mean()
                    st.metric("평균 가격", f"₩{avg_price:,.0f}")
            with col3:
                if '할인율' in filtered_data.columns:
                    avg_discount = filtered_data['할인율'].mean()
                    st.metric("평균 할인율", f"{avg_discount:.1f}%")
            
            # 상품 목록
            st.subheader("상품 목록")
            
            # 표시할 컬럼 선택
            display_columns = []
            for col in ['브랜드', '상품명', '가격', '원가', '할인율', '상품ID', '상품링크']:
                if col in filtered_data.columns:
                    display_columns.append(col)
            
            if display_columns:
                st.dataframe(
                    filtered_data[display_columns].head(100),
                    use_container_width=True,
                    hide_index=True
                )
            
            # 다운로드 버튼
            csv = filtered_data.to_csv(index=False, encoding='utf-8-sig')
            st.download_button(
                label="📥 검색 결과 다운로드 (CSV)",
                data=csv,
                file_name=f"search_results_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv",
                mime="text/csv"
            )
        
        with tabs[1]:  # 가격 분석
            st.header("📈 가격 분석")
            
            if '가격' in data.columns:
                col1, col2 = st.columns(2)
                
                with col1:
                    # 가격 분포
                    fig = px.histogram(
                        data,
                        x='가격',
                        nbins=30,
                        title="가격 분포",
                        labels={'가격': '가격 (원)', 'count': '상품 수'}
                    )
                    st.plotly_chart(fig, use_container_width=True)
                
                with col2:
                    # 할인율 분포
                    if '할인율' in data.columns:
                        fig = px.histogram(
                            data[data['할인율'] > 0],
                            x='할인율',
                            nbins=20,
                            title="할인율 분포",
                            labels={'할인율': '할인율 (%)', 'count': '상품 수'}
                        )
                        st.plotly_chart(fig, use_container_width=True)
                
                # 가격대별 상품 수
                st.subheader("가격대별 분포")
                price_ranges = pd.cut(
                    data['가격'],
                    bins=[0, 30000, 50000, 100000, 200000, float('inf')],
                    labels=['~3만원', '3-5만원', '5-10만원', '10-20만원', '20만원~']
                )
                price_dist = price_ranges.value_counts().sort_index()
                
                fig = px.bar(
                    x=price_dist.index,
                    y=price_dist.values,
                    title="가격대별 상품 수",
                    labels={'x': '가격대', 'y': '상품 수'}
                )
                st.plotly_chart(fig, use_container_width=True)
        
        with tabs[2]:  # 브랜드 분석
            st.header("🏷️ 브랜드 분석")
            
            if '브랜드' in data.columns:
                # 브랜드별 상품 수
                brand_counts = data['브랜드'].value_counts().head(20)
                
                col1, col2 = st.columns(2)
                
                with col1:
                    fig = px.bar(
                        x=brand_counts.values,
                        y=brand_counts.index,
                        orientation='h',
                        title="브랜드별 상품 수 (Top 20)",
                        labels={'x': '상품 수', 'y': '브랜드'}
                    )
                    fig.update_layout(height=600)
                    st.plotly_chart(fig, use_container_width=True)
                
                with col2:
                    if '가격' in data.columns:
                        # 브랜드별 평균 가격
                        brand_avg_price = data.groupby('브랜드')['가격'].mean().sort_values(ascending=False).head(20)
                        
                        fig = px.bar(
                            x=brand_avg_price.values,
                            y=brand_avg_price.index,
                            orientation='h',
                            title="브랜드별 평균 가격 (Top 20)",
                            labels={'x': '평균 가격 (원)', 'y': '브랜드'},
                            color=brand_avg_price.values,
                            color_continuous_scale='Viridis'
                        )
                        fig.update_layout(height=600)
                        st.plotly_chart(fig, use_container_width=True)
        
        with tabs[3]:  # 스타일 분석
            st.header("🎨 스타일 분석")
            
            # 키워드 분석 (상품명에서 추출)
            if '상품명' in data.columns or 'TEXT' in data.columns:
                text_column = '상품명' if '상품명' in data.columns else 'TEXT'
                
                # 스타일 키워드
                style_keywords = {
                    '플로럴': ['플로럴', '꽃', '플라워'],
                    '체크': ['체크', '격자'],
                    '스트라이프': ['스트라이프', '줄무늬'],
                    '도트': ['도트', '물방울'],
                    '레이스': ['레이스'],
                    '프릴': ['프릴', '러플'],
                    '플리츠': ['플리츠', '주름'],
                    '데님': ['데님', '청'],
                    '니트': ['니트'],
                    '셔츠': ['셔츠']
                }
                
                style_counts = {}
                for style, keywords in style_keywords.items():
                    count = 0
                    for keyword in keywords:
                        count += data[text_column].str.contains(keyword, na=False).sum()
                    style_counts[style] = count
                
                # 스타일 분포 차트
                style_df = pd.DataFrame(list(style_counts.items()), columns=['스타일', '상품 수'])
                style_df = style_df.sort_values('상품 수', ascending=False)
                
                fig = px.pie(
                    style_df,
                    values='상품 수',
                    names='스타일',
                    title="스타일별 상품 분포"
                )
                st.plotly_chart(fig, use_container_width=True)
                
                # 색상 키워드 분석
                color_keywords = {
                    '블랙': ['블랙', '검정', '검은'],
                    '화이트': ['화이트', '흰', '백색'],
                    '베이지': ['베이지', '크림'],
                    '네이비': ['네이비', '남색'],
                    '그레이': ['그레이', '회색'],
                    '브라운': ['브라운', '갈색'],
                    '핑크': ['핑크', '분홍'],
                    '블루': ['블루', '파란', '청색'],
                    '그린': ['그린', '초록', '녹색'],
                    '레드': ['레드', '빨간', '적색']
                }
                
                color_counts = {}
                for color, keywords in color_keywords.items():
                    count = 0
                    for keyword in keywords:
                        count += data[text_column].str.contains(keyword, na=False).sum()
                    color_counts[color] = count
                
                # 색상 분포 차트
                color_df = pd.DataFrame(list(color_counts.items()), columns=['색상', '상품 수'])
                color_df = color_df.sort_values('상품 수', ascending=False)
                
                fig = px.bar(
                    color_df,
                    x='색상',
                    y='상품 수',
                    title="색상별 상품 분포",
                    color='상품 수',
                    color_continuous_scale='Rainbow'
                )
                st.plotly_chart(fig, use_container_width=True)
        
        with tabs[4]:  # 리뷰 분석
            st.header("💬 리뷰 분석")
            
            # 리뷰 데이터 확인
            review_files = [
                "musinsa_reviews_enhanced.csv",
                "musinsa_reviews.csv"
            ]
            
            reviews_df = None
            for file in review_files:
                if os.path.exists(file):
                    try:
                        reviews_df = pd.read_csv(file)
                        st.success(f"리뷰 데이터 로드: {len(reviews_df)}개 리뷰")
                        break
                    except:
                        continue
            
            if reviews_df is not None:
                # 리뷰 분석
                analyzer = ReviewAnalyzer()
                sentiment_df = analyzer.analyze_sentiment(reviews_df)
                
                col1, col2, col3 = st.columns(3)
                
                with col1:
                    # 감성 분포
                    sentiment_counts = sentiment_df['sentiment'].value_counts()
                    fig = px.pie(
                        values=sentiment_counts.values,
                        names=sentiment_counts.index,
                        title="리뷰 감성 분포",
                        color_discrete_map={'positive': '#28a745', 'negative': '#dc3545', 'neutral': '#6c757d'}
                    )
                    st.plotly_chart(fig, use_container_width=True)
                
                with col2:
                    st.metric("총 리뷰 수", f"{len(reviews_df):,}개")
                    positive_ratio = (sentiment_df['sentiment'] == 'positive').mean() * 100
                    st.metric("긍정 리뷰 비율", f"{positive_ratio:.1f}%")
                
                with col3:
                    # 브랜드별 리뷰 수
                    if 'brand' in reviews_df.columns:
                        brand_review_counts = reviews_df['brand'].value_counts().head(10)
                        st.subheader("리뷰 많은 브랜드")
                        for brand, count in brand_review_counts.items():
                            st.write(f"• {brand}: {count}개")
            else:
                st.info("리뷰 데이터가 없습니다. 리뷰 크롤러를 실행해주세요.")
        
        with tabs[5]:  # 추천 상품
            st.header("🛒 추천 상품")
            
            st.subheader("💎 베스트 상품")
            
            # 할인율 높은 상품
            if '할인율' in data.columns and '가격' in data.columns:
                best_discount = data.nlargest(10, '할인율')
                
                st.write("### 🔥 할인율 TOP 10")
                for idx, row in best_discount.iterrows():
                    col1, col2, col3, col4 = st.columns([3, 2, 2, 2])
                    with col1:
                        st.write(f"**{row.get('브랜드', 'Unknown')}**")
                    with col2:
                        st.write(f"₩{row['가격']:,.0f}")
                    with col3:
                        st.write(f"🔻 {row['할인율']:.0f}%")
                    with col4:
                        if '상품링크' in row:
                            st.link_button("구매하기", row['상품링크'])
            
            # 가성비 상품 (낮은 가격 + 높은 할인율)
            if '가격' in data.columns and '할인율' in data.columns:
                st.write("### 💰 가성비 추천")
                
                # 가성비 점수 계산 (정규화된 할인율 / 정규화된 가격)
                data_copy = data.copy()
                data_copy['price_norm'] = (data_copy['가격'] - data_copy['가격'].min()) / (data_copy['가격'].max() - data_copy['가격'].min())
                data_copy['discount_norm'] = data_copy['할인율'] / 100
                data_copy['value_score'] = data_copy['discount_norm'] / (data_copy['price_norm'] + 0.1)
                
                best_value = data_copy.nlargest(10, 'value_score')
                
                for idx, row in best_value.iterrows():
                    col1, col2, col3 = st.columns([3, 2, 2])
                    with col1:
                        st.write(f"**{row.get('브랜드', 'Unknown')}**")
                    with col2:
                        st.write(f"₩{row['가격']:,.0f} ({row['할인율']:.0f}% 할인)")
                    with col3:
                        st.write(f"⭐ 가성비 점수: {row['value_score']:.2f}")

else:
    # 데이터가 없을 때
    st.info("""
    👋 검색을 시작하려면:
    1. 왼쪽 사이드바에서 검색어와 조건을 입력하세요
    2. '검색 실행' 버튼을 클릭하세요
    3. 또는 기존 CSV 파일을 업로드하세요
    
    💡 검색 팁:
    - 구체적인 키워드를 사용하면 더 정확한 결과를 얻을 수 있습니다
    - 가격과 할인율 필터를 활용하여 원하는 상품을 찾으세요
    - 여러 검색어를 한번에 검색하려면 '일괄 검색' 모드를 사용하세요
    """)

# 푸터
st.markdown("---")
st.markdown("🔍 무신사 검색 & 분석 대시보드 | " + datetime.now().strftime("%Y-%m-%d %H:%M"))