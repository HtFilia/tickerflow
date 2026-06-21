from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
from pathlib import Path

import polars as pl

from tickerflow.core.schemas import OHLCV_COLUMNS, OHLCV_KEY_COLUMNS, empty_ohlcv_frame
from tickerflow.storage.duckdb_query import query_ohlcv_parquet_files
from tickerflow.storage.partitions import ohlcv_partition_file


@dataclass(frozen=True)
class OhlcvWriteResult:
    input_rows: int
    stored_rows: int
    partitions_written: int


class ParquetOhlcvStore:
    def __init__(self, root: Path, dataset: str = "ohlcv") -> None:
        self.root = root
        self.dataset = dataset

    @property
    def dataset_path(self) -> Path:
        return self.root / self.dataset

    def write_ohlcv(self, frame: pl.DataFrame) -> OhlcvWriteResult:
        if frame.is_empty():
            return OhlcvWriteResult(input_rows=0, stored_rows=0, partitions_written=0)

        partitioned_frame = frame.select(OHLCV_COLUMNS).with_columns(
            pl.col("timestamp_utc").dt.strftime("%Y-%m-%d").alias("_date")
        )
        partitions = partitioned_frame.select("symbol", "_date").unique().sort("symbol", "_date")

        stored_rows = 0
        partitions_written = 0
        for partition in partitions.iter_rows(named=True):
            symbol = str(partition["symbol"])
            date = str(partition["_date"])
            target = ohlcv_partition_file(self.root, self.dataset, symbol, date)
            incoming = partitioned_frame.filter(
                (pl.col("symbol") == symbol) & (pl.col("_date") == date)
            ).select(OHLCV_COLUMNS)
            existing = pl.read_parquet(target) if target.exists() else empty_ohlcv_frame()
            combined = pl.concat([existing, incoming], how="vertical_relaxed")
            combined = combined.unique(subset=OHLCV_KEY_COLUMNS, keep="last").sort(
                ["symbol", "timestamp_utc"]
            )

            target.parent.mkdir(parents=True, exist_ok=True)
            combined.write_parquet(target)
            stored_rows += combined.height
            partitions_written += 1

        return OhlcvWriteResult(
            input_rows=frame.height,
            stored_rows=stored_rows,
            partitions_written=partitions_written,
        )

    def read_ohlcv(self, *, symbol: str, start: datetime, end: datetime) -> pl.DataFrame:
        files = sorted((self.dataset_path / f"symbol={symbol}").glob("date=*/data.parquet"))
        return query_ohlcv_parquet_files(files, symbol=symbol, start=start, end=end)

    def list_datasets(self) -> list[str]:
        if not self.root.exists():
            return []

        datasets: list[str] = []
        for dataset_path in self.root.iterdir():
            if dataset_path.is_dir() and any(dataset_path.glob("symbol=*/date=*/data.parquet")):
                datasets.append(dataset_path.name)
        return sorted(datasets)

    def list_symbols(self, *, dataset: str = "ohlcv") -> list[str]:
        dataset_path = self.root / dataset
        if not dataset_path.exists():
            return []

        symbols: list[str] = []
        for symbol_path in dataset_path.glob("symbol=*"):
            if symbol_path.is_dir() and any(symbol_path.glob("date=*/data.parquet")):
                symbols.append(symbol_path.name.removeprefix("symbol="))
        return sorted(symbols)
