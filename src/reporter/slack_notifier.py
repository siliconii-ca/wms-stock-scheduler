import os
import sys
import json
import re
import logging
import requests
from typing import Dict, List, Any
from dotenv import load_dotenv

# Windows 터미널 cp949 환경에서 UTF-8 출력 가능하도록 강제 설정
if sys.stdout.encoding != 'utf-8':
    sys.stdout.reconfigure(encoding='utf-8')

load_dotenv()

# 로거 설정
logger = logging.getLogger(__name__)
if not logger.handlers:
    handler = logging.StreamHandler(sys.stdout)
    handler.setStream(sys.stdout)  # UTF-8로 재설정된 stdout 사용
    formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    handler.setFormatter(formatter)
    logger.addHandler(handler)
    logger.setLevel(logging.INFO)


class SlackNotificationService:
    """
    슬랙 DM 메시지 전송 서비스
    공통 API를 통한 슬랙 알림
    """

    def __init__(self):
        self.base_url = os.getenv("COMMON_API_PATH", "")
        if not self.base_url:
            logger.warning("COMMON_API_PATH 환경변수가 설정되지 않았습니다.")

    def send_dm_message(self, payload_items: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        슬랙 DM 메시지 전송

        Args:
            payload_items: 페이로드 아이템 리스트
                [
                    {
                        "msgType": "daily-stock-report",
                        "additionalData": {
                            "targets": [...]
                        }
                    }
                ]

        Returns:
            전송 결과
        """
        if not self.base_url:
            return {
                "onResult": -1,
                "ovErrDesc": "COMMON_API_PATH가 설정되지 않았습니다."
            }

        url = f"{self.base_url}/api/slack/dm"

        try:
            logger.info(f"슬랙 메시지 전송: {url}")

            # SSL 검증 비활성화 (개발 환경 self-signed certificate 대응)
            import urllib3
            urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

            response = requests.post(
                url,
                json=payload_items,
                headers={"Content-Type": "application/json; charset=utf-8"},
                timeout=30,
                verify=False  # SSL 인증서 검증 비활성화
            )

            response.raise_for_status()

            logger.info(f"슬랙 DM 전송 완료: {response.text}")
            return {
                "onResult": 1,
                "ovErrDesc": f"Slack DM 전송 완료: {response.text}"
            }

        except requests.exceptions.RequestException as e:
            logger.error(f"슬랙 DM API 호출 실패: {e}")
            return {
                "onResult": -1,
                "ovErrDesc": f"Slack DM API 호출 실패: {str(e)}"
            }


def send_stock_report_to_slack(
    md_report: str,
    today_str: str,
    yesterday_str: str,
    dm_receiver: str = None
):
    """
    재고 일치율 변동 레포트를 슬랙으로 전송 (현재 테스트 모드)

    Args:
        md_report: 마크다운 레포트 전체 내용
        today_str: 오늘 날짜 문자열
        yesterday_str: 어제 날짜 문자열
        dm_receiver: DM 수신자 이메일 (None이면 환경변수에서 가져옴)
    """
    slack = SlackNotificationService()

    if dm_receiver is None:
        dm_receiver = os.getenv("SLACK_DM_RECEIVER", "sona@siliconii.net")

    if not dm_receiver:
        logger.warning("슬랙 수신자가 설정되지 않았습니다. (SLACK_DM_RECEIVER)")
        return

    # title = f"📈 Stock Report ({today_str} vs {yesterday_str})"
    # contents = f"*{title}*\n\n" + _truncate_for_slack(md_report)

    slack_contents = format_stock_report_for_slack(md_report)


    # 페이로드 구성
    payload_items = [
        {
            "msgType": "daily-stock-report",
            "dmReceiver": dm_receiver,
            "date_from": yesterday_str,
            "date_to": today_str,
            "contents": slack_contents
        }
    ]

    # 전송
    result = slack.send_dm_message(payload_items)

    if result["onResult"] == 0:
        logger.info(f"슬랙 테스트 메시지 전송 완료: {dm_receiver}")
    else:
        logger.error(f"슬랙 테스트 메시지 전송 실패: {result['ovErrDesc']}")

    return result



def _truncate_for_slack(text: str, limit: int = 35000) -> str:
    # Slack/중간 게이트웨이에서 길이 제한에 걸릴 수 있어서 안전하게 컷
    if text is None:
        return ""
    return text if len(text) <= limit else text[:limit] + "\n\n…(내용이 길어 일부만 전송됨)"


def format_stock_report_for_slack(md_report: str) -> str:
    lines = md_report.splitlines()

    total = changed = change_rate = avg = max_v = min_v = ""
    inc = dec = ""

    top_items = []

    for line in lines:
        if "총 상품 수" in line:
            total = re.findall(r"\d[\d,]*", line)[0]
        elif "변동 상품" in line:
            changed = re.findall(r"\d[\d,]*", line)[0]
        elif "변동 비율" in line:
            change_rate = re.findall(r"[\d.]+%", line)[0]
        elif "평균 변동폭" in line:
            avg = re.findall(r"[\d.]+%", line)[0]
        elif "최대 변동" in line:
            max_v = re.findall(r"[\d.]+%", line)[0]
        elif "최소 변동" in line:
            min_v = re.findall(r"[\d.]+%", line)[0]
        elif "증가" in line and "개" in line:
            inc = re.findall(r"\d+", line)[0]
        elif "감소" in line and "개" in line:
            dec = re.findall(r"\d+", line)[0]
        elif line.strip().startswith(tuple(str(i) + "." for i in range(1, 10))):
            # 상세 목록 파싱
            parts = line.split("**")
            if len(parts) >= 3:
                name = parts[1]
                diff_match = re.search(r"\((\+?[\d.]+%)\)", line)
                diff = diff_match.group(1) if diff_match else ""
                top_items.append(f"{len(top_items)+1}) {name} ({diff})")

    top_items = top_items[:5]

    slack_message = f"""
📊 *재고 일치율 변동 분석 리포트*

━━━━━━━━━━━━━━━━━━
📈 *요약*
• 총 상품 수: {total}개
• 변동 상품: {changed}개 ({change_rate})
• 평균 변동폭: {avg}
• 최대/최소 변동: {max_v} / {min_v}

━━━━━━━━━━━━━━━━━━
🔁 *변동 방향*
• 증가: {inc}개
• 감소: {dec}개

━━━━━━━━━━━━━━━━━━
⚠️ *일치율 증가 TOP 5*
""" + "\n".join(top_items) + "\n\n(전체 상세는 리포트 참조)"

    return slack_message.strip()