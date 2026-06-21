# Architecture

## Design principles

- Ingestion adapters normalize external data into canonical schemas.
- Validation reports are first-class outputs, not log messages.
- Storage code should be replaceable without changing API contracts.
- Data transformations should be deterministic and testable.

## Proposed module boundaries

```text
api/
  main.py
  routes_data.py
  routes_bars.py
  schemas.py

core/
  schemas.py             # canonical column definitions
  time.py                # UTC conversion and interval boundaries
  identifiers.py         # dataset/symbol validation

ingestion/
  csv_loader.py
  normalizer.py
  source_config.py

validation/
  checks.py
  report.py

storage/
  parquet_store.py
  duckdb_query.py
  partitions.py

query/
  filters.py
  market_data_query.py

bars/
  time_bars.py
  volume_bars.py
  dollar_bars.py

services/
  ingestion_service.py
  query_service.py
  bar_service.py
```

## Dependency direction

```text
api -> services -> ingestion/storage/query/bars/validation -> core
```

No module below `api` should import FastAPI.

## Data flow

```text
local file -> ingestion adapter -> canonical frame -> validation report -> storage -> query service -> API response
```

## Error handling

- Invalid schema: fail fast with clear error.
- Dirty rows: configurable behavior: reject, quarantine, or repair if safe.
- Duplicate ingestion: idempotent behavior preferred; never duplicate silently.
- Empty query result: return an empty result with metadata, not an exception.

## Bar construction boundaries

Define intervals as half-open: `[start, end)`. Document timezone and sorting requirements. Tests must cover boundary cases.

## Future extensions

- Quotes and NBBO-like examples.
- Order-book snapshots.
- Data catalog metadata.
- Incremental ingestion manifests.
- Small dashboard or OpenAPI examples.
