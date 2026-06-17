# NEXT_TASKS.md

最后更新：2026-06-17

## 最高优先级
1. 轮换曾在聊天中暴露过的 Telegram、OpenAI、Stripe 密钥。
2. 替换 `.env` / 部署环境中的生产值：`APP_BASE_URL`、真实 MySQL `DATABASE_URL`、`STRIPE_WEBHOOK_SECRET`。
3. 增加每用户后台定时 alert worker：读取 `User`、`WatchlistItem`、`telegram_chat_id`，只给 active/trial-allowed 用户发送 Telegram alert。
4. 增加 subscription gating：明确 trial 规则，限制未付费用户的 watchlist、report、alert 功能。
5. 在 Stripe Dashboard 配置 `POST /api/webhook/stripe` 的 webhook endpoint，并使用测试模式完整跑一遍 Checkout。

## 已上传文件清单
- `AGENTS.md`
- `MEMORY_INDEX.md`
- `PROJECT_CONTEXT.md`
- `PROGRESS.md`
- `DECISIONS.md`
- `NEXT_TASKS.md`
- `.env.example`
- `.gitignore`
- `README.md`
- `requirements.txt`
- `config.py`
- `ta_lib_wrapper.py`
- `telegram_bot.py`
- `ai_agent.py`
- `backtest.py`
- `subscription.py`
- `stock_alert.py`
- `database.py`
- `app.py`
- `static/styles.css`
- `templates/base.html`
- `templates/index.html`
- `templates/login.html`
- `templates/register.html`
- `templates/dashboard.html`
- `tests/test_core.py`

## 已完成复查
- `python -m compileall -q .` 通过。
- `python -m unittest discover -s tests -v` 通过，10 个测试 OK。
- 敏感信息扫描通过。
- GitHub 远端 `.env` 回读为 404，确认未上传。
- 2026-06-17 项目记忆文档已同步到 GitHub `main`。
- 2026-06-17 本地 `.env` 已补齐缺失 key；剩余问题是生产值尚未替换。

## 可选改进
- 增加 `--once` CLI 参数，方便只运行一次监控。
- 增加日志文件或简单 structured logging。
- 增加 Customer Portal，允许用户自助取消或管理订阅。
- 增加后台任务队列，避免 dashboard 每次请求同步抓取行情。
- 增加 CSRF protection、rate limiting、password reset、email verification。
- 增加 Terms、Privacy、Refund Policy 和更完整的 non-financial-advice disclaimer。
