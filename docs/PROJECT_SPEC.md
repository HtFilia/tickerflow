# Project specification

## Objective

Create a Python backend that ingests local market-data files, validates and normalizes them, stores them as Parquet, and exposes query/bar-construction services.

## Target users

- Quant researchers who need reproducible local datasets.
- Quant developers building internal market-data tools.
- Data engineers working with financial time series.
- Technical recruiters evaluating backend/data-engineering maturity.

## In scope

### Data types

- OHLCV bars.
- Trades.
- Quotes as a later milestone.
- Order-book snapshots as an optional later milestone.

### Ingestion

- Local CSV and Parquet input.
- Schema mapping from source columns to canonical columns.
- Timezone normalization to UTC.
- Idempotent writes.

### Validation

- Required columns.
- Type checks.
- Missing values.
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
- `/trades`
- `/bars/time`
- `/bars/volume`

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

## Canonical trade schema

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
