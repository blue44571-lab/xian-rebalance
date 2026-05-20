import yfinance as yf
import pytz
from datetime import datetime


def fetch_prices(tickers: list[str]) -> dict[str, float]:
    """抓取多檔股票最新收盤價，回傳 {ticker: price}。"""
    prices = {}
    for ticker in tickers:
        try:
            stock = yf.Ticker(ticker)
            hist = stock.history(period="5d")
            if hist.empty:
                raise ValueError(f"查無價格資料：{ticker}")
            prices[ticker] = float(hist["Close"].iloc[-1])
        except Exception as e:
            print(f"[data_fetcher] 抓取 {ticker} 失敗：{e}")
            prices[ticker] = 0.0
    return prices


def is_market_open(config: dict) -> bool:
    """判斷台灣股市目前是否開盤中。"""
    tz = pytz.timezone(config["monitoring"]["timezone"])
    now = datetime.now(tz)

    if now.weekday() >= 5:
        return False

    open_t = datetime.strptime(config["monitoring"]["market_open"], "%H:%M").time()
    close_t = datetime.strptime(config["monitoring"]["market_close"], "%H:%M").time()
    return open_t <= now.time() <= close_t


def get_taipei_now(config: dict) -> datetime:
    tz = pytz.timezone(config["monitoring"]["timezone"])
    return datetime.now(tz)
