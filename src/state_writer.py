import json
import os
from datetime import datetime


STATE_PATH = os.path.join(os.path.dirname(__file__), "..", "docs", "data", "state.json")


def write_state(portfolio: dict, rebalance: dict, now: datetime) -> None:
    """將最新狀態寫入 docs/data/state.json，供 GitHub Pages Dashboard 讀取。"""
    state = {
        "last_updated": now.isoformat(),
        "portfolio": {
            "total_value": portfolio["total_value"],
            "total_stock_value": portfolio["total_stock_value"],
            "cash_twd": portfolio["cash_twd"],
            "cash_weight": round(portfolio["cash_weight"], 4),
            "positions": [
                {
                    "ticker": p["ticker"],
                    "name": p["name"],
                    "shares": p["shares"],
                    "price": p["price"],
                    "value": round(p["value"], 0),
                    "weight": round(p["weight"], 4),
                    "beta": p["beta"],
                }
                for p in portfolio["positions"]
            ],
        },
        "beta": {
            "current": rebalance["current_beta"],
            "target": rebalance["target_beta"],
            "upper_limit": rebalance["upper_limit"],
            "lower_limit": rebalance["lower_limit"],
            "deviation_pct": rebalance["deviation_pct"],
            "status": rebalance["status"],
        },
        "rebalancing": {
            "triggered": rebalance["triggered"],
            "action": rebalance["action"],
            "amount_twd": rebalance["amount_twd"],
            "shares_estimate": rebalance.get("shares_estimate", 0),
        },
    }

    path = os.path.abspath(STATE_PATH)
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w", encoding="utf-8") as f:
        json.dump(state, f, ensure_ascii=False, indent=2)
    print(f"[state_writer] 狀態已寫入 {path}")
