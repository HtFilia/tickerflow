from __future__ import annotations

import os
from pathlib import Path

from fastapi import FastAPI

from market_data_backend.api.routes_data import build_data_router
from market_data_backend.api.schemas import HealthResponse
from market_data_backend.query.market_data_query import OhlcvQueryService
from market_data_backend.storage.parquet_store import ParquetOhlcvStore


def create_app(data_root: Path | None = None) -> FastAPI:
    root = data_root or Path(os.environ.get("MARKET_DATA_BACKEND_DATA_DIR", ".market_data"))
    store = ParquetOhlcvStore(root)
    query_service = OhlcvQueryService(store)

    app = FastAPI(
        title="Market Data Backend",
        version="0.1.0",
        description="Local market-data ingestion, validation, storage, and query API.",
    )
    app.state.store = store
    app.state.query_service = query_service

    @app.get("/health", response_model=HealthResponse)
    def health() -> HealthResponse:
        return HealthResponse(status="ok")

    app.include_router(build_data_router(query_service))
    return app


app = create_app()
