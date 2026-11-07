from __future__ import annotations

import os
from pathlib import Path

from fastapi import FastAPI
from fastapi.openapi.docs import get_swagger_ui_html
from fastapi.responses import HTMLResponse, RedirectResponse

from tickerflow.api.routes_bars import build_bars_router
from tickerflow.api.routes_data import build_data_router
from tickerflow.api.routes_demo import build_demo_router
from tickerflow.api.schemas import HealthResponse
from tickerflow.query.market_data_query import OhlcvQueryService
from tickerflow.services.bar_service import BarService
from tickerflow.services.demo_service import DemoService
from tickerflow.storage.parquet_store import ParquetOhlcvStore


def create_app(data_root: Path | None = None) -> FastAPI:
    storage_root = data_root or Path(os.environ.get("TICKERFLOW_DATA_DIR", ".tickerflow"))
    store = ParquetOhlcvStore(storage_root)
    query_service = OhlcvQueryService(store)
    bar_service = BarService(query_service)
    demo_service = DemoService(store)

    # The API page carries the portfolio's favicon instead of FastAPI's.
    app = FastAPI(
        title="TickerFlow",
        version="0.1.0",
        description="Turn local market CSVs into validated, queryable API data.",
        docs_url=None,
    )

    @app.get("/docs", include_in_schema=False)
    def docs() -> HTMLResponse:
        return get_swagger_ui_html(
            openapi_url=app.openapi_url or "/openapi.json",
            title="TickerFlow - Swagger UI",
            swagger_favicon_url="/demo-assets/favicon.svg",
        )

    app.state.store = store
    app.state.query_service = query_service
    app.state.bar_service = bar_service
    app.state.demo_service = demo_service

    @app.get("/", include_in_schema=False)
    def redirect_to_demo() -> RedirectResponse:
        return RedirectResponse(url="/demo")

    @app.get("/health", response_model=HealthResponse)
    def health() -> HealthResponse:
        return HealthResponse(status="ok")

    app.include_router(build_data_router(query_service))
    app.include_router(build_bars_router(bar_service))
    app.include_router(build_demo_router(demo_service))
    return app


app = create_app()
