from __future__ import annotations

from typing import Literal

import polars as pl

from tickerflow.core.schemas import OHLCV_COLUMNS

TimeBarInterval = Literal["1h", "1d"]

TIME_BAR_COLUMNS = [
    "bar_start_utc",
    "bar_end_utc",
    "symbol",
    "open",
    "high",
    "low",
    "close",
    "volume",
    "input_rows",
    "source",
]
TIME_BAR_POLARS_SCHEMA: dict[str, pl.DataType] = {
    "bar_start_utc": pl.Datetime(time_unit="us", time_zone="UTC"),
    "bar_end_utc": pl.Datetime(time_unit="us", time_zone="UTC"),
    "symbol": pl.String(),
    "open": pl.Float64(),
    "high": pl.Float64(),
    "low": pl.Float64(),
    "close": pl.Float64(),
    "volume": pl.Float64(),
    "input_rows": pl.UInt32(),
    "source": pl.String(),
}


def empty_time_bars_frame() -> pl.DataFrame:
    return pl.DataFrame(schema=TIME_BAR_POLARS_SCHEMA)


def construct_time_bars(frame: pl.DataFrame, *, interval: TimeBarInterval) -> pl.DataFrame:
    if frame.is_empty():
        return empty_time_bars_frame()

    ordered = frame.select(OHLCV_COLUMNS).sort(["symbol", "timestamp_utc"])
    grouped = (
        ordered.with_columns(pl.col("timestamp_utc").dt.truncate(interval).alias("bar_start_utc"))
        .group_by(["symbol", "bar_start_utc"])
        .agg(
            pl.col("open").sort_by("timestamp_utc").first().alias("open"),
            pl.col("high").max().alias("high"),
            pl.col("low").min().alias("low"),
            pl.col("close").sort_by("timestamp_utc").last().alias("close"),
            pl.col("volume").sum().alias("volume"),
            pl.len().alias("input_rows"),
        )
    )
    return (
        grouped.with_columns(
            _bar_end_expression(interval),
            pl.lit(f"time_bar:{interval}").alias("source"),
        )
        .select(TIME_BAR_COLUMNS)
        .sort(["symbol", "bar_start_utc"])
    )


def _bar_end_expression(interval: TimeBarInterval) -> pl.Expr:
    if interval == "1h":
        return (pl.col("bar_start_utc") + pl.duration(hours=1)).alias("bar_end_utc")
    return (pl.col("bar_start_utc") + pl.duration(days=1)).alias("bar_end_utc")
