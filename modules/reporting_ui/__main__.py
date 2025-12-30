"""Reporting/UI helper entrypoint."""

import argparse
from pathlib import Path

from .report import ReportBundle, write_report


def _parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Reporting/UI helper")
    parser.add_argument("--demo", action="store_true", help="输出一个示例报告文件")
    parser.add_argument("--output", default="/tmp/report_demo.txt", help="报告输出路径")
    return parser.parse_args()


def main() -> None:
    args = _parse_args()
    if not args.demo:
        print("使用 --demo 生成示例报告，或在管线中调用 reporting_ui.build_report。")
        return

    bundle = ReportBundle(metrics={"total_return": 0.0, "max_drawdown": 0.0}, equity_curve_path=None)
    path = Path(args.output)
    path.parent.mkdir(parents=True, exist_ok=True)
    write_report(bundle, path)
    print(f"已生成示例报告: {path}")


if __name__ == "__main__":
    main()
