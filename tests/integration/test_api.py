from __future__ import annotations

import asyncio
from pathlib import Path

import httpx
import pytest
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


def test_catalog_endpoints_list_datasets_and_symbols(tmp_path: Path) -> None:
    ingestion = load_ohlcv_csv(
        FIXTURES / "ohlcv_clean.csv",
        OhlcvCsvConfig(source="synthetic_clean"),
    )
    ParquetOhlcvStore(tmp_path).write_ohlcv(ingestion.frame)
    app = create_app(data_root=tmp_path)

    datasets_response = asyncio.run(_get(app, "/datasets"))
    symbols_response = asyncio.run(_get(app, "/symbols", params={"dataset": "ohlcv"}))

    assert datasets_response.status_code == 200
    assert datasets_response.json() == {"datasets": ["ohlcv"]}
    assert symbols_response.status_code == 200
    assert symbols_response.json() == {"dataset": "ohlcv", "symbols": ["AAPL", "MSFT"]}


def test_app_reads_data_root_from_tickerflow_env_var(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    data_root = tmp_path / "tickerflow-data"
    ingestion = load_ohlcv_csv(
        FIXTURES / "ohlcv_clean.csv",
        OhlcvCsvConfig(source="synthetic_clean"),
    )
    ParquetOhlcvStore(data_root).write_ohlcv(ingestion.frame)
    monkeypatch.setenv("TICKERFLOW_DATA_DIR", str(data_root))

    response = asyncio.run(_get(create_app(), "/datasets"))

    assert response.status_code == 200
    assert response.json() == {"datasets": ["ohlcv"]}
