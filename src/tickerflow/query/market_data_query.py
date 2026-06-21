from __future__ import annotations

from dataclasses import dataclass

import polars as pl

from tickerflow.query.filters import OhlcvQueryFilter
from tickerflow.storage.parquet_store import ParquetOhlcvStore


@dataclass(frozen=True)
class OhlcvQueryResult:
    query_filter: OhlcvQueryFilter
    frame: pl.DataFrame

    @property
    def row_count(self) -> int:
        return self.frame.height


class OhlcvQueryService:
    def __init__(self, store: ParquetOhlcvStore) -> None:
        self._store = store

    def get_ohlcv(self, query_filter: OhlcvQueryFilter) -> OhlcvQueryResult:
        frame = self._store.read_ohlcv(
            symbol=query_filter.symbol,
            start=query_filter.start,
            end=query_filter.end,
        )
        return OhlcvQueryResult(query_filter=query_filter, frame=frame)
