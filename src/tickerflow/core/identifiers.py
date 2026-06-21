from __future__ import annotations

import re

SYMBOL_PATTERN = re.compile(r"^[A-Z0-9][A-Z0-9._-]{0,31}$")


def normalize_symbol(symbol: str) -> str:
    return symbol.strip().upper()


def is_valid_symbol(symbol: str) -> bool:
    return bool(SYMBOL_PATTERN.fullmatch(symbol))
