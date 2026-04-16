import sys
import os
import subprocess
import webbrowser
import time
from threading import Thread

def run_streamlit():
    """Streamlit 앱 실행"""
    # 현재 실행 파일의 디렉토리
    if getattr(sys, 'frozen', False):
        # 실행 파일로 실행된 경우
        app_dir = os.path.dirname(sys.executable)
    else:
        # 스크립트로 실행된 경우
        app_dir = os.path.dirname(os.path.abspath(__file__))
    
    app_path = os.path.join(app_dir, "app.py")
    
    # Streamlit 실행
    cmd = [sys.executable, "-m", "streamlit", "run", app_path, 
           "--server.port", "8505",
           "--server.headless", "true",
           "--browser.serverAddress", "localhost"]
    
    subprocess.run(cmd)

def open_browser():
    """브라우저 열기"""
    time.sleep(3)  # Streamlit이 시작될 때까지 대기
    webbrowser.open("http://localhost:8505")

if __name__ == "__main__":
    print("🚀 무신사 패션 분석 대시보드 시작 중...")
    print("📊 브라우저가 자동으로 열립니다...")
    print("종료하려면 Ctrl+C를 누르세요")
    
    # 브라우저를 별도 스레드에서 열기
    browser_thread = Thread(target=open_browser)
    browser_thread.daemon = True
    browser_thread.start()
    
    # Streamlit 실행
    run_streamlit()
