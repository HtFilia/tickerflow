from __future__ import annotations

from fastapi import APIRouter
from fastapi.responses import HTMLResponse

from tickerflow.api.schemas import DemoSeedResponse, OhlcvWriteSummary
from tickerflow.services.demo_service import DemoService


def build_demo_router(demo_service: DemoService) -> APIRouter:
    router = APIRouter()

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
    return """<!doctype html>
<html lang="en">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>TickerFlow Demo</title>
  <style>
    :root {
      color-scheme: light;
      --ink: #17202a;
      --muted: #5e6b78;
      --line: #d8e0e7;
      --panel: #ffffff;
      --page: #f3f6f8;
      --blue: #1769aa;
      --green: #16845b;
      --amber: #b76619;
      --red: #b3373c;
    }
    * { box-sizing: border-box; }
    body {
      margin: 0;
      background: var(--page);
      color: var(--ink);
      font:
        14px/1.45 Inter,
        ui-sans-serif,
        system-ui,
        -apple-system,
        BlinkMacSystemFont,
        "Segoe UI",
        sans-serif;
    }
    button, input, select { font: inherit; }
    .shell { max-width: 1180px; margin: 0 auto; padding: 24px; }
    .topbar {
      display: grid;
      grid-template-columns: minmax(260px, 1fr) auto;
      gap: 16px;
      align-items: end;
      padding-bottom: 18px;
      border-bottom: 1px solid var(--line);
    }
    h1 { margin: 0; font-size: 30px; line-height: 1.1; letter-spacing: 0; }
    .subtitle { margin: 8px 0 0; color: var(--muted); max-width: 680px; }
    .actions { display: flex; gap: 10px; flex-wrap: wrap; justify-content: flex-end; }
    .button {
      border: 1px solid var(--blue);
      background: var(--blue);
      color: white;
      min-height: 38px;
      padding: 8px 12px;
      border-radius: 6px;
      cursor: pointer;
    }
    .button.secondary { background: white; color: var(--blue); }
    .status { color: var(--muted); margin-top: 10px; min-height: 20px; }
    .grid { display: grid; gap: 14px; margin-top: 18px; }
    .metrics { grid-template-columns: repeat(5, minmax(0, 1fr)); }
    .main { grid-template-columns: minmax(0, 1.2fr) minmax(320px, 0.8fr); align-items: start; }
    .panel {
      background: var(--panel);
      border: 1px solid var(--line);
      border-radius: 8px;
      padding: 14px;
      min-width: 0;
    }
    .metric strong { display: block; font-size: 26px; letter-spacing: 0; margin-bottom: 4px; }
    .metric span,
    .panel-label {
      color: var(--muted);
      font-size: 12px;
      text-transform: uppercase;
      letter-spacing: .08em;
    }
    .panel h2 { margin: 2px 0 12px; font-size: 18px; letter-spacing: 0; }
    .row {
      display: flex;
      align-items: center;
      justify-content: space-between;
      gap: 12px;
      padding: 8px 0;
      border-top: 1px solid #edf1f4;
    }
    .row:first-child { border-top: 0; }
    .badge {
      border-radius: 999px;
      padding: 4px 9px;
      font-size: 12px;
      background: #e8f2fb;
      color: var(--blue);
      white-space: nowrap;
    }
    .badge.green { background: #e8f6ef; color: var(--green); }
    .badge.amber { background: #fff2df; color: var(--amber); }
    .badge.red { background: #fdecee; color: var(--red); }
    table { width: 100%; border-collapse: collapse; table-layout: fixed; }
    th,
    td {
      padding: 9px 8px;
      border-bottom: 1px solid #edf1f4;
      text-align: left;
      overflow: hidden;
      text-overflow: ellipsis;
      white-space: nowrap;
    }
    th { color: var(--muted); font-size: 12px; text-transform: uppercase; letter-spacing: .06em; }
    .bars { display: grid; gap: 10px; }
    .bar-row {
      display: grid;
      grid-template-columns: 108px minmax(0, 1fr) 68px;
      gap: 10px;
      align-items: center;
    }
    .bar-track { height: 14px; border-radius: 999px; background: #e7edf2; overflow: hidden; }
    .bar-fill {
      height: 100%;
      border-radius: 999px;
      background: linear-gradient(90deg, var(--blue), var(--green));
      min-width: 4px;
    }
    .footnote { color: var(--muted); font-size: 12px; margin-top: 10px; }
    @media (max-width: 820px) {
      .shell { padding: 16px; }
      .topbar, .main { grid-template-columns: 1fr; }
      .actions { justify-content: flex-start; }
      .metrics { grid-template-columns: repeat(2, minmax(0, 1fr)); }
      h1 { font-size: 26px; }
    }
  </style>
</head>
<body>
  <main class="shell" id="demo-app">
    <section class="topbar">
      <div>
        <div class="panel-label">Recruiter demo</div>
        <h1>TickerFlow</h1>
        <p class="subtitle">
          Local CSV market data becomes validated Parquet storage, searchable API rows,
          and feature-ready time bars.
        </p>
        <div class="status" id="status">Preparing deterministic demo data.</div>
      </div>
      <div class="actions">
        <button class="button" id="refresh" type="button">Refresh demo data</button>
        <button class="button secondary" id="docs" type="button">Open API docs</button>
      </div>
    </section>

    <section class="grid metrics" aria-label="TickerFlow metrics">
      <div class="panel metric"><strong id="dataset-count">0</strong><span>Datasets</span></div>
      <div class="panel metric"><strong id="symbol-count">0</strong><span>Symbols</span></div>
      <div class="panel metric"><strong id="valid-rows">0</strong><span>Valid rows</span></div>
      <div class="panel metric">
        <strong id="dirty-rows">0</strong><span>Quarantined rows</span>
      </div>
      <div class="panel metric"><strong id="bar-count">0</strong><span>Hourly bars</span></div>
    </section>

    <section class="grid main">
      <div class="panel">
        <h2>Hourly AAPL Bars</h2>
        <div class="bars" id="bars"></div>
        <p class="footnote">Intervals are half-open: start included, end excluded.</p>
      </div>
      <div class="panel">
        <h2>Quality report</h2>
        <div id="quality"></div>
      </div>
      <div class="panel">
        <h2>OHLCV Query</h2>
        <table>
          <thead><tr><th>Time</th><th>Symbol</th><th>Close</th><th>Volume</th></tr></thead>
          <tbody id="ohlcv"></tbody>
        </table>
      </div>
      <div class="panel">
        <h2>Catalog</h2>
        <div id="catalog"></div>
      </div>
    </section>
  </main>

  <script>
    const statusNode = document.getElementById('status');
    const setText = (id, value) => { document.getElementById(id).textContent = String(value); };
    const jsonFetch = async (url, options = {}) => {
      const response = await fetch(url, options);
      if (!response.ok) throw new Error(`${response.status} ${response.statusText}`);
      return response.json();
    };
    const formatTime = (value) => value.slice(11, 16);

    async function loadDemo() {
      statusNode.textContent = 'Loading demo data from committed synthetic fixtures.';
      const seed = await jsonFetch('/demo/seed', { method: 'POST' });
      const datasets = await jsonFetch('/datasets');
      const symbols = await jsonFetch('/symbols?dataset=ohlcv');
      const range = 'start=2024-01-02T14:00:00Z&end=2024-01-02T17:00:00Z';
      const ohlcv = await jsonFetch(`/ohlcv?symbol=AAPL&${range}`);
      const bars = await jsonFetch(`/bars/time?symbol=AAPL&${range}&interval=1h`);

      setText('dataset-count', datasets.datasets.length);
      setText('symbol-count', symbols.symbols.length);
      setText('valid-rows', seed.clean_report.valid_rows);
      setText('dirty-rows', seed.dirty_report.quarantined_rows);
      setText('bar-count', bars.metadata.row_count);

      document.getElementById('catalog').innerHTML = [
        `<div class="row"><span>Dataset</span><span class="badge">${seed.dataset}</span></div>`,
        `<div class="row"><span>Symbols</span><span class="badge green">`
          + `${symbols.symbols.join(', ')}</span></div>`,
        `<div class="row"><span>Parquet partitions</span><span class="badge amber">`
          + `${seed.write_result.partitions_written}</span></div>`
      ].join('');

      document.getElementById('quality').innerHTML = seed.dirty_report.issues.map((issue) =>
        `<div class="row"><span>${issue.code.replaceAll('_', ' ')}</span>`
          + `<span class="badge red">${issue.count}</span></div>`
      ).join('');

      const maxVolume = Math.max(...bars.data.map((row) => row.volume));
      document.getElementById('bars').innerHTML = bars.data.map((row) => {
        const width = Math.max(5, Math.round((row.volume / maxVolume) * 100));
        return `<div class="bar-row"><span>${formatTime(row.bar_start_utc)}</span>`
          + `<div class="bar-track"><div class="bar-fill" style="width:${width}%">`
          + `</div></div><strong>${row.close.toFixed(1)}</strong></div>`;
      }).join('');

      document.getElementById('ohlcv').innerHTML = ohlcv.data.map((row) =>
        `<tr><td>${formatTime(row.timestamp_utc)}</td><td>${row.symbol}</td>`
          + `<td>${row.close.toFixed(1)}</td><td>${row.volume.toFixed(0)}</td></tr>`
      ).join('');

      statusNode.textContent = 'Demo ready: validation, storage, query, and time bars are loaded.';
    }

    document.getElementById('refresh')
      .addEventListener('click', () => loadDemo().catch(showError));
    document.getElementById('docs')
      .addEventListener('click', () => { window.location.href = '/docs'; });
    function showError(error) { statusNode.textContent = `Demo failed: ${error.message}`; }
    loadDemo().catch(showError);
  </script>
</body>
</html>"""
