from __future__ import annotations

from collections.abc import Sequence
from datetime import datetime
from pathlib import Path
from typing import cast

import duckdb
import polars as pl

from tickerflow.core.schemas import OHLCV_COLUMNS, empty_ohlcv_frame


def query_ohlcv_parquet_files(
    files: Sequence[Path],
    *,
    symbol: str,
    start: datetime,
    end: datetime,
) -> pl.DataFrame:
    if not files:
        return empty_ohlcv_frame()

    connection = duckdb.connect(database=":memory:")
    try:
        arrow_table = connection.execute(
            """
            SELECT timestamp_utc, symbol, open, high, low, close, volume, source
            FROM read_parquet(?)
            WHERE symbol = ?
              AND timestamp_utc >= ?
              AND timestamp_utc < ?
            ORDER BY timestamp_utc
            """,
            [[str(file) for file in files], symbol, start, end],
        ).to_arrow_table()
    finally:
        connection.close()

    if arrow_table.num_rows == 0:
        return empty_ohlcv_frame()

    frame = cast(pl.DataFrame, pl.from_arrow(arrow_table))
    return frame.with_columns(
        pl.col("timestamp_utc").cast(pl.Datetime(time_unit="us", time_zone="UTC"))
    ).select(OHLCV_COLUMNS)
