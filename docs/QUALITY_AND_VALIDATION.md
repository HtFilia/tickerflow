# Quality and validation

## Test categories

### Unit tests

- Schema normalization.
- Timestamp conversion.
- Validation checks.
- Bar-construction boundaries.
- Partition path generation.

### Integration tests

- CSV fixture -> validation report -> Parquet storage -> query result.
- API query returns expected rows and metadata.

### Regression tests

- Dirty fixture produces stable quality report counts.
- Bar construction on a known fixture produces stable output.

## Data-quality checklist

For each ingestion source, document:

- Input schema.
- Canonical output schema.
- Timezone handling.
- Validation checks.
- Drop/repair/quarantine behavior.
- Idempotency behavior.

## Recommended checks

```bash
uv run ruff format --check .
uv run ruff check .
uv run mypy src tests
uv run pytest
```

## Fixture policy

- Keep fixtures small enough to inspect manually.
- Prefer synthetic data over copied vendor data.
- Include at least one clean fixture and one dirty fixture.
- Do not commit proprietary market data.

## Benchmarking principles

- Benchmarks should be optional and separate from unit tests.
- Include dataset size, machine notes, and operation definition.
- Do not overstate benchmark conclusions from toy datasets.

## Documentation quality bar

Every major feature should include:

- Input/output schema.
- One example call.
- One validation or edge-case note.
- One limitation note.

## OHLCV rejection policy

The existing seven-row dirty fixture returns one valid row and six quarantined
rows, zero repairs/drops. Its report counts are `duplicate_key: 2`,
`invalid_timestamp: 1`, `negative_volume: 1`, `non_monotonic_timestamp: 1`,
`non_positive_price: 1`. The [unit regression](../tests/unit/test_ohlcv_ingestion_validation.py)
and [seed → query demo](DEMO.md) make those decisions inspectable.

All OHLC prices must be finite and strictly positive; volume must be finite
and nonnegative (zero is valid). Require `low <= high` and both open and close
inside the inclusive low/high range. No invalid values are repaired.
`non_finite_numeric_value` and `invalid_ohlc_range` identify these failures.
A row can contribute to multiple issue counts but is quarantined once. Examples
represent NaN/infinities as strings so reports remain valid JSON.

The three-row `tests/fixtures/ohlcv_invalid.csv` regression yields zero valid
rows: two non-finite issues and one range issue. Unit boundary cases cover NaN,
both infinity signs, flat OHLC and zero volume. Integration tests verify rejected
rows cannot reach Parquet or queries through the ingestion service.
