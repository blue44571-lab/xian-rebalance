"""
再平衡監控主程式
用法：
  python main.py --mode monitor       # 盤中監控（GitHub Actions 每 15 分鐘呼叫）
  python main.py --mode daily-report  # 收盤日報（GitHub Actions 每日 13:45 呼叫）
"""
import argparse
import yaml
import os

from src.data_fetcher import fetch_prices, is_market_open, get_taipei_now
from src.portfolio import calculate_portfolio
from src.rebalancer import check_rebalance
from src.notifier import send_alert, send_daily_report
from src.state_writer import write_state, append_daily_record

CONFIG_PATH = os.path.join(os.path.dirname(__file__), "config", "settings.yaml")


def load_config() -> dict:
    with open(CONFIG_PATH, "r", encoding="utf-8") as f:
        return yaml.safe_load(f)


def run(mode: str) -> None:
    config = load_config()
    now = get_taipei_now(config)

    if mode == "monitor" and not is_market_open(config):
        print(f"[main] {now.strftime('%H:%M')} 非交易時段，結束。")
        return

    positions = config["portfolio"]["positions"]
    cash_twd  = config["portfolio"]["cash_twd"]
    tickers   = [p["ticker"] for p in positions]

    print(f"[main] 抓取價格：{tickers}")
    prices = fetch_prices(tickers)

    portfolio = calculate_portfolio(positions, cash_twd, prices)
    rebalance = check_rebalance(portfolio, config)

    print(
        f"[main] 總資產 ${portfolio['total_value']:,.0f}｜"
        f"正二 {rebalance['current_alloc']*100:.1f}%（目標 {rebalance['target_alloc']*100:.0f}%，"
        f"偏離 {rebalance['dev_pct']:+.2f}%）"
    )

    write_state(portfolio, rebalance, now)

    if mode == "monitor" and rebalance["triggered"]:
        print(f"[main] ⚠️ 觸發再平衡！動作：{rebalance['action']}，金額：${rebalance['amount_twd']:,.0f}")
        send_alert(portfolio, rebalance, now)
    elif mode == "daily-report":
        prev_record = append_daily_record(portfolio, rebalance, now)
        send_daily_report(portfolio, rebalance, now, prev_record)
    else:
        print("[main] 配置在正常範圍內，無需操作。")


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--mode", choices=["monitor", "daily-report"], default="monitor")
    args = parser.parse_args()
    run(args.mode)
