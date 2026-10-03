# Architecture

## Design principles

- Ingestion adapters normalize external data into canonical schemas.
- Validation reports are first-class outputs, not log messages.
- Storage code should be replaceable without changing API contracts.
- Data transformations should be deterministic and testable.

## Current module boundaries

```text
api/
  main.py
  routes_data.py
  routes_bars.py
  routes_demo.py
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
  volume_bars.py         # planned placeholder
  dollar_bars.py         # planned placeholder

services/
  ingestion_service.py
  query_service.py
  bar_service.py
  demo_service.py
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
- Dirty rows: quarantine and report; no repair or silent dropping.
- Duplicate ingestion: identical keys are deduplicated in local storage; see DEMO.md.
- Empty query result: return an empty result with metadata, not an exception.

## Bar construction boundaries

Define intervals as half-open: `[start, end)`. Document timezone and sorting requirements. Tests must cover boundary cases.

## Future extensions

- Trade/quote ingestion and NBBO-like examples.
- Tick, volume and dollar bars.
- Order-book snapshots.
- Data catalog metadata.
- Incremental ingestion manifests.
- Richer dashboard examples; the current `/demo` and `/docs` already exist.
