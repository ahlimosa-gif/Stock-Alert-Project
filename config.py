from dotenv import load_dotenv
import os

load_dotenv()


def _get_int(name: str, default: int) -> int:
    value = os.getenv(name, str(default))
    try:
        return int(value)
    except (TypeError, ValueError):
        return default


TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
TELEGRAM_CHAT_ID = os.getenv("TELEGRAM_CHAT_ID")
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
STRIPE_API_KEY = os.getenv("STRIPE_API_KEY")
STRIPE_PRICE_ID = os.getenv("STRIPE_PRICE_ID")
STRIPE_WEBHOOK_SECRET = os.getenv("STRIPE_WEBHOOK_SECRET", "")
APP_BASE_URL = os.getenv("APP_BASE_URL", "http://localhost:5000").rstrip("/")
SECRET_KEY = os.getenv("SECRET_KEY", "dev-change-this-secret")
DATABASE_URL = os.getenv(
    "DATABASE_URL",
    "mysql+pymysql://stock_alert_user:change_me@localhost:3306/stock_alert_project",
)
SUBSCRIPTION_PRICE = _get_int("SUBSCRIPTION_PRICE", 29)
STOCK_SYMBOLS = [symbol.strip() for symbol in os.getenv("STOCK_SYMBOLS", "AAPL,TSLA,NVDA,MSFT").split(",") if symbol.strip()]
RSI_BUY_THRESHOLD = _get_int("RSI_BUY_THRESHOLD", 30)
RSI_SELL_THRESHOLD = _get_int("RSI_SELL_THRESHOLD", 70)
MA_PERIOD = _get_int("MA_PERIOD", 20)
