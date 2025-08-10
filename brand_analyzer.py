import pandas as pd
import numpy as np
from collections import Counter, defaultdict
import re
from datetime import datetime, timedelta
import warnings
warnings.filterwarnings('ignore')

class BrandAnalyzer:
    def __init__(self):
        """브랜드 분석기 초기화"""
        # 브랜드 포지셔닝 키워드
        self.brand_positioning = {
            '프리미엄': ['고급', '프리미엄', '명품', '퀄리티', '품질', '소재', '마감'],
            '트렌디': ['트렌드', '유행', '인기', '핫', '세련', '스타일', '패션'],
            '실용적': ['편한', '편하', '실용', '데일리', '일상', '활용', '기본'],
            '가성비': ['가성비', '저렴', '싸', '할인', '세일', '가격', '부담'],
            '유니크': ['독특', '유니크', '특별', '개성', '차별', '남다른'],
            '베이직': ['베이직', '기본', '무난', '깔끔', '심플', '단순'],
            '영캐주얼': ['귀여운', '귀엽', '러블리', '큐트', '발랄', '화사'],
            '미니멀': ['미니멀', '심플', '모던', '깔끔', '절제', '간결']
        }
        
        # 구매 결정 요인
        self.purchase_factors = {
            '디자인': ['디자인', '예쁘', '이쁘', '스타일', '모양', '패턴', '무늬'],
            '품질': ['품질', '퀄리티', '소재', '재질', '원단', '마감', '바느질'],
            '가격': ['가격', '가성비', '저렴', '비싸', '할인', '세일', '쿠폰'],
            '사이즈': ['사이즈', '핏', '맞아', '크기', '기장', '길이', '넉넉'],
            '색상': ['색상', '색깔', '컬러', '색이', '색도', '톤', '색감'],
            '배송': ['배송', '도착', '포장', '빠른', '늦은', '신속'],
            '브랜드': ['브랜드', '믿고', '신뢰', '유명', '인지도']
        }
        
        # 타겟 고객층 추정 키워드
        self.target_customer = {
            '10대': ['학생', '교복', '학교', '귀여운', '캠퍼스'],
            '20대': ['대학', '데이트', '취업', '면접', '클럽', '파티'],
            '30대': ['회사', '직장', '출근', '오피스', '결혼식', '하객'],
            '40대': ['품위', '단정', '격식', '모임', '학부모'],
            '체형': {
                '마른': ['마른', '슬림', '스키니', '날씬'],
                '통통': ['통통', '넉넉', '여유', '커버', '가려'],
                '보통': ['보통', '평범', '일반', '표준']
            }
        }

    def analyze_brand_positioning(self, brand_reviews):
        """브랜드 포지셔닝 분석"""
        positioning_scores = defaultdict(int)
        
        all_text = ' '.join(brand_reviews['text'].astype(str))
        
        for position, keywords in self.brand_positioning.items():
            for keyword in keywords:
                count = all_text.count(keyword)
                positioning_scores[position] += count
        
        # 정규화
        total = sum(positioning_scores.values())
        if total > 0:
            positioning_percentages = {k: (v/total)*100 for k, v in positioning_scores.items()}
        else:
            positioning_percentages = positioning_scores
        
        # 상위 3개 포지션
        top_positions = sorted(positioning_percentages.items(), key=lambda x: x[1], reverse=True)[:3]
        
        return {
            'positioning_scores': dict(positioning_scores),
            'positioning_percentages': positioning_percentages,
            'top_positions': top_positions,
            'primary_position': top_positions[0] if top_positions else ('Unknown', 0)
        }

    def analyze_purchase_factors(self, brand_reviews):
        """구매 결정 요인 분석"""
        factor_scores = defaultdict(int)
        factor_examples = defaultdict(list)
        
        for idx, review in brand_reviews.iterrows():
            text = str(review.get('text', ''))
            
            for factor, keywords in self.purchase_factors.items():
                for keyword in keywords:
                    if keyword in text:
                        factor_scores[factor] += 1
                        if len(factor_examples[factor]) < 3:  # 요인별 예시 3개까지
                            factor_examples[factor].append(text[:100])
                        break
        
        # 정규화
        total_reviews = len(brand_reviews)
        factor_percentages = {k: (v/total_reviews)*100 for k, v in factor_scores.items()}
        
        # 순위 매기기
        ranked_factors = sorted(factor_percentages.items(), key=lambda x: x[1], reverse=True)
        
        return {
            'factor_scores': dict(factor_scores),
            'factor_percentages': factor_percentages,
            'ranked_factors': ranked_factors,
            'factor_examples': dict(factor_examples)
        }

    def analyze_target_customers(self, brand_reviews):
        """타겟 고객층 분석"""
        age_scores = defaultdict(int)
        body_type_scores = defaultdict(int)
        
        all_text = ' '.join(brand_reviews['text'].astype(str))
        
        # 연령대 추정
        for age_group, keywords in self.target_customer.items():
            if age_group != '체형':
                for keyword in keywords:
                    count = all_text.count(keyword)
                    age_scores[age_group] += count
        
        # 체형 추정
        if '체형' in self.target_customer:
            for body_type, keywords in self.target_customer['체형'].items():
                for keyword in keywords:
                    count = all_text.count(keyword)
                    body_type_scores[body_type] += count
        
        return {
            'age_scores': dict(age_scores),
            'primary_age_group': max(age_scores.items(), key=lambda x: x[1])[0] if age_scores else 'Unknown',
            'body_type_scores': dict(body_type_scores),
            'primary_body_type': max(body_type_scores.items(), key=lambda x: x[1])[0] if body_type_scores else 'Unknown'
        }

    def analyze_brand_strengths_weaknesses(self, sentiment_df):
        """브랜드 강점/약점 분석"""
        # 긍정 리뷰 분석
        positive_reviews = sentiment_df[sentiment_df['sentiment'] == 'positive']
        negative_reviews = sentiment_df[sentiment_df['sentiment'] == 'negative']
        
        strengths = []
        weaknesses = []
        
        # 강점 도출
        if len(positive_reviews) > 0:
            positive_reasons = []
            for reasons in positive_reviews['positive_reasons']:
                if reasons:
                    positive_reasons.extend(reasons.split(', '))
            
            reason_counts = Counter(positive_reasons)
            for reason, count in reason_counts.most_common(5):
                if ':' in reason:
                    category, keyword = reason.split(':')
                    percentage = (count / len(positive_reviews) * 100)
                    strengths.append({
                        'category': category,
                        'keyword': keyword,
                        'frequency': count,
                        'percentage': percentage
                    })
        
        # 약점 도출
        if len(negative_reviews) > 0:
            negative_reasons = []
            for reasons in negative_reviews['negative_reasons']:
                if reasons:
                    negative_reasons.extend(reasons.split(', '))
            
            reason_counts = Counter(negative_reasons)
            for reason, count in reason_counts.most_common(5):
                if ':' in reason:
                    category, keyword = reason.split(':')
                    percentage = (count / len(negative_reviews) * 100)
                    weaknesses.append({
                        'category': category,
                        'keyword': keyword,
                        'frequency': count,
                        'percentage': percentage
                    })
        
        return {
            'strengths': strengths,
            'weaknesses': weaknesses,
            'positive_ratio': len(positive_reviews) / len(sentiment_df) * 100 if len(sentiment_df) > 0 else 0,
            'negative_ratio': len(negative_reviews) / len(sentiment_df) * 100 if len(sentiment_df) > 0 else 0
        }

    def analyze_review_trends(self, brand_reviews):
        """리뷰 트렌드 분석"""
        trends = {
            'total_reviews': len(brand_reviews),
            'avg_review_length': brand_reviews['text'].astype(str).str.len().mean(),
            'has_image_ratio': 0,
            'helpful_avg': 0,
            'page_distribution': {}
        }
        
        # 이미지 포함 리뷰 비율
        if 'has_image' in brand_reviews.columns:
            image_reviews = brand_reviews['has_image'] == 'Y'
            trends['has_image_ratio'] = (image_reviews.sum() / len(brand_reviews) * 100) if len(brand_reviews) > 0 else 0
        
        # 도움이 됨 평균
        if 'helpful_count' in brand_reviews.columns:
            brand_reviews['helpful_count'] = pd.to_numeric(brand_reviews['helpful_count'], errors='coerce')
            trends['helpful_avg'] = brand_reviews['helpful_count'].mean()
        
        # 페이지별 분포
        if 'page_number' in brand_reviews.columns:
            page_dist = brand_reviews['page_number'].value_counts().to_dict()
            trends['page_distribution'] = page_dist
        
        return trends

    def generate_brand_report(self, brand_name, reviews_df, sentiment_df, products_df):
        """브랜드 종합 리포트 생성"""
        # 브랜드 관련 데이터 필터링
        brand_reviews = reviews_df[reviews_df['brand'] == brand_name]
        brand_sentiment = sentiment_df[sentiment_df['brand'] == brand_name]
        brand_products = products_df[products_df['브랜드'] == brand_name]
        
        if len(brand_reviews) == 0:
            return None
        
        report = {
            'brand_name': brand_name,
            'basic_stats': {
                'total_products': len(brand_products),
                'total_reviews': len(brand_reviews),
                'unique_products_reviewed': brand_reviews['product_id'].nunique(),
                'avg_price': brand_products['가격'].mean() if len(brand_products) > 0 else 0,
                'avg_discount': brand_products['할인율'].mean() if len(brand_products) > 0 else 0
            }
        }
        
        # 포지셔닝 분석
        report['positioning'] = self.analyze_brand_positioning(brand_reviews)
        
        # 구매 요인 분석
        report['purchase_factors'] = self.analyze_purchase_factors(brand_reviews)
        
        # 타겟 고객 분석
        report['target_customers'] = self.analyze_target_customers(brand_reviews)
        
        # 강점/약점 분석
        if len(brand_sentiment) > 0:
            report['swot'] = self.analyze_brand_strengths_weaknesses(brand_sentiment)
        else:
            report['swot'] = {'strengths': [], 'weaknesses': [], 'positive_ratio': 0, 'negative_ratio': 0}
        
        # 리뷰 트렌드
        report['trends'] = self.analyze_review_trends(brand_reviews)
        
        # 마케팅 제안
        report['marketing_suggestions'] = self.generate_marketing_suggestions(report)
        
        return report

    def generate_marketing_suggestions(self, report):
        """브랜드별 맞춤 마케팅 제안"""
        suggestions = {
            'positioning_strategy': '',
            'target_marketing': '',
            'improvement_areas': [],
            'competitive_advantages': []
        }
        
        # 포지셔닝 전략
        if report['positioning']['primary_position'][0]:
            position = report['positioning']['primary_position'][0]
            position_strategies = {
                '프리미엄': "프리미엄 이미지 강화 - 품질과 디테일 강조, VIP 프로그램 운영",
                '트렌디': "SNS 마케팅 강화 - 인플루언서 협업, 시즌별 신상품 홍보",
                '실용적': "일상 착용 사례 강조 - 리얼 리뷰 활용, 코디 제안",
                '가성비': "가격 경쟁력 홍보 - 할인 이벤트, 번들 상품 기획",
                '유니크': "차별화 포인트 강조 - 독특한 디자인 스토리텔링",
                '베이직': "기본 아이템 라인업 강화 - 사이즈/컬러 다양화",
                '영캐주얼': "젊은 감성 어필 - 밝고 활기찬 이미지, 캠퍼스룩 제안",
                '미니멀': "세련된 심플함 강조 - 고급스러운 이미지 연출"
            }
            suggestions['positioning_strategy'] = position_strategies.get(position, "브랜드 아이덴티티 강화")
        
        # 타겟 마케팅
        if report['target_customers']['primary_age_group'] != 'Unknown':
            age_group = report['target_customers']['primary_age_group']
            age_strategies = {
                '10대': "학생 할인, 교복 코디 제안, 틱톡/인스타 마케팅",
                '20대': "인스타그램 중심 마케팅, 데이트룩/면접룩 스타일링",
                '30대': "오피스룩 제안, 품질과 실용성 강조, 네이버 블로그 마케팅",
                '40대': "품격있는 이미지, 체형 커버 강조, 카페/블로그 마케팅"
            }
            suggestions['target_marketing'] = age_strategies.get(age_group, "타겟 연령층 맞춤 마케팅")
        
        # 개선 영역
        if report['swot']['weaknesses']:
            for weakness in report['swot']['weaknesses'][:3]:
                suggestions['improvement_areas'].append({
                    'area': weakness['category'],
                    'issue': weakness['keyword'],
                    'priority': 'High' if weakness['percentage'] > 20 else 'Medium'
                })
        
        # 경쟁 우위
        if report['swot']['strengths']:
            for strength in report['swot']['strengths'][:3]:
                suggestions['competitive_advantages'].append({
                    'advantage': f"{strength['category']} - {strength['keyword']}",
                    'usage': f"마케팅 카피에 활용 ({strength['percentage']:.0f}% 고객 만족)"
                })
        
        return suggestions

    def compare_brands(self, brands_list, reviews_df, sentiment_df, products_df):
        """여러 브랜드 비교 분석"""
        comparison = {}
        
        for brand in brands_list:
            report = self.generate_brand_report(brand, reviews_df, sentiment_df, products_df)
            if report:
                comparison[brand] = {
                    'total_reviews': report['basic_stats']['total_reviews'],
                    'positive_ratio': report['swot']['positive_ratio'],
                    'primary_position': report['positioning']['primary_position'][0],
                    'top_purchase_factor': report['purchase_factors']['ranked_factors'][0] if report['purchase_factors']['ranked_factors'] else ('Unknown', 0),
                    'avg_price': report['basic_stats']['avg_price'],
                    'target_age': report['target_customers']['primary_age_group']
                }
        
        # 브랜드 순위 매기기
        rankings = {
            'by_reviews': sorted(comparison.items(), key=lambda x: x[1]['total_reviews'], reverse=True),
            'by_satisfaction': sorted(comparison.items(), key=lambda x: x[1]['positive_ratio'], reverse=True),
            'by_price': sorted(comparison.items(), key=lambda x: x[1]['avg_price'], reverse=True)
        }
        
        return {
            'comparison': comparison,
            'rankings': rankings
        }

# 사용 예시
if __name__ == "__main__":
    # 데이터 로드
    try:
        products_df = pd.read_csv("musinsa_onepiece_all.csv")
        reviews_df = pd.read_csv("musinsa_reviews_enhanced.csv")
        
        # 감성 분석 결과 로드 (있는 경우)
        try:
            sentiment_df = pd.read_csv("review_sentiment_analysis.csv")
        except:
            from review_analyzer import ReviewAnalyzer
            analyzer = ReviewAnalyzer()
            sentiment_df = analyzer.analyze_sentiment(reviews_df)
        
        # 브랜드 분석기 초기화
        brand_analyzer = BrandAnalyzer()
        
        # 상위 5개 브랜드 분석
        top_brands = reviews_df['brand'].value_counts().head(5).index.tolist()
        
        print("="*50)
        print("브랜드별 상세 분석 리포트")
        print("="*50)
        
        for brand in top_brands:
            print(f"\n브랜드: {brand}")
            print("-"*30)
            
            report = brand_analyzer.generate_brand_report(brand, reviews_df, sentiment_df, products_df)
            
            if report:
                print(f"총 리뷰: {report['basic_stats']['total_reviews']}개")
                print(f"주요 포지션: {report['positioning']['primary_position'][0]} ({report['positioning']['primary_position'][1]:.1f}%)")
                print(f"긍정 비율: {report['swot']['positive_ratio']:.1f}%")
                print(f"주요 구매 요인: {report['purchase_factors']['ranked_factors'][0][0] if report['purchase_factors']['ranked_factors'] else 'N/A'}")
                print(f"타겟 연령: {report['target_customers']['primary_age_group']}")
                print(f"마케팅 전략: {report['marketing_suggestions']['positioning_strategy']}")
        
        # 브랜드 비교
        print("\n" + "="*50)
        print("브랜드 비교 분석")
        print("="*50)
        
        comparison_result = brand_analyzer.compare_brands(top_brands, reviews_df, sentiment_df, products_df)
        
        print("\n리뷰 수 순위:")
        for i, (brand, data) in enumerate(comparison_result['rankings']['by_reviews'][:5], 1):
            print(f"{i}. {brand}: {data['total_reviews']}개")
        
        print("\n만족도 순위:")
        for i, (brand, data) in enumerate(comparison_result['rankings']['by_satisfaction'][:5], 1):
            print(f"{i}. {brand}: {data['positive_ratio']:.1f}%")
        
    except Exception as e:
        print(f"에러 발생: {e}")
        print("필요한 파일을 확인해주세요.")