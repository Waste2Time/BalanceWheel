"""Shared utilities for data providers."""

from __future__ import annotations

from typing import Tuple


SH_PREFIXES: Tuple[str, ...] = ("600", "601", "603", "605", "688", "900", "51", "58")
SZ_PREFIXES: Tuple[str, ...] = ("000", "001", "002", "003", "300", "200", "15", "16")


def infer_exchange(symbol: str) -> str:
    """Infer exchange code ("sh" or "sz") from a symbol."""
    if symbol.startswith(("sh", "sz")):
        return symbol[:2]
    if "." in symbol:
        head, tail = symbol.split(".", 1)
        if head in ("sh", "sz"):
            return head
        symbol = tail
    if symbol.startswith(SH_PREFIXES):
        return "sh"
    if symbol.startswith(SZ_PREFIXES):
        return "sz"
    return "sh"


def strip_exchange_prefix(symbol: str) -> str:
    """Remove exchange prefix ("sh", "sz", "sh.", "sz.") from symbol."""
    if symbol.startswith(("sh.", "sz.")):
        return symbol[3:]
    if symbol.startswith(("sh", "sz")):
        return symbol[2:]
    if "." in symbol:
        head, tail = symbol.split(".", 1)
        if head in ("sh", "sz"):
            return tail
    return symbol


def format_symbol_for_sina(symbol: str) -> str:
    """Format symbol with exchange prefix for Sina (e.g., sh510300)."""
    if symbol.startswith(("sh", "sz")) and not symbol.startswith(("sh.", "sz.")):
        return symbol
    code = strip_exchange_prefix(symbol)
    exchange = infer_exchange(symbol)
    return f"{exchange}{code}"


def format_symbol_for_baostock(symbol: str) -> str:
    """Format symbol with exchange prefix for baostock (e.g., sh.600000)."""
    if "." in symbol:
        return symbol
    code = strip_exchange_prefix(symbol)
    exchange = infer_exchange(symbol)
    return f"{exchange}.{code}"
