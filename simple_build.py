"""
간단한 EXE 빌드 스크립트
"""
import subprocess
import sys

# PyInstaller 실행
print("EXE 파일 빌드 중...")

subprocess.call([
    sys.executable, "-m", "PyInstaller",
    "--onefile",
    "--name", "musinsa_dashboard",
    "--add-data", "app.py;.",
    "--add-data", "requirements.txt;.",
    "--hidden-import", "streamlit",
    "--hidden-import", "pandas",
    "--hidden-import", "plotly",
    "--console",
    "app.py"
])

print("빌드 완료! dist 폴더를 확인하세요.")