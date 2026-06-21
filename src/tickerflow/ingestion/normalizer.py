from __future__ import annotations

import polars as pl

from tickerflow.core.schemas import OHLCV_COLUMNS
from tickerflow.ingestion.source_config import OhlcvCsvConfig


def normalize_ohlcv_csv_frame(raw_frame: pl.DataFrame, config: OhlcvCsvConfig) -> pl.DataFrame:
    rename_map = config.rename_map()
    missing_columns = sorted(set(rename_map) - set(raw_frame.columns))
    if missing_columns:
        missing = ", ".join(missing_columns)
        raise ValueError(f"missing required OHLCV CSV columns: {missing}")

    return (
        raw_frame.rename(rename_map)
        .with_row_index("_row_number", offset=1)
        .with_columns(
            pl.col("timestamp_utc")
            .cast(pl.String, strict=False)
            .str.to_datetime(time_unit="us", time_zone="UTC", strict=False)
            .dt.cast_time_unit("us")
            .alias("timestamp_utc"),
            pl.col("symbol").cast(pl.String, strict=False).str.strip_chars().str.to_uppercase(),
            pl.col("open").cast(pl.Float64, strict=False),
            pl.col("high").cast(pl.Float64, strict=False),
            pl.col("low").cast(pl.Float64, strict=False),
            pl.col("close").cast(pl.Float64, strict=False),
            pl.col("volume").cast(pl.Float64, strict=False),
            pl.lit(config.source).alias("source"),
        )
        .select(["_row_number", *OHLCV_COLUMNS])
    )
