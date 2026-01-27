"""Fetch sample A-share data for quick testing."""

from __future__ import annotations

from datetime import date, timedelta

from balancewheel.data import DataRequest, CsvRepository, DataService
from balancewheel.data.providers import AkshareProvider, BaostockProvider


def _yyyymmdd(value: date) -> str:
    return value.strftime("%Y%m%d")


def main() -> None:
    end_date = date.today()
    start_date = end_date - timedelta(days=365)
    start = _yyyymmdd(start_date)
    end = _yyyymmdd(end_date)

    service = DataService(
        providers={"akshare": AkshareProvider(), "baostock": BaostockProvider()},
        repository=CsvRepository("data"),
    )

    requests = [
        # baostock 的akshare单位是手，baostock的单位是股，这里数据不一样，在校验匹配的时候需要特殊处理一下


        DataRequest(symbol="000001", asset_type="stock", start=start, end=end, adjust="none"),
        # DataRequest(symbol="510300", asset_type="etf", start=start, end=end, adjust="none"),
    ]

    for request in requests:
        data = service.fetch_and_save(request, provider_name="akshare")
        if data.empty:
            print(f"{request.asset_type} {request.symbol}: no data returned")
            continue
        print(
            f"{request.asset_type} {request.symbol}: rows={len(data)} "
            f"start={data['datetime'].min().date()} end={data['datetime'].max().date()}"
        )


if __name__ == "__main__":
    main()
