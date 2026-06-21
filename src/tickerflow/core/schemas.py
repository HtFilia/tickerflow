from __future__ import annotations

import polars as pl

OHLCV_COLUMNS = [
    "timestamp_utc",
    "symbol",
    "open",
    "high",
    "low",
    "close",
    "volume",
    "source",
]
OHLCV_KEY_COLUMNS = ["timestamp_utc", "symbol"]
OHLCV_PRICE_COLUMNS = ["open", "high", "low", "close"]
OHLCV_NUMERIC_COLUMNS = [*OHLCV_PRICE_COLUMNS, "volume"]
OHLCV_POLARS_SCHEMA: dict[str, pl.DataType] = {
    "timestamp_utc": pl.Datetime(time_unit="us", time_zone="UTC"),
    "symbol": pl.String(),
    "open": pl.Float64(),
    "high": pl.Float64(),
    "low": pl.Float64(),
    "close": pl.Float64(),
    "volume": pl.Float64(),
    "source": pl.String(),
}


def empty_ohlcv_frame() -> pl.DataFrame:
    return pl.DataFrame(schema=OHLCV_POLARS_SCHEMA)
