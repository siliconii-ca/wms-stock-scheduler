from datetime import datetime
from pathlib import Path
import pandas as pd
from loguru import logger
from config.settings import REPORTS_DIR


class ReportGenerator:
    """
    분석 결과를 기반으로 레포트를 생성하고 reports/ 폴더에 저장합니다.
    """

    def __init__(self):
        REPORTS_DIR.mkdir(parents=True, exist_ok=True)

    def _get_timestamp(self) -> str:
        return datetime.now().strftime("%Y%m%d_%H%M%S")

    def save_csv_report(self, df: pd.DataFrame, prefix: str = "report") -> Path:
        """분석 결과를 CSV 레포트로 저장합니다."""
        filename = f"{prefix}_{self._get_timestamp()}.csv"
        output_path = REPORTS_DIR / filename
        df.to_csv(output_path, index=False, encoding="utf-8-sig")
        logger.info(f"CSV 레포트 저장: {output_path}")
        return output_path

    def save_excel_report(self, data: dict, prefix: str = "report") -> Path:
        """분석 결과를 Excel 레포트로 저장합니다 (시트별 구성)."""
        filename = f"{prefix}_{self._get_timestamp()}.xlsx"
        output_path = REPORTS_DIR / filename
        with pd.ExcelWriter(output_path, engine="openpyxl") as writer:
            for sheet_name, df in data.items():
                if isinstance(df, pd.DataFrame):
                    df.to_excel(writer, sheet_name=str(sheet_name)[:31], index=True)
        logger.info(f"Excel 레포트 저장: {output_path}")
        return output_path

    def generate(self, analysis_result: dict, df: pd.DataFrame) -> None:
        """
        분석 결과를 바탕으로 레포트를 생성합니다.
        필요에 따라 CSV, Excel 등 형식을 선택하세요.
        """
        logger.info("레포트 생성 시작")

        try:
            # CSV 레포트
            self.save_csv_report(df, prefix="stock_report")

            # Excel 레포트 (시트별)
            report_sheets = {
                "summary": analysis_result.get("summary", pd.DataFrame()),
            }
            self.save_excel_report(report_sheets, prefix="stock_report")

            logger.info("레포트 생성 완료")
        except Exception as e:
            logger.error(f"레포트 생성 실패: {e}")
