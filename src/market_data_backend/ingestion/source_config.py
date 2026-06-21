from __future__ import annotations

from pydantic import BaseModel, ConfigDict, Field, field_validator


class OhlcvCsvConfig(BaseModel):
    model_config = ConfigDict(extra="forbid")

    source: str = Field(default="local_csv", min_length=1)
    timestamp_column: str = "timestamp"
    symbol_column: str = "symbol"
    open_column: str = "open"
    high_column: str = "high"
    low_column: str = "low"
    close_column: str = "close"
    volume_column: str = "volume"

    @field_validator(
        "source",
        "timestamp_column",
        "symbol_column",
        "open_column",
        "high_column",
        "low_column",
        "close_column",
        "volume_column",
    )
    @classmethod
    def _strip_required_text(cls, value: str) -> str:
        stripped = value.strip()
        if not stripped:
            raise ValueError("value must not be blank")
        return stripped

    def rename_map(self) -> dict[str, str]:
        return {
            self.timestamp_column: "timestamp_utc",
            self.symbol_column: "symbol",
            self.open_column: "open",
            self.high_column: "high",
            self.low_column: "low",
            self.close_column: "close",
            self.volume_column: "volume",
        }
