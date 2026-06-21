from __future__ import annotations

from datetime import datetime
from typing import Literal

from pydantic import BaseModel, ConfigDict

from tickerflow.bars.time_bars import TimeBarInterval
from tickerflow.validation.report import ValidationReport


class HealthResponse(BaseModel):
    status: Literal["ok"]


class DatasetsResponse(BaseModel):
    datasets: list[str]


class SymbolsResponse(BaseModel):
    dataset: str
    symbols: list[str]


class OhlcvRecord(BaseModel):
    model_config = ConfigDict(extra="forbid")

    timestamp_utc: datetime
    symbol: str
    open: float
    high: float
    low: float
    close: float
    volume: float
    source: str


class OhlcvMetadata(BaseModel):
    symbol: str
    start: datetime
    end: datetime
    row_count: int


class OhlcvResponse(BaseModel):
    metadata: OhlcvMetadata
    data: list[OhlcvRecord]


class TimeBarRecord(BaseModel):
    model_config = ConfigDict(extra="forbid")

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


class TimeBarMetadata(BaseModel):
    symbol: str
    start: datetime
    end: datetime
    interval: TimeBarInterval
    row_count: int


class TimeBarsResponse(BaseModel):
    metadata: TimeBarMetadata
    data: list[TimeBarRecord]


class OhlcvWriteSummary(BaseModel):
    input_rows: int
    stored_rows: int
    partitions_written: int


class DemoSeedResponse(BaseModel):
    dataset: str
    symbols: list[str]
    clean_report: ValidationReport
    dirty_report: ValidationReport
    write_result: OhlcvWriteSummary
