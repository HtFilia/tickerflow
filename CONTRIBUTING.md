# Contributing

## Scope and architecture

TickerFlow is a Python backend for local market-data ingestion, validation,
Parquet storage, querying, and bar construction. Keep dependency flow directed
from the API through services into ingestion, storage, query, bars, validation,
and core modules. Modules below the API layer must not depend on FastAPI.

Backend code must remain Python-only and must not require proprietary or paid
data sources for tests or examples.

## Engineering requirements

- Use typed Pydantic models at API and ingestion boundaries.
- Prefer Polars lazy operations for larger tabular transformations.
- Use Parquet for durable local storage and DuckDB for analytical queries.
- Keep test data small, synthetic, and committed under `tests/fixtures/`.
- Use timezone-aware UTC internally.
- Report dropped, repaired, or quarantined rows; never discard rows silently.
- Keep ingestion deterministic and idempotent.
- Update public documentation when behavior or schemas change.

## Financial-data requirements

Document timestamp precision, symbol format, price and volume units, timezone,
and adjusted/unadjusted status for every schema. Keep OHLCV, trades, quotes, and
order-book snapshots distinct. Bar constructors must define inclusion and
exclusion boundaries precisely. Corporate actions remain out of scope until
implemented explicitly.

## Local quality gate

```bash
uv sync --extra dev
uv run ruff format --check .
uv run ruff check .
uv run mypy src tests
uv run pytest
```

Changes are ready when typing, tests, data-quality behavior, affected
documentation, and public API contracts all agree.
