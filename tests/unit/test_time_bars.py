from __future__ import annotations

from datetime import UTC, datetime
from pathlib import Path

from tickerflow.bars.time_bars import construct_time_bars
from tickerflow.ingestion.csv_loader import load_ohlcv_csv
from tickerflow.ingestion.source_config import OhlcvCsvConfig

FIXTURES = Path(__file__).resolve().parents[1] / "fixtures"


def test_construct_time_bars_aggregates_ohlcv_by_hour() -> None:
    ingestion = load_ohlcv_csv(
        FIXTURES / "ohlcv_intraday.csv",
        OhlcvCsvConfig(source="synthetic_intraday"),
    )

    bars = construct_time_bars(ingestion.frame, interval="1h")

    assert bars.filter(bars["symbol"] == "AAPL").select(
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
    ).rows() == [
        (
            datetime(2024, 1, 2, 14, tzinfo=UTC),
            datetime(2024, 1, 2, 15, tzinfo=UTC),
            "AAPL",
            100.0,
            102.0,
            99.0,
            101.0,
            100.0,
            1,
            "time_bar:1h",
        ),
        (
            datetime(2024, 1, 2, 15, tzinfo=UTC),
            datetime(2024, 1, 2, 16, tzinfo=UTC),
            "AAPL",
            101.0,
            105.0,
            100.0,
            104.0,
            500.0,
            2,
            "time_bar:1h",
        ),
        (
            datetime(2024, 1, 2, 16, tzinfo=UTC),
            datetime(2024, 1, 2, 17, tzinfo=UTC),
            "AAPL",
            104.0,
            106.0,
            103.0,
            105.0,
            400.0,
            1,
            "time_bar:1h",
        ),
    ]
