"""
DB 연결 테스트 스크립트
"""
import os
import sys
from pathlib import Path
from dotenv import load_dotenv

# Windows 터미널 cp949 환경에서 이모지 출력 가능하도록 utf-8 강제 설정
if sys.stdout.encoding != 'utf-8':
    sys.stdout.reconfigure(encoding='utf-8')

# 프로젝트 루트 경로 설정
project_root = Path(__file__).resolve().parent
env_path = project_root / '.env'

print(f"프로젝트 루트: {project_root}")
print(f".env 파일 경로: {env_path}")
print(f".env 파일 존재: {env_path.exists()}")
print()

# .env 파일 로드
load_dotenv(env_path)

DB_HOST = os.getenv("DB_HOST", "")
DB_PORT = os.getenv("DB_PORT", "")
DB_NAME = os.getenv("DB_NAME", "")
DB_USER = os.getenv("DB_USER", "")
DB_PASSWORD = os.getenv("DB_PASSWORD", "")

if not DB_HOST:
    print("❌ DB_HOST가 설정되지 않았습니다!")
    print("   .env 파일을 확인하세요.")
    sys.exit(1)

print("=" * 60)
print("DB 연결 정보:")
print("=" * 60)
print(f"호스트: {DB_HOST}")
print(f"포트: {DB_PORT}")
print(f"DB명: {DB_NAME}")
print(f"사용자: {DB_USER}")
print(f"비밀번호: {'*' * len(DB_PASSWORD) if DB_PASSWORD else '(없음)'}")
print("=" * 60)

# SQLAlchemy로 연결 테스트
try:
    from sqlalchemy import create_engine, text
    from urllib.parse import quote_plus

    # 특수문자 URL 인코딩
    encoded_password = quote_plus(DB_PASSWORD)
    encoded_user = quote_plus(DB_USER)

    # 포트가 있으면 포함, 없으면 제외
    if DB_PORT:
        host_port = f"{DB_HOST}:{DB_PORT}"
    else:
        host_port = DB_HOST

    conn_str = (
        f"mssql+pyodbc://{encoded_user}:{encoded_password}@"
        f"{host_port}/{DB_NAME}"
        f"?driver=ODBC+Driver+17+for+SQL+Server&timeout=30"
    )

    print("\n연결 문자열:")
    print(conn_str.replace(DB_PASSWORD, "***"))
    print("\n연결 시도 중...")

    engine = create_engine(conn_str, connect_args={'timeout': 10})

    with engine.connect() as conn:
        result = conn.execute(text("SELECT 1 AS test"))
        print("✅ DB 연결 성공!")
        print(f"테스트 쿼리 결과: {result.fetchone()}")

        # 서버 버전 확인
        result = conn.execute(text("SELECT @@VERSION AS version"))
        version = result.fetchone()[0]
        print(f"\nSQL Server 버전:\n{version[:100]}...")

except Exception as e:
    print(f"❌ DB 연결 실패!")
    print(f"에러: {e}")
    import traceback
    print("\n상세 에러:")
    print(traceback.format_exc())

    print("\n" + "=" * 60)
    print("해결 방법:")
    print("=" * 60)
    print("1. AWS RDS 콘솔에서 포트 번호 확인 (보통 1433)")
    print("2. 보안 그룹 인바운드 규칙에서 현재 IP 허용 확인")
    print("   - 현재 IP: https://www.whatismyip.com/ 에서 확인")
    print("   - 보안 그룹에 해당 IP/32 추가")
    print("3. RDS가 'Public accessible' 상태인지 확인")
    print("4. DB 비밀번호 확인")
