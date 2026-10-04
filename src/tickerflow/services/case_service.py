"""Real validation, temporary Parquet round trips and lineage for bounded presets."""

from __future__ import annotations

import csv
import hashlib
import math
import os
from datetime import UTC, datetime, timedelta
from io import StringIO
from pathlib import Path
from tempfile import TemporaryDirectory
from typing import Literal

import polars as pl
from pydantic import BaseModel, ConfigDict, model_validator

from tickerflow.bars.time_bars import TimeBarInterval, construct_time_bars
from tickerflow.ingestion.normalizer import normalize_ohlcv_csv_frame
from tickerflow.ingestion.source_config import OhlcvCsvConfig
from tickerflow.storage.parquet_store import ParquetOhlcvStore
from tickerflow.validation.checks import validate_ohlcv_frame
from tickerflow.validation.report import ValidationReport

CaseId = Literal["duplicates", "ranges", "timestamps", "boundaries"]
Scalar = str | float | int | None
_FIXTURES = Path(__file__).parents[1] / "demo" / "fixtures"
CASE_DESCRIPTIONS = {
    "duplicates": "Find a duplicate pair; both rows are quarantined, not silently merged.",
    "ranges": "Investigate impossible OHLC ranges, NaN and Infinity.",
    "timestamps": "Investigate source-order timestamps, malformed dates and negative volume.",
    "boundaries": "Trace observations exactly on hourly and daily half-open boundaries.",
}


class DemoRunRequest(BaseModel):
    model_config = ConfigDict(extra="forbid")
    case_id: CaseId = "duplicates"
    case_version: Literal["v1"] = "v1"
    symbol: Literal["AAPL", "MSFT"] = "AAPL"
    start: datetime = datetime(2024, 1, 2, tzinfo=UTC)
    end: datetime = datetime(2024, 1, 4, tzinfo=UTC)
    interval: TimeBarInterval = "1h"

    @model_validator(mode="after")
    def valid_range(self) -> DemoRunRequest:
        if self.start.tzinfo is None or self.end.tzinfo is None:
            raise ValueError("Use timezone-aware UTC ranges")
        if self.end <= self.start or self.end - self.start > timedelta(days=31):
            raise ValueError("End must follow start; maximum query span is 31 days")
        return self


class InvestigatedRow(BaseModel):
    row_id: int
    disposition: Literal["accepted", "quarantined"]
    rule_codes: list[str]
    original: dict[str, str]
    normalized: dict[str, Scalar]


class CaseObservation(BaseModel):
    timestamp_utc: datetime
    symbol: str
    open: float
    high: float
    low: float
    close: float
    volume: float
    source: str
    row_id: int


class CaseBar(BaseModel):
    bar_start_utc: datetime
    bar_end_utc: datetime
    symbol: str
    open: float
    high: float
    low: float
    close: float
    volume: float
    input_rows: int
    source: str
    contributor_ids: list[int]
    partial_query_boundary: bool


class CaseRun(BaseModel):
    schema_version: Literal[1] = 1
    case_id: CaseId
    case_version: Literal["v1"] = "v1"
    fixture_sha256: str
    run_id: str
    engine_revision: str
    filters: DemoRunRequest
    conventions: str
    report: ValidationReport
    rows: list[InvestigatedRow]
    query: list[CaseObservation]
    bars: list[CaseBar]
    temporary_storage: dict[str, int]


def case_catalog() -> list[dict[str, object]]:
    return [
        {
            "case_id": key,
            "case_version": "v1",
            "description": description,
            "symbols": ["AAPL", "MSFT"],
            "intervals": ["1h", "1d"],
        }
        for key, description in CASE_DESCRIPTIONS.items()
    ]


def _safe(value: object) -> Scalar:
    if isinstance(value, datetime):
        return value.astimezone(UTC).isoformat().replace("+00:00", "Z")
    if isinstance(value, float):
        return value if math.isfinite(value) else None
    if isinstance(value, (str, int)) or value is None:
        return value
    raise ValueError("Unexpected normalized cell type")


def run_case(request: DemoRunRequest) -> CaseRun:
    """Each request owns and cleans its temporary files; shared demo storage is untouched."""
    csv_text = (_FIXTURES / f"{request.case_id}.csv").read_text()
    originals = list(csv.DictReader(StringIO(csv_text)))
    if len(originals) > 64:
        raise ValueError("Fixture exceeds bounded demonstration size")
    frame = pl.read_csv(StringIO(csv_text), infer_schema=False)
    normalized = normalize_ohlcv_csv_frame(
        frame, OhlcvCsvConfig(source=f"demo:{request.case_id}:v1")
    )
    validation = validate_ohlcv_frame(normalized, source=f"demo:{request.case_id}:v1")
    norm_rows = normalized.to_dicts()
    rows = [
        InvestigatedRow(
            row_id=decision.row_id,
            rule_codes=list(decision.rule_codes),
            disposition="quarantined" if decision.rule_codes else "accepted",
            original=originals[decision.row_id - 1],
            normalized={key: _safe(value) for key, value in norm_rows[decision.row_id - 1].items()},
        )
        for decision in validation.row_decisions
    ]
    key_to_row = {
        (norm_rows[r.row_id - 1]["symbol"], norm_rows[r.row_id - 1]["timestamp_utc"]): r.row_id
        for r in rows
        if r.disposition == "accepted"
    }
    with TemporaryDirectory(prefix="tickerflow-case-") as directory:
        store = ParquetOhlcvStore(Path(directory))
        write = store.write_ohlcv(validation.valid_frame)
        queried = store.read_ohlcv(symbol=request.symbol, start=request.start, end=request.end)
        observations = [
            CaseObservation(**row, row_id=key_to_row[(row["symbol"], row["timestamp_utc"])])
            for row in queried.to_dicts()
        ]
        bars = [
            CaseBar(
                **bar,
                contributor_ids=[
                    row.row_id
                    for row in observations
                    if bar["bar_start_utc"] <= row.timestamp_utc < bar["bar_end_utc"]
                ],
                partial_query_boundary=bar["bar_start_utc"] < request.start
                or bar["bar_end_utc"] > request.end,
            )
            for bar in construct_time_bars(queried, interval=request.interval).to_dicts()
        ]
    fixture_hash = hashlib.sha256(csv_text.encode()).hexdigest()
    revision = os.environ.get("DEMO_BUILD_REVISION", "unknown")
    identity = fixture_hash + request.model_dump_json() + revision
    return CaseRun(
        case_id=request.case_id,
        fixture_sha256=fixture_hash,
        run_id=hashlib.sha256(identity.encode()).hexdigest(),
        engine_revision=revision,
        filters=request,
        report=validation.report,
        rows=rows,
        query=observations,
        bars=bars,
        conventions="Synthetic unadjusted OHLCV; uppercase symbols; UTC microseconds; "
        "prices in currency units, volume in synthetic units; [start,end). "
        "Bars use only observations in the selected query, no gap filling.",
        temporary_storage={
            "input_rows": write.input_rows,
            "stored_rows": write.stored_rows,
            "partitions_written": write.partitions_written,
        },
    )
