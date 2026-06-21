# AGENTS.md

## Repository mission

Build a Python-only backend for market-data ingestion, validation, storage, querying, and feature-ready bar construction. The project should demonstrate data engineering discipline for financial time series, not just exploratory notebooks.

## Read first

Before changing code, read these files in order:

1. `README.md`
2. `docs/PROJECT_SPEC.md`
3. `docs/ARCHITECTURE.md`
4. `docs/QUALITY_AND_VALIDATION.md`
5. `PLANS.md`

## Python-only constraint

- Backend code must be written in Python.
- Do not add C++, Rust, Java, Go, or custom native extensions.
- Python libraries with native internals are allowed: Polars, DuckDB, PyArrow, NumPy, FastAPI, Pydantic.
- Do not require proprietary or paid data sources for tests or examples.

## Expected layout

```text
src/market_data_backend/
  api/              # FastAPI app and routes
  core/             # domain entities and time-series rules
  ingestion/        # source adapters and normalization
  storage/          # parquet/duckdb repositories
  query/            # query services and filters
  bars/             # time, tick, volume, dollar, imbalance bars
  validation/       # schema checks, anomaly detection, quality reports
  services/         # orchestration between API and domain logic
  utils/            # small utilities only

tests/
  unit/
  integration/
  fixtures/

docs/
benchmarks/
notebooks/
```

## Development commands

Prefer `uv`. If the project is not bootstrapped yet, create `pyproject.toml` first.

```bash
uv sync --extra dev
uv run ruff format .
uv run ruff check .
uv run mypy src tests
uv run pytest
```

API smoke test once implemented:

```bash
uv run uvicorn market_data_backend.api.main:app --reload
```

## Engineering rules

- Use typed Pydantic models at API and ingestion boundaries.
- Use Polars lazy operations for large tabular transformations when practical.
- Use DuckDB for query-style examples and Parquet for durable local storage.
- Keep all test data small, synthetic, and committed under `tests/fixtures/`.
- Do not fetch live data during tests.
- Avoid ambiguous timestamps. Use timezone-aware UTC internally.
- Never silently drop rows. Validation must report dropped, repaired, or quarantined rows.
- Prefer deterministic idempotent ingestion: running the same ingestion twice should not duplicate records.

## Financial-data rules

- Always document schema assumptions: timestamp precision, symbol format, price units, volume units, timezone, and adjusted/unadjusted status.
- Keep OHLCV, trades, quotes, and order-book snapshots as distinct schemas.
- Bar construction must define inclusion/exclusion boundaries precisely.
- Corporate-action support is out of scope until explicitly requested; do not fake it.

## Definition of done

A task is done only when:

- Implementation is typed and covered by tests.
- Data-quality behavior is tested on at least one dirty fixture.
- `ruff`, `mypy`, and `pytest` pass for the relevant scope.
- README or docs are updated if public behavior changed.
- Codex final response lists changed files, checks run, and known limitations.
