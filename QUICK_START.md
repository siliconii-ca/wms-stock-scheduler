# WMS Stock Scheduler - 빠른 시작 가이드

## 🚀 빌드 & 배포 3단계

### 1단계: 빌드하기

```bash
build.bat
```

**결과**: `dist\WMS-Stock-Scheduler.exe` 생성 (44MB)

---

### 2단계: 배포 패키지 만들기

```bash
deploy.bat
```

**결과**: `WMS-Stock-Scheduler-Deploy` 폴더 생성

**폴더 구조**:
```
WMS-Stock-Scheduler-Deploy/
├── WMS-Stock-Scheduler.exe     ← 실행 파일
├── .env.example                 ← 설정 파일 (이름 변경 필요)
├── repository/
│   └── stock_export.sql         ← SQL 쿼리
├── README.md                    ← 가이드
└── 사용방법.txt                 ← 간단 가이드
```

---

### 3단계: 배포하기

#### A. 압축하기
`WMS-Stock-Scheduler-Deploy` 폴더를 우클릭 → "보내기" → "압축(ZIP) 폴더"

#### B. 서버에 설치
1. ZIP 파일을 대상 서버에 복사
2. 압축 해제
3. `.env.example` → `.env`로 이름 변경
4. `.env` 파일 열어서 설정 수정:
   ```env
   DB_HOST=실제데이터베이스주소
   DB_USER=실제사용자명
   DB_PASSWORD=실제비밀번호
   ```

#### C. 실행
```bash
WMS-Stock-Scheduler.exe
```

---

## 📋 빠른 체크리스트

### 빌드 전
- [ ] Python 3.12 설치됨
- [ ] `pip install -r requirements.txt` 실행됨
- [ ] PyInstaller 설치 확인됨

### 배포 전
- [ ] `build.bat` 실행 완료
- [ ] `dist\WMS-Stock-Scheduler.exe` 존재 확인
- [ ] `deploy.bat` 실행 완료
- [ ] 배포 폴더에 모든 파일 있음

### 서버 설치 전
- [ ] SQL Server ODBC 드라이버 설치됨
- [ ] 데이터베이스 접속 가능
- [ ] 출력 경로 폴더 존재 (또는 생성 권한 있음)
- [ ] Notion Integration 생성 및 페이지 연결

---

## 🎯 주요 명령어

| 작업 | 명령어 |
|------|--------|
| 빌드 | `build.bat` |
| 배포 패키지 생성 | `deploy.bat` |
| 스케줄러 실행 | `WMS-Stock-Scheduler.exe` |
| DB Export 실행 | `WMS-Stock-Scheduler.exe export` |
| Notion 테스트 | `python test_notion_connection.py` |

---

## 💡 문제 해결

### "빌드가 안 돼요!"
```bash
# PyInstaller 재설치
pip uninstall pyinstaller
pip install pyinstaller

# 클린 빌드
build.bat
```

### "실행이 안 돼요!"
1. `.env` 파일 있는지 확인
2. `repository\stock_export.sql` 파일 있는지 확인
3. 로그 폴더 확인: `logs\app_YYYY-MM-DD.log`

### "Notion 연결 안 돼요!"
```bash
# 테스트 실행
python test_notion_connection.py

# 페이지 ID 재확인
# Notion 페이지 → 우측 상단 ⋯ → Connections → Integration 연결
```

---

## 📞 도움말

- 상세 가이드: `BUILD_GUIDE.md`
- 사용 방법: `사용방법.txt` (배포 폴더)
- 로그 확인: `logs/` 폴더
