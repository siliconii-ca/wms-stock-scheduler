@echo off
chcp 65001 >nul
echo ====================================
echo WMS Stock Scheduler 배포 패키지 생성
echo ====================================
echo.

REM 배포 폴더 이름 설정
set DEPLOY_DIR=WMS-Stock-Scheduler-Deploy

REM 이전 배포 폴더 삭제
if exist "%DEPLOY_DIR%" (
    echo [1/5] 이전 배포 폴더 삭제 중...
    rmdir /s /q "%DEPLOY_DIR%"
)

REM 배포 폴더 생성
echo [2/5] 배포 폴더 생성 중...
mkdir "%DEPLOY_DIR%"
mkdir "%DEPLOY_DIR%\repository"

REM 실행 파일 복사
echo [3/5] 실행 파일 복사 중...
if exist "dist\WMS-Stock-Scheduler.exe" (
    copy "dist\WMS-Stock-Scheduler.exe" "%DEPLOY_DIR%\" >nul
    echo ✅ WMS-Stock-Scheduler.exe 복사 완료
) else (
    echo ❌ 실행 파일이 없습니다. 먼저 build.bat를 실행하세요.
    pause
    exit /b 1
)

REM 필수 파일 복사
echo [4/5] 필수 파일 복사 중...

REM .env 파일
if exist ".env" (
    copy ".env" "%DEPLOY_DIR%\.env.example" >nul
    echo ✅ .env.example 복사 완료 (배포 시 .env로 이름 변경 필요)
)

REM SQL 파일
if exist "repository\stock_export.sql" (
    copy "repository\stock_export.sql" "%DEPLOY_DIR%\repository\" >nul
    echo ✅ stock_export.sql 복사 완료
)

REM README 파일
if exist "BUILD_GUIDE.md" (
    copy "BUILD_GUIDE.md" "%DEPLOY_DIR%\README.md" >nul
    echo ✅ README 복사 완료
)

REM 사용 설명서 생성
echo [5/5] 사용 설명서 생성 중...
(
echo WMS Stock Scheduler 사용 가이드
echo ===================================
echo.
echo 1. 설치 방법
echo    - .env.example 파일을 .env로 이름 변경
echo    - .env 파일을 열어서 데이터베이스 정보 등 설정 수정
echo.
echo 2. 실행 방법
echo    [스케줄러 모드]
echo    WMS-Stock-Scheduler.exe
echo.
echo    [DB Export 모드]
echo    WMS-Stock-Scheduler.exe export
echo.
echo 3. 필수 확인 사항
echo    - SQL Server ODBC 드라이버 설치 필요
echo    - 데이터베이스 접속 정보 확인
echo    - 출력 경로 폴더 생성
echo    - Notion Integration 연결
echo.
echo 4. 로그 확인
echo    - logs 폴더에 일별 로그 자동 생성
echo.
echo 자세한 내용은 README.md를 참고하세요.
) > "%DEPLOY_DIR%\사용방법.txt"
echo ✅ 사용방법.txt 생성 완료

echo.
echo ====================================
echo 배포 패키지 생성 완료!
echo ====================================
echo.
echo 📁 배포 폴더: %DEPLOY_DIR%\
echo.
echo 💡 다음 단계:
echo    1. %DEPLOY_DIR% 폴더를 압축
echo    2. 대상 서버에 압축 해제
echo    3. .env.example을 .env로 이름 변경
echo    4. .env 파일 설정 수정
echo    5. WMS-Stock-Scheduler.exe 실행
echo.
echo 📦 압축하려면: 우클릭 -^> "보내기" -^> "압축(ZIP) 폴더"
echo.
pause
