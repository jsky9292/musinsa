import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from wordcloud import WordCloud
import matplotlib.pyplot as plt
from datetime import datetime, timedelta
import re
import numpy as np
from review_analyzer import ReviewAnalyzer
import warnings
warnings.filterwarnings('ignore')

# 페이지 설정
st.set_page_config(
    page_title="무신사 원피스 고급 분석 대시보드",
    page_icon="👗",
    layout="wide"
)

# 스타일 설정
st.markdown("""
<style>
    .main > div {
        padding-top: 2rem;
    }
    .stTabs [data-baseweb="tab-list"] button [data-testid="stMarkdownContainer"] p {
        font-size: 1.1rem;
    }
    .metric-card {
        background-color: #f0f2f6;
        padding: 1rem;
        border-radius: 0.5rem;
        margin: 0.5rem 0;
    }
</style>
""", unsafe_allow_html=True)

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

# 리뷰 분석
@st.cache_data
def analyze_reviews(reviews_df):
    analyzer = ReviewAnalyzer()
    sentiment_df = analyzer.analyze_sentiment(reviews_df)
    return sentiment_df, analyzer

# 타이틀
st.title("👗 무신사 원피스/스커트 고급 분석 대시보드")
st.markdown("##### 💡 리뷰 감성 분석 & 마케팅 인사이트 도출")
st.markdown("---")

# 데이터 로드
products_df, reviews_df = load_data()

if products_df is not None and reviews_df is not None:
    
    # 리뷰 분석 실행
    with st.spinner("리뷰 데이터 분석 중..."):
        sentiment_df, analyzer = analyze_reviews(reviews_df)
    
    # 탭 구성
    tab1, tab2, tab3, tab4, tab5 = st.tabs([
        "📊 전체 개요", 
        "💬 리뷰 감성 분석", 
        "🎯 마케팅 인사이트", 
        "📈 상품별 분석",
        "💡 개선사항 & 제안"
    ])
    
    with tab1:
        st.header("📊 전체 개요")
        
        # 주요 지표
        col1, col2, col3, col4, col5, col6 = st.columns(6)
        
        with col1:
            st.metric("총 상품 수", f"{len(products_df):,}개")
        
        with col2:
            st.metric("총 리뷰 수", f"{len(reviews_df):,}개")
        
        with col3:
            positive_ratio = (sentiment_df['sentiment'] == 'positive').mean() * 100
            st.metric("긍정 리뷰 비율", f"{positive_ratio:.1f}%")
        
        with col4:
            negative_ratio = (sentiment_df['sentiment'] == 'negative').mean() * 100
            st.metric("부정 리뷰 비율", f"{negative_ratio:.1f}%")
        
        with col5:
            avg_price = products_df['가격'].mean()
            st.metric("평균 가격", f"₩{avg_price:,.0f}")
        
        with col6:
            avg_discount = products_df['할인율'].mean()
            st.metric("평균 할인율", f"{avg_discount:.1f}%")
        
        st.markdown("---")
        
        # 브랜드별 리뷰 감성 분석
        col1, col2 = st.columns(2)
        
        with col1:
            # 브랜드별 감성 비율
            brand_sentiment = sentiment_df.groupby(['brand', 'sentiment']).size().unstack(fill_value=0)
            brand_sentiment['total'] = brand_sentiment.sum(axis=1)
            brand_sentiment = brand_sentiment.sort_values('total', ascending=False).head(10)
            
            fig = go.Figure()
            for sentiment in ['positive', 'negative', 'neutral']:
                if sentiment in brand_sentiment.columns:
                    fig.add_trace(go.Bar(
                        name=sentiment.capitalize(),
                        x=brand_sentiment.index,
                        y=brand_sentiment[sentiment],
                        marker_color={'positive': '#28a745', 'negative': '#dc3545', 'neutral': '#6c757d'}[sentiment]
                    ))
            
            fig.update_layout(
                title="브랜드별 리뷰 감성 분포 (Top 10)",
                barmode='stack',
                height=400
            )
            st.plotly_chart(fig, use_container_width=True)
        
        with col2:
            # 감성 점수 분포
            fig = px.scatter(
                sentiment_df,
                x='positive_score',
                y='negative_score',
                color='sentiment',
                color_discrete_map={'positive': '#28a745', 'negative': '#dc3545', 'neutral': '#6c757d'},
                title="리뷰 감성 점수 분포",
                labels={'positive_score': '긍정 점수', 'negative_score': '부정 점수'}
            )
            fig.update_layout(height=400)
            st.plotly_chart(fig, use_container_width=True)
    
    with tab2:
        st.header("💬 리뷰 감성 분석")
        
        # 감성별 리뷰 비율
        col1, col2, col3 = st.columns(3)
        
        with col1:
            # 감성 분포 파이 차트
            sentiment_counts = sentiment_df['sentiment'].value_counts()
            fig = px.pie(
                values=sentiment_counts.values,
                names=sentiment_counts.index,
                title="전체 리뷰 감성 분포",
                color_discrete_map={'positive': '#28a745', 'negative': '#dc3545', 'neutral': '#6c757d'}
            )
            st.plotly_chart(fig, use_container_width=True)
        
        with col2:
            # 긍정 리뷰 주요 키워드
            st.subheader("😊 긍정 리뷰 주요 이유")
            positive_reviews = sentiment_df[sentiment_df['sentiment'] == 'positive']
            positive_reasons = []
            for reasons in positive_reviews['positive_reasons']:
                if reasons:
                    positive_reasons.extend(reasons.split(', '))
            
            from collections import Counter
            reason_counts = Counter(positive_reasons)
            top_positive = reason_counts.most_common(10)
            
            for reason, count in top_positive:
                if ':' in reason:
                    category, keyword = reason.split(':')
                    percentage = (count / len(positive_reviews) * 100) if len(positive_reviews) > 0 else 0
                    st.write(f"**{category}** - {keyword}: {count}회 ({percentage:.1f}%)")
        
        with col3:
            # 부정 리뷰 주요 키워드
            st.subheader("😞 부정 리뷰 주요 이유")
            negative_reviews = sentiment_df[sentiment_df['sentiment'] == 'negative']
            negative_reasons = []
            for reasons in negative_reviews['negative_reasons']:
                if reasons:
                    negative_reasons.extend(reasons.split(', '))
            
            reason_counts = Counter(negative_reasons)
            top_negative = reason_counts.most_common(10)
            
            for reason, count in top_negative:
                if ':' in reason:
                    category, keyword = reason.split(':')
                    percentage = (count / len(negative_reviews) * 100) if len(negative_reviews) > 0 else 0
                    st.write(f"**{category}** - {keyword}: {count}회 ({percentage:.1f}%)")
        
        st.markdown("---")
        
        # 감성별 리뷰 예시
        st.subheader("📝 감성별 리뷰 예시")
        
        col1, col2, col3 = st.columns(3)
        
        with col1:
            st.markdown("### 🟢 긍정 리뷰")
            positive_samples = sentiment_df[sentiment_df['sentiment'] == 'positive'].head(3)
            for idx, row in positive_samples.iterrows():
                with st.expander(f"긍정 리뷰 #{idx+1}"):
                    st.write(row['text'])
                    st.caption(f"긍정 이유: {row['positive_reasons']}")
        
        with col2:
            st.markdown("### 🔴 부정 리뷰")
            negative_samples = sentiment_df[sentiment_df['sentiment'] == 'negative'].head(3)
            for idx, row in negative_samples.iterrows():
                with st.expander(f"부정 리뷰 #{idx+1}"):
                    st.write(row['text'])
                    st.caption(f"부정 이유: {row['negative_reasons']}")
        
        with col3:
            st.markdown("### ⚪ 중립 리뷰")
            neutral_samples = sentiment_df[sentiment_df['sentiment'] == 'neutral'].head(3)
            for idx, row in neutral_samples.iterrows():
                with st.expander(f"중립 리뷰 #{idx+1}"):
                    st.write(row['text'])
    
    with tab3:
        st.header("🎯 마케팅 인사이트")
        
        # 마케팅 인사이트 도출
        marketing_insights = analyzer.get_marketing_insights(sentiment_df)
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.subheader("💪 강점 (마케팅 소구점)")
            st.markdown("##### 고객이 가장 만족하는 포인트")
            
            for strength in marketing_insights['strengths']:
                with st.container():
                    st.markdown(f"""
                    <div class="metric-card">
                        <h4>{strength['marketing_message']}</h4>
                        <p>카테고리: {strength['category']} | 빈도: {strength['frequency']}회 ({strength['percentage']:.1f}%)</p>
                    </div>
                    """, unsafe_allow_html=True)
            
            # 추천 마케팅 메시지
            st.subheader("📢 추천 마케팅 메시지")
            if marketing_insights['strengths']:
                top_strength = marketing_insights['strengths'][0]
                st.info(f"""
                **메인 카피:** {top_strength['marketing_message']}
                
                **서브 카피 제안:**
                - "실제 구매 고객이 증명하는 품질"
                - "리뷰가 말해주는 진짜 가치"
                - "고민하지 마세요, {top_strength['percentage']:.0f}%가 선택했습니다"
                """)
        
        with col2:
            st.subheader("⚠️ 약점 (개선 필요)")
            st.markdown("##### 고객 불만족 요인")
            
            for weakness in marketing_insights['weaknesses']:
                with st.container():
                    st.markdown(f"""
                    <div class="metric-card" style="background-color: #fff3cd;">
                        <h4>{weakness['category']} - {weakness['keyword']}</h4>
                        <p>빈도: {weakness['frequency']}회 ({weakness['percentage']:.1f}%)</p>
                        <p><strong>개선 제안:</strong> {weakness['improvement_suggestion']}</p>
                    </div>
                    """, unsafe_allow_html=True)
        
        st.markdown("---")
        
        # 고객 니즈
        if marketing_insights['customer_needs']:
            st.subheader("🎤 고객의 목소리 (Voice of Customer)")
            st.markdown("##### 고객이 원하는 것")
            
            for need in marketing_insights['customer_needs']:
                with st.expander(f"'{need['keyword']}' 관련 고객 요구"):
                    for example in need['examples'][:3]:
                        st.write(f"• {example[:200]}")
    
    with tab4:
        st.header("📈 상품별 상세 분석")
        
        # 상품 선택
        products_with_reviews = sentiment_df['product_id'].unique()
        
        # 리뷰가 있는 상품 정보 매칭
        products_info = []
        for pid in products_with_reviews:
            brand = sentiment_df[sentiment_df['product_id'] == pid]['brand'].iloc[0]
            review_count = len(sentiment_df[sentiment_df['product_id'] == pid])
            products_info.append(f"{brand} - {pid} ({review_count}개 리뷰)")
        
        selected_product_info = st.selectbox("분석할 상품 선택", products_info)
        
        if selected_product_info:
            selected_product_id = int(selected_product_info.split(' - ')[1].split(' ')[0])
            
            # 상품별 분석 실행
            product_analysis = analyzer.analyze_product_reviews(selected_product_id, reviews_df)
            
            if product_analysis:
                col1, col2, col3 = st.columns(3)
                
                with col1:
                    st.metric("총 리뷰 수", f"{product_analysis['total_reviews']}개")
                    
                    # 감성 비율
                    sentiment_ratio = product_analysis['sentiment_ratio']
                    fig = px.pie(
                        values=list(sentiment_ratio.values()),
                        names=list(sentiment_ratio.keys()),
                        title="감성 분포",
                        color_discrete_map={'positive': '#28a745', 'negative': '#dc3545', 'neutral': '#6c757d'}
                    )
                    st.plotly_chart(fig, use_container_width=True)
                
                with col2:
                    st.metric("평균 긍정 점수", f"{product_analysis['avg_positive_score']:.1f}")
                    
                    # 긍정 테마
                    st.subheader("긍정 키워드")
                    for keyword, count in product_analysis['positive_themes'][:5]:
                        st.write(f"• {keyword}: {count}회")
                
                with col3:
                    st.metric("평균 부정 점수", f"{product_analysis['avg_negative_score']:.1f}")
                    
                    # 부정 테마
                    st.subheader("부정 키워드")
                    for keyword, count in product_analysis['negative_themes'][:5]:
                        st.write(f"• {keyword}: {count}회")
                
                # 상품별 마케팅 인사이트
                st.markdown("---")
                st.subheader("🎯 상품별 마케팅 전략")
                
                product_insights = product_analysis['marketing_insights']
                
                col1, col2 = st.columns(2)
                
                with col1:
                    if product_insights['strengths']:
                        st.success(f"""
                        **주요 강점:**
                        {product_insights['strengths'][0]['marketing_message'] if product_insights['strengths'] else ''}
                        """)
                
                with col2:
                    if product_insights['weaknesses']:
                        st.warning(f"""
                        **주요 개선점:**
                        {product_insights['weaknesses'][0]['improvement_suggestion'] if product_insights['weaknesses'] else ''}
                        """)
    
    with tab5:
        st.header("💡 개선사항 & 제안")
        
        # 전체 개선사항 분석
        improvements = analyzer.get_improvement_insights(sentiment_df)
        
        st.subheader("📋 카테고리별 개선 우선순위")
        
        if improvements:
            # 개선 우선순위 정렬
            sorted_improvements = sorted(improvements.items(), key=lambda x: x[1]['count'], reverse=True)
            
            for category, data in sorted_improvements:
                with st.expander(f"{category} - {data['count']}건 ({data['percentage']:.1f}%)"):
                    st.write(f"**개선 필요도:** {'🔴' * min(5, int(data['percentage']//20 + 1))}")
                    
                    st.write("**관련 리뷰 예시:**")
                    for example in data['examples']:
                        st.write(f"• {example}...")
                    
                    # 카테고리별 구체적 개선안
                    st.write("**개선 제안:**")
                    if category == '사이즈':
                        st.write("""
                        1. 상세 사이즈표 제공 (실측 치수 포함)
                        2. 모델 착용 정보 상세 기재
                        3. 사이즈 교환 정책 개선
                        """)
                    elif category == '소재':
                        st.write("""
                        1. 소재 구성 상세 설명
                        2. 계절별 착용감 정보 제공
                        3. 세탁 및 관리법 안내
                        """)
                    elif category == '색상':
                        st.write("""
                        1. 다양한 조명에서 촬영한 이미지 제공
                        2. 실제 색상 차이 안내 문구 추가
                        3. 색상 교환 보장 서비스
                        """)
        
        st.markdown("---")
        
        # 종합 제안
        st.subheader("🚀 종합 개선 제안")
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.info("""
            **📈 마케팅 전략 제안**
            
            1. **강점 극대화**
               - 긍정 리뷰 키워드를 활용한 상품 설명 강화
               - 실제 구매 고객 후기를 메인 페이지에 노출
               - SNS 마케팅 시 만족도 높은 포인트 집중 홍보
            
            2. **타겟 마케팅**
               - 긍정 리뷰가 많은 브랜드 집중 프로모션
               - 고객 만족도 높은 카테고리 번들 상품 기획
            
            3. **신뢰도 구축**
               - 리뷰 인증 배지 시스템 도입
               - 포토 리뷰 인센티브 강화
            """)
        
        with col2:
            st.warning("""
            **🔧 운영 개선 제안**
            
            1. **상품 정보 개선**
               - 사이즈 가이드 표준화
               - 360도 상품 이미지 제공
               - 소재별 착용감 동영상 제작
            
            2. **고객 서비스**
               - 사이즈 문의 챗봇 도입
               - 교환/반품 프로세스 간소화
               - 구매 전 상담 서비스 강화
            
            3. **품질 관리**
               - 부정 리뷰 많은 상품 재검토
               - 시즌별 소재 최적화
               - QC 기준 강화
            """)
        
        # 데이터 다운로드
        st.markdown("---")
        st.subheader("📥 분석 결과 다운로드")
        
        col1, col2, col3 = st.columns(3)
        
        with col1:
            csv = sentiment_df.to_csv(index=False, encoding='utf-8-sig')
            st.download_button(
                label="📊 감성 분석 결과 (CSV)",
                data=csv,
                file_name=f"sentiment_analysis_{datetime.now().strftime('%Y%m%d')}.csv",
                mime="text/csv"
            )
        
        with col2:
            # 마케팅 인사이트를 DataFrame으로 변환
            insights_data = []
            for strength in marketing_insights['strengths']:
                insights_data.append({
                    'type': '강점',
                    'category': strength['category'],
                    'keyword': strength['keyword'],
                    'frequency': strength['frequency'],
                    'percentage': strength['percentage'],
                    'message': strength['marketing_message']
                })
            
            if insights_data:
                insights_df = pd.DataFrame(insights_data)
                csv_insights = insights_df.to_csv(index=False, encoding='utf-8-sig')
                st.download_button(
                    label="🎯 마케팅 인사이트 (CSV)",
                    data=csv_insights,
                    file_name=f"marketing_insights_{datetime.now().strftime('%Y%m%d')}.csv",
                    mime="text/csv"
                )
        
        with col3:
            # 개선사항 데이터
            improvements_data = []
            for category, data in improvements.items():
                improvements_data.append({
                    'category': category,
                    'count': data['count'],
                    'percentage': data['percentage']
                })
            
            if improvements_data:
                improvements_df = pd.DataFrame(improvements_data)
                csv_improvements = improvements_df.to_csv(index=False, encoding='utf-8-sig')
                st.download_button(
                    label="💡 개선사항 (CSV)",
                    data=csv_improvements,
                    file_name=f"improvements_{datetime.now().strftime('%Y%m%d')}.csv",
                    mime="text/csv"
                )

else:
    st.error("데이터 파일을 찾을 수 없습니다.")
    st.info("""
    필요한 파일:
    - musinsa_onepiece_all.csv (상품 데이터)
    - musinsa_reviews.csv (리뷰 데이터)
    
    실행 순서:
    1. `python musinsa_onepiece.py` - 상품 데이터 수집
    2. `python musinsa_review_crawler.py` - 리뷰 데이터 수집  
    3. `streamlit run dashboard_advanced.py` - 대시보드 실행
    """)

# 푸터
st.markdown("---")
st.markdown("🚀 무신사 원피스/스커트 고급 분석 대시보드 | " + datetime.now().strftime("%Y-%m-%d %H:%M"))