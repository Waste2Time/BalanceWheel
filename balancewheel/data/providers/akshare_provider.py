"""Akshare provider implementation."""

from __future__ import annotations

import pandas as pd

from balancewheel.data.interfaces import DataProvider, DataRequest


class AkshareProvider(DataProvider):
    name = "akshare"

    def fetch_daily_ohlcv(self, request: DataRequest) -> pd.DataFrame:
        import akshare as ak

        if request.asset_type == "stock":
            data = ak.stock_zh_a_hist(
                symbol=request.symbol,
                start_date=request.start,
                end_date=request.end,
                adjust="",
            )
        elif request.asset_type == "etf":
            data = ak.fund_etf_hist_em(
                symbol=request.symbol,
                start_date=request.start,
                end_date=request.end,
                adjust="",
            )
        elif request.asset_type == "index":
            data = ak.index_zh_a_hist(
                symbol=request.symbol,
                start_date=request.start,
                end_date=request.end,
            )
        else:
            raise ValueError(f"Unsupported asset type: {request.asset_type}")

        return data.copy()
