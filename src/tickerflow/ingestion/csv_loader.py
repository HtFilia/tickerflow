from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

import polars as pl

from tickerflow.ingestion.normalizer import normalize_ohlcv_csv_frame
from tickerflow.ingestion.source_config import OhlcvCsvConfig
from tickerflow.validation.checks import validate_ohlcv_frame
from tickerflow.validation.report import ValidationReport


@dataclass(frozen=True)
class OhlcvLoadResult:
    frame: pl.DataFrame
    report: ValidationReport


def load_ohlcv_csv(path: Path, config: OhlcvCsvConfig | None = None) -> OhlcvLoadResult:
    csv_config = config or OhlcvCsvConfig()
    raw_frame = pl.read_csv(path)
    normalized_frame = normalize_ohlcv_csv_frame(raw_frame, csv_config)
    validation_result = validate_ohlcv_frame(normalized_frame, source=csv_config.source)
    return OhlcvLoadResult(
        frame=validation_result.valid_frame,
        report=validation_result.report,
    )
