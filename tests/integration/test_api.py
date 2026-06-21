from __future__ import annotations

import asyncio
from pathlib import Path

import httpx
from fastapi import FastAPI

from tickerflow.api.main import create_app
from tickerflow.ingestion.csv_loader import load_ohlcv_csv
from tickerflow.ingestion.source_config import OhlcvCsvConfig
from tickerflow.storage.parquet_store import ParquetOhlcvStore

FIXTURES = Path(__file__).resolve().parents[1] / "fixtures"


async def _get(app: FastAPI, path: str, params: dict[str, str] | None = None) -> httpx.Response:
    transport = httpx.ASGITransport(app=app)
    async with httpx.AsyncClient(transport=transport, base_url="http://testserver") as client:
        return await client.get(path, params=params)


def test_health_endpoint_reports_ok(tmp_path: Path) -> None:
    response = asyncio.run(_get(create_app(data_root=tmp_path), "/health"))

    assert response.status_code == 200
    assert response.json() == {"status": "ok"}


def test_ohlcv_endpoint_returns_symbol_date_range(tmp_path: Path) -> None:
    ingestion = load_ohlcv_csv(
        FIXTURES / "ohlcv_clean.csv",
        OhlcvCsvConfig(source="synthetic_clean"),
    )
    ParquetOhlcvStore(tmp_path).write_ohlcv(ingestion.frame)

    response = asyncio.run(
        _get(
            create_app(data_root=tmp_path),
            "/ohlcv",
            params={
                "symbol": "AAPL",
                "start": "2024-01-02T00:00:00Z",
                "end": "2024-01-04T00:00:00Z",
            },
        )
    )

    assert response.status_code == 200
    payload = response.json()
    assert payload["metadata"] == {
        "symbol": "AAPL",
        "start": "2024-01-02T00:00:00Z",
        "end": "2024-01-04T00:00:00Z",
        "row_count": 2,
    }
    assert [row["close"] for row in payload["data"]] == [101.0, 102.0]
    assert payload["data"][0]["timestamp_utc"] == "2024-01-02T14:30:00Z"
