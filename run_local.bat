@echo off
echo ====================================
echo 무신사 패션 분석 대시보드 실행
echo ====================================
echo.

REM Python 확인
python --version >nul 2>&1
if %errorlevel% neq 0 (
    echo [오류] Python이 설치되어 있지 않습니다.
    echo Python을 먼저 설치해주세요: https://www.python.org
    pause
    exit /b 1
)

echo [1/3] 필요한 패키지 설치 중...
pip install streamlit pandas plotly --quiet

echo [2/3] 대시보드 시작 중...
echo.
echo 브라우저에서 http://localhost:8505 로 접속하세요
echo 종료하려면 Ctrl+C를 누르세요
echo.

echo [3/3] Streamlit 실행...
streamlit run app.py --server.port 8505

pause