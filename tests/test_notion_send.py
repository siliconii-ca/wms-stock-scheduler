#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
기존 report.md 파일을 Notion으로 전송하는 테스트 스크립트
"""

import sys
import os
from pathlib import Path

# 프로젝트 루트 설정 (tests/ 폴더의 부모)
project_root = Path(__file__).resolve().parent.parent
if str(project_root) not in sys.path:
    sys.path.insert(0, str(project_root))

# Windows 터미널 UTF-8 출력
if sys.stdout.encoding != 'utf-8':
    sys.stdout.reconfigure(encoding='utf-8')

# 환경변수 로드
from dotenv import load_dotenv
load_dotenv(project_root / "config.env")
if (project_root / "config.local.env").exists():
    load_dotenv(project_root / "config.local.env", override=True)

# SSL 경고 비활성화
import urllib3
os.environ['PYTHONHTTPSVERIFY'] = '0'
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)


def main():
    # 보낼 report 파일 경로
    report_date = "2026-03-13"
    report_path = project_root / "output" / f"report_{report_date}.md"

    print(f"📄 리포트 파일: {report_path}")

    if not report_path.exists():
        print(f"❌ 파일이 없습니다: {report_path}")
        return

    # 파일 읽기
    with open(report_path, encoding='utf-8') as f:
        md_content = f.read()

    print(f"  ✅ 파일 로드 완료 ({len(md_content)} 문자)")

    # Notion 설정 확인
    notion_token = os.getenv("NOTION_API_TOKEN", "")
    notion_page_id = os.getenv("NOTION_PAGE_ID", "")
    test_mode = os.getenv("TEST_MODE", "false").lower() == "true"

    print(f"\n🔧 Notion 설정:")
    print(f"  TOKEN: {'설정됨' if notion_token else '❌ 없음'}")
    print(f"  PAGE_ID: {notion_page_id or '❌ 없음'}")
    print(f"  TEST_MODE: {test_mode}")

    if not notion_token or not notion_page_id:
        print("\n❌ Notion 설정이 없습니다. config.local.env 확인하세요.")
        return

    # Notion 전송
    from src.reporter.notion_client import send_report_to_notion

    test_prefix = "[TEST] " if test_mode else ""
    title = f"{test_prefix}재고 일치율 변동 분석 ({report_date})"

    print(f"\n📤 Notion 전송 중...")
    print(f"  제목: {title}")

    result = send_report_to_notion(
        markdown_content=md_content,
        title=title
    )

    if result.get("success"):
        print(f"\n✅ Notion 전송 성공!")
        print(f"   URL: {result.get('url')}")
    else:
        print(f"\n❌ Notion 전송 실패: {result.get('error')}")


if __name__ == "__main__":
    main()
