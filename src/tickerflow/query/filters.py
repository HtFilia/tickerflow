from __future__ import annotations

from datetime import datetime
from typing import Self

from pydantic import BaseModel, ConfigDict, field_validator, model_validator

from tickerflow.core.identifiers import is_valid_symbol, normalize_symbol
from tickerflow.core.time import ensure_utc


class OhlcvQueryFilter(BaseModel):
    model_config = ConfigDict(extra="forbid")

    symbol: str
    start: datetime
    end: datetime

    @field_validator("symbol")
    @classmethod
    def _normalize_symbol(cls, value: str) -> str:
        normalized = normalize_symbol(value)
        if not is_valid_symbol(normalized):
            raise ValueError(
                "symbol must be 1-32 uppercase letters, digits, dots, dashes, or underscores"
            )
        return normalized

    @field_validator("start", "end")
    @classmethod
    def _require_utc(cls, value: datetime) -> datetime:
        return ensure_utc(value)

    @model_validator(mode="after")
    def _require_half_open_range(self) -> Self:
        if self.start >= self.end:
            raise ValueError("start must be before end")
        return self
