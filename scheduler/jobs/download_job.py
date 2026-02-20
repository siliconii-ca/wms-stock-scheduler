from loguru import logger
from src.downloader.data_downloader import DataDownloader


def run_download_job():
    """스케줄러에 의해 주기적으로 실행되는 다운로드 잡"""
    logger.info("=== [JOB] 데이터 다운로드 잡 시작 ===")
    try:
        downloader = DataDownloader()
        downloader.download()
        logger.info("=== [JOB] 데이터 다운로드 잡 완료 ===")
    except Exception as e:
        logger.error(f"[JOB] 다운로드 잡 오류: {e}")
