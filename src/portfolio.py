from typing import Any


def calculate_portfolio(positions: list, cash_twd: float, prices: dict[str, float]) -> dict[str, Any]:
    """計算投資組合的各項數值。"""
    enriched = []
    total_stock_value = 0.0

    for pos in positions:
        price = prices.get(pos["ticker"], 0.0)
        value = pos["shares"] * price
        total_stock_value += value
        enriched.append({
            "ticker": pos["ticker"],
            "name": pos["name"],
            "shares": pos["shares"],
            "price": price,
            "value": value,
            "beta": pos["beta"],
            "weight": 0.0,
        })

    total_value = total_stock_value + cash_twd

    portfolio_beta = 0.0
    for item in enriched:
        item["weight"] = item["value"] / total_value if total_value > 0 else 0.0
        portfolio_beta += item["weight"] * item["beta"]

    cash_weight = cash_twd / total_value if total_value > 0 else 0.0

    return {
        "positions": enriched,
        "cash_twd": cash_twd,
        "cash_weight": cash_weight,
        "total_stock_value": total_stock_value,
        "total_value": total_value,
        "portfolio_beta": round(portfolio_beta, 4),
    }
