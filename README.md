# 👗 무신사 패션 분석 대시보드

무신사의 원피스/스커트 상품 데이터를 분석하는 웹 대시보드입니다.

[![Streamlit App](https://static.streamlit.io/badges/streamlit_badge_black_white.svg)](https://musinsa-analysis.streamlit.app)
[![Python](https://img.shields.io/badge/Python-3.9+-blue.svg)](https://www.python.org)
[![License](https://img.shields.io/badge/License-MIT-green.svg)](LICENSE)

## 📱 라이브 데모

🔗 **[대시보드 바로가기](https://musinsa-analysis.streamlit.app)**

## ✨ 주요 기능

### 📊 데이터 분석
- **가격 분석**: 가격 분포, 할인율 분석
- **브랜드 분석**: 브랜드별 상품 수, 평균 가격
- **트렌드 분석**: 스타일 키워드, 색상 트렌드
- **마케팅 인사이트**: 데이터 기반 전략 제안

### 🔍 데이터 수집
- 무신사 상품 자동 크롤링
- 리뷰 데이터 수집
- GitHub Actions를 통한 자동화

## 🚀 시작하기

### 온라인 사용 (권장)

1. [대시보드](https://musinsa-analysis.streamlit.app) 접속
2. 샘플 데이터 다운로드 또는 직접 데이터 업로드
3. 분석 결과 확인

### 로컬 설치

```bash
# 저장소 클론
git clone https://github.com/yourusername/musinsa-analysis.git
cd musinsa-analysis

# 가상환경 생성 및 활성화
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate

# 패키지 설치
pip install -r requirements.txt

# 대시보드 실행
streamlit run app.py
```

## 📁 프로젝트 구조

```
musinsa-analysis/
├── app.py                 # Streamlit 메인 앱
├── requirements.txt       # Python 패키지
├── .streamlit/           
│   └── config.toml       # Streamlit 설정
├── crawler/              
│   └── musinsa_crawler.py # 데이터 크롤러
├── data/                 # 수집된 데이터 (gitignore)
│   └── sample/          # 샘플 데이터
└── .github/workflows/   
    └── crawl.yml        # GitHub Actions 워크플로우
```

## 🛠️ 데이터 수집

### 수동 크롤링

```bash
# 원피스 데이터 수집 (100개)
python crawler/musinsa_crawler.py --category onepiece --max-products 100

# 스커트 데이터 수집
python crawler/musinsa_crawler.py --category skirt --max-products 100

# 옵션
# --headless: 백그라운드 실행
# --max-scroll: 최대 스크롤 횟수
# --output: 출력 디렉토리
```

### 자동 크롤링 (GitHub Actions)

- 매주 월요일 자동 실행
- Actions 탭에서 수동 실행 가능
- 수집된 데이터는 Artifacts로 저장

## 📊 데이터 형식

### 상품 데이터 (CSV)

| 컬럼명 | 설명 | 예시 |
|--------|------|------|
| 상품ID | 고유 식별자 | 12345 |
| 브랜드 | 브랜드명 | ZARA |
| 상품명 | 상품 이름 | 플로럴 원피스 |
| 가격 | 현재 가격 | 45000 |
| 원가 | 원래 가격 | 60000 |
| 할인율 | 할인 비율 | 25 |
| 상품링크 | URL | https://... |

## 🤝 기여하기

1. Fork the Project
2. Create your Feature Branch (`git checkout -b feature/AmazingFeature`)
3. Commit your Changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the Branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

## 📝 라이선스

MIT License - 자세한 내용은 [LICENSE](LICENSE) 파일 참조

## 🙏 감사의 글

- [Streamlit](https://streamlit.io) - 웹 앱 프레임워크
- [Plotly](https://plotly.com) - 데이터 시각화
- [Selenium](https://selenium.dev) - 웹 크롤링

## 📧 문의

프로젝트 관련 문의사항은 [Issues](https://github.com/yourusername/musinsa-analysis/issues)에 등록해주세요.

---

⭐ 이 프로젝트가 도움이 되었다면 Star를 눌러주세요!