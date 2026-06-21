from __future__ import annotations

import os
from pathlib import Path

from fastapi import FastAPI

from tickerflow.api.routes_bars import build_bars_router
from tickerflow.api.routes_data import build_data_router
from tickerflow.api.schemas import HealthResponse
from tickerflow.query.market_data_query import OhlcvQueryService
from tickerflow.services.bar_service import BarService
from tickerflow.storage.parquet_store import ParquetOhlcvStore


def create_app(data_root: Path | None = None) -> FastAPI:
    root = data_root or Path(os.environ.get("TICKERFLOW_DATA_DIR", ".tickerflow"))
    store = ParquetOhlcvStore(root)
    query_service = OhlcvQueryService(store)
    bar_service = BarService(query_service)

    app = FastAPI(
        title="TickerFlow",
        version="0.1.0",
        description="Turn local market CSVs into validated, queryable API data.",
    )
    app.state.store = store
    app.state.query_service = query_service
    app.state.bar_service = bar_service

    @app.get("/health", response_model=HealthResponse)
    def health() -> HealthResponse:
        return HealthResponse(status="ok")

    app.include_router(build_data_router(query_service))
    app.include_router(build_bars_router(bar_service))
    return app


app = create_app()
