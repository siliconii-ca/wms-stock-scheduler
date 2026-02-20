"""
설치된 ODBC 드라이버 확인
"""
import pyodbc

print("=" * 60)
print("설치된 ODBC 드라이버 목록:")
print("=" * 60)

drivers = pyodbc.drivers()
for i, driver in enumerate(drivers, 1):
    print(f"{i}. {driver}")

print("\n" + "=" * 60)
print("권장 드라이버:")
print("=" * 60)

if any("17" in d for d in drivers):
    print("✅ ODBC Driver 17 for SQL Server - 사용 가능")
elif any("13" in d for d in drivers):
    print("⚠️ ODBC Driver 13 for SQL Server - 사용 가능 (구버전)")
elif any("11" in d for d in drivers):
    print("⚠️ SQL Server Native Client 11.0 - 사용 가능 (구버전)")
else:
    print("❌ SQL Server용 ODBC 드라이버를 찾을 수 없습니다!")
    print("\n다운로드: https://learn.microsoft.com/en-us/sql/connect/odbc/download-odbc-driver-for-sql-server")
