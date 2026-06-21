from __future__ import annotations

from datetime import datetime
from typing import Literal

from pydantic import BaseModel, ConfigDict


class HealthResponse(BaseModel):
    status: Literal["ok"]


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
