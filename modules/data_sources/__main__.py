"""Command-line helpers for data source utilities."""

import argparse
from datetime import datetime
from pathlib import Path

from . import AkshareSource, BaostockSource, SyntheticSource, save_csv


_AVAILABLE = {
    "synthetic": SyntheticSource,
    "baostock": BaostockSource,
    "akshare": AkshareSource,
}


def _parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Data source helper entrypoint")
    parser.add_argument("--list", action="store_true", help="列出支持的数据源")
    parser.add_argument("--source", default="synthetic", help="数据源：synthetic/baostock/akshare")
    parser.add_argument("--symbol", default="SYNTH", help="标的代码，例如 sh.600000")
    parser.add_argument("--start", default="2020-01-01", help="起始日期 YYYY-MM-DD")
    parser.add_argument("--end", default="2020-06-30", help="结束日期 YYYY-MM-DD")
    parser.add_argument("--frequency", default="1d", help="频率，默认 1d")
    parser.add_argument("--csv-path", help="如指定则保存到 CSV")
    return parser.parse_args()


def main() -> None:
    args = _parse_args()
    if args.list:
        print("可用数据源：" + ", ".join(sorted(_AVAILABLE)))
        return

    source_cls = _AVAILABLE.get(args.source.lower())
    if source_cls is None:
        raise SystemExit(f"未知数据源: {args.source}")

    source = source_cls()
    start = datetime.strptime(args.start, "%Y-%m-%d")
    end = datetime.strptime(args.end, "%Y-%m-%d")
    dataset = source.fetch(args.symbol, start, end, args.frequency)
    print(f"已获取 {len(dataset.bars)} 条记录，频率 {dataset.frequency}，标的 {dataset.symbol}。")

    if args.csv_path:
        path = Path(args.csv_path)
        path.parent.mkdir(parents=True, exist_ok=True)
        save_csv(path, dataset)
        print(f"已保存到 {path}")


if __name__ == "__main__":
    main()
