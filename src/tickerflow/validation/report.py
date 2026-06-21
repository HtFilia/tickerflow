from __future__ import annotations

from pydantic import BaseModel, ConfigDict, Field


class ValidationIssue(BaseModel):
    model_config = ConfigDict(extra="forbid")

    code: str
    message: str
    count: int
    examples: list[dict[str, object]] = Field(default_factory=list)


class ValidationReport(BaseModel):
    model_config = ConfigDict(extra="forbid")

    source: str
    input_rows: int
    valid_rows: int
    quarantined_rows: int
    repaired_rows: int
    dropped_rows: int
    issues: list[ValidationIssue] = Field(default_factory=list)
