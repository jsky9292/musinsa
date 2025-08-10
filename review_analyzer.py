import pandas as pd
import numpy as np
from collections import Counter
import re
# from konlpy.tag import Okt  # KoNLPy 설치 필요시 주석 해제
import warnings
warnings.filterwarnings('ignore')

class ReviewAnalyzer:
    def __init__(self):
        # self.okt = Okt()  # KoNLPy 설치 필요시 주석 해제
        
        # 긍정/부정 키워드 사전
        self.positive_keywords = {
            '디자인': ['예쁘', '예뻐', '이쁘', '이뻐', '귀엽', '세련', '독특', '유니크', '트렌디', '스타일리시'],
            '품질': ['좋아', '좋은', '좋고', '탄탄', '튼튼', '고급', '퀄리티', '만족', '최고', '훌륭'],
            '핏': ['핏이', '핏도', '슬림', '여리', '날씬', '잘맞', '딱맞', '완벽'],
            '가격': ['저렴', '싸게', '가성비', '가격대비', '할인', '세일', '이가격'],
            '편안함': ['편하', '편안', '편해', '활동', '신축성', '스판', '늘어나'],
            '만족도': ['만족', '추천', '재구매', '또사', '좋아요', '최고', '대박', '성공'],
            '색상': ['색이', '색도', '색깔', '색상', '화사', '선명'],
            '사이즈': ['넉넉', '여유', '충분', '적당'],
            '소재': ['부드럽', '보들', '촉감', '시원', '가벼', '얇아', '두껍지'],
        }
        
        self.negative_keywords = {
            '사이즈': ['작아', '작은', '작음', '짧아', '짧은', '짧음', '커요', '큰', '크다', '안맞', '타이트', '꽉', '끼'],
            '품질': ['별로', '실망', '후회', '아쉬', '그저', '보통', '싸구려', '저렴해보', '나쁘', '최악'],
            '소재': ['까슬', '따가', '답답', '더워', '두꺼', '뻣뻣', '거칠', '얇아서', '비침', '비쳐'],
            '색상': ['다르', '다른', '차이', '바랜', '색바램'],
            '배송': ['늦게', '늦어', '오래', '지연'],
            '가격': ['비싸', '비싼', '비쌈', '부담'],
            '디자인': ['촌스럽', '올드', '구식', '평범', '심심'],
            '내구성': ['찢어', '뜯어', '해짐', '풀림', '늘어남', '변형'],
            '불편함': ['불편', '거슬', '신경쓰'],
        }
        
        # 개선 요구사항 키워드
        self.improvement_keywords = {
            '사이즈': ['사이즈표', '정사이즈', '실측', '상세사이즈'],
            '소재': ['소재설명', '두께감', '비침정도', '신축성'],
            '색상': ['실제색상', '색차이', '모니터'],
            '길이': ['기장', '총장', '길이조절', '길이감'],
            '디테일': ['마감', '박음질', '지퍼', '단추', '안감'],
        }

    def extract_keywords(self, text):
        """텍스트에서 키워드 추출 (간단한 버전)"""
        # KoNLPy 없이 간단한 키워드 추출
        words = re.findall(r'[가-힣]+', text)
        # 2글자 이상인 단어만 추출
        keywords = [word for word in words if len(word) >= 2]
        return keywords

    def analyze_sentiment(self, reviews_df):
        """리뷰 감성 분석"""
        results = []
        
        for idx, row in reviews_df.iterrows():
            text = str(row.get('text', ''))
            
            # 긍정/부정 점수 계산
            positive_score = 0
            negative_score = 0
            positive_reasons = []
            negative_reasons = []
            
            for category, keywords in self.positive_keywords.items():
                for keyword in keywords:
                    if keyword in text:
                        positive_score += 1
                        positive_reasons.append(f"{category}:{keyword}")
            
            for category, keywords in self.negative_keywords.items():
                for keyword in keywords:
                    if keyword in text:
                        negative_score += 1
                        negative_reasons.append(f"{category}:{keyword}")
            
            # 감성 판단
            if positive_score > negative_score:
                sentiment = 'positive'
            elif negative_score > positive_score:
                sentiment = 'negative'
            else:
                sentiment = 'neutral'
            
            results.append({
                'product_id': row.get('product_id', ''),
                'brand': row.get('brand', ''),
                'text': text,
                'sentiment': sentiment,
                'positive_score': positive_score,
                'negative_score': negative_score,
                'positive_reasons': ', '.join(positive_reasons[:3]),  # 상위 3개만
                'negative_reasons': ', '.join(negative_reasons[:3]),  # 상위 3개만
            })
        
        return pd.DataFrame(results)

    def extract_common_themes(self, reviews_df, sentiment_type='all'):
        """공통 테마 추출"""
        if sentiment_type != 'all':
            reviews_df = reviews_df[reviews_df['sentiment'] == sentiment_type]
        
        all_keywords = []
        for text in reviews_df['text']:
            keywords = self.extract_keywords(str(text))
            all_keywords.extend(keywords)
        
        # 빈도수 계산
        keyword_counts = Counter(all_keywords)
        
        # 불용어 제거
        stopwords = ['제품', '상품', '구매', '배송', '옷', '원피스', '스커트', '사이즈', '색상', '디자인']
        for word in stopwords:
            keyword_counts.pop(word, None)
        
        return keyword_counts.most_common(20)

    def get_improvement_insights(self, reviews_df):
        """개선사항 도출"""
        improvements = {}
        
        negative_reviews = reviews_df[reviews_df['sentiment'] == 'negative']
        
        for category, keywords in self.improvement_keywords.items():
            count = 0
            examples = []
            
            for idx, row in negative_reviews.iterrows():
                text = str(row.get('text', ''))
                for keyword in keywords:
                    if keyword in text:
                        count += 1
                        if len(examples) < 3:  # 예시는 3개까지만
                            examples.append(text[:100])
                        break
            
            if count > 0:
                improvements[category] = {
                    'count': count,
                    'percentage': (count / len(negative_reviews) * 100) if len(negative_reviews) > 0 else 0,
                    'examples': examples
                }
        
        return improvements

    def get_marketing_insights(self, sentiment_df):
        """마케팅 인사이트 도출"""
        insights = {
            'strengths': [],  # 강점 (마케팅 소구점)
            'weaknesses': [],  # 약점 (개선 필요)
            'opportunities': [],  # 기회
            'customer_needs': []  # 고객 니즈
        }
        
        # 긍정 리뷰 분석 - 강점 도출
        positive_reviews = sentiment_df[sentiment_df['sentiment'] == 'positive']
        if len(positive_reviews) > 0:
            # 긍정 이유 빈도 분석
            positive_reasons = []
            for reasons in positive_reviews['positive_reasons']:
                if reasons:
                    positive_reasons.extend(reasons.split(', '))
            
            reason_counts = Counter(positive_reasons)
            top_strengths = reason_counts.most_common(5)
            
            for reason, count in top_strengths:
                if ':' in reason:
                    category, keyword = reason.split(':')
                    percentage = (count / len(positive_reviews) * 100)
                    insights['strengths'].append({
                        'category': category,
                        'keyword': keyword,
                        'frequency': count,
                        'percentage': percentage,
                        'marketing_message': self.generate_marketing_message(category, keyword, percentage)
                    })
        
        # 부정 리뷰 분석 - 약점 도출
        negative_reviews = sentiment_df[sentiment_df['sentiment'] == 'negative']
        if len(negative_reviews) > 0:
            negative_reasons = []
            for reasons in negative_reviews['negative_reasons']:
                if reasons:
                    negative_reasons.extend(reasons.split(', '))
            
            reason_counts = Counter(negative_reasons)
            top_weaknesses = reason_counts.most_common(5)
            
            for reason, count in top_weaknesses:
                if ':' in reason:
                    category, keyword = reason.split(':')
                    percentage = (count / len(negative_reviews) * 100)
                    insights['weaknesses'].append({
                        'category': category,
                        'keyword': keyword,
                        'frequency': count,
                        'percentage': percentage,
                        'improvement_suggestion': self.generate_improvement_suggestion(category, keyword)
                    })
        
        # 고객 니즈 파악
        all_reviews_text = ' '.join(sentiment_df['text'].astype(str))
        
        # 자주 언급되는 니즈
        needs_keywords = ['원해', '있으면', '있었으면', '필요', '바라', '기대', '원합니다', '좋겠']
        for keyword in needs_keywords:
            if keyword in all_reviews_text:
                # 해당 키워드가 포함된 문장 추출
                sentences = [s for s in all_reviews_text.split('.') if keyword in s]
                if sentences:
                    insights['customer_needs'].append({
                        'keyword': keyword,
                        'examples': sentences[:3]  # 예시 3개
                    })
        
        return insights

    def generate_marketing_message(self, category, keyword, percentage):
        """마케팅 메시지 생성"""
        messages = {
            '디자인': {
                '예쁘': f"고객 {percentage:.0f}%가 인정한 세련된 디자인",
                '독특': "남들과 다른 유니크한 스타일",
                '트렌디': "최신 트렌드를 반영한 감각적인 디자인"
            },
            '품질': {
                '좋아': f"구매 고객 {percentage:.0f}%가 만족한 우수한 품질",
                '탄탄': "오래 입어도 변하지 않는 탄탄한 내구성",
                '퀄리티': "프리미엄 퀄리티, 가격 그 이상의 가치"
            },
            '핏': {
                '핏이': f"{percentage:.0f}%의 고객이 극찬한 완벽한 핏",
                '슬림': "몸매를 살려주는 슬림한 실루엣",
                '날씬': "날씬해 보이는 마법의 핏"
            },
            '가격': {
                '가성비': "합리적인 가격, 탁월한 선택",
                '저렴': "부담 없는 가격으로 즐기는 트렌드",
                '할인': "특별 할인가로 만나는 프리미엄"
            }
        }
        
        if category in messages and keyword in messages[category]:
            return messages[category][keyword]
        else:
            return f"{category} 부문 고객 만족도 {percentage:.0f}%"

    def generate_improvement_suggestion(self, category, keyword):
        """개선 제안 생성"""
        suggestions = {
            '사이즈': {
                '작아': "사이즈 재검토 및 상세 치수 정보 제공 필요",
                '짧아': "기장 옵션 다양화 또는 길이 조절 기능 추가 검토",
                '타이트': "여유있는 핏 옵션 추가 고려"
            },
            '품질': {
                '실망': "품질 관리 강화 및 검수 프로세스 개선",
                '싸구려': "소재 업그레이드 및 마감 처리 개선"
            },
            '소재': {
                '비침': "안감 추가 또는 도톰한 소재로 변경 검토",
                '답답': "통기성 좋은 소재로 교체 검토",
                '따가': "피부 친화적 소재 사용 검토"
            },
            '색상': {
                '다르': "실제 색상과 유사한 상품 이미지 촬영",
                '바랜': "색상 유지력 강화 가공 처리"
            }
        }
        
        if category in suggestions and keyword in suggestions[category]:
            return suggestions[category][keyword]
        else:
            return f"{category} 관련 개선 필요"

    def analyze_product_reviews(self, product_id, reviews_df):
        """특정 상품의 리뷰 종합 분석"""
        product_reviews = reviews_df[reviews_df['product_id'] == product_id]
        
        if len(product_reviews) == 0:
            return None
        
        # 감성 분석
        sentiment_df = self.analyze_sentiment(product_reviews)
        
        # 감성 비율
        sentiment_ratio = sentiment_df['sentiment'].value_counts(normalize=True).to_dict()
        
        # 평균 점수
        avg_positive_score = sentiment_df['positive_score'].mean()
        avg_negative_score = sentiment_df['negative_score'].mean()
        
        # 공통 테마
        positive_themes = self.extract_common_themes(sentiment_df, 'positive')
        negative_themes = self.extract_common_themes(sentiment_df, 'negative')
        
        # 개선사항
        improvements = self.get_improvement_insights(sentiment_df)
        
        # 마케팅 인사이트
        marketing_insights = self.get_marketing_insights(sentiment_df)
        
        return {
            'product_id': product_id,
            'total_reviews': len(product_reviews),
            'sentiment_ratio': sentiment_ratio,
            'avg_positive_score': avg_positive_score,
            'avg_negative_score': avg_negative_score,
            'positive_themes': positive_themes[:10],
            'negative_themes': negative_themes[:10],
            'improvements': improvements,
            'marketing_insights': marketing_insights
        }

# 사용 예시
if __name__ == "__main__":
    # 리뷰 데이터 로드
    reviews_df = pd.read_csv("musinsa_reviews.csv")
    
    # 분석기 초기화
    analyzer = ReviewAnalyzer()
    
    # 전체 리뷰 감성 분석
    sentiment_results = analyzer.analyze_sentiment(reviews_df)
    
    # 결과 저장
    sentiment_results.to_csv("review_sentiment_analysis.csv", index=False, encoding='utf-8-sig')
    
    print("리뷰 감성 분석 완료!")
    print(f"긍정 리뷰: {len(sentiment_results[sentiment_results['sentiment'] == 'positive'])}개")
    print(f"부정 리뷰: {len(sentiment_results[sentiment_results['sentiment'] == 'negative'])}개")
    print(f"중립 리뷰: {len(sentiment_results[sentiment_results['sentiment'] == 'neutral'])}개")