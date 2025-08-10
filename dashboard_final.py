import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import matplotlib.pyplot as plt
from datetime import datetime, timedelta
import re
import numpy as np
from review_analyzer import ReviewAnalyzer
from brand_analyzer import BrandAnalyzer
import warnings
warnings.filterwarnings('ignore')

# 페이지 설정
st.set_page_config(
    page_title="무신사 원피스 통합 분석 대시보드",
    page_icon="👗",
    layout="wide"
)

# 스타일 설정
st.markdown("""
<style>
    .main > div {
        padding-top: 2rem;
    }
    .brand-card {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
        padding: 1.5rem;
        border-radius: 10px;
        margin: 1rem 0;
    }
    .metric-card {
        background-color: #f0f2f6;
        padding: 1rem;
        border-radius: 0.5rem;
        margin: 0.5rem 0;
    }
    .success-card {
        background-color: #d4edda;
        border-left: 4px solid #28a745;
        padding: 1rem;
        margin: 0.5rem 0;
    }
    .warning-card {
        background-color: #fff3cd;
        border-left: 4px solid #ffc107;
        padding: 1rem;
        margin: 0.5rem 0;
    }
</style>
""", unsafe_allow_html=True)

# 데이터 로드
@st.cache_data
def load_data():
    try:
        products_df = pd.read_csv("musinsa_onepiece_all.csv")
        
        # 리뷰 데이터 - enhanced 버전 우선, 없으면 일반 버전
        try:
            reviews_df = pd.read_csv("musinsa_reviews_enhanced.csv")
        except:
            reviews_df = pd.read_csv("musinsa_reviews.csv")
        
        # 가격 데이터 정리
        products_df['가격'] = pd.to_numeric(products_df['가격'], errors='coerce')
        products_df['원가'] = pd.to_numeric(products_df['원가'], errors='coerce')
        products_df['할인율'] = pd.to_numeric(products_df['할인율'], errors='coerce')
        
        return products_df, reviews_df
    except Exception as e:
        st.error(f"데이터 로딩 오류: {e}")
        return None, None

# 분석 실행
@st.cache_data
def run_analysis(reviews_df, products_df):
    # 리뷰 분석
    review_analyzer = ReviewAnalyzer()
    sentiment_df = review_analyzer.analyze_sentiment(reviews_df)
    
    # 브랜드 분석
    brand_analyzer = BrandAnalyzer()
    
    return sentiment_df, review_analyzer, brand_analyzer

# 타이틀
st.title("👗 무신사 원피스/스커트 통합 분석 대시보드")
st.markdown("##### 💡 브랜드별 심층 분석 & 마케팅 인사이트")
st.markdown("---")

# 데이터 로드
products_df, reviews_df = load_data()

if products_df is not None and reviews_df is not None:
    
    # 분석 실행
    with st.spinner("데이터 분석 중..."):
        sentiment_df, review_analyzer, brand_analyzer = run_analysis(reviews_df, products_df)
    
    # 탭 구성
    tabs = st.tabs([
        "📊 대시보드 개요",
        "🏢 브랜드별 심층 분석", 
        "🆚 브랜드 비교",
        "💬 리뷰 감성 분석",
        "🎯 마케팅 인사이트",
        "📈 트렌드 분석",
        "💡 전략 제안"
    ])
    
    with tabs[0]:  # 대시보드 개요
        st.header("📊 대시보드 개요")
        
        # 주요 지표
        col1, col2, col3, col4, col5, col6 = st.columns(6)
        
        with col1:
            st.metric("총 상품 수", f"{len(products_df):,}개")
        
        with col2:
            st.metric("총 리뷰 수", f"{len(reviews_df):,}개")
        
        with col3:
            unique_brands = products_df['브랜드'].nunique()
            st.metric("브랜드 수", f"{unique_brands}개")
        
        with col4:
            avg_price = products_df['가격'].mean()
            st.metric("평균 가격", f"₩{avg_price:,.0f}")
        
        with col5:
            positive_ratio = (sentiment_df['sentiment'] == 'positive').mean() * 100
            st.metric("긍정 리뷰", f"{positive_ratio:.1f}%", delta=f"+{positive_ratio-50:.1f}%")
        
        with col6:
            if 'page_number' in reviews_df.columns:
                avg_pages = reviews_df.groupby('product_id')['page_number'].max().mean()
                st.metric("평균 리뷰 페이지", f"{avg_pages:.1f}페이지")
            else:
                st.metric("리뷰 밀도", f"{len(reviews_df)/len(products_df):.1f}개/상품")
        
        st.markdown("---")
        
        # 상위 브랜드 현황
        col1, col2 = st.columns(2)
        
        with col1:
            # 브랜드별 리뷰 수
            brand_review_counts = reviews_df['brand'].value_counts().head(15)
            fig = px.bar(
                x=brand_review_counts.values,
                y=brand_review_counts.index,
                orientation='h',
                title="브랜드별 리뷰 수 (Top 15)",
                labels={'x': '리뷰 수', 'y': '브랜드'},
                color=brand_review_counts.values,
                color_continuous_scale='Viridis'
            )
            fig.update_layout(height=500)
            st.plotly_chart(fig, use_container_width=True)
        
        with col2:
            # 브랜드별 감성 분포
            brand_sentiment = sentiment_df.groupby('brand')['sentiment'].value_counts().unstack(fill_value=0)
            brand_sentiment['positive_ratio'] = brand_sentiment.get('positive', 0) / brand_sentiment.sum(axis=1) * 100
            top_positive_brands = brand_sentiment.nlargest(15, 'positive_ratio')
            
            fig = px.bar(
                x=top_positive_brands['positive_ratio'],
                y=top_positive_brands.index,
                orientation='h',
                title="브랜드별 긍정 리뷰 비율 (Top 15)",
                labels={'x': '긍정 리뷰 비율 (%)', 'y': '브랜드'},
                color=top_positive_brands['positive_ratio'],
                color_continuous_scale='RdYlGn'
            )
            fig.update_layout(height=500)
            st.plotly_chart(fig, use_container_width=True)
    
    with tabs[1]:  # 브랜드별 심층 분석
        st.header("🏢 브랜드별 심층 분석")
        
        # 브랜드 선택
        top_brands = reviews_df['brand'].value_counts().head(20).index.tolist()
        selected_brand = st.selectbox(
            "분석할 브랜드 선택",
            options=top_brands,
            format_func=lambda x: f"{x} ({reviews_df[reviews_df['brand']==x].shape[0]}개 리뷰)"
        )
        
        if selected_brand:
            # 브랜드 리포트 생성
            brand_report = brand_analyzer.generate_brand_report(
                selected_brand, reviews_df, sentiment_df, products_df
            )
            
            if brand_report:
                # 브랜드 카드
                st.markdown(f"""
                <div class="brand-card">
                    <h2>{selected_brand}</h2>
                    <p>총 {brand_report['basic_stats']['total_products']}개 상품 | 
                       {brand_report['basic_stats']['total_reviews']}개 리뷰 | 
                       평균 ₩{brand_report['basic_stats']['avg_price']:,.0f}</p>
                </div>
                """, unsafe_allow_html=True)
                
                # 4개 컬럼으로 주요 지표 표시
                col1, col2, col3, col4 = st.columns(4)
                
                with col1:
                    st.metric(
                        "브랜드 포지션",
                        brand_report['positioning']['primary_position'][0],
                        f"{brand_report['positioning']['primary_position'][1]:.1f}%"
                    )
                
                with col2:
                    st.metric(
                        "긍정 리뷰 비율",
                        f"{brand_report['swot']['positive_ratio']:.1f}%",
                        delta=f"{brand_report['swot']['positive_ratio']-50:.1f}%"
                    )
                
                with col3:
                    if brand_report['purchase_factors']['ranked_factors']:
                        st.metric(
                            "주요 구매 요인",
                            brand_report['purchase_factors']['ranked_factors'][0][0],
                            f"{brand_report['purchase_factors']['ranked_factors'][0][1]:.1f}%"
                        )
                
                with col4:
                    st.metric(
                        "타겟 연령층",
                        brand_report['target_customers']['primary_age_group'],
                        "주요 고객층"
                    )
                
                st.markdown("---")
                
                # 상세 분석
                col1, col2 = st.columns(2)
                
                with col1:
                    # 포지셔닝 분석
                    st.subheader("🎯 브랜드 포지셔닝")
                    positioning_df = pd.DataFrame(
                        list(brand_report['positioning']['positioning_percentages'].items()),
                        columns=['포지션', '비율']
                    ).sort_values('비율', ascending=False)
                    
                    fig = px.pie(
                        positioning_df,
                        values='비율',
                        names='포지션',
                        title="브랜드 포지셔닝 분포"
                    )
                    st.plotly_chart(fig, use_container_width=True)
                    
                    # 구매 요인
                    st.subheader("🛒 구매 결정 요인")
                    if brand_report['purchase_factors']['ranked_factors']:
                        factors_df = pd.DataFrame(
                            brand_report['purchase_factors']['ranked_factors'][:7],
                            columns=['요인', '비율']
                        )
                        
                        fig = px.bar(
                            factors_df,
                            x='비율',
                            y='요인',
                            orientation='h',
                            title="구매 결정 요인 순위",
                            color='비율',
                            color_continuous_scale='Blues'
                        )
                        st.plotly_chart(fig, use_container_width=True)
                
                with col2:
                    # SWOT 분석
                    st.subheader("💪 강점 분석")
                    if brand_report['swot']['strengths']:
                        for strength in brand_report['swot']['strengths'][:3]:
                            st.markdown(f"""
                            <div class="success-card">
                                <strong>{strength['category']} - {strength['keyword']}</strong><br>
                                빈도: {strength['frequency']}회 ({strength['percentage']:.1f}%)
                            </div>
                            """, unsafe_allow_html=True)
                    
                    st.subheader("⚠️ 개선 영역")
                    if brand_report['swot']['weaknesses']:
                        for weakness in brand_report['swot']['weaknesses'][:3]:
                            st.markdown(f"""
                            <div class="warning-card">
                                <strong>{weakness['category']} - {weakness['keyword']}</strong><br>
                                빈도: {weakness['frequency']}회 ({weakness['percentage']:.1f}%)
                            </div>
                            """, unsafe_allow_html=True)
                
                # 마케팅 제안
                st.markdown("---")
                st.subheader("📢 브랜드별 마케팅 전략")
                
                col1, col2 = st.columns(2)
                
                with col1:
                    st.info(f"""
                    **포지셔닝 전략**
                    {brand_report['marketing_suggestions']['positioning_strategy']}
                    
                    **타겟 마케팅**
                    {brand_report['marketing_suggestions']['target_marketing']}
                    """)
                
                with col2:
                    if brand_report['marketing_suggestions']['competitive_advantages']:
                        st.success(f"""
                        **경쟁 우위 요소**
                        """ + "\n".join([f"• {adv['advantage']}" for adv in brand_report['marketing_suggestions']['competitive_advantages']]))
    
    with tabs[2]:  # 브랜드 비교
        st.header("🆚 브랜드 비교 분석")
        
        # 비교할 브랜드 선택
        top_10_brands = reviews_df['brand'].value_counts().head(10).index.tolist()
        selected_brands = st.multiselect(
            "비교할 브랜드 선택 (최대 5개)",
            options=top_10_brands,
            default=top_10_brands[:3],
            max_selections=5
        )
        
        if selected_brands:
            # 브랜드 비교 실행
            comparison_result = brand_analyzer.compare_brands(
                selected_brands, reviews_df, sentiment_df, products_df
            )
            
            # 비교 테이블
            comparison_df = pd.DataFrame(comparison_result['comparison']).T
            comparison_df = comparison_df.round(1)
            
            st.subheader("📊 브랜드 비교 테이블")
            st.dataframe(
                comparison_df,
                use_container_width=True,
                column_config={
                    'total_reviews': st.column_config.NumberColumn('리뷰 수', format="%d"),
                    'positive_ratio': st.column_config.NumberColumn('긍정 비율', format="%.1f%%"),
                    'primary_position': '주요 포지션',
                    'avg_price': st.column_config.NumberColumn('평균 가격', format="₩%,.0f"),
                    'target_age': '타겟 연령'
                }
            )
            
            # 시각화 비교
            col1, col2 = st.columns(2)
            
            with col1:
                # 리뷰 수 비교
                fig = px.bar(
                    x=selected_brands,
                    y=[comparison_result['comparison'][b]['total_reviews'] for b in selected_brands],
                    title="브랜드별 리뷰 수",
                    labels={'x': '브랜드', 'y': '리뷰 수'},
                    color=selected_brands
                )
                st.plotly_chart(fig, use_container_width=True)
            
            with col2:
                # 긍정 비율 비교
                fig = px.bar(
                    x=selected_brands,
                    y=[comparison_result['comparison'][b]['positive_ratio'] for b in selected_brands],
                    title="브랜드별 긍정 리뷰 비율",
                    labels={'x': '브랜드', 'y': '긍정 비율 (%)'},
                    color=[comparison_result['comparison'][b]['positive_ratio'] for b in selected_brands],
                    color_continuous_scale='RdYlGn'
                )
                st.plotly_chart(fig, use_container_width=True)
            
            # 레이더 차트 - 브랜드 특성 비교
            st.subheader("🎯 브랜드 특성 비교")
            
            # 각 브랜드의 구매 요인 데이터 수집
            categories = ['디자인', '품질', '가격', '사이즈', '색상']
            
            fig = go.Figure()
            
            for brand in selected_brands[:3]:  # 최대 3개 브랜드만
                brand_reviews = reviews_df[reviews_df['brand'] == brand]
                brand_report = brand_analyzer.generate_brand_report(
                    brand, reviews_df, sentiment_df, products_df
                )
                
                if brand_report:
                    values = []
                    for cat in categories:
                        for factor, pct in brand_report['purchase_factors']['factor_percentages'].items():
                            if factor == cat:
                                values.append(pct)
                                break
                        else:
                            values.append(0)
                    
                    fig.add_trace(go.Scatterpolar(
                        r=values,
                        theta=categories,
                        fill='toself',
                        name=brand
                    ))
            
            fig.update_layout(
                polar=dict(
                    radialaxis=dict(
                        visible=True,
                        range=[0, 50]
                    )),
                showlegend=True,
                title="브랜드별 구매 요인 강도"
            )
            
            st.plotly_chart(fig, use_container_width=True)
    
    with tabs[3]:  # 리뷰 감성 분석
        st.header("💬 리뷰 감성 분석")
        
        # 전체 감성 분포
        col1, col2, col3 = st.columns(3)
        
        with col1:
            sentiment_counts = sentiment_df['sentiment'].value_counts()
            fig = px.pie(
                values=sentiment_counts.values,
                names=sentiment_counts.index,
                title="전체 리뷰 감성 분포",
                color_discrete_map={'positive': '#28a745', 'negative': '#dc3545', 'neutral': '#6c757d'}
            )
            st.plotly_chart(fig, use_container_width=True)
        
        with col2:
            # 긍정 키워드 워드클라우드 대체
            st.subheader("😊 긍정 리뷰 키워드")
            positive_reviews = sentiment_df[sentiment_df['sentiment'] == 'positive']
            positive_keywords = review_analyzer.extract_common_themes(positive_reviews, 'positive')
            
            keywords_df = pd.DataFrame(positive_keywords[:10], columns=['키워드', '빈도'])
            fig = px.bar(
                keywords_df,
                x='빈도',
                y='키워드',
                orientation='h',
                color='빈도',
                color_continuous_scale='Greens'
            )
            st.plotly_chart(fig, use_container_width=True)
        
        with col3:
            # 부정 키워드
            st.subheader("😞 부정 리뷰 키워드")
            negative_reviews = sentiment_df[sentiment_df['sentiment'] == 'negative']
            negative_keywords = review_analyzer.extract_common_themes(negative_reviews, 'negative')
            
            keywords_df = pd.DataFrame(negative_keywords[:10], columns=['키워드', '빈도'])
            fig = px.bar(
                keywords_df,
                x='빈도',
                y='키워드',
                orientation='h',
                color='빈도',
                color_continuous_scale='Reds'
            )
            st.plotly_chart(fig, use_container_width=True)
    
    with tabs[4]:  # 마케팅 인사이트
        st.header("🎯 마케팅 인사이트")
        
        # 전체 마케팅 인사이트
        marketing_insights = review_analyzer.get_marketing_insights(sentiment_df)
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.subheader("💪 주요 마케팅 소구점")
            
            for i, strength in enumerate(marketing_insights['strengths'][:5], 1):
                st.markdown(f"""
                <div class="metric-card">
                    <h4>{i}. {strength['marketing_message']}</h4>
                    <p>카테고리: {strength['category']} | 언급률: {strength['percentage']:.1f}%</p>
                </div>
                """, unsafe_allow_html=True)
        
        with col2:
            st.subheader("📈 마케팅 활용 방안")
            
            st.info("""
            **상품 페이지 카피**
            - 메인: 실제 구매 고객이 증명하는 품질
            - 서브: 리뷰가 말해주는 진짜 가치
            
            **SNS 마케팅**
            - 긍정 키워드를 해시태그로 활용
            - 실제 리뷰 스크린샷 공유
            - 고객 후기 이벤트 진행
            
            **이메일 마케팅**
            - 베스트 리뷰 상품 큐레이션
            - 고객 만족도 높은 브랜드 특집
            """)
        
        # 개선 우선순위
        st.markdown("---")
        st.subheader("🔧 개선 우선순위")
        
        improvements = review_analyzer.get_improvement_insights(sentiment_df)
        
        if improvements:
            improvement_df = pd.DataFrame([
                {'카테고리': cat, '언급 수': data['count'], '비율': data['percentage']}
                for cat, data in improvements.items()
            ]).sort_values('비율', ascending=False)
            
            fig = px.bar(
                improvement_df,
                x='비율',
                y='카테고리',
                orientation='h',
                title="카테고리별 개선 필요도",
                color='비율',
                color_continuous_scale='Reds'
            )
            st.plotly_chart(fig, use_container_width=True)
    
    with tabs[5]:  # 트렌드 분석
        st.header("📈 트렌드 분석")
        
        # 페이지별 리뷰 분포 (enhanced 데이터인 경우)
        if 'page_number' in reviews_df.columns:
            col1, col2 = st.columns(2)
            
            with col1:
                # 페이지별 리뷰 수
                page_dist = reviews_df['page_number'].value_counts().sort_index()
                fig = px.bar(
                    x=page_dist.index,
                    y=page_dist.values,
                    title="페이지별 리뷰 분포",
                    labels={'x': '페이지 번호', 'y': '리뷰 수'}
                )
                st.plotly_chart(fig, use_container_width=True)
            
            with col2:
                # 페이지별 감성 변화
                page_sentiment = reviews_df.merge(sentiment_df[['product_id', 'sentiment']], on='product_id')
                page_sentiment_dist = page_sentiment.groupby(['page_number', 'sentiment']).size().unstack(fill_value=0)
                
                fig = go.Figure()
                for sentiment in ['positive', 'negative', 'neutral']:
                    if sentiment in page_sentiment_dist.columns:
                        fig.add_trace(go.Scatter(
                            x=page_sentiment_dist.index,
                            y=page_sentiment_dist[sentiment],
                            mode='lines+markers',
                            name=sentiment.capitalize(),
                            line=dict(color={'positive': '#28a745', 'negative': '#dc3545', 'neutral': '#6c757d'}[sentiment])
                        ))
                
                fig.update_layout(
                    title="페이지별 감성 변화",
                    xaxis_title="페이지 번호",
                    yaxis_title="리뷰 수"
                )
                st.plotly_chart(fig, use_container_width=True)
        
        # 이미지 포함 리뷰 분석
        if 'has_image' in reviews_df.columns:
            st.subheader("📸 이미지 리뷰 분석")
            
            col1, col2, col3 = st.columns(3)
            
            with col1:
                image_ratio = (reviews_df['has_image'] == 'Y').mean() * 100
                st.metric("이미지 포함 리뷰", f"{image_ratio:.1f}%")
            
            with col2:
                # 브랜드별 이미지 리뷰 비율
                brand_image = reviews_df.groupby('brand')['has_image'].apply(lambda x: (x == 'Y').mean() * 100)
                top_image_brands = brand_image.nlargest(5)
                st.metric("이미지 리뷰 1위 브랜드", f"{top_image_brands.index[0]}", f"{top_image_brands.iloc[0]:.1f}%")
            
            with col3:
                # 이미지 리뷰의 감성 분포
                if len(sentiment_df) > 0:
                    image_reviews = reviews_df[reviews_df['has_image'] == 'Y']['product_id']
                    image_sentiment = sentiment_df[sentiment_df['product_id'].isin(image_reviews)]
                    image_positive_ratio = (image_sentiment['sentiment'] == 'positive').mean() * 100
                    st.metric("이미지 리뷰 긍정률", f"{image_positive_ratio:.1f}%")
    
    with tabs[6]:  # 전략 제안
        st.header("💡 종합 전략 제안")
        
        # 상위 브랜드 분석 기반 제안
        top_5_brands = reviews_df['brand'].value_counts().head(5).index.tolist()
        
        st.subheader("🏆 벤치마킹 브랜드")
        
        # 상위 브랜드 특성 요약
        benchmark_data = []
        for brand in top_5_brands:
            report = brand_analyzer.generate_brand_report(brand, reviews_df, sentiment_df, products_df)
            if report:
                benchmark_data.append({
                    '브랜드': brand,
                    '포지션': report['positioning']['primary_position'][0],
                    '긍정률': f"{report['swot']['positive_ratio']:.1f}%",
                    '주요 강점': report['swot']['strengths'][0]['category'] if report['swot']['strengths'] else 'N/A',
                    '평균 가격': f"₩{report['basic_stats']['avg_price']:,.0f}"
                })
        
        benchmark_df = pd.DataFrame(benchmark_data)
        st.dataframe(benchmark_df, use_container_width=True, hide_index=True)
        
        # 전략 제안
        col1, col2 = st.columns(2)
        
        with col1:
            st.info("""
            **🎯 단기 전략 (1-3개월)**
            
            1. **리뷰 수집 강화**
               - 포토 리뷰 이벤트 진행
               - 구매 후 리뷰 작성 유도 (포인트/할인 쿠폰)
               - 베스트 리뷰어 선정 및 혜택 제공
            
            2. **상품 정보 개선**
               - 사이즈 가이드 상세화 (실측 정보 포함)
               - 다각도 상품 이미지 추가
               - 소재 정보 및 관리법 명시
            
            3. **고객 소통 강화**
               - 리뷰 답변 활성화
               - FAQ 섹션 강화
               - 실시간 채팅 상담 도입
            """)
        
        with col2:
            st.success("""
            **🚀 중장기 전략 (3-12개월)**
            
            1. **브랜드 포지셔닝 강화**
               - 상위 브랜드 벤치마킹
               - 차별화된 브랜드 스토리 개발
               - 타겟 고객층 맞춤 마케팅
            
            2. **상품 라인업 최적화**
               - 긍정 리뷰 많은 스타일 확대
               - 부정 리뷰 많은 상품 개선/단종
               - 시즌별 트렌드 반영 신상품 기획
            
            3. **데이터 기반 의사결정**
               - 리뷰 분석 정기 리포트 작성
               - 고객 피드백 반영 프로세스 구축
               - A/B 테스트를 통한 최적화
            """)
        
        # 액션 플랜
        st.markdown("---")
        st.subheader("📋 실행 계획")
        
        action_plan = pd.DataFrame({
            '우선순위': ['1', '2', '3', '4', '5'],
            '액션': [
                '사이즈 정보 상세화 및 실측 가이드 제공',
                '포토 리뷰 이벤트 진행 (월 1회)',
                '상위 5개 브랜드 벤치마킹 리포트 작성',
                '부정 리뷰 분석 및 개선안 도출',
                '타겟 고객층별 마케팅 메시지 개발'
            ],
            '담당': ['상품팀', '마케팅팀', '기획팀', '품질관리팀', '마케팅팀'],
            '기한': ['2주 내', '1개월 내', '1개월 내', '2개월 내', '3개월 내'],
            '기대효과': [
                '사이즈 관련 부정 리뷰 30% 감소',
                '이미지 리뷰 50% 증가',
                '경쟁 우위 요소 파악',
                '고객 만족도 10% 향상',
                '타겟 마케팅 효율 20% 개선'
            ]
        })
        
        st.dataframe(action_plan, use_container_width=True, hide_index=True)
        
        # 다운로드 버튼
        st.markdown("---")
        col1, col2, col3 = st.columns(3)
        
        with col1:
            csv = sentiment_df.to_csv(index=False, encoding='utf-8-sig')
            st.download_button(
                label="📊 감성 분석 결과 다운로드",
                data=csv,
                file_name=f"sentiment_analysis_{datetime.now().strftime('%Y%m%d')}.csv",
                mime="text/csv"
            )
        
        with col2:
            # 브랜드 리포트 다운로드
            if top_5_brands:
                brand_reports = []
                for brand in top_5_brands:
                    report = brand_analyzer.generate_brand_report(brand, reviews_df, sentiment_df, products_df)
                    if report:
                        brand_reports.append({
                            '브랜드': brand,
                            '리뷰수': report['basic_stats']['total_reviews'],
                            '긍정률': report['swot']['positive_ratio'],
                            '포지션': report['positioning']['primary_position'][0],
                            '평균가격': report['basic_stats']['avg_price']
                        })
                
                if brand_reports:
                    brand_df = pd.DataFrame(brand_reports)
                    csv_brand = brand_df.to_csv(index=False, encoding='utf-8-sig')
                    st.download_button(
                        label="🏢 브랜드 분석 리포트",
                        data=csv_brand,
                        file_name=f"brand_analysis_{datetime.now().strftime('%Y%m%d')}.csv",
                        mime="text/csv"
                    )
        
        with col3:
            st.download_button(
                label="📋 액션 플랜 다운로드",
                data=action_plan.to_csv(index=False, encoding='utf-8-sig'),
                file_name=f"action_plan_{datetime.now().strftime('%Y%m%d')}.csv",
                mime="text/csv"
            )

else:
    st.error("데이터 파일을 찾을 수 없습니다.")
    st.info("""
    필요한 파일:
    - musinsa_onepiece_all.csv (상품 데이터)
    - musinsa_reviews_enhanced.csv 또는 musinsa_reviews.csv (리뷰 데이터)
    
    실행 순서:
    1. `python musinsa_onepiece.py` - 상품 데이터 수집
    2. `python musinsa_review_crawler_enhanced.py` - 개선된 리뷰 수집 (5페이지, 100개)
    3. `streamlit run dashboard_final.py` - 통합 대시보드 실행
    """)

# 푸터
st.markdown("---")
st.markdown("🚀 무신사 원피스/스커트 통합 분석 대시보드 | " + datetime.now().strftime("%Y-%m-%d %H:%M"))