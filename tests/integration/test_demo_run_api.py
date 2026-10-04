from concurrent.futures import ThreadPoolExecutor
from datetime import UTC, datetime
from pathlib import Path

import pytest
from fastapi.testclient import TestClient
from pytest import MonkeyPatch

from tickerflow.api.main import create_app
from tickerflow.services.case_service import CaseId, DemoRunRequest, run_case


def test_real_isolated_run_and_boundary_lineage(tmp_path: Path) -> None:
    client = TestClient(create_app(tmp_path))
    assert len(client.get("/demo/cases").json()) == 4
    response = client.post("/demo/run", json={"case_id": "boundaries"})
    assert response.status_code == 200
    result = response.json()
    assert [b["contributor_ids"] for b in result["bars"]] == [[1], [2, 3], [4], [5]]
    assert result["bars"][1]["volume"] == 500
    assert not list(tmp_path.rglob("*.parquet"))  # Shared data directory untouched.
    day = client.post("/demo/run", json={"case_id": "boundaries", "interval": "1d"}).json()
    assert day["bars"][0]["contributor_ids"] == [1, 2, 3, 4]
    empty = client.post(
        "/demo/run", json={"start": "2024-02-01T00:00:00Z", "end": "2024-02-02T00:00:00Z"}
    ).json()
    assert empty["query"] == empty["bars"] == []
    for payload in [
        {"case_id": "missing"},
        {"case_version": "v2"},
        {"interval": "1m"},
        {"start": "2024-01-02T00:00:00"},
        {"start": "2024-01-04T00:00:00Z"},
        {"sql": "delete everything"},
    ]:
        assert client.post("/demo/run", json=payload).status_code == 422


def test_interleaved_runs_and_partial_window() -> None:
    cases: list[CaseId] = ["duplicates", "ranges"]
    with ThreadPoolExecutor(max_workers=2) as executor:
        futures = [executor.submit(run_case, DemoRunRequest(case_id=case)) for case in cases]
        first, second = [f.result() for f in futures]
    assert first.report.valid_rows == 6 and second.report.valid_rows == 4
    assert first.fixture_sha256 != second.fixture_sha256
    partial = run_case(
        DemoRunRequest(case_id="boundaries", start=datetime(2024, 1, 2, 15, 30, tzinfo=UTC))
    )
    assert partial.bars[0].partial_query_boundary
    assert partial.bars[0].contributor_ids == [3]


def test_temporary_files_cleaned_on_success_and_storage_failure(
    tmp_path: Path, monkeypatch: MonkeyPatch
) -> None:
    from tempfile import TemporaryDirectory

    import tickerflow.services.case_service as service
    from tickerflow.storage.parquet_store import ParquetOhlcvStore

    def temporary(prefix: str) -> TemporaryDirectory[str]:
        return TemporaryDirectory(prefix=prefix, dir=tmp_path)

    monkeypatch.setattr(service, "TemporaryDirectory", temporary)
    run_case(DemoRunRequest())
    assert list(tmp_path.iterdir()) == []

    def failed_write(*args: object, **kwargs: object) -> None:
        raise RuntimeError("Storage unavailable")

    monkeypatch.setattr(ParquetOhlcvStore, "write_ohlcv", failed_write)
    with pytest.raises(RuntimeError, match="Storage unavailable"):
        run_case(DemoRunRequest())
    assert list(tmp_path.iterdir()) == []
