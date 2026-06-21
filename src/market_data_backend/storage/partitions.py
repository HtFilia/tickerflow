from __future__ import annotations

from pathlib import Path


def ohlcv_partition_file(root: Path, dataset: str, symbol: str, date: str) -> Path:
    return root / dataset / f"symbol={symbol}" / f"date={date}" / "data.parquet"
