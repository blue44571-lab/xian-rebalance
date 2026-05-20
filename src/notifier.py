import os
import requests
from datetime import datetime


TELEGRAM_TOKEN = os.environ.get("TELEGRAM_BOT_TOKEN", "")
TELEGRAM_CHAT_ID = os.environ.get("TELEGRAM_CHAT_ID", "")


def _send_telegram(text: str) -> bool:
    if not TELEGRAM_TOKEN or not TELEGRAM_CHAT_ID:
        print("[notifier] 未設定 TELEGRAM_BOT_TOKEN 或 TELEGRAM_CHAT_ID，跳過通知。")
        return False
    url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage"
    payload = {"chat_id": TELEGRAM_CHAT_ID, "text": text, "parse_mode": "HTML"}
    try:
        resp = requests.post(url, json=payload, timeout=10)
        resp.raise_for_status()
        print("[notifier] Telegram 通知已發送。")
        return True
    except Exception as e:
        print(f"[notifier] 發送失敗：{e}")
        return False


def _fmt_money(v: float) -> str:
    return f"${v:,.0f}"


def _beta_emoji(status: str) -> str:
    return {"normal": "✅", "sell": "🔴", "buy": "🟢"}.get(status, "⚪")


def send_alert(portfolio: dict, rebalance: dict, now: datetime) -> bool:
    """觸發再平衡條件時發送警報。"""
    pos = portfolio["positions"][0] if portfolio["positions"] else {}
    action_text = (
        f"賣出 {pos.get('name','')} 約 <b>{_fmt_money(rebalance['amount_twd'])} TWD</b>"
        f"（約 {rebalance.get('shares_estimate', '?')} 股）"
        if rebalance["action"] == "SELL"
        else f"買進 {pos.get('name','')} 約 <b>{_fmt_money(rebalance['amount_twd'])} TWD</b>"
        f"（約 {rebalance.get('shares_estimate', '?')} 股）"
    )

    msg = (
        f"⚠️ <b>再平衡觸發警報</b>｜{now.strftime('%Y-%m-%d %H:%M')}\n"
        f"━━━━━━━━━━━━━━━━\n"
        f"📐 Portfolio Beta：<b>{rebalance['current_beta']}</b>\n"
        f"目標 Beta：{rebalance['target_beta']}  "
        f"（上限 {rebalance['upper_limit']} / 下限 {rebalance['lower_limit']}）\n"
        f"偏離幅度：{rebalance['deviation_pct']:+.2f}%\n"
        f"\n"
        f"💼 持倉現況\n"
    )
    for p in portfolio["positions"]:
        msg += f"  {p['name']}：{_fmt_money(p['value'])}（{p['weight']*100:.1f}%）\n"
    msg += f"  現金：{_fmt_money(portfolio['cash_twd'])}（{portfolio['cash_weight']*100:.1f}%）\n"
    msg += f"  總資產：{_fmt_money(portfolio['total_value'])}\n"
    msg += f"\n🔔 建議操作\n  {action_text}\n"
    msg += f"  執行後 Beta 回到 {rebalance['target_beta']}"

    return _send_telegram(msg)


def send_daily_report(portfolio: dict, rebalance: dict, now: datetime) -> bool:
    """每日收盤後發送日報。"""
    status_line = (
        "正常範圍內，無需操作 ✅"
        if not rebalance["triggered"]
        else f"{'🔴 需賣出' if rebalance['action']=='SELL' else '🟢 需買進'}，請查看警報"
    )

    msg = (
        f"📊 <b>再平衡日報</b>｜{now.strftime('%Y-%m-%d')} 收盤\n"
        f"━━━━━━━━━━━━━━━━\n"
        f"💼 投資組合\n"
    )
    for p in portfolio["positions"]:
        msg += f"  {p['name']}：{_fmt_money(p['value'])}（{p['weight']*100:.1f}%）\n"
    msg += f"  現金：{_fmt_money(portfolio['cash_twd'])}（{portfolio['cash_weight']*100:.1f}%）\n"
    msg += f"  總資產：{_fmt_money(portfolio['total_value'])}\n\n"
    msg += (
        f"📐 Portfolio Beta\n"
        f"  目前：<b>{rebalance['current_beta']}</b>　目標：{rebalance['target_beta']}\n"
        f"  偏離：{rebalance['deviation_pct']:+.2f}%\n"
        f"  區間：{rebalance['lower_limit']} ～ {rebalance['upper_limit']}\n\n"
        f"🔔 再平衡狀態：{status_line}"
    )
    return _send_telegram(msg)
