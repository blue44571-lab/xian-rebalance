from typing import Any


def check_rebalance(portfolio: dict[str, Any], config: dict) -> dict[str, Any]:
    """
    判斷是否需要再平衡，並計算精確的買賣金額（台幣）。

    再平衡公式：
      目標股票市值 = target_beta × 總資產 / 股票Beta
      買賣金額     = 目前股票市值 - 目標股票市值
    """
    target_beta = config["rebalancing"]["target_beta"]
    threshold = config["rebalancing"]["deviation_threshold"]
    current_beta = portfolio["portfolio_beta"]
    total_value = portfolio["total_value"]

    upper_limit = round(target_beta * (1 + threshold), 4)
    lower_limit = round(target_beta * (1 - threshold), 4)
    deviation_pct = round((current_beta - target_beta) / target_beta * 100, 2)

    result = {
        "current_beta": current_beta,
        "target_beta": target_beta,
        "upper_limit": upper_limit,
        "lower_limit": lower_limit,
        "deviation_pct": deviation_pct,
        "triggered": False,
        "action": None,
        "amount_twd": 0,
        "status": "normal",
    }

    for pos in portfolio["positions"]:
        if pos["beta"] <= 0:
            continue

        target_stock_value = target_beta * total_value / pos["beta"]
        diff = pos["value"] - target_stock_value  # 正 → 持股過多；負 → 持股不足

        if current_beta > upper_limit:
            result["triggered"] = True
            result["action"] = "SELL"
            result["amount_twd"] = round(diff)
            result["status"] = "sell"
            # 換算約需賣幾股
            if pos["price"] > 0:
                result["shares_estimate"] = round(diff / pos["price"])
        elif current_beta < lower_limit:
            result["triggered"] = True
            result["action"] = "BUY"
            result["amount_twd"] = round(-diff)
            result["status"] = "buy"
            if pos["price"] > 0:
                result["shares_estimate"] = round(-diff / pos["price"])
        break  # 目前只有一檔持倉

    return result
