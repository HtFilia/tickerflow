# Market-data demo

## Purpose

The `/demo` route shows the deterministic TickerFlow data path: local CSV rows
are normalized and validated, valid rows are written to Parquet, and the stored
dataset is exposed through catalog, query, and time-bar APIs.

## Demo script

1. Install dependencies and run the quality gate.
2. Start the API with `uv run uvicorn tickerflow.api.main:app --reload`.
3. Open `/demo` and seed the committed synthetic OHLCV fixtures.
4. Inspect `/datasets` and `/symbols` for local catalog discovery.
5. Query `/ohlcv` for a symbol and half-open UTC date range.
6. Query `/bars/time?interval=1h` to inspect deterministic time-bar construction.
7. Open `/docs` to inspect the same operations through OpenAPI.

Use only committed fixtures. Do not use live or proprietary market data in
demos, tests, or documentation.

## Current limitation

The demo is a lightweight FastAPI-served interface for exercising the backend,
not a full analytical dashboard.
