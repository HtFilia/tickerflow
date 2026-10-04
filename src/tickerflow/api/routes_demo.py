from __future__ import annotations

from pathlib import Path

from fastapi import APIRouter, HTTPException
from fastapi.responses import FileResponse, HTMLResponse

from tickerflow.api.schemas import DemoSeedResponse, OhlcvWriteSummary
from tickerflow.services.case_service import CaseRun, DemoRunRequest, case_catalog, run_case
from tickerflow.services.demo_service import DemoService

_STATIC = Path(__file__).with_name("static")


def build_demo_router(demo_service: DemoService) -> APIRouter:
    router = APIRouter()

    @router.get("/demo-assets/{name}", include_in_schema=False)
    def asset(name: str) -> FileResponse:
        if name not in {"demo.css", "demo.js"}:
            raise HTTPException(status_code=404, detail="Asset not found")
        return FileResponse(_STATIC / name)

    @router.get("/demo/cases")
    def cases() -> list[dict[str, object]]:
        return case_catalog()

    @router.post("/demo/run", response_model=CaseRun)
    def run(request: DemoRunRequest) -> CaseRun:
        return run_case(request)

    @router.get("/demo", response_class=HTMLResponse, include_in_schema=False)
    def get_demo() -> HTMLResponse:
        return HTMLResponse(_render_demo_page())

    @router.post("/demo/seed", response_model=DemoSeedResponse)
    def seed_demo() -> DemoSeedResponse:
        result = demo_service.seed()
        return DemoSeedResponse(
            dataset=result.dataset,
            symbols=result.symbols,
            clean_report=result.clean_report,
            dirty_report=result.dirty_report,
            write_result=OhlcvWriteSummary(
                input_rows=result.write_result.input_rows,
                stored_rows=result.write_result.stored_rows,
                partitions_written=result.write_result.partitions_written,
            ),
        )

    return router


def _render_demo_page() -> str:
    return (_STATIC / "demo.html").read_text()
