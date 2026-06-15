from datetime import datetime
from functools import wraps
from typing import Optional

import stripe
from flask import Flask, flash, jsonify, redirect, render_template, request, session, url_for
from sqlalchemy.exc import IntegrityError

from config import (
    APP_BASE_URL,
    SECRET_KEY,
    STOCK_SYMBOLS,
    STRIPE_API_KEY,
    STRIPE_PRICE_ID,
    STRIPE_WEBHOOK_SECRET,
    SUBSCRIPTION_PRICE,
)
from database import DailyReport, User, WatchlistItem, configure_database, get_session, init_db, remove_session
from stock_alert import StockAlert

stripe.api_key = STRIPE_API_KEY


def create_app(database_url: Optional[str] = None, testing: bool = False):
    app = Flask(__name__)
    app.secret_key = SECRET_KEY
    app.config["TESTING"] = testing
    app.config["DB_READY"] = False
    app.config["DB_ERROR"] = None

    try:
        configure_database(database_url)
        init_db()
        app.config["DB_READY"] = True
    except Exception as e:
        app.config["DB_ERROR"] = str(e)

    app.teardown_appcontext(remove_session)

    def db_or_error():
        if not app.config["DB_READY"]:
            return None, "Database is not ready: " + str(app.config["DB_ERROR"])
        return get_session(), None

    def current_user():
        user_id = session.get("user_id")
        if not user_id or not app.config["DB_READY"]:
            return None
        db = get_session()
        return db.get(User, user_id)

    def login_required(view):
        @wraps(view)
        def wrapped(*args, **kwargs):
            if not current_user():
                flash("Please log in first.", "error")
                return redirect(url_for("login"))
            return view(*args, **kwargs)

        return wrapped

    def build_snapshot(symbols):
        alert = StockAlert()
        rows = []
        for symbol in symbols:
            data = alert.get_stock_data(symbol)
            if not data:
                rows.append({"symbol": symbol, "price": None, "rsi": None, "ma": None, "signal": "NO DATA"})
                continue
            signal = alert.determine_action(data) or "HOLD"
            rows.append(
                {
                    "symbol": data["symbol"],
                    "price": round(data["price"], 2),
                    "rsi": round(data["rsi"], 2),
                    "ma": round(data["ma"], 2),
                    "signal": signal,
                }
            )
        return rows

    def build_daily_report(user, rows):
        lines = [
            "Daily AI Report",
            "This report is for information only and is not financial advice.",
            "",
        ]
        actionable = [row for row in rows if row["signal"] in {"BUY", "SELL"}]
        if not rows:
            lines.append("Your watchlist is empty. Add symbols to start monitoring.")
        elif actionable:
            for row in actionable:
                lines.append(
                    row["symbol"]
                    + ": "
                    + row["signal"]
                    + " signal, price "
                    + str(row["price"])
                    + ", RSI "
                    + str(row["rsi"])
                    + "."
                )
        else:
            lines.append("No strong BUY or SELL alerts today. Keep watching your list.")
        if user.telegram_chat_id:
            lines.append("")
            lines.append("Telegram delivery is connected.")
        else:
            lines.append("")
            lines.append("Telegram is not connected yet.")
        return "\n".join(lines)

    @app.context_processor
    def inject_globals():
        return {"current_user": current_user(), "subscription_price": SUBSCRIPTION_PRICE}

    @app.route("/")
    def index():
        return render_template("index.html")

    @app.route("/register", methods=["GET", "POST"])
    def register():
        if request.method == "GET":
            return render_template("register.html")
        db, error = db_or_error()
        if error:
            flash(error, "error")
            return render_template("register.html"), 500
        email = (request.form.get("email") or "").strip().lower()
        password = request.form.get("password") or ""
        if not email or len(password) < 8:
            flash("Email is required and password must be at least 8 characters.", "error")
            return render_template("register.html"), 400
        user = User(email=email)
        user.set_password(password)
        db.add(user)
        try:
            db.commit()
        except IntegrityError:
            db.rollback()
            flash("This email is already registered.", "error")
            return render_template("register.html"), 409
        for symbol in STOCK_SYMBOLS[:4]:
            db.add(WatchlistItem(user_id=user.id, symbol=symbol))
        db.commit()
        session["user_id"] = user.id
        flash("Account created. Your starter watchlist is ready.", "success")
        return redirect(url_for("dashboard"))

    @app.route("/login", methods=["GET", "POST"])
    def login():
        if request.method == "GET":
            return render_template("login.html")
        db, error = db_or_error()
        if error:
            flash(error, "error")
            return render_template("login.html"), 500
        email = (request.form.get("email") or "").strip().lower()
        password = request.form.get("password") or ""
        user = db.query(User).filter(User.email == email).first()
        if not user or not user.check_password(password):
            flash("Invalid email or password.", "error")
            return render_template("login.html"), 401
        session["user_id"] = user.id
        flash("Welcome back.", "success")
        return redirect(url_for("dashboard"))

    @app.route("/logout", methods=["POST"])
    def logout():
        session.clear()
        flash("Logged out.", "success")
        return redirect(url_for("index"))

    @app.route("/dashboard")
    @login_required
    def dashboard():
        user = current_user()
        db = get_session()
        items = db.query(WatchlistItem).filter(WatchlistItem.user_id == user.id).order_by(WatchlistItem.symbol).all()
        symbols = [item.symbol for item in items]
        rows = build_snapshot(symbols)
        latest_report = db.query(DailyReport).filter(DailyReport.user_id == user.id).order_by(DailyReport.created_at.desc()).first()
        return render_template("dashboard.html", rows=rows, items=items, latest_report=latest_report)

    @app.route("/watchlist", methods=["POST"])
    @login_required
    def add_watchlist_item():
        user = current_user()
        symbol = (request.form.get("symbol") or "").strip().upper()
        if not symbol:
            flash("Symbol is required.", "error")
            return redirect(url_for("dashboard"))
        db = get_session()
        db.add(WatchlistItem(user_id=user.id, symbol=symbol))
        try:
            db.commit()
            flash(symbol + " added to your watchlist.", "success")
        except IntegrityError:
            db.rollback()
            flash(symbol + " is already in your watchlist.", "error")
        return redirect(url_for("dashboard"))

    @app.route("/watchlist/<int:item_id>/delete", methods=["POST"])
    @login_required
    def delete_watchlist_item(item_id):
        user = current_user()
        db = get_session()
        item = db.query(WatchlistItem).filter(WatchlistItem.id == item_id, WatchlistItem.user_id == user.id).first()
        if item:
            db.delete(item)
            db.commit()
            flash(item.symbol + " removed.", "success")
        return redirect(url_for("dashboard"))

    @app.route("/settings/telegram", methods=["POST"])
    @login_required
    def update_telegram():
        user = current_user()
        user.telegram_chat_id = (request.form.get("telegram_chat_id") or "").strip()
        get_session().commit()
        flash("Telegram chat ID saved.", "success")
        return redirect(url_for("dashboard"))

    @app.route("/report/daily", methods=["POST"])
    @login_required
    def create_daily_report():
        user = current_user()
        db = get_session()
        symbols = [item.symbol for item in user.watchlist_items]
        rows = build_snapshot(symbols)
        content = build_daily_report(user, rows)
        report = DailyReport(user_id=user.id, content=content)
        db.add(report)
        db.commit()
        flash("Daily report generated.", "success")
        return redirect(url_for("dashboard"))

    @app.route("/billing/checkout", methods=["POST"])
    @login_required
    def billing_checkout():
        user = current_user()
        result, status = create_checkout_session(user)
        if status != 200:
            flash(result["error"], "error")
            return redirect(url_for("dashboard"))
        return redirect(result["checkout_url"])

    @app.route("/api/subscribe", methods=["POST"])
    def api_subscribe():
        data = request.json or {}
        user_id = data.get("user_id") or session.get("user_id")
        db, error = db_or_error()
        if error:
            return jsonify({"success": False, "error": error}), 500
        if not user_id:
            return jsonify({"success": False, "error": "Missing user_id"}), 400
        user = db.get(User, int(user_id))
        if not user:
            return jsonify({"success": False, "error": "User not found"}), 404
        result, status = create_checkout_session(user)
        return jsonify(result), status

    def create_checkout_session(user):
        if not STRIPE_API_KEY or not STRIPE_PRICE_ID:
            return {"success": False, "error": "Stripe not configured"}, 500
        try:
            checkout = stripe.checkout.Session.create(
                mode="subscription",
                customer=user.stripe_customer_id or None,
                customer_email=None if user.stripe_customer_id else user.email,
                line_items=[{"price": STRIPE_PRICE_ID, "quantity": 1}],
                success_url=APP_BASE_URL + url_for("dashboard") + "?checkout=success",
                cancel_url=APP_BASE_URL + url_for("dashboard") + "?checkout=cancelled",
                metadata={"user_id": str(user.id)},
                subscription_data={"metadata": {"user_id": str(user.id)}},
            )
        except stripe.error.StripeError as e:
            return {"success": False, "error": "Stripe error: " + str(e)}, 502
        return {"success": True, "session_id": checkout.id, "checkout_url": checkout.url, "price": "$" + str(SUBSCRIPTION_PRICE) + "/month"}, 200

    @app.route("/api/webhook/stripe", methods=["POST"])
    def stripe_webhook():
        payload = request.data
        sig_header = request.headers.get("Stripe-Signature")
        try:
            if STRIPE_WEBHOOK_SECRET:
                event = stripe.Webhook.construct_event(payload, sig_header, STRIPE_WEBHOOK_SECRET)
            else:
                event = request.get_json(force=True)
        except Exception as e:
            return jsonify({"success": False, "error": "Invalid webhook: " + str(e)}), 400
        db, error = db_or_error()
        if error:
            return jsonify({"success": False, "error": error}), 500
        apply_stripe_event(db, event)
        return jsonify({"success": True})

    def apply_stripe_event(db, event):
        event_type = event.get("type")
        obj = event.get("data", {}).get("object", {})
        metadata = obj.get("metadata") or {}
        user_id = metadata.get("user_id")
        if not user_id and event_type and event_type.startswith("customer.subscription"):
            subscription_id = obj.get("id")
            user = db.query(User).filter(User.stripe_subscription_id == subscription_id).first()
        else:
            user = db.get(User, int(user_id)) if user_id else None
        if not user:
            return
        if event_type == "checkout.session.completed":
            user.stripe_customer_id = obj.get("customer")
            user.stripe_subscription_id = obj.get("subscription")
            user.subscription_status = "active"
        elif event_type == "customer.subscription.deleted":
            user.subscription_status = "cancelled"
        elif event_type == "customer.subscription.updated":
            user.subscription_status = obj.get("status") or user.subscription_status
        elif event_type == "invoice.payment_failed":
            user.subscription_status = "past_due"
        db.commit()

    @app.route("/health")
    def health():
        return jsonify({"status": "ok", "database_ready": app.config["DB_READY"], "time": datetime.utcnow().isoformat()})

    return app


app = create_app()


if __name__ == "__main__":
    app.run(port=5000, debug=True)
