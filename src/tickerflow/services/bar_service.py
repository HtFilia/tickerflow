from __future__ import annotations

from dataclasses import dataclass

import polars as pl

from tickerflow.bars.time_bars import TimeBarInterval, construct_time_bars
from tickerflow.query.filters import OhlcvQueryFilter
from tickerflow.query.market_data_query import OhlcvQueryService


@dataclass(frozen=True)
class TimeBarsResult:
    query_filter: OhlcvQueryFilter
    interval: TimeBarInterval
    frame: pl.DataFrame

    @property
    def row_count(self) -> int:
        return self.frame.height


class BarService:
    def __init__(self, ohlcv_query_service: OhlcvQueryService) -> None:
        self._ohlcv_query_service = ohlcv_query_service

    def get_time_bars(
        self,
        query_filter: OhlcvQueryFilter,
        *,
        interval: TimeBarInterval,
    ) -> TimeBarsResult:
        ohlcv_result = self._ohlcv_query_service.get_ohlcv(query_filter)
        bars = construct_time_bars(ohlcv_result.frame, interval=interval)
        return TimeBarsResult(query_filter=query_filter, interval=interval, frame=bars)
