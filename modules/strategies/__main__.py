"""Strategies helper entrypoint."""

import argparse

from .moving_average import MovingAverageCrossStrategy
from .portfolio import PortfolioStrategy
from .rotation import RotationStrategy


_STRATEGIES = {
    "moving_average": MovingAverageCrossStrategy,
    "rotation": RotationStrategy,
    "portfolio": PortfolioStrategy,
}


def _parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Strategies helper")
    parser.add_argument("--list", action="store_true", help="列出已内置的示例策略")
    return parser.parse_args()


def main() -> None:
    args = _parse_args()
    if args.list:
        print("可用策略：")
        for name, cls in _STRATEGIES.items():
            print(f"- {name}: {cls.__name__}")
        return
    print("使用 --list 查看策略清单，或在管线/实验中直接导入策略类。")


if __name__ == "__main__":
    main()
