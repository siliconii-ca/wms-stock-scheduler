import logging

logger = logging.getLogger(__name__)


def run_report_job():
    """스케줄러에 의해 주기적으로 실행되는 분석/레포팅 잡"""
    logger.info("=== [JOB] 레포트 잡 시작 ===")
    try:
        # data_analyzer의 main() 함수 실행
        import sys
        from pathlib import Path

        # 프로젝트 루트를 sys.path에 추가
        project_root = Path(__file__).resolve().parent.parent.parent
        if str(project_root) not in sys.path:
            sys.path.insert(0, str(project_root))

        # data_analyzer 모듈의 main 함수 임포트 및 실행
        from src.analyzer import data_analyzer
        data_analyzer.main()

        logger.info("=== [JOB] 레포트 잡 완료 ===")
    except Exception as e:
        logger.error(f"[JOB] 레포트 잡 오류: {e}")
