"""Portfolio risk helper entrypoint."""

import argparse

from .risk import MaxDrawdownLimiter
from .sizing import PositionSizer


def _parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Portfolio risk helper")
    parser.add_argument("--list", action="store_true", help="列出可用的风控/仓位工具")
    return parser.parse_args()


def main() -> None:
    args = _parse_args()
    if args.list:
        print("可用工具：")
        print("- PositionSizer: 固定目标仓位百分比")
        print("- MaxDrawdownLimiter: 基于最大回撤的风控检查")
        return
    print("使用 --list 查看可用组件，或在回测/策略代码中直接导入 PositionSizer/MaxDrawdownLimiter。")


if __name__ == "__main__":
    main()
