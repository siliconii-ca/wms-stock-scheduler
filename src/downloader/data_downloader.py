import shutil
from pathlib import Path
from loguru import logger
from config.settings import RAW_DIR, DATA_SOURCE_URL, DATA_SOURCE_API_KEY


class DataDownloader:
    """
    외부 소스에서 데이터를 다운로드하고 raw/ 폴더에 CSV로 저장합니다.
    추후 실제 다운로드 로직(API, FTP, DB 등)을 구현하세요.
    """

    def __init__(self):
        RAW_DIR.mkdir(parents=True, exist_ok=True)

    def download(self) -> Path | None:
        """
        데이터를 다운로드하고 저장된 파일 경로를 반환합니다.
        실제 구현 시 이 메서드를 수정하세요.
        """
        logger.info("데이터 다운로드 시작")

        try:
            # TODO: 실제 다운로드 로직 구현
            # 예시: requests, ftplib, sqlalchemy 등 사용
            # response = requests.get(DATA_SOURCE_URL, headers={"Authorization": DATA_SOURCE_API_KEY})
            # ...

            logger.info("데이터 다운로드 완료")
            return None

        except Exception as e:
            logger.error(f"데이터 다운로드 실패: {e}")
            return None
