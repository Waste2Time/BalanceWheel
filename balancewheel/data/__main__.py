"""Run a quick schema normalization check."""

import pandas as pd

from balancewheel.data.normalize import normalize_ohlcv


def main() -> None:
    sample = pd.DataFrame(
        {
            "date": ["2024-01-01"],
            "open": [1.0],
            "high": [2.0],
            "low": [0.5],
            "close": [1.5],
        }
    )
    normalized = normalize_ohlcv(sample)
    print(normalized.dtypes)


if __name__ == "__main__":
    main()
