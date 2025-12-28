from __future__ import annotations

import numpy as np
import pandas as pd


def max_drawdown(equity: pd.Series) -> float:
    rolling_max = equity.cummax()
    drawdowns = (rolling_max - equity) / rolling_max
    return drawdowns.max() if not drawdowns.empty else 0.0


def compute_metrics(equity: pd.Series) -> dict:
    returns = equity.pct_change().dropna()
    total_return = equity.iloc[-1] / equity.iloc[0] - 1 if len(equity) > 1 else 0.0
    ann_factor = 252 / max(len(returns), 1)
    ann_return = (1 + total_return) ** ann_factor - 1 if total_return > -1 else -1
    ann_vol = returns.std() * np.sqrt(252) if not returns.empty else 0.0
    sharpe = ann_return / ann_vol if ann_vol else 0.0
    mdd = max_drawdown(equity)
    win_rate = (returns > 0).mean() if not returns.empty else 0.0
    avg_gain = returns[returns > 0].mean() if (returns > 0).any() else 0.0
    avg_loss = returns[returns < 0].mean() if (returns < 0).any() else 0.0
    return {
        "total_return": total_return,
        "ann_return": ann_return,
        "ann_vol": ann_vol,
        "sharpe": sharpe,
        "max_drawdown": mdd,
        "win_rate": win_rate,
        "avg_gain": avg_gain,
        "avg_loss": avg_loss,
    }
