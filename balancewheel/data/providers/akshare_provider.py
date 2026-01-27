"""Akshare provider implementation."""

from __future__ import annotations

import pandas as pd

from balancewheel.data.interfaces import DataProvider, DataRequest
from balancewheel.data.utils import format_symbol_for_sina


class AkshareProvider(DataProvider):
    name = "akshare"

    def fetch_daily_ohlcv(self, request: DataRequest) -> pd.DataFrame:
        import akshare as ak

        adjust = map_adjust_for_akshare(request.adjust)
        if request.asset_type == "stock":
            data = ak.stock_zh_a_hist(
                symbol=request.symbol,
                start_date=request.start,
                end_date=request.end,
                adjust=adjust,
            )
        elif request.asset_type == "etf":
            data = ak.fund_etf_hist_em(
                symbol=request.symbol,
                start_date=request.start,
                end_date=request.end,
                adjust=adjust,
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


class AkshareEtfSinaProvider(DataProvider):
    name = "akshare_sina"

    def fetch_daily_ohlcv(self, request: DataRequest) -> pd.DataFrame:
        import akshare as ak

        if request.asset_type != "etf":
            raise ValueError("AkshareEtfSinaProvider only supports ETF data")

        symbol = format_symbol_for_sina(request.symbol)
        data = ak.fund_etf_hist_sina(symbol=symbol)
        data = data.copy()
        start = pd.to_datetime(request.start)
        end = pd.to_datetime(request.end)
        if "日期" in data.columns:
            dates = pd.to_datetime(data["日期"])
        elif "date" in data.columns:
            dates = pd.to_datetime(data["date"])
        else:
            dates = pd.to_datetime(data.iloc[:, 0])
        data = data[(dates >= start) & (dates <= end)].reset_index(drop=True)
        return data


def map_adjust_for_akshare(adjust: str) -> str:
    mapping = {"none": "", "qfq": "qfq", "hfq": "hfq"}
    if adjust not in mapping:
        raise ValueError(f"Unsupported adjust value: {adjust}")
    return mapping[adjust]
