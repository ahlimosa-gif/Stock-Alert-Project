from datetime import datetime, timezone
from typing import Optional

from sqlalchemy import Column, DateTime, ForeignKey, Integer, String, Text, UniqueConstraint, create_engine
from sqlalchemy.orm import declarative_base, relationship, scoped_session, sessionmaker
from werkzeug.security import check_password_hash, generate_password_hash

from config import DATABASE_URL


Base = declarative_base()
SessionLocal = scoped_session(sessionmaker(autoflush=False, autocommit=False))
engine = None


def utc_now():
    return datetime.now(timezone.utc)


class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True)
    email = Column(String(255), unique=True, nullable=False, index=True)
    password_hash = Column(String(255), nullable=False)
    telegram_chat_id = Column(String(64), nullable=True)
    stripe_customer_id = Column(String(255), nullable=True)
    stripe_subscription_id = Column(String(255), nullable=True)
    subscription_status = Column(String(32), nullable=False, default="trial")
    created_at = Column(DateTime, nullable=False, default=utc_now)

    watchlist_items = relationship("WatchlistItem", back_populates="user", cascade="all, delete-orphan")
    reports = relationship("DailyReport", back_populates="user", cascade="all, delete-orphan")

    def set_password(self, password: str):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password: str) -> bool:
        return check_password_hash(self.password_hash, password)


class WatchlistItem(Base):
    __tablename__ = "watchlist_items"
    __table_args__ = (UniqueConstraint("user_id", "symbol", name="uq_watchlist_user_symbol"),)

    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False, index=True)
    symbol = Column(String(32), nullable=False)
    created_at = Column(DateTime, nullable=False, default=utc_now)

    user = relationship("User", back_populates="watchlist_items")


class DailyReport(Base):
    __tablename__ = "daily_reports"

    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False, index=True)
    content = Column(Text, nullable=False)
    created_at = Column(DateTime, nullable=False, default=utc_now)

    user = relationship("User", back_populates="reports")


def configure_database(database_url: Optional[str] = None):
    global engine
    SessionLocal.remove()
    engine = create_engine(database_url or DATABASE_URL, pool_pre_ping=True)
    SessionLocal.configure(bind=engine)
    return engine


def init_db():
    if engine is None:
        configure_database()
    Base.metadata.create_all(bind=engine)


def reset_db_for_tests(database_url: str):
    configure_database(database_url)
    Base.metadata.drop_all(bind=engine)
    Base.metadata.create_all(bind=engine)


def get_session():
    return SessionLocal()


def remove_session(exception=None):
    SessionLocal.remove()
