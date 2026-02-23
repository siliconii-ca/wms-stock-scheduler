@echo off
chcp 65001 >nul
echo ====================================
echo WMS Stock Scheduler 빌드 스크립트
echo ====================================
echo.

REM 이전 빌드 파일 정리
echo [1/4] 이전 빌드 정리 중...
if exist "dist" rmdir /s /q "dist"
if exist "build" rmdir /s /q "build"
echo ✅ 정리 완료
echo.

REM PyInstaller로 빌드
echo [2/4] PyInstaller 빌드 중...
pyinstaller --clean wms-stock-scheduler.spec
if %errorlevel% neq 0 (
    echo ❌ 빌드 실패!
    pause
    exit /b 1
)
echo ✅ 빌드 완료
echo.

REM 필요한 파일 복사
echo [3/4] 추가 파일 복사 중...

REM .env 파일이 이미 spec에서 포함됨
REM 하지만 사용자가 수정할 수 있도록 dist 폴더에 .env.example 생성
if exist ".env" (
    copy ".env" "dist\.env.example" >nul
    echo ✅ .env.example 복사 완료
)

REM README 파일 복사 (있으면)
if exist "README.md" (
    copy "README.md" "dist\README.md" >nul
    echo ✅ README 복사 완료
)

echo.

REM 완료
echo [4/4] 빌드 완료!
echo.
echo 📁 실행 파일 위치: dist\WMS-Stock-Scheduler.exe
echo.
echo 💡 사용 방법:
echo    1. dist 폴더를 원하는 위치에 복사
echo    2. .env.example을 .env로 복사하고 설정 수정
echo    3. WMS-Stock-Scheduler.exe 실행
echo.
echo 💡 DB Export 모드 실행:
echo    WMS-Stock-Scheduler.exe export
echo.
pause
