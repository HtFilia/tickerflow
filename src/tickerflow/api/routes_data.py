from __future__ import annotations

from datetime import datetime
from typing import Annotated

from fastapi import APIRouter, HTTPException, Query
from pydantic import ValidationError

from tickerflow.api.schemas import OhlcvMetadata, OhlcvRecord, OhlcvResponse
from tickerflow.query.filters import OhlcvQueryFilter
from tickerflow.query.market_data_query import OhlcvQueryService


def build_data_router(query_service: OhlcvQueryService) -> APIRouter:
    router = APIRouter()

    @router.get("/ohlcv", response_model=OhlcvResponse)
    def get_ohlcv(
        symbol: Annotated[str, Query(min_length=1)],
        start: Annotated[datetime, Query()],
        end: Annotated[datetime, Query()],
    ) -> OhlcvResponse:
        try:
            query_filter = OhlcvQueryFilter(symbol=symbol, start=start, end=end)
        except ValidationError as exc:
            raise HTTPException(status_code=422, detail=exc.errors()) from exc

        result = query_service.get_ohlcv(query_filter)
        rows = [OhlcvRecord.model_validate(row) for row in result.frame.to_dicts()]
        return OhlcvResponse(
            metadata=OhlcvMetadata(
                symbol=query_filter.symbol,
                start=query_filter.start,
                end=query_filter.end,
                row_count=result.row_count,
            ),
            data=rows,
        )

    return router
