"""
📊 재고 일치율 변동 분석 도구
- CSV 파일 비교
- 마크다운 리포트 자동 생성
- Claude AI와 호환되는 형식
"""

import sys
import pandas as pd
from datetime import datetime, timedelta
import os
from dotenv import load_dotenv

# .env 파일 로드 (환경변수 읽기)
load_dotenv()

# Windows 터미널 cp949 환경에서 이모지 출력 가능하도록 utf-8 강제 설정
if sys.stdout.encoding != 'utf-8':
    sys.stdout.reconfigure(encoding='utf-8')

# ========================================
# ⚙️ 설정 (여기만 수정하면 됨!)
# ========================================

# CSV 파일이 있는 폴더 (당신의 환경에 맞게 수정)
INPUT_DIR = "D:/inventory-test/daily-stock" 

# 리포트 저장 폴더
OUTPUT_DIR = "./output"

# 파일명 형식 (당신의 파일명에 맞게)
# 예: Stock2026-02-11.csv
FILE_FORMAT = "Stock{date}.csv"

# ========================================
# 📋 CSV 컬럼명 매핑 (파일 컬럼명에 맞게 수정)
# ========================================
COL_PROD_CD   = "상품코드"
COL_PRODUCT_NAME = "상품명"
COL_BRAND        = "브랜드"
COL_CMS_QTY      = "CMS 재고"
COL_WMS_QTY      = "WMS 재고"
COL_WAITING_QTY  = "대기 수량"
COL_ACCURACY     = "일치율"    # CSV에 이미 존재하는 일치율 컬럼

print(f"🔧 설정")
print(f"  입력: {INPUT_DIR}")
print(f"  출력: {OUTPUT_DIR}")

# ========================================
# 📐 함수들
# ========================================

def calculate_accuracy(cms_qty, wms_qty, waiting_qty):
    """
    일치율 계산 정책 (JS 로직 동일 적용)

    규칙:
    - cms == 0 AND physical == 0 → 100.0
    - cms == 0 OR  physical == 0 → 0.0
    - cms <  0 OR  physical <  0 → 0.0
    - 그 외 → round(min/max * 100, 1)
      - 반올림으로 100이 됐지만 실제로 같지 않으면 → 99.9
      - 진짜 cms == physical 이면 → 100.0
    """
    try:
        cms = float(cms_qty) if pd.notna(cms_qty) else 0
        physical = float(wms_qty or 0) + float(waiting_qty or 0)

        if cms == 0 and physical == 0:
            return 100.0
        elif cms == 0 or physical == 0:
            return 0.0
        elif cms < 0 or physical < 0:
            return 0.0
        else:
            least = min(cms, physical)
            greatest = max(cms, physical)
            valid = round(least / greatest * 100, 1)
            if valid >= 100 and least != greatest:
                valid = 99.9
            return valid
    except:
        return 0.0


def load_and_prepare_data(input_dir, file_format, target_date):
    """
    CSV 파일 로드 및 컬럼 정규화

    Args:
        input_dir: CSV 파일이 있는 폴더
        file_format: 파일명 형식 (예: "Stock{date}.csv")
        target_date: 대상 날짜 (datetime)

    Returns:
        정규화된 DataFrame (컬럼: prod_cd, prod_nm, cms_qty, wms_qty, waiting_qty, accuracy)
    """
    date_str = target_date.strftime("%Y-%m-%d")

    # 파일명 생성
    filename = file_format.replace("{date}", date_str)
    filepath = os.path.join(input_dir, filename)

    print(f"\n📂 파일 로드: {filename}")

    try:
        # CSV 읽기 (한글 인코딩 - utf-8-sig는 BOM 포함 파일도 처리)
        try:
            df = pd.read_csv(filepath, encoding='utf-8-sig')
        except UnicodeDecodeError:
            df = pd.read_csv(filepath, encoding='cp949')

        # 마지막 행 제거 (합계/요약 행)
        df = df.iloc[:-1]

        # 컬럼 정규화 (내부 처리용 이름으로 통일)
        df = df.rename(columns={
            COL_PROD_CD:     'prod_cd',
            COL_PRODUCT_NAME: 'prod_nm',
            COL_CMS_QTY:     'cms_qty',
            COL_WMS_QTY:     'wms_qty',
            COL_WAITING_QTY: 'waiting_qty',
        })

        # 수치 컬럼 강제 변환 (문자열/NaN → 숫자, 변환 불가 값은 0)
        for col in ('cms_qty', 'wms_qty', 'waiting_qty'):
            if col in df.columns:
                df[col] = pd.to_numeric(df[col], errors='coerce').fillna(0)

        # 일치율: CSV에 이미 존재하면 그대로 사용, 없으면 계산
        if COL_ACCURACY in df.columns:
            # "0%" 같은 문자열이면 숫자로 변환
            df['accuracy'] = (
                df[COL_ACCURACY]
                .astype(str)
                .str.replace('%', '', regex=False)
                .str.strip()
                .apply(lambda x: float(x) if x not in ('', 'nan') else 0.0)
            )
        else:
            df['accuracy'] = df.apply(
                lambda row: calculate_accuracy(
                    row.get('cms_qty'),
                    row.get('wms_qty'),
                    row.get('waiting_qty')
                ), axis=1
            )

        print(f"  ✅ 로드 완료: {len(df)}개 상품")
        return df

    except FileNotFoundError:
        print(f"  ❌ 파일 없음: {filepath}")
        return None
    except Exception as e:
        print(f"  ❌ 오류: {str(e)}")
        return None


def compare_inventory(yesterday_df, today_df):
    """
    어제와 오늘 데이터 비교
    
    Returns:
        변동이 있는 상품들의 DataFrame
    """
    if yesterday_df is None or today_df is None:
        print("❌ 데이터 로드 실패")
        return None
    
    print("\n📊 데이터 비교 중...")
    
    # 병합 (상품코드 기준)
    comparison = today_df.merge(
        yesterday_df,
        on='prod_cd',
        suffixes=('_today', '_yesterday'),
        how='outer'
    )

    # 필요한 컬럼만 선택
    columns_needed = [
        'prod_cd', 'prod_nm_today',
        'cms_qty_today', 'wms_qty_today', 'waiting_qty_today', 'accuracy_today',
        'cms_qty_yesterday', 'wms_qty_yesterday', 'waiting_qty_yesterday', 'accuracy_yesterday'
    ]

    # 없는 컬럼 제거
    columns_to_use = [col for col in columns_needed if col in comparison.columns]
    comparison = comparison[columns_to_use]

    # 컬럼 이름 정리
    rename_map = {
        'prod_nm_today': 'prod_nm',
    }
    comparison = comparison.rename(columns=rename_map)

    # 한쪽 날짜에 상품이 없는 경우: 재고 0, 일치율 100으로 처리
    qty_today_cols = [c for c in ['cms_qty_today', 'wms_qty_today', 'waiting_qty_today'] if c in comparison.columns]
    qty_yesterday_cols = [c for c in ['cms_qty_yesterday', 'wms_qty_yesterday', 'waiting_qty_yesterday'] if c in comparison.columns]

    for col in qty_today_cols:
        comparison[col] = pd.to_numeric(comparison[col], errors='coerce').fillna(0)
    for col in qty_yesterday_cols:
        comparison[col] = pd.to_numeric(comparison[col], errors='coerce').fillna(0)

    # 일치율: 데이터가 없는 쪽(NaN)은 100으로 채우기
    if 'accuracy_today' in comparison.columns:
        comparison['accuracy_today'] = pd.to_numeric(comparison['accuracy_today'], errors='coerce').fillna(100)
    if 'accuracy_yesterday' in comparison.columns:
        comparison['accuracy_yesterday'] = pd.to_numeric(comparison['accuracy_yesterday'], errors='coerce').fillna(100)    
    # 일치율 변동 계산
    comparison['change'] = comparison['accuracy_today'] - comparison['accuracy_yesterday']
    comparison['change_abs'] = abs(comparison['change'])

    # CMS 변화량 및 WMS수량(wms+waiting) 변화량 계산
    comparison['cms_diff'] = comparison['cms_qty_today'] - comparison['cms_qty_yesterday']
    waiting_today = comparison.get('waiting_qty_today', 0).fillna(0)
    waiting_yesterday = comparison.get('waiting_qty_yesterday', 0).fillna(0)
    comparison['physical_today'] = comparison['wms_qty_today'] + waiting_today
    comparison['physical_yesterday'] = comparison['wms_qty_yesterday'] + waiting_yesterday
    comparison['physical_diff'] = comparison['physical_today'] - comparison['physical_yesterday']

    # 변동 있는 상품만 필터 (일치율 변화 & CMS/WMS수량 변화량이 다른 것만)
    changed = comparison[
        (comparison['change_abs'] > 0.0) &
        (comparison['cms_diff'] != comparison['physical_diff'])
    ].copy()
    changed = changed.sort_values('change_abs', ascending=False)
    
    print(f"  📈 총 상품: {len(comparison)}")
    print(f"  🔄 변동 상품: {len(changed)}")
    print(f"  📊 변동 비율: {len(changed)/len(comparison)*100:.1f}%")
    
    return comparison, changed


def generate_markdown_report(comparison, changed, date_str):
    """
    마크다운 형식의 리포트 생성
    
    Claude AI가 읽기 쉽도록 최적화
    """
    
    total = len(comparison)
    change_count = len(changed)
    
    # 통계
    if change_count > 0:
        avg_change = changed['change_abs'].mean()
        max_change = changed['change_abs'].max()
        min_change = changed['change_abs'].min()
        increase_count = len(changed[changed['change'] > 0])
        decrease_count = len(changed[changed['change'] < 0])
    else:
        avg_change = max_change = min_change = 0
        increase_count = decrease_count = 0
    
    # 마크다운 작성
    md = f"""# 📊 재고 일치율 변동 분석 리포트

**기준일:** {date_str}  
**생성일시:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

---

## 📈 개요

| 지표 | 값 |
|------|-----|
| 총 상품 수 | {total}개 |
| 변동 상품 | {change_count}개 |
| 변동 비율 | {change_count/total*100:.1f}% |
| 평균 변동폭 | {avg_change:.2f}% |
| 최대 변동 | {max_change:.2f}% |
| 최소 변동 | {min_change:.2f}% |

---

## 🔄 변동 분석

### 변동 방향
- **증가** (일치율 상승): {increase_count}개
- **감소** (일치율 하락): {decrease_count}개

"""
    
    # 변동 상품 상세 정보
    if change_count > 0:
        md += "## ⚠️ 변동 상품 상세\n\n"

        def format_row(idx, row):
            waiting_today     = float(row.get('waiting_qty_today', 0) or 0)
            waiting_yesterday = float(row.get('waiting_qty_yesterday', 0) or 0)
            cms_diff      = float(row['cms_qty_today']) - float(row['cms_qty_yesterday'])
            # WMS 수량 = wms + waiting, 일치율 정책 기준 물리재고
            physical_today     = float(row['wms_qty_today']) + waiting_today
            physical_yesterday = float(row['wms_qty_yesterday']) + waiting_yesterday
            physical_diff      = physical_today - physical_yesterday
            return (
                f"{idx}. **{row['prod_cd']}** | "
                f"일치율 {row['accuracy_today']:.1f}% ({row['change']:+.1f}%) | "
                f"CMS {row['cms_qty_today']:.0f} ({cms_diff:+.0f}) | "
                f"WMS수량 {physical_today:.0f} ({physical_diff:+.0f})\n"
            )

        # 일치율 증가 섹션 (변동폭 큰 순)
        increased = changed[changed['change'] > 0].sort_values('change', ascending=False)
        if len(increased) > 0:
            md += f"### 📈 일치율 증가 ({len(increased)}개)\n\n"
            for idx, (_, row) in enumerate(increased.iterrows(), 1):
                md += format_row(idx, row)
            md += "\n"

        # 일치율 감소 섹션 (변동폭 큰 순)
        decreased = changed[changed['change'] < 0].sort_values('change', ascending=True)
        if len(decreased) > 0:
            md += f"### 📉 일치율 감소 ({len(decreased)}개)\n\n"
            for idx, (_, row) in enumerate(decreased.iterrows(), 1):
                md += format_row(idx, row)
            md += "\n"
    else:
        md += "\n✅ **변동 상품 없음** - 재고가 정상입니다.\n\n"
    
    # 마크다운 결론
    md += f"""
---

## 💡 해석

- **일치율 정의:** min(전산재고, 물류재고) / max(전산재고, 물류재고) × 100
- **높은 변동 원인:**
  - 출고/입고 후 WMS 미반영
  - 순환재고조사 실시
  - 시스템 동기화 오류
  - 반품/취소 처리

---

## 📝 다음 조치

1. **변동 상품 확인** - 우선순위순 확인
2. **원인 파악** - 출입고 이력 검토
3. **조정** - 필요시 재고 조정
4. **검증** - 다음 주기에 개선 확인

---

*이 리포트는 자동으로 생성되었습니다.*
"""
    
    return md


def generate_csv_report(changed, date_str):
    """
    CSV 형식의 리포트도 생성 (엑셀에서 열 수 있음)
    """
    if changed is None or len(changed) == 0:
        return None
    
    # 존재하는 컬럼만 선택
    base_cols = [
        'prod_cd', 'prod_nm',
        'accuracy_yesterday', 'accuracy_today', 'change',
        'cms_qty_yesterday', 'cms_qty_today',
        'wms_qty_yesterday', 'wms_qty_today',
    ]
    waiting_cols = [c for c in ['waiting_qty_yesterday', 'waiting_qty_today'] if c in changed.columns]
    select_cols = base_cols + waiting_cols
    select_cols = [c for c in select_cols if c in changed.columns]

    report = changed[select_cols].copy()

    rename_map = {
        'prod_cd':  '상품코드',
        'prod_nm':  '상품명',
        'accuracy_yesterday':  '어제_일치율(%)',
        'accuracy_today':      '오늘_일치율(%)',
        'change':              '변동(%)',
        'cms_qty_yesterday':   '어제_CMS재고',
        'cms_qty_today':       '오늘_CMS재고',
        'wms_qty_yesterday':   '어제_WMS재고',
        'wms_qty_today':       '오늘_WMS재고',
        'waiting_qty_yesterday':   '어제_대기재고',
        'waiting_qty_today':       '오늘_대기재고',
    }
    report = report.rename(columns=rename_map)
    
    return report


def save_reports(markdown_content, csv_df, date_str, output_dir):
    """
    리포트 저장 (마크다운 + CSV)
    """
    # 출력 폴더 생성
    os.makedirs(output_dir, exist_ok=True)
    
    print(f"\n💾 리포트 저장 중...")
    
    # 마크다운 저장
    md_filename = f"report_{date_str}.md"
    md_path = os.path.join(output_dir, md_filename)
    
    with open(md_path, 'w', encoding='utf-8') as f:
        f.write(markdown_content)
    
    print(f"  ✅ 마크다운: {md_filename}")
    
    # CSV 저장
    if csv_df is not None and len(csv_df) > 0:
        csv_filename = f"report_{date_str}.csv"
        csv_path = os.path.join(output_dir, csv_filename)
        
        csv_df.to_csv(csv_path, index=False, encoding='utf-8-sig')
        print(f"  ✅ CSV: {csv_filename}")
    
    print(f"\n📁 저장 경로: {os.path.abspath(output_dir)}")
    
    return md_path


# ========================================
# 🚀 메인 실행
# ========================================

def main():
    print("=" * 60)
    print("📊 재고 일치율 변동 분석 시작")
    print("=" * 60)

    # 날짜 설정
    today = datetime.now()
    today_str = today.strftime("%Y-%m-%d")

    # 1. 오늘 데이터 로드
    today_df = load_and_prepare_data(INPUT_DIR, FILE_FORMAT, today)
    if today_df is None:
        print("\n❌ 오늘 데이터 로드 실패. 파일을 확인하세요.")
        print(f"   예상 경로: {INPUT_DIR}/{FILE_FORMAT.replace('{date}', today_str)}")
        return

    # 2. 전일 데이터 로드 (없으면 최근 7일 내 파일 검색)
    yesterday_df = None
    yesterday_str = None

    for days_ago in range(1, 8):  # 1일 전 ~ 7일 전까지 검색
        check_date = today - timedelta(days=days_ago)
        check_str = check_date.strftime("%Y-%m-%d")

        print(f"\n📂 {check_str} 파일 검색 중...")
        yesterday_df = load_and_prepare_data(INPUT_DIR, FILE_FORMAT, check_date)

        if yesterday_df is not None:
            yesterday_str = check_str
            print(f"  ✅ 비교 기준일: {yesterday_str} ({days_ago}일 전)")
            break

    if yesterday_df is None:
        print("\n❌ 비교할 과거 데이터를 찾을 수 없습니다 (최근 7일 검색)")
        return

    print(f"\n📅 비교 날짜")
    print(f"  기준일: {yesterday_str}")
    print(f"  오늘: {today_str}")
    
    # 2. 데이터 비교
    comparison, changed = compare_inventory(yesterday_df, today_df)
    
    if comparison is None:
        return
    
    # 3. 리포트 생성
    print("\n📝 마크다운 리포트 생성 중...")
    md_report = generate_markdown_report(comparison, changed, today_str)
    
    print("📝 CSV 리포트 생성 중...")
    csv_report = generate_csv_report(changed, today_str)
    
    # 4. 리포트 저장
    md_path = save_reports(md_report, csv_report, today_str, OUTPUT_DIR)

    # 5. 슬랙 전송 (선택적)
    print(f"\n🔍 슬랙 전송 체크:")
    print(f"  변동 상품 수: {len(changed)}개")

    send_to_slack = os.getenv("SEND_SLACK_NOTIFICATION", "false").lower() == "true"
    print(f"  SEND_SLACK_NOTIFICATION: {os.getenv('SEND_SLACK_NOTIFICATION', 'false')} → {send_to_slack}")

    if send_to_slack and len(changed) > 0:
        print("\n📤 슬랙 메시지 전송 중...")
        try:
            # 프로젝트 루트를 sys.path에 추가
            from pathlib import Path
            project_root = Path(__file__).resolve().parent.parent.parent
            if str(project_root) not in sys.path:
                sys.path.insert(0, str(project_root))

            from src.reporter.slack_notifier import send_stock_report_to_slack
            send_stock_report_to_slack(md_report, today_str, yesterday_str)
        except ImportError as e:
            print(f"⚠️ 슬랙 전송 모듈 로드 실패: {e}")
        except Exception as e:
            print(f"⚠️ 슬랙 전송 실패: {e}")

    # 6. 완료
    print("\n" + "=" * 60)
    print("✅ 분석 완료!")
    print("=" * 60)

    # 마크다운 미리보기 (처음 부분만)
    print(f"\n📄 리포트 미리보기:\n")
    print(md_report[:500] + "...\n")

    print(f"💡 마크다운 파일을 Claude AI에 복사해서 붙여넣으세요!")
    print(f"   또는 VS Code에서 {md_path} 파일을 열어보세요.")


if __name__ == "__main__":
    main()

