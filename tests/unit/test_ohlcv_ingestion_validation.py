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


def test_audit_regression_rejects_all_three_rows() -> None:
    result = load_ohlcv_csv(FIXTURES / "ohlcv_invalid.csv")
    assert result.report.valid_rows == 0
    assert result.report.quarantined_rows == 3
    assert {issue.code for issue in result.report.issues} >= {
        "non_finite_numeric_value",
        "invalid_ohlc_range",
    }


def test_numeric_and_range_boundaries(tmp_path: Path) -> None:
    cases = [
        ("100,110,90,100,0", True),
        ("100,100,100,100,10", True),
        ("100,90,110,105,10", False),
        ("120,110,90,100,10", False),
        ("100,110,90,80,10", False),
        ("NaN,110,90,100,10", False),
        ("100,inf,90,100,10", False),
        ("100,110,-inf,100,10", False),
        ("100,110,90,inf,10", False),
        ("100,110,90,100,inf", False),
        ("100,110,90,100,-inf", False),
        ("100,110,90,100,NaN", False),
        ("-inf,90,110,120,-1", False),
    ]
    for values, valid in cases:
        path = tmp_path / "case.csv"
        path.write_text(
            "timestamp,symbol,open,high,low,close,volume\n"
            + "2024-01-02T14:30:00Z,TEST,"
            + values
            + "\n"
        )
        result = load_ohlcv_csv(path)
        assert result.report.valid_rows == int(valid), values
        assert result.report.quarantined_rows == int(not valid), values
        if values == "-inf,90,110,120,-1":
            assert {issue.code for issue in result.report.issues} >= {
                "non_finite_numeric_value",
                "non_positive_price",
                "invalid_ohlc_range",
                "negative_volume",
            }
        # Reports must be valid JSON, including examples of non-finite inputs.
        import json

        json.loads(result.report.model_dump_json())
