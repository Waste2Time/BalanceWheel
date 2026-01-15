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
            start_date = format_baostock_date(request.start)
            end_date = format_baostock_date(request.end)
            adjustflag = map_adjust_for_baostock(request.adjust)
            result = bs.query_history_k_data_plus(
                symbol,
                fields,
                start_date=start_date,
                end_date=end_date,
                frequency="d",
                adjustflag=adjustflag,
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


def format_baostock_date(value: str) -> str:
    """Format date string to YYYY-MM-DD for baostock."""
    if "-" in value:
        return value
    if len(value) != 8 or not value.isdigit():
        raise ValueError(f"Invalid date format: {value}")
    return f"{value[:4]}-{value[4:6]}-{value[6:]}"


def map_adjust_for_baostock(adjust: str) -> str:
    mapping = {"none": "3", "qfq": "2", "hfq": "1"}
    if adjust not in mapping:
        raise ValueError(f"Unsupported adjust value: {adjust}")
    return mapping[adjust]
