from datetime import datetime
import time
import yfinance as yf
from telegram_bot import TelegramNotifier
from ai_agent import AIAgent
from ta_lib_wrapper import TALIBWrapper
from config import STOCK_SYMBOLS, RSI_BUY_THRESHOLD, RSI_SELL_THRESHOLD


class StockAlert:
    def __init__(self, telegram=None, ai=None, ta=None):
        self.telegram = telegram if telegram is not None else TelegramNotifier()
        self.ai = ai if ai is not None else AIAgent()
        self.ta = ta if ta is not None else TALIBWrapper()

    def get_stock_data(self, symbol):
        symbol = symbol.strip()
        if not symbol:
            return None
        try:
            df = yf.Ticker(symbol).history(period="3mo")
        except Exception as e:
            print("Data fetch error for " + symbol + ": " + str(e))
            return None
        if df.empty or "Close" not in df:
            print("No market data for " + symbol)
            return None
        ind = self.ta.get_all_indicators(df)
        return {"symbol": symbol, "price": float(df["Close"].iloc[-1]), "rsi": ind["RSI_14"], "ma": ind["EMA_20"], "timestamp": datetime.now().isoformat()}

    def check_alert(self, data):
        if not data:
            return None
        action = self.determine_action(data)
        if action:
            symbol, price, rsi, ma = data["symbol"], data["price"], data["rsi"], data["ma"]
            ai_suggestion = self.ai.generate_trading_suggestion(symbol, price, rsi, ma)
            try:
                self.telegram.send_alert(str(round(price, 2)), symbol, rsi, action)
            except Exception as e:
                print("Telegram error: " + str(e))
            print(symbol + " " + action + " | Price: " + str(round(price, 2)) + " | RSI: " + str(round(rsi, 2)) + "\n" + ai_suggestion)
        return action

    def determine_action(self, data):
        symbol, price, rsi, ma = data["symbol"], data["price"], data["rsi"], data["ma"]
        action = None
        if rsi < RSI_BUY_THRESHOLD:
            action = "BUY"
        elif rsi > RSI_SELL_THRESHOLD:
            action = "SELL"
        elif price > ma * 1.02:
            action = "BUY"
        elif price < ma * 0.98:
            action = "SELL"
        return action

    def run_once(self, symbols=None):
        results = []
        for s in symbols or STOCK_SYMBOLS:
            d = self.get_stock_data(s)
            action = self.check_alert(d) if d else None
            results.append({"symbol": s, "has_data": bool(d), "action": action})
        return results

    def monitor_portfolio(self, interval=300):
        print("Starting stock alert monitor...")
        while True:
            self.run_once()
            time.sleep(interval)


if __name__ == "__main__":
    StockAlert().monitor_portfolio()
