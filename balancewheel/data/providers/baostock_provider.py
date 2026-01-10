"""Baostock provider implementation."""

from __future__ import annotations

import pandas as pd

from balancewheel.data.interfaces import DataProvider, DataRequest


class BaostockProvider(DataProvider):
    name = "baostock"

    def fetch_daily_ohlcv(self, request: DataRequest) -> pd.DataFrame:
        import baostock as bs

        login = bs.login()
        if login.error_code != "0":
            raise RuntimeError(f"Baostock login failed: {login.error_msg}")

        try:
            fields = "date,open,high,low,close,volume,amount"
            symbol = format_baostock_symbol(request.symbol, request.asset_type)
            result = bs.query_history_k_data_plus(
                symbol,
                fields,
                start_date=request.start,
                end_date=request.end,
                frequency="d",
                adjustflag=request.adjust or "3",
            )

            rows = []
            while result.next():
                rows.append(result.get_row_data())
        finally:
            bs.logout()

        data = pd.DataFrame(rows, columns=result.fields)
        return data


def format_baostock_symbol(symbol: str, asset_type: str) -> str:
    """Format symbol to baostock's 9-character exchange.code convention."""
    if "." in symbol:
        return symbol

    if asset_type == "index":
        if symbol.startswith("000") or symbol.startswith("399"):
            return f"sz.{symbol}"
        return f"sh.{symbol}"

    if symbol.startswith(("600", "601", "603", "605", "688", "689")):
        return f"sh.{symbol}"
    if symbol.startswith(("000", "001", "002", "003", "300", "301")):
        return f"sz.{symbol}"
    if symbol.startswith(("510", "511", "512", "513", "515", "516", "518", "588", "159", "160")):
        return f"sh.{symbol}"
    return f"sz.{symbol}"
