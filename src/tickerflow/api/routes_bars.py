from __future__ import annotations

from datetime import datetime
from typing import Annotated

from fastapi import APIRouter, HTTPException, Query
from pydantic import ValidationError

from tickerflow.api.schemas import TimeBarMetadata, TimeBarRecord, TimeBarsResponse
from tickerflow.bars.time_bars import TimeBarInterval
from tickerflow.query.filters import OhlcvQueryFilter
from tickerflow.services.bar_service import BarService


def build_bars_router(bar_service: BarService) -> APIRouter:
    router = APIRouter()

    @router.get("/bars/time", response_model=TimeBarsResponse)
    def get_time_bars(
        symbol: Annotated[str, Query(min_length=1)],
        start: Annotated[datetime, Query()],
        end: Annotated[datetime, Query()],
        interval: Annotated[TimeBarInterval, Query()] = "1d",
    ) -> TimeBarsResponse:
        try:
            query_filter = OhlcvQueryFilter(symbol=symbol, start=start, end=end)
        except ValidationError as exc:
            raise HTTPException(status_code=422, detail=exc.errors()) from exc

        result = bar_service.get_time_bars(query_filter, interval=interval)
        rows = [TimeBarRecord.model_validate(row) for row in result.frame.to_dicts()]
        return TimeBarsResponse(
            metadata=TimeBarMetadata(
                symbol=query_filter.symbol,
                start=query_filter.start,
                end=query_filter.end,
                interval=interval,
                row_count=result.row_count,
            ),
            data=rows,
        )

    return router
