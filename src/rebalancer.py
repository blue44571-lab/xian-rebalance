from typing import Any


def check_rebalance(portfolio: dict[str, Any], config: dict) -> dict[str, Any]:
    """
    配置比例再平衡計算（三步驟）：
      Step 1：總資產 = 正二市值 + 現金
      Step 2：目標正二金額 = 總資產 × 目標配置比例
      Step 3：調整金額 = 目標正二金額 - 目前正二市值
              正值 → 買進；負值 → 賣出
    """
    target_alloc = config["rebalancing"]["target_allocation"]      # e.g., 0.60
    threshold    = config["rebalancing"]["deviation_threshold"]    # e.g., 0.10

    total_value  = portfolio["total_value"]
    stock_value  = portfolio["total_stock_value"]

    target_stock = total_value * target_alloc
    adjustment   = target_stock - stock_value   # + = 買進, - = 賣出

    current_alloc = stock_value / total_value if total_value > 0 else 0
    upper = target_alloc * (1 + threshold)
    lower = target_alloc * (1 - threshold)
    dev_pct = round((current_alloc - target_alloc) / target_alloc * 100, 2) if target_alloc > 0 else 0

    status = "sell" if current_alloc > upper else "buy" if current_alloc < lower else "normal"
    action = "SELL" if status == "sell" else "BUY" if status == "buy" else None

    shares_estimate = 0
    if action and portfolio["positions"]:
        price = portfolio["positions"][0]["price"]
        if price > 0:
            shares_estimate = round(abs(adjustment) / price)

    # Beta 資訊（供顯示用）
    portfolio_beta = portfolio["portfolio_beta"]
    stock_beta = portfolio["positions"][0]["beta"] if portfolio["positions"] else 2.0
    target_beta = round(target_alloc * stock_beta, 4)

    return {
        "target_alloc":     round(target_alloc, 4),
        "target_stock":     round(target_stock),
        "current_stock":    round(stock_value),
        "adjustment":       round(adjustment),
        "shares_estimate":  shares_estimate,
        "action":           action,
        "status":           status,
        "dev_pct":          dev_pct,
        "current_alloc":    round(current_alloc, 4),
        "upper":            round(upper, 4),
        "lower":            round(lower, 4),
        "triggered":        status != "normal",
        "amount_twd":       abs(round(adjustment)),
        "current_beta":     portfolio_beta,
        "target_beta":      target_beta,
    }
