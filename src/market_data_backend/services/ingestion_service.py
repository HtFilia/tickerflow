from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

from market_data_backend.ingestion.csv_loader import OhlcvLoadResult, load_ohlcv_csv
from market_data_backend.ingestion.source_config import OhlcvCsvConfig
from market_data_backend.storage.parquet_store import OhlcvWriteResult, ParquetOhlcvStore


@dataclass(frozen=True)
class OhlcvIngestionResult:
    load_result: OhlcvLoadResult
    write_result: OhlcvWriteResult


def ingest_ohlcv_csv_to_store(
    path: Path,
    store: ParquetOhlcvStore,
    config: OhlcvCsvConfig | None = None,
) -> OhlcvIngestionResult:
    load_result = load_ohlcv_csv(path, config)
    write_result = store.write_ohlcv(load_result.frame)
    return OhlcvIngestionResult(load_result=load_result, write_result=write_result)
