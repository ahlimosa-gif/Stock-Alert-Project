# PROJECT_CONTEXT.md

最后更新：2026-06-15

## 项目结构
- `stock_alert_project/`：Python 股票提醒项目。
- `stock_alert_project/tests/`：本地单元测试。
- `stock_alert_project/templates/`：Flask 页面模板。
- `stock_alert_project/static/`：Flask 页面样式。
- 根目录项目记忆文件：`AGENTS.md`、`MEMORY_INDEX.md`、`PROJECT_CONTEXT.md`、`PROGRESS.md`、`DECISIONS.md`、`NEXT_TASKS.md`。

## stock_alert_project 模块
- `app.py`：Flask MVP 主入口，包含 landing、注册、登录、dashboard、watchlist、Telegram 设置、Stripe Checkout、Stripe webhook 和 health check。
- `database.py`：SQLAlchemy 数据层，默认 MySQL，包含 `User`、`WatchlistItem`、`DailyReport`。
- `config.py`：读取 `.env` 配置，包含 Telegram、OpenAI、Stripe、数据库、站点 URL、股票列表、RSI 阈值和 MA 周期。
- `ta_lib_wrapper.py`：计算 RSI 和 EMA，已处理空数据和缺失 `Close` 的情况。
- `telegram_bot.py`：构造并发送 Telegram 提醒，兼容 `python-telegram-bot==20.7` 的 async `send_message`。
- `ai_agent.py`：使用 OpenAI 生成广东话交易建议；未配置 API key 时返回本地 fallback。
- `stock_alert.py`：抓取行情、判断买卖信号、发送通知、支持 `run_once()` 和持续监控。
- `backtest.py`：基于 RSI 阈值做简单回测。
- `subscription.py`：兼容入口，复用 `app.py` 的 Flask app。
- `tests/test_core.py`：不调用真实 Telegram/OpenAI/Stripe/Yahoo 的核心单元测试，覆盖 dashboard、webhook、订阅校验。

## 运行方式
- 安装依赖：`pip install -r requirements.txt`
- 运行 Web MVP：`python app.py`
- 运行监控：`python stock_alert.py`
- 运行回测：`python backtest.py`
- 运行兼容订阅入口：`python subscription.py`
- 运行测试：`python -m unittest discover -s tests -v`

## API
- `POST /api/subscribe`
- 请求字段：`user_id`
- 成功返回：`success`、`session_id`、`checkout_url`、`price`
- 失败返回：`success=false`、`error`
- `POST /api/webhook/stripe`
- 处理事件：`checkout.session.completed`、`customer.subscription.updated`、`customer.subscription.deleted`、`invoice.payment_failed`
