"""
무신사 대시보드 EXE 빌드 스크립트
PyInstaller를 사용하여 실행 파일 생성
"""

import os
import sys
import subprocess
import shutil

def install_pyinstaller():
    """PyInstaller 설치"""
    print("PyInstaller 설치 중...")
    subprocess.check_call([sys.executable, "-m", "pip", "install", "pyinstaller"])

def create_run_script():
    """실행 스크립트 생성"""
    run_script = '''import sys
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
'''
    
    with open("run_app.py", "w", encoding="utf-8") as f:
        f.write(run_script)
    
    print("실행 스크립트 생성 완료")

def create_spec_file():
    """PyInstaller spec 파일 생성"""
    spec_content = '''# -*- mode: python ; coding: utf-8 -*-

block_cipher = None

a = Analysis(
    ['run_app.py'],
    pathex=[],
    binaries=[],
    datas=[
        ('app.py', '.'),
        ('requirements.txt', '.'),
        ('.streamlit', '.streamlit'),
    ],
    hiddenimports=[
        'streamlit',
        'pandas',
        'plotly',
        'plotly.express',
        'plotly.graph_objects',
        'altair',
        'numpy',
        'pyarrow',
    ],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[],
    win_no_prefer_redirects=False,
    win_private_assemblies=False,
    cipher=block_cipher,
    noarchive=False,
)

pyz = PYZ(a.pure, a.zipped_data, cipher=block_cipher)

exe = EXE(
    pyz,
    a.scripts,
    a.binaries,
    a.zipfiles,
    a.datas,
    [],
    name='무신사_대시보드',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    upx_exclude=[],
    runtime_tmpdir=None,
    console=True,
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
    icon='icon.ico' if os.path.exists('icon.ico') else None,
)
'''
    
    with open("musinsa_dashboard.spec", "w", encoding="utf-8") as f:
        f.write(spec_content)
    
    print(" Spec 파일 생성 완료")

def build_exe():
    """EXE 파일 빌드"""
    print(" EXE 파일 빌드 중... (시간이 걸릴 수 있습니다)")
    
    # PyInstaller 실행
    subprocess.check_call([
        sys.executable, "-m", "PyInstaller",
        "--onefile",
        "--name", "무신사_대시보드",
        "--add-data", "app.py;.",
        "--add-data", "requirements.txt;.",
        "--add-data", ".streamlit;.streamlit",
        "--hidden-import", "streamlit",
        "--hidden-import", "pandas",
        "--hidden-import", "plotly",
        "--collect-all", "streamlit",
        "--collect-all", "plotly",
        "--console",
        "run_app.py"
    ])
    
    print(" EXE 파일 빌드 완료")
    print(" dist 폴더에서 '무신사_대시보드.exe' 파일을 확인하세요")

def create_installer_script():
    """NSIS 설치 스크립트 생성"""
    nsis_script = '''!define PRODUCT_NAME "무신사 패션 분석 대시보드"
!define PRODUCT_VERSION "1.0"
!define PRODUCT_PUBLISHER "Musinsa Analysis"

Name "${PRODUCT_NAME} ${PRODUCT_VERSION}"
OutFile "무신사_대시보드_설치.exe"
InstallDir "$PROGRAMFILES\\무신사대시보드"

Section "MainSection" SEC01
    SetOutPath "$INSTDIR"
    File "dist\\무신사_대시보드.exe"
    File "app.py"
    File "requirements.txt"
    CreateDirectory "$INSTDIR\\.streamlit"
    File /r ".streamlit\\*.*"
    
    CreateDirectory "$SMPROGRAMS\\무신사 대시보드"
    CreateShortcut "$SMPROGRAMS\\무신사 대시보드\\무신사 대시보드.lnk" "$INSTDIR\\무신사_대시보드.exe"
    CreateShortcut "$DESKTOP\\무신사 대시보드.lnk" "$INSTDIR\\무신사_대시보드.exe"
SectionEnd

Section "Uninstall"
    Delete "$INSTDIR\\*.*"
    RMDir /r "$INSTDIR"
    Delete "$SMPROGRAMS\\무신사 대시보드\\*.*"
    RMDir "$SMPROGRAMS\\무신사 대시보드"
    Delete "$DESKTOP\\무신사 대시보드.lnk"
SectionEnd
'''
    
    with open("installer.nsi", "w", encoding="utf-8") as f:
        f.write(nsis_script)
    
    print(" 설치 스크립트 생성 완료")
    print(" NSIS를 사용하여 installer.nsi를 컴파일하면 설치 파일이 생성됩니다")

def main():
    print("무신사 대시보드 EXE 빌드 시작")
    
    # 1. PyInstaller 설치
    try:
        import PyInstaller
        print("PyInstaller가 이미 설치되어 있습니다")
    except ImportError:
        install_pyinstaller()
    
    # 2. 실행 스크립트 생성
    create_run_script()
    
    # 3. EXE 빌드
    build_exe()
    
    # 4. 설치 스크립트 생성
    create_installer_script()
    
    print("\n빌드 완료!")
    print("dist/무신사_대시보드.exe - 실행 파일")
    print("installer.nsi - 설치 프로그램 스크립트 (NSIS 필요)")

if __name__ == "__main__":
    main()