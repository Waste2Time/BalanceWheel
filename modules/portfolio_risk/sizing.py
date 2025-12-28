from __future__ import annotations

import math


def fixed_fractional_size(capital: float, price: float, fraction: float, min_qty: int = 1) -> int:
    risk_capital = capital * fraction
    qty = math.floor(risk_capital / price)
    return max(qty, min_qty)
