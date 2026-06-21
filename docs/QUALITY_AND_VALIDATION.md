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
