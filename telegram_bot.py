import asyncio
import inspect
from typing import Optional
from telegram import Bot
from config import TELEGRAM_BOT_TOKEN, TELEGRAM_CHAT_ID


class TelegramNotifier:
    def __init__(self, bot=None, token: Optional[str] = None, chat_id: Optional[str] = None):
        self.token = token if token is not None else TELEGRAM_BOT_TOKEN
        self.chat_id = chat_id if chat_id is not None else TELEGRAM_CHAT_ID
        self.enabled = bool(self.token and self.chat_id)
        self.bot = bot if bot is not None else (Bot(token=self.token) if self.enabled else None)

    def build_alert_text(self, message: str, symbol: str, rsi: float, action: str) -> str:
        link = "https://www.tradingview.com/symbols/" + symbol + "/"
        if action == "BUY":
            return "*" + symbol + " 買入信號!*\n\n價格：$" + message + "\nRSI：" + str(round(rsi, 2)) + "（過低，強烈買入！）\n\n查看：" + link
        if action == "SELL":
            return "*" + symbol + " 賣出信號!*\n\n價格：$" + message + "\nRSI：" + str(round(rsi, 2)) + "（過高，強烈賣出！）\n\n查看：" + link
        return "*" + symbol + " 技術信號!*\n\n價格：$" + message + "\nRSI：" + str(round(rsi, 2)) + "\n\n查看：" + link

    def send_alert(self, message: str, symbol: str, rsi: float, action: str):
        if not self.enabled or not self.bot:
            print("Telegram is not configured; skipped alert for " + symbol)
            return False
        txt = self.build_alert_text(message, symbol, rsi, action)
        result = self.bot.send_message(chat_id=self.chat_id, text=txt, parse_mode="Markdown")
        if inspect.isawaitable(result):
            asyncio.run(result)
        return True
