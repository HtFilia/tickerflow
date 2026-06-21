# Recruiter demo plan

## Audience

Recruiters and hiring managers should understand TickerFlow without knowing financial data engineering. The demo should show a simple story: raw CSV data becomes validated, stored, searchable API data.

## Demo script

1. Show the README headline and current vertical slice.
2. Run the test suite to show engineering discipline.
3. Load the synthetic OHLCV fixture through the ingestion service.
4. Query `/datasets` and `/symbols` to show local catalog discovery.
5. Query `/ohlcv` for a symbol/date range.
6. Query `/bars/time` with `interval=1h` to show feature-ready bar construction.
7. Open `/demo` to show the recruiter-facing UI.
8. Open FastAPI docs at `/docs` when running locally if API-level screenshots are needed.

## Screenshot checklist

Store future images in `docs/assets/screenshots/`.

- `tickerflow-demo-desktop.png`: desktop view of `/demo`.
- `tickerflow-demo-mobile.png`: mobile view of `/demo`.
- `api-health.png`: `/health` response or Swagger operation.
- `catalog-endpoints.png`: `/datasets` and `/symbols` responses.
- `ohlcv-query.png`: `/ohlcv` response for `AAPL`.
- `time-bars.png`: `/bars/time` response showing hourly aggregation.
- `validation-report.png`: validation output from the dirty fixture once exposed in a CLI or API workflow.

## Deterministic demo data

Use only committed fixtures in `tests/fixtures/`. Do not fetch live market data for demos, screenshots, tests, or examples.

## Current limitation

TickerFlow now includes a lightweight `/demo` UI. It is intentionally a static FastAPI-served demo surface, not a full dashboard application.
