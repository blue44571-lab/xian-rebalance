import json
import os
from datetime import datetime

STATE_PATH   = os.path.join(os.path.dirname(__file__), "..", "docs", "data", "state.json")
RECORDS_PATH = os.path.join(os.path.dirname(__file__), "..", "docs", "data", "records.json")


def write_state(portfolio: dict, rebalance: dict, now: datetime) -> None:
    """將最新狀態寫入 state.json，供 Dashboard 讀取。"""
    state = {
        "last_updated": now.isoformat(),
        "portfolio": {
            "total_value":       portfolio["total_value"],
            "total_stock_value": portfolio["total_stock_value"],
            "cash_twd":          portfolio["cash_twd"],
            "cash_weight":       round(portfolio["cash_weight"], 4),
            "positions": [
                {
                    "ticker": p["ticker"],
                    "name":   p["name"],
                    "shares": p["shares"],
                    "price":  p["price"],
                    "value":  round(p["value"], 0),
                    "weight": round(p["weight"], 4),
                    "beta":   p["beta"],
                }
                for p in portfolio["positions"]
            ],
        },
        "rebalancing": {
            "target_alloc":      rebalance["target_alloc"],
            "target_stock":      rebalance["target_stock"],
            "current_stock":     rebalance["current_stock"],
            "adjustment":        rebalance["adjustment"],
            "shares_estimate":   rebalance["shares_estimate"],
            "action":            rebalance["action"],
            "status":            rebalance["status"],
            "triggered":         rebalance["triggered"],
            "amount_twd":        rebalance["amount_twd"],
            "current_alloc":     rebalance["current_alloc"],
            "dev_pct":           rebalance["dev_pct"],
            "upper":             rebalance["upper"],
            "lower":             rebalance["lower"],
            "current_beta":      rebalance["current_beta"],
            "target_beta":       rebalance["target_beta"],
        },
    }
    path = os.path.abspath(STATE_PATH)
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w", encoding="utf-8") as f:
        json.dump(state, f, ensure_ascii=False, indent=2)
    print(f"[state_writer] 狀態已更新")


def append_daily_record(portfolio: dict, rebalance: dict, now: datetime) -> dict | None:
    """
    將當日收盤快照追加到 records.json。
    回傳昨日紀錄（供計算資產變化用），若無則回傳 None。
    """
    path = os.path.abspath(RECORDS_PATH)
    os.makedirs(os.path.dirname(path), exist_ok=True)

    # 讀取現有紀錄
    try:
        with open(path, "r", encoding="utf-8") as f:
            data = json.load(f)
    except (FileNotFoundError, json.JSONDecodeError):
        data = {"records": []}

    records = data.get("records", [])
    today   = now.strftime("%Y-%m-%d")

    # 若今日已有紀錄（被重複呼叫），直接回傳前一日紀錄
    if records and records[-1].get("date") == today:
        print(f"[state_writer] 今日紀錄已存在，跳過")
        return records[-2] if len(records) >= 2 else None

    prev_record = records[-1] if records else None

    pos = portfolio["positions"][0] if portfolio["positions"] else {}
    new_record = {
        "date":      today,
        "total":     portfolio["total_value"],
        "stock":     portfolio["total_stock_value"],
        "cash":      portfolio["cash_twd"],
        "stock_pct": round(rebalance["current_alloc"] * 100, 2),
        "cash_pct":  round((1 - rebalance["current_alloc"]) * 100, 2),
        "price":     pos.get("price", 0),
        "shares":    pos.get("shares", 0),
        "beta":      portfolio["portfolio_beta"],
        "adjustment":rebalance["adjustment"],
    }
    records.append(new_record)
    data["records"] = records

    with open(path, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
    print(f"[state_writer] 每日紀錄已追加（{today}，共 {len(records)} 筆）")

    return prev_record
