from __future__ import annotations

from datetime import UTC, datetime
from pathlib import Path

import polars as pl

from tickerflow.ingestion.csv_loader import load_ohlcv_csv
from tickerflow.ingestion.source_config import OhlcvCsvConfig

FIXTURES = Path(__file__).resolve().parents[1] / "fixtures"


def test_clean_ohlcv_csv_is_normalized_to_canonical_schema() -> None:
    result = load_ohlcv_csv(
        FIXTURES / "ohlcv_clean.csv",
        OhlcvCsvConfig(source="synthetic_clean"),
    )

    assert result.report.input_rows == 3
    assert result.report.valid_rows == 3
    assert result.report.quarantined_rows == 0
    assert result.frame.columns == [
        "timestamp_utc",
        "symbol",
        "open",
        "high",
        "low",
        "close",
        "volume",
        "source",
    ]
    assert result.frame.schema["timestamp_utc"] == pl.Datetime(time_unit="us", time_zone="UTC")
    assert result.frame.select("source").unique().to_series().to_list() == ["synthetic_clean"]


def test_dirty_ohlcv_csv_reports_quarantined_rows_without_silent_drops() -> None:
    result = load_ohlcv_csv(
        FIXTURES / "ohlcv_dirty.csv",
        OhlcvCsvConfig(source="synthetic_dirty"),
    )

    issue_counts = {issue.code: issue.count for issue in result.report.issues}

    assert result.report.input_rows == 7
    assert result.report.valid_rows == 1
    assert result.report.quarantined_rows == 6
    assert result.report.dropped_rows == 0
    assert result.report.repaired_rows == 0
    assert issue_counts == {
        "duplicate_key": 2,
        "invalid_timestamp": 1,
        "negative_volume": 1,
        "non_monotonic_timestamp": 1,
        "non_positive_price": 1,
    }
    assert result.frame.select("timestamp_utc", "symbol").rows() == [
        (datetime(2024, 1, 2, 14, 30, tzinfo=UTC), "AAPL")
    ]
