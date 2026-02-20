from pathlib import Path
import pandas as pd
from loguru import logger
from config.settings import RAW_DIR, PROCESSED_DIR


class DataProcessor:
    """
    raw/ 폴더의 CSV 파일을 읽어 전처리 후 processed/ 폴더에 저장합니다.
    """

    def __init__(self):
        PROCESSED_DIR.mkdir(parents=True, exist_ok=True)

    def load_csv(self, file_path: Path, encoding: str = "utf-8-sig") -> pd.DataFrame | None:
        """CSV 파일을 읽어 DataFrame으로 반환합니다."""
        try:
            df = pd.read_csv(file_path, encoding=encoding)
            logger.info(f"CSV 로드 완료: {file_path.name} ({len(df)} rows)")
            return df
        except Exception as e:
            logger.error(f"CSV 로드 실패 [{file_path}]: {e}")
            return None

    def process(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        전처리 로직을 구현합니다.
        예: 결측값 처리, 타입 변환, 컬럼 정리 등
        """
        # TODO: 실제 전처리 로직 구현
        df = df.dropna(how="all")
        logger.info("데이터 전처리 완료")
        return df

    def save_csv(self, df: pd.DataFrame, filename: str) -> Path:
        """전처리된 DataFrame을 processed/ 폴더에 저장합니다."""
        output_path = PROCESSED_DIR / filename
        df.to_csv(output_path, index=False, encoding="utf-8-sig")
        logger.info(f"전처리 데이터 저장: {output_path}")
        return output_path

    def run(self, file_path: Path) -> pd.DataFrame | None:
        """로드 → 전처리 → 저장 파이프라인을 실행합니다."""
        df = self.load_csv(file_path)
        if df is None:
            return None
        df = self.process(df)
        self.save_csv(df, f"processed_{file_path.name}")
        return df
