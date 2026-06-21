from __future__ import annotations

from dataclasses import dataclass
from io import StringIO

import polars as pl

from tickerflow.ingestion.normalizer import normalize_ohlcv_csv_frame
from tickerflow.ingestion.source_config import OhlcvCsvConfig
from tickerflow.storage.parquet_store import OhlcvWriteResult, ParquetOhlcvStore
from tickerflow.validation.checks import validate_ohlcv_frame
from tickerflow.validation.report import ValidationReport

_DEMO_CLEAN_OHLCV_CSV = """timestamp,symbol,open,high,low,close,volume
2024-01-02T14:30:00Z,AAPL,100.0,102.0,99.0,101.0,100
2024-01-02T15:00:00Z,AAPL,101.0,104.0,100.0,103.0,200
2024-01-02T15:30:00Z,AAPL,103.0,105.0,102.0,104.0,300
2024-01-02T16:00:00Z,AAPL,104.0,106.0,103.0,105.0,400
2024-01-02T15:00:00Z,MSFT,200.0,202.0,199.0,201.0,500
"""

_DEMO_DIRTY_OHLCV_CSV = """timestamp,symbol,open,high,low,close,volume
2024-01-02T14:30:00Z,AAPL,100.0,102.0,99.0,101.0,1000
2024-01-03T14:30:00Z,AAPL,101.0,103.0,100.0,102.0,1100
2024-01-03T14:30:00Z,AAPL,101.0,103.0,100.0,102.0,1100
2024-01-04T14:30:00Z,AAPL,-1.0,103.0,-2.0,102.0,1200
2024-01-05T14:30:00Z,AAPL,102.0,104.0,101.0,103.0,-5
not-a-date,MSFT,200.0,201.0,198.0,199.0,900
2024-01-01T14:30:00Z,AAPL,99.0,100.0,98.0,99.5,800
"""


@dataclass(frozen=True)
class DemoSeedResult:
    dataset: str
    symbols: list[str]
    clean_report: ValidationReport
    dirty_report: ValidationReport
    write_result: OhlcvWriteResult


class DemoService:
    def __init__(self, store: ParquetOhlcvStore) -> None:
        self._store = store

    def seed(self) -> DemoSeedResult:
        clean_frame, clean_report = _load_demo_ohlcv(
            _DEMO_CLEAN_OHLCV_CSV,
            source="tickerflow_demo_clean",
        )
        _, dirty_report = _load_demo_ohlcv(
            _DEMO_DIRTY_OHLCV_CSV,
            source="tickerflow_demo_dirty",
        )
        write_result = self._store.write_ohlcv(clean_frame)
        return DemoSeedResult(
            dataset=self._store.dataset,
            symbols=self._store.list_symbols(dataset=self._store.dataset),
            clean_report=clean_report,
            dirty_report=dirty_report,
            write_result=write_result,
        )


def _load_demo_ohlcv(csv_text: str, *, source: str) -> tuple[pl.DataFrame, ValidationReport]:
    raw_frame = pl.read_csv(StringIO(csv_text))
    config = OhlcvCsvConfig(source=source)
    normalized = normalize_ohlcv_csv_frame(raw_frame, config)
    result = validate_ohlcv_frame(normalized, source=source)
    return result.valid_frame, result.report
