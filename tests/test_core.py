import unittest
from types import SimpleNamespace
from unittest.mock import patch

import pandas as pd

from app import create_app
from ai_agent import AIAgent
from backtest import backtest_rsi_ma
from database import User, WatchlistItem, get_session
from stock_alert import StockAlert
from ta_lib_wrapper import TALIBWrapper
from telegram_bot import TelegramNotifier


class FakeBot:
    def __init__(self):
        self.calls = []

    async def send_message(self, **kwargs):
        self.calls.append(kwargs)
        return {"ok": True}


class FakeAI:
    def generate_trading_suggestion(self, symbol, price, rsi, ma):
        return "mock suggestion"


class FakeTelegram:
    def __init__(self):
        self.calls = []

    def send_alert(self, message, symbol, rsi, action):
        self.calls.append((message, symbol, rsi, action))
        return True


class FakeTicker:
    def __init__(self, df):
        self.df = df

    def history(self, period):
        return self.df


def price_frame():
    return pd.DataFrame(
        {
            "Close": [
                100,
                101,
                102,
                100,
                99,
                98,
                97,
                99,
                101,
                103,
                104,
                102,
                100,
                98,
                99,
                101,
                103,
                105,
                104,
                106,
            ]
        }
    )


class CoreTests(unittest.TestCase):
    def setUp(self):
        self.app = create_app(database_url="sqlite:///:memory:", testing=True)
        self.client = self.app.test_client()

    def test_indicators_handle_empty_data(self):
        wrapper = TALIBWrapper()
        self.assertEqual(wrapper.calculate_rsi(pd.Series(dtype="float64")), 0.0)
        self.assertEqual(wrapper.calculate_ema(pd.Series(dtype="float64")), 0.0)
        self.assertEqual(wrapper.get_all_indicators(pd.DataFrame()), {"RSI_14": 0.0, "EMA_20": 0.0})

    def test_telegram_notifier_uses_async_bot(self):
        bot = FakeBot()
        notifier = TelegramNotifier(bot=bot, token="token", chat_id="chat")
        self.assertTrue(notifier.send_alert("123.45", "AAPL", 28.1, "BUY"))
        self.assertEqual(len(bot.calls), 1)
        self.assertEqual(bot.calls[0]["chat_id"], "chat")
        self.assertEqual(bot.calls[0]["parse_mode"], "Markdown")

    def test_ai_agent_handles_mock_response(self):
        agent = AIAgent()
        agent.client = SimpleNamespace(
            chat=SimpleNamespace(
                completions=SimpleNamespace(
                    create=lambda **kwargs: SimpleNamespace(
                        choices=[SimpleNamespace(message=SimpleNamespace(content="mock suggestion"))]
                    )
                )
            )
        )
        self.assertEqual(agent.generate_trading_suggestion("AAPL", 100, 50, 99), "mock suggestion")

    def test_stock_alert_get_stock_data_and_check_alert(self):
        telegram = FakeTelegram()
        alert = StockAlert(telegram=telegram, ai=FakeAI(), ta=TALIBWrapper())
        with patch("stock_alert.yf.Ticker", return_value=FakeTicker(price_frame())):
            data = alert.get_stock_data("AAPL")
        self.assertEqual(data["symbol"], "AAPL")
        self.assertIsInstance(data["price"], float)

        action = alert.check_alert({"symbol": "AAPL", "price": 100.0, "rsi": 20.0, "ma": 98.0})
        self.assertEqual(action, "BUY")
        self.assertEqual(telegram.calls[0][1], "AAPL")

    def test_stock_alert_determine_action_does_not_send(self):
        telegram = FakeTelegram()
        alert = StockAlert(telegram=telegram, ai=FakeAI(), ta=TALIBWrapper())
        action = alert.determine_action({"symbol": "AAPL", "price": 100.0, "rsi": 20.0, "ma": 98.0})
        self.assertEqual(action, "BUY")
        self.assertEqual(telegram.calls, [])

    def test_backtest_uses_mock_market_data(self):
        with patch("backtest.yf.Ticker", return_value=FakeTicker(price_frame())):
            result = backtest_rsi_ma("AAPL", period="1mo")
        self.assertNotIn("error", result)
        self.assertEqual(result["symbol"], "AAPL")
        self.assertIsInstance(result["final_value"], float)

    def test_subscribe_validates_required_fields(self):
        response = self.client.post("/api/subscribe", json={})
        self.assertEqual(response.status_code, 400)
        self.assertFalse(response.get_json()["success"])

    def test_register_creates_user_and_starter_watchlist(self):
        response = self.client.post(
            "/register",
            data={"email": "user@example.com", "password": "password123"},
            follow_redirects=True,
        )
        self.assertEqual(response.status_code, 200)
        db = get_session()
        user = db.query(User).filter(User.email == "user@example.com").first()
        self.assertIsNotNone(user)
        items = db.query(WatchlistItem).filter(WatchlistItem.user_id == user.id).all()
        self.assertGreaterEqual(len(items), 1)

    def test_stripe_webhook_updates_subscription_status(self):
        self.client.post("/register", data={"email": "paid@example.com", "password": "password123"})
        db = get_session()
        user = db.query(User).filter(User.email == "paid@example.com").first()
        event = {
            "type": "checkout.session.completed",
            "data": {
                "object": {
                    "customer": "cus_test",
                    "subscription": "sub_test",
                    "metadata": {"user_id": str(user.id)},
                }
            },
        }
        response = self.client.post("/api/webhook/stripe", json=event)
        self.assertEqual(response.status_code, 200)
        updated_user = get_session().query(User).filter(User.email == "paid@example.com").first()
        self.assertEqual(updated_user.subscription_status, "active")
        self.assertEqual(updated_user.stripe_subscription_id, "sub_test")

    def test_dashboard_renders_empty_state_without_market_call(self):
        self.client.post("/register", data={"email": "dash@example.com", "password": "password123"})
        db = get_session()
        user = db.query(User).filter(User.email == "dash@example.com").first()
        db.query(WatchlistItem).filter(WatchlistItem.user_id == user.id).delete()
        db.commit()
        response = self.client.get("/dashboard")
        self.assertEqual(response.status_code, 200)
        self.assertIn(b"No symbols yet", response.data)


if __name__ == "__main__":
    unittest.main()
