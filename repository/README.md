# Repository - SQL 쿼리 관리

이 폴더는 DB 조회에 사용되는 SQL 쿼리를 관리합니다.

## 📁 파일 구조

```
repository/
├── README.md
└── stock_export.sql      # 재고 데이터 조회 쿼리
```

## 📝 SQL 파일 수정 방법

### stock_export.sql

재고 데이터를 조회하는 쿼리입니다.

**주의사항:**
- 컬럼 별칭(AS)은 반드시 작은따옴표로 감싸야 합니다: `AS '상품코드'`
- 필수 컬럼: 상품코드, 상품명, CMS 재고, WMS 재고, 대기 수량, 일치율
- WHERE 조건을 수정하여 특정 조건의 데이터만 가져올 수 있습니다

**예시:**
```sql
SELECT
    prod_cd AS '상품코드',
    prod_nm AS '상품명',
    brand AS '브랜드',
    cms_total_qty AS 'CMS 재고',
    wms_total_qty AS 'WMS 재고',
    waiting_qty AS '대기 수량',
    accuracy AS '일치율'
FROM stock_view
WHERE is_active = 1
    AND date = CONVERT(DATE, GETDATE())
ORDER BY prod_cd
```

## 🔧 환경 설정

`.env` 파일에서 사용할 SQL 파일을 지정할 수 있습니다:

```env
DB_EXPORT_SQL_FILE=repository/stock_export.sql
```

## 📌 추가 SQL 파일 작성

다른 용도의 SQL 파일을 추가로 만들 수 있습니다:

```
repository/
├── stock_export.sql           # 기본 재고 조회
├── stock_history_export.sql   # 재고 이력 조회
└── custom_report.sql          # 커스텀 리포트
```

각 파일은 독립적으로 관리되며, 환경변수로 선택할 수 있습니다.
