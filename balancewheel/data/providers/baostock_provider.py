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
            result = bs.query_history_k_data_plus(
                request.symbol,
                fields,
                start_date=request.start,
                end_date=request.end,
                frequency="d",
                adjustflag="3",
            )

            rows = []
            while result.next():
                rows.append(result.get_row_data())
        finally:
            bs.logout()

        data = pd.DataFrame(rows, columns=result.fields)
        return data
