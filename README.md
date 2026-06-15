# Stock Alert Project

Stock Alert Project is a subscription-ready Flask MVP for Chinese stock alerts. It includes user accounts, watchlists, Telegram binding, Stripe Checkout, Stripe webhook status updates, technical indicators, and daily report generation.

## Setup
1. Copy `.env.example` to `.env`
2. Fill in your API keys in `.env`
3. Set `DATABASE_URL` to a MySQL database, for example `mysql+pymysql://stock_alert_user:change_me@localhost:3306/stock_alert_project`
4. Install: `pip install -r requirements.txt`
5. Run web MVP: `python app.py`

## Commands
- Run web MVP: `python app.py`
- Run monitor: `python stock_alert.py`
- Run backtest: `python backtest.py`
- Run subscription-compatible entry: `python subscription.py`
- Run tests: `python -m unittest discover -s tests`

## Pages
- `GET /`: landing page
- `GET|POST /register`: create an account
- `GET|POST /login`: login
- `GET /dashboard`: watchlist, Telegram, billing, and daily report dashboard
- `POST /watchlist`: add a symbol
- `POST /watchlist/<item_id>/delete`: remove a symbol
- `POST /settings/telegram`: bind Telegram chat ID
- `POST /report/daily`: generate a daily watchlist report
- `POST /billing/checkout`: redirect logged-in user to Stripe Checkout

## API: Subscribe
`POST /api/subscribe`

Request JSON:
- `user_id`: local user ID

Response fields:
- `success`: boolean result
- `session_id`: Stripe Checkout Session ID when successful
- `checkout_url`: Stripe-hosted checkout URL when successful
- `price`: configured monthly price string
- `error`: error message when unsuccessful

## API: Stripe Webhook
`POST /api/webhook/stripe`

Handled event types:
- `checkout.session.completed`
- `customer.subscription.updated`
- `customer.subscription.deleted`
- `invoice.payment_failed`

The webhook uses `STRIPE_WEBHOOK_SECRET` when configured. For local tests, unsigned JSON is accepted only when that secret is empty.

## Notes
- Never commit `.env` to GitHub
- Use Stripe test keys during development
- Telegram alerts require a valid bot token and chat ID
- `.env.example` is safe to upload; `.env` is local only
- Stock indicators and AI summaries are for information only, not financial advice
