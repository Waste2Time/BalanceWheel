from __future__ import annotations

from pathlib import Path
from typing import Dict, Optional

import pandas as pd

try:
    import matplotlib.pyplot as plt
except Exception:  # pragma: no cover
    plt = None


def plot_equity_curves(results: Dict[str, pd.Series], output: Path) -> Optional[Path]:
    if plt is None:
        return None
    output.parent.mkdir(parents=True, exist_ok=True)
    for name, series in results.items():
        series.sort_index().plot(label=name)
    plt.legend()
    plt.title("Equity Curve Comparison")
    plt.xlabel("Date")
    plt.ylabel("Equity")
    plt.tight_layout()
    plt.savefig(output)
    plt.close()
    return output
