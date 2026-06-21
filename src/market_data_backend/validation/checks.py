from __future__ import annotations

from dataclasses import dataclass
from datetime import UTC, datetime
from typing import Any

import polars as pl

from market_data_backend.core.schemas import (
    OHLCV_COLUMNS,
    OHLCV_NUMERIC_COLUMNS,
    OHLCV_PRICE_COLUMNS,
)
from market_data_backend.validation.report import ValidationIssue, ValidationReport

_ISSUE_PREFIX = "_issue_"


@dataclass(frozen=True)
class ValidationResult:
    valid_frame: pl.DataFrame
    report: ValidationReport


def validate_ohlcv_frame(frame: pl.DataFrame, *, source: str) -> ValidationResult:
    _require_columns(frame, ["_row_number", *OHLCV_COLUMNS])

    checked = frame.with_columns(
        pl.col("timestamp_utc").shift(1).over("symbol").alias("_prev_timestamp_utc")
    ).with_columns(
        pl.col("timestamp_utc").is_null().alias("_issue_invalid_timestamp"),
        _invalid_symbol_expr().alias("_issue_invalid_symbol"),
        pl.any_horizontal([pl.col(column).is_null() for column in OHLCV_NUMERIC_COLUMNS]).alias(
            "_issue_missing_numeric_value"
        ),
        pl.any_horizontal([pl.col(column) <= 0 for column in OHLCV_PRICE_COLUMNS])
        .fill_null(False)
        .alias("_issue_non_positive_price"),
        (pl.col("volume") < 0).fill_null(False).alias("_issue_negative_volume"),
        (pl.struct(["timestamp_utc", "symbol"]).is_duplicated())
        .fill_null(False)
        .alias("_issue_duplicate_key"),
        (
            pl.col("timestamp_utc").is_not_null()
            & pl.col("_prev_timestamp_utc").is_not_null()
            & (pl.col("timestamp_utc") < pl.col("_prev_timestamp_utc"))
        )
        .fill_null(False)
        .alias("_issue_non_monotonic_timestamp"),
    )
    issue_columns = [column for column in checked.columns if column.startswith(_ISSUE_PREFIX)]
    issues = _build_issues(checked, issue_columns)

    invalid_expr = pl.any_horizontal([pl.col(column) for column in issue_columns]).fill_null(False)
    valid_frame = (
        checked.filter(~invalid_expr).select(OHLCV_COLUMNS).sort(["symbol", "timestamp_utc"])
    )
    report = ValidationReport(
        source=source,
        input_rows=frame.height,
        valid_rows=valid_frame.height,
        quarantined_rows=frame.height - valid_frame.height,
        repaired_rows=0,
        dropped_rows=0,
        issues=issues,
    )
    return ValidationResult(valid_frame=valid_frame, report=report)


def _require_columns(frame: pl.DataFrame, columns: list[str]) -> None:
    missing = sorted(set(columns) - set(frame.columns))
    if missing:
        raise ValueError(f"missing canonical OHLCV columns: {', '.join(missing)}")


def _invalid_symbol_expr() -> pl.Expr:
    return (
        pl.col("symbol").is_null()
        | pl.col("symbol").str.contains(r"^[A-Z0-9][A-Z0-9._-]{0,31}$").not_()
    ).fill_null(True)


def _build_issues(frame: pl.DataFrame, issue_columns: list[str]) -> list[ValidationIssue]:
    issue_specs = {
        "_issue_duplicate_key": ("duplicate_key", "Duplicate timestamp_utc and symbol key."),
        "_issue_invalid_symbol": (
            "invalid_symbol",
            "Symbol is blank or outside the supported format.",
        ),
        "_issue_invalid_timestamp": ("invalid_timestamp", "Timestamp could not be parsed as UTC."),
        "_issue_missing_numeric_value": (
            "missing_numeric_value",
            "A numeric OHLCV field is missing.",
        ),
        "_issue_negative_volume": ("negative_volume", "Volume must be zero or greater."),
        "_issue_non_monotonic_timestamp": (
            "non_monotonic_timestamp",
            "Timestamps must not move backward within a symbol in source order.",
        ),
        "_issue_non_positive_price": (
            "non_positive_price",
            "OHLC prices must be greater than zero.",
        ),
    }
    issues: list[ValidationIssue] = []
    for issue_column in sorted(issue_columns):
        count = frame.filter(pl.col(issue_column)).height
        if count == 0:
            continue
        code, message = issue_specs[issue_column]
        issues.append(
            ValidationIssue(
                code=code,
                message=message,
                count=count,
                examples=_issue_examples(frame, issue_column),
            )
        )
    return issues


def _issue_examples(frame: pl.DataFrame, issue_column: str) -> list[dict[str, object]]:
    rows = (
        frame.filter(pl.col(issue_column))
        .select(["_row_number", *OHLCV_COLUMNS])
        .head(3)
        .to_dicts()
    )
    return [{key: _json_safe(value) for key, value in row.items()} for row in rows]


def _json_safe(value: Any) -> object:
    if isinstance(value, datetime):
        utc_value = value.astimezone(UTC)
        return utc_value.isoformat().replace("+00:00", "Z")
    return value
