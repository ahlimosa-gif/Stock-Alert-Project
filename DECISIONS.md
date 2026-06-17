# DECISIONS.md

最后更新：2026-06-15

## 技术决策
- 项目从轻量 Python 脚本升级为 Flask 订阅型 MVP，同时保留原监控脚本和回测脚本。
- 使用 Flask templates 和静态 CSS 实现 Web 页面，不额外引入 React/Vite。
- 使用 SQLAlchemy + PyMySQL，默认数据库为 MySQL；测试和本地浏览器 smoke test 可使用 SQLite。
- 使用 `.env` 存放真实密钥，`.env.example` 作为可上传模板。
- `.env` 必须由 `.gitignore` 忽略，不上传 GitHub。
- 使用 `python-dotenv` 读取环境变量。
- 使用 `yfinance==1.4.1`，因为原始 `0.2.40` 在当前环境无法成功获取 `AAPL` 行情。
- 使用 `python-telegram-bot==20.7`，并通过 `asyncio.run(...)` 执行 async `send_message`。
- Stripe 订阅采用 Checkout Session + Billing subscription 模式，不直接手写付款流程。
- 单元测试使用 `unittest` 和 mock，避免调用真实 Telegram、OpenAI、Stripe、Yahoo。

## 安全决策
- 不在代码、README、测试或记忆文件中记录真实 API key、bot token、Stripe key。
- 上传前必须扫描源码和文档，确认没有 `sk-`、`rk_live`、Telegram bot token 等真实凭据。
- GitHub 上传只能包含非敏感文件：源码、测试、README、`.env.example`、`.gitignore`、`requirements.txt`。

## 发布决策
- 目标仓库实际名称使用 `Stock-Alert-Project`，URL 为 `https://github.com/ahlimosa-gif/Stock-Alert-Project`。
- 如果远端仓库已存在，优先使用 GitHub connector 上传文件并回读验证。
- 当前环境无系统 `git`/`gh`，发布通过 GitHub connector 的 Git tree/commit/ref 完成。
