# PROGRESS.md

最后更新：2026-06-17

## 已完成
- 创建项目记忆文件：`AGENTS.md`、`MEMORY_INDEX.md`、`PROJECT_CONTEXT.md`、`PROGRESS.md`、`DECISIONS.md`、`NEXT_TASKS.md`。
- 创建 `stock_alert_project` Python 项目。
- 创建 `.gitignore`、`.env.example`、`requirements.txt`、核心 Python 文件和 `README.md`。
- 本地创建 `.env`，只用于本机运行；确认 `.gitignore` 已忽略 `.env`。
- 修复 `stock_alert.py` 中误混入的 `python` 标记。
- 修复 `README.md` 中误混入的 `text` 标记。
- 修复 `ai_agent.py` 中 OpenAI 返回值读取方式。
- 将 `yfinance` 升级到 `1.4.1`，解决旧版本无法拉取 `AAPL` 数据的问题。
- 修复 `telegram_bot.py`，兼容 Telegram v20 async `send_message`。
- 增强 `config.py`、`ta_lib_wrapper.py`、`stock_alert.py`、`backtest.py`、`subscription.py` 的错误处理。
- 增加 `tests/test_core.py`，覆盖指标、Telegram mock、AI mock、StockAlert、backtest、Flask 参数校验。
- 更新 `README.md`，补充命令、API 字段和 `.env` 安全说明。
- 将项目升级为 Flask 订阅型 MVP：新增用户注册/登录、dashboard、watchlist、Telegram 设置、Daily AI Report、Stripe Checkout 和 Stripe webhook。
- 新增 SQLAlchemy 数据层，默认使用 MySQL，测试和浏览器验证使用临时 SQLite。
- 新增 `templates/` 和 `static/styles.css`，完成可用的 landing、auth 和 dashboard 页面。
- 已上传到 GitHub：`ahlimosa-gif/Stock-Alert-Project`，提交 `cb7b347910e357a70a47197703846bec522df33f`。

## 已验证
- `pip install -r requirements.txt` 通过。
- `pip check` 通过。
- `python -m compileall -q .` 通过。
- `python -m unittest discover -s tests -v` 通过，6 个测试 OK。
- 临时虚拟环境中 `python -m unittest discover -s tests -v` 通过，10 个测试 OK。
- 真实 `yfinance` 拉取 `AAPL` 5 日数据成功。
- `backtest_rsi_ma("AAPL", period="1mo")` 成功。
- 清理过 `__pycache__`。
- 敏感信息扫描通过，上传清单不包含 `.env`。
- 本地 Flask `/health` 返回 200，`database_ready=true`。
- 浏览器验证通过：landing、register、dashboard、添加 `AMD`、生成 Daily AI Report、桌面和 390px 手机宽度无页面级横向溢出。
- GitHub 回读确认：远端 `app.py` 和 `templates/dashboard.html` 可读，远端 `.env` 返回 404。
- 2026-06-17 再次运行 `python -m compileall -q .` 通过。
- 2026-06-17 再次运行 `python -m unittest discover -s tests -v` 通过，10 个测试 OK。
- 2026-06-17 已将项目记忆文档上传到 `ahlimosa-gif/Stock-Alert-Project`：`AGENTS.md`、`MEMORY_INDEX.md`、`PROJECT_CONTEXT.md`、`PROGRESS.md`、`DECISIONS.md`、`NEXT_TASKS.md`。
- 2026-06-17 远端回读确认 `NEXT_TASKS.md`、`PROGRESS.md`、`AGENTS.md` 可读，远端 `.env` 仍为 404。
- 2026-06-17 已审计本地 `.env`，补齐 `APP_BASE_URL`、`SECRET_KEY`、`DATABASE_URL`，并确认 `.env.example` 的所有必需 key 在 `.env` 中均存在。
- 2026-06-17 `.env` 敏感值未回显；`.gitignore` 仍包含 `.env`；GitHub 远端 `.env` 仍为 404。
- 2026-06-17 `python -m compileall -q .` 和 `python -m unittest discover -s tests -v` 通过，10 个测试 OK。

## 当前阻塞
- 无上传阻塞。
- 后续正式上线前仍需配置生产 MySQL、生产域名、Stripe webhook endpoint、测试/生产 Stripe key 切换策略，并轮换曾在聊天中暴露过的真实密钥。
- 当前 `.env` 仍需要真实生产值：`APP_BASE_URL`、`DATABASE_URL`、`STRIPE_WEBHOOK_SECRET`。其中 `DATABASE_URL` 是 MySQL 占位值，会导致直接启动时 `database_ready=false`。
- 当前适合 private beta / demo launch，不适合直接公开正式收费上线。
- 正式收费上线前必须补齐：每用户后台定时 alert worker、订阅权限 gating、Stripe Customer Portal、CSRF 保护、生产部署配置、法律页面和密钥轮换。
