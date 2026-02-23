# WMS Stock Scheduler 빌드 가이드

## 📦 빌드 방법

### 1. 사전 준비

```bash
# PyInstaller 설치 확인
pip install -r requirements.txt
```

### 2. 빌드 실행

#### 방법 1: 배치 스크립트 사용 (추천)
```bash
build.bat
```

#### 방법 2: 직접 명령 실행
```bash
# 이전 빌드 정리
rmdir /s /q dist
rmdir /s /q build

# PyInstaller 실행
python -m PyInstaller --clean wms-stock-scheduler.spec
```

### 3. 빌드 결과

빌드가 완료되면 `dist` 폴더에 실행 파일이 생성됩니다:

```
dist/
└── WMS-Stock-Scheduler.exe  (약 44MB)
```

---

## 📂 배포 파일 준비

### 1. 필수 파일 복사

배포할 폴더를 만들고 다음 파일들을 복사합니다:

```
WMS-Stock-Scheduler/
├── WMS-Stock-Scheduler.exe  (빌드된 실행 파일)
├── .env                      (환경 설정 파일)
└── repository/
    └── stock_export.sql      (SQL 쿼리 파일)
```

### 2. .env 파일 준비

`.env` 파일을 배포 폴더에 복사하고 필요한 설정을 수정합니다:

```env
# 데이터베이스 설정
DB_TYPE=mssql
DB_HOST=your-database-host
DB_PORT=1433
DB_NAME=CMSGLOBAL
DB_USER=your-username
DB_PASSWORD=your-password

# 출력 경로
DB_EXPORT_OUTPUT_DIR=D:/inventory-test/daily-stock

# 슬랙 알림
SEND_SLACK_NOTIFICATION=true
COMMON_API_PATH=https://your-api-server
SLACK_DM_RECEIVER=your-email@example.com

# Notion 리포트
SEND_NOTION_REPORT=true
NOTION_API_TOKEN=your-notion-token
NOTION_PAGE_ID=your-notion-page-id
```

### 3. SQL 파일 확인

`repository/stock_export.sql` 파일이 있는지 확인합니다.

---

## 🚀 실행 방법

### 일반 실행 (스케줄러 모드)

```bash
WMS-Stock-Scheduler.exe
```

### DB Export 모드

```bash
WMS-Stock-Scheduler.exe export
```

---

## 📋 배포 체크리스트

배포하기 전에 다음 항목을 확인하세요:

- [ ] `WMS-Stock-Scheduler.exe` 파일이 있는가?
- [ ] `.env` 파일이 올바르게 설정되었는가?
- [ ] `repository/stock_export.sql` 파일이 있는가?
- [ ] 데이터베이스 연결 정보가 정확한가?
- [ ] 출력 경로가 존재하는가? (없으면 자동 생성됨)
- [ ] Notion 페이지가 Integration과 연결되었는가?

---

## 🔧 문제 해결

### 실행 시 "Unable to connect to database" 오류
- `.env` 파일의 DB 연결 정보 확인
- 네트워크 방화벽 확인
- SQL Server ODBC 드라이버 설치 확인

### 실행 시 "ModuleNotFoundError" 오류
- 빌드를 다시 실행해주세요
- `--clean` 옵션으로 완전히 새로 빌드

### 슬랙 전송 실패
- `COMMON_API_PATH` 주소 확인
- SSL 인증서 문제일 수 있음 (코드에서 verify=False 처리됨)

### Notion 페이지 생성 실패
- `NOTION_PAGE_ID`가 올바른지 확인
- Notion 페이지에서 Integration 연결 확인
- `python test_notion_connection.py`로 테스트

---

## 📦 전체 배포 폴더 구조 예시

```
WMS-Stock-Scheduler-v1.0/
├── WMS-Stock-Scheduler.exe
├── .env
├── repository/
│   └── stock_export.sql
├── README.md (선택)
└── logs/ (자동 생성됨)
```

이 폴더를 압축하여 배포하면 됩니다.

---

## 💡 팁

### 자동 시작 설정 (Windows)

1. `WMS-Stock-Scheduler.exe` 바로가기 생성
2. 바로가기를 `shell:startup` 폴더에 복사
   - `Win + R` → `shell:startup` 입력
3. Windows 시작 시 자동 실행됩니다

### Windows 서비스로 등록 (선택)

NSSM (Non-Sucking Service Manager) 사용:
```bash
nssm install WMSStockScheduler "C:\path\to\WMS-Stock-Scheduler.exe"
nssm start WMSStockScheduler
```

---

## 🔄 업데이트 방법

1. 코드 수정 후 다시 빌드
2. `dist/WMS-Stock-Scheduler.exe` 파일만 교체
3. `.env` 파일은 유지 (설정이 변경되지 않았다면)
