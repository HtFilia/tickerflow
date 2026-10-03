# Project specification

## Objective

Create a Python backend that ingests local market-data files, validates and normalizes them, stores them as Parquet, and exposes query/bar-construction services.

## Implemented scope

Current delivery is local OHLCV **CSV** ingestion, UTC normalization, explicit
quality reports, partitioned Parquet output, half-open OHLCV queries, hourly/daily
time bars and a FastAPI demo. Tests in `tests/unit/` and `tests/integration/`
exercise this path with committed synthetic fixtures. The target scope below
also includes proposals; it does not describe delivered trade/quote ingestion.

## Target users

- Quant researchers who need reproducible local datasets.
- Quant developers building internal market-data tools.
- Data engineers working with financial time series.

## Target scope and current status

### Data types

- OHLCV bars (implemented).
- Trades (planned).
- Quotes as a later milestone.
- Order-book snapshots as an optional later milestone.

### Ingestion

- Local CSV input (implemented); Parquet ingestion is planned. Parquet is currently storage output.
- Schema mapping from source columns to canonical columns.
- Timezone normalization to UTC.
- Idempotent writes.

### Validation

- Required columns.
- Type checks.
- Missing values.
- Finite OHLC prices/volume and consistent inclusive low/high bounds.
- Duplicate keys.
- Negative or zero prices where invalid.
- Negative volume.
- Non-monotonic timestamps per symbol.
- Quality report with counts and examples.

### Storage

- Partitioned Parquet by dataset/symbol/date or dataset/date/symbol.
- DuckDB query support.
- Local filesystem abstraction.

### Query API

- `/health`
- `/datasets`
- `/symbols`
- `/ohlcv`
- `/trades` (planned)
- `/bars/time`
- `/bars/volume` (planned)

## Out of scope for the first version

- Live vendor integrations.
- Authentication/authorization.
- Corporate actions.
- Real-time streaming.
- Distributed storage.
- Tick-level datasets too large to include in repo.

## Canonical OHLCV schema

```text
timestamp_utc: datetime[us, UTC]
symbol: str
open: float
high: float
low: float
close: float
volume: float
source: str
```

## Proposed canonical trade schema

```text
timestamp_utc: datetime[us, UTC]
symbol: str
price: float
size: float
trade_id: str | null
exchange: str | null
source: str
```

## Acceptance criteria for v0.1

- Local CSV ingestion for OHLCV.
- Validation report produced and tested.
- Partitioned Parquet write/read.
- Query service by symbol and date range.
- FastAPI endpoint for OHLCV queries.
- Tests use committed synthetic fixtures only.
