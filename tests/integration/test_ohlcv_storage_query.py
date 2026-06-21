from __future__ import annotations

from datetime import UTC, datetime
from pathlib import Path

from tickerflow.ingestion.csv_loader import load_ohlcv_csv
from tickerflow.ingestion.source_config import OhlcvCsvConfig
from tickerflow.query.filters import OhlcvQueryFilter
from tickerflow.query.market_data_query import OhlcvQueryService
from tickerflow.storage.parquet_store import ParquetOhlcvStore

FIXTURES = Path(__file__).resolve().parents[1] / "fixtures"


def test_parquet_store_is_idempotent_and_query_filters_by_symbol_and_range(
    tmp_path: Path,
) -> None:
    ingestion = load_ohlcv_csv(
        FIXTURES / "ohlcv_clean.csv",
        OhlcvCsvConfig(source="synthetic_clean"),
    )
    store = ParquetOhlcvStore(tmp_path)
    query_service = OhlcvQueryService(store)

    first_write = store.write_ohlcv(ingestion.frame)
    second_write = store.write_ohlcv(ingestion.frame)

    result = query_service.get_ohlcv(
        OhlcvQueryFilter(
            symbol="AAPL",
            start=datetime(2024, 1, 2, tzinfo=UTC),
            end=datetime(2024, 1, 4, tzinfo=UTC),
        )
    )

    assert first_write.input_rows == 3
    assert second_write.input_rows == 3
    assert result.row_count == 2
    assert result.frame.select("timestamp_utc", "symbol", "close").rows() == [
        (datetime(2024, 1, 2, 14, 30, tzinfo=UTC), "AAPL", 101.0),
        (datetime(2024, 1, 3, 14, 30, tzinfo=UTC), "AAPL", 102.0),
    ]
