# TickerFlow

TickerFlow is a Python backend that turns local market CSVs into validated, queryable API data.

## Why this project exists

Many quant projects start with a notebook and a CSV. This repository is designed to show a more professional approach: explicit schemas, deterministic ingestion, validation reports, storage abstractions, query APIs, and tests.

## Core capabilities

- Ingest synthetic or local OHLCV/trade/quote files.
- Normalize schemas and timestamps.
- Validate quality issues such as duplicates, missing values, negative prices, non-monotonic timestamps, and invalid volumes.
- Store normalized data as partitioned Parquet.
- Query symbol/date/frequency slices through Python services and FastAPI endpoints.
- Build time bars, tick bars, volume bars, and dollar bars.
- Benchmark Pandas/Polars/DuckDB style operations where useful.

## Suggested stack

- Python 3.12+
- Polars for DataFrame transformations.
- DuckDB for local analytical queries.
- PyArrow/Parquet for storage.
- Pydantic and FastAPI for backend contracts.
- pytest, ruff, and mypy for quality.

## Repository philosophy

1. Schemas before pipelines.
2. Deterministic local fixtures before live data.
3. Validation reports before silent cleaning.
4. Small vertical slices over broad unsupported features.

## First milestones

1. Bootstrap Python package, CI, linting, typing, and tests.
2. Define canonical schemas for OHLCV and trades.
3. Implement local CSV ingestion with validation reports.
4. Store normalized data as partitioned Parquet.
5. Add query service and FastAPI endpoint.
6. Implement time bars and volume bars.
7. Add benchmarks and quality-report examples.

## Success signal for GitHub

A reviewer should see that you can design a real backend around financial time-series data: schemas, validation, storage, APIs, tests, and clear trade-offs.

## Current vertical slice

TickerFlow currently implements the first OHLCV backend slice:

- Load local OHLCV CSV files with typed ingestion configuration.
- Normalize timestamps to timezone-aware UTC at microsecond precision.
- Validate dirty rows and return a structured quality report instead of silently dropping data.
- Store valid rows as partitioned local Parquet under `ohlcv/symbol=<SYMBOL>/date=<YYYY-MM-DD>/data.parquet`.
- Query OHLCV rows by symbol and half-open UTC date range `[start, end)`.
- Discover available local datasets and symbols from Parquet partitions.
- Expose `/health`, `/datasets`, `/symbols`, and `/ohlcv` through FastAPI.

### OHLCV schema assumptions

Input CSV fixtures use these columns:

```text
timestamp,symbol,open,high,low,close,volume
```

Canonical rows use:

```text
timestamp_utc: datetime[us, UTC]
symbol: uppercase string
open: float
high: float
low: float
close: float
volume: float
source: string
```

Prices are unadjusted fixture values in arbitrary currency units. Volume is a non-negative numeric quantity. Corporate actions and live data sources are intentionally out of scope.

### Local development

```bash
uv sync --extra dev
uv run ruff format .
uv run ruff check .
uv run mypy src tests
uv run pytest
```

Run the API locally:

```bash
uv run uvicorn tickerflow.api.main:app --reload
```

Example query after writing Parquet data into the configured data directory:

```bash
curl "http://127.0.0.1:8000/ohlcv?symbol=AAPL&start=2024-01-02T00:00:00Z&end=2024-01-04T00:00:00Z"
```

Catalog endpoints:

```bash
curl "http://127.0.0.1:8000/datasets"
curl "http://127.0.0.1:8000/symbols?dataset=ohlcv"
```

By default, the API reads from `.tickerflow`. Set `TICKERFLOW_DATA_DIR` to point at another local Parquet root.
