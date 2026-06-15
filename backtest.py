import yfinance as yf
from config import RSI_BUY_THRESHOLD, RSI_SELL_THRESHOLD
from ta_lib_wrapper import TALIBWrapper


def backtest_rsi_ma(symbol: str, period: str = "1y", initial_cash: float = 10000):
    symbol = symbol.strip()
    if not symbol:
        return {"error": "Missing symbol"}
    if initial_cash <= 0:
        return {"error": "Initial cash must be positive"}
    try:
        df = yf.Ticker(symbol).history(period=period)
    except Exception as e:
        return {"error": "Data fetch failed: " + str(e)}
    if df.empty or "Close" not in df:
        return {"error": "No data"}
    t = TALIBWrapper()
    close = df["Close"].dropna()
    if close.empty:
        return {"error": "No close prices"}
    cash = initial_cash
    position = 0.0
    trades = 0
    for i in range(len(close)):
        s = close.iloc[:i + 1]
        rsi = t.calculate_rsi(s) if len(s) >= 15 else None
        if rsi is None:
            continue
        price = float(close.iloc[i])
        if rsi < RSI_BUY_THRESHOLD and position == 0:
            position = cash / price
            cash = 0
            trades += 1
        elif rsi > RSI_SELL_THRESHOLD and position > 0:
            cash = position * price
            position = 0
            trades += 1
    final_value = cash + position * float(close.iloc[-1])
    return {"symbol": symbol, "initial_cash": initial_cash, "final_value": round(final_value, 2), "profit": round(final_value - initial_cash, 2), "profit_pct": round((final_value - initial_cash) / initial_cash * 100, 2), "trades": trades}


if __name__ == "__main__":
    print(backtest_rsi_ma("AAPL"))
