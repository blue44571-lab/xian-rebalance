import os
import requests
from datetime import datetime


TELEGRAM_TOKEN  = os.environ.get("TELEGRAM_BOT_TOKEN", "")
TELEGRAM_CHAT_ID = os.environ.get("TELEGRAM_CHAT_ID", "")


def _send_telegram(text: str) -> bool:
    if not TELEGRAM_TOKEN or not TELEGRAM_CHAT_ID:
        print("[notifier] 未設定 TELEGRAM_BOT_TOKEN 或 TELEGRAM_CHAT_ID，跳過通知。")
        return False
    url     = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage"
    payload = {"chat_id": TELEGRAM_CHAT_ID, "text": text, "parse_mode": "HTML"}
    try:
        resp = requests.post(url, json=payload, timeout=10)
        resp.raise_for_status()
        print("[notifier] Telegram 通知已發送。")
        return True
    except Exception as e:
        print(f"[notifier] 發送失敗：{e}")
        return False


def _fmt(v: float) -> str:
    return f"${v:,.0f}"


def send_alert(portfolio: dict, rebalance: dict, now: datetime) -> bool:
    """觸發再平衡條件時發送警報。"""
    pos        = portfolio["positions"][0] if portfolio["positions"] else {}
    verb       = "賣出" if rebalance["action"] == "SELL" else "買進"
    adj_sign   = "-" if rebalance["action"] == "SELL" else "+"
    target_pct = round(rebalance["target_alloc"] * 100)
    cash_pct   = 100 - target_pct

    msg = (
        f"⚠️ <b>再平衡觸發警報</b>｜{now.strftime('%Y-%m-%d %H:%M')}\n"
        f"━━━━━━━━━━━━━━━━\n"
        f"\n"
        f"📊 三步驟計算結果\n"
        f"  <b>Step 1</b> 總資產：{_fmt(portfolio['total_value'])}\n"
        f"  <b>Step 2</b> 目標正二金額：{_fmt(rebalance['target_stock'])}（{target_pct}%）\n"
        f"  <b>Step 3</b> 調整金額：<b>{adj_sign}{_fmt(rebalance['amount_twd'])}</b>\n"
        f"\n"
        f"💼 目前持倉\n"
        f"  {pos.get('name','正二')}：{_fmt(rebalance['current_stock'])}（{rebalance['current_alloc']*100:.1f}%）\n"
        f"  現金：{_fmt(portfolio['cash_twd'])}（{portfolio['cash_weight']*100:.1f}%）\n"
        f"\n"
        f"🔔 建議操作\n"
        f"  <b>{verb}</b> 00631L 約 {_fmt(rebalance['amount_twd'])} TWD\n"
        f"  約需 {rebalance['shares_estimate']:,} 股（@${pos.get('price', 0):.2f}）\n"
        f"  執行後：{target_pct}% 正二 / {cash_pct}% 現金"
    )
    return _send_telegram(msg)


def send_daily_report(portfolio: dict, rebalance: dict, now: datetime) -> bool:
    """每日收盤後發送日報。"""
    target_pct  = round(rebalance["target_alloc"] * 100)
    cash_pct    = 100 - target_pct
    adj         = rebalance["adjustment"]
    adj_sign    = "+" if adj >= 0 else ""
    status_line = (
        "✅ 正常，無需操作"
        if not rebalance["triggered"]
        else f"{'🔴 建議賣出' if rebalance['action']=='SELL' else '🟢 建議買進'} {_fmt(rebalance['amount_twd'])} TWD"
    )

    msg = (
        f"📊 <b>再平衡日報</b>｜{now.strftime('%Y-%m-%d')} 收盤\n"
        f"━━━━━━━━━━━━━━━━\n"
        f"\n"
        f"📈 三步驟計算\n"
        f"  總資產：{_fmt(portfolio['total_value'])}\n"
        f"  目標正二金額：{_fmt(rebalance['target_stock'])}（{target_pct}%）\n"
        f"  目前正二市值：{_fmt(rebalance['current_stock'])}（{rebalance['current_alloc']*100:.1f}%）\n"
        f"  調整金額：<b>{adj_sign}{_fmt(abs(adj))}</b>（{'買進' if adj >= 0 else '賣出'}）\n"
        f"\n"
        f"💼 持倉\n"
    )
    for p in portfolio["positions"]:
        msg += f"  {p['name']}：{_fmt(p['value'])}（{p['weight']*100:.1f}%）\n"
    msg += (
        f"  現金：{_fmt(portfolio['cash_twd'])}（{portfolio['cash_weight']*100:.1f}%）\n"
        f"\n"
        f"📐 Portfolio Beta：{rebalance['current_beta']}（目標 {rebalance['target_beta']}）\n"
        f"\n"
        f"🔔 狀態：{status_line}"
    )
    return _send_telegram(msg)
