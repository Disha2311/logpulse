from datetime import datetime, timezone
from typing import Optional, List
from sqlalchemy import String, Text, ForeignKey, DateTime, Integer
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.database import Base

def utc_now():
    return datetime.now(timezone.utc)

class User(Base):
    __tablename__ = "users"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    email: Mapped[str] = mapped_column(String(255), unique=True, index=True, nullable=False)
    hashed_password: Mapped[str] = mapped_column(String(255), nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utc_now, nullable=False)

    # Relationships
    logs: Mapped[List["Log"]] = relationship(back_populates="user", cascade="all, delete-orphan")

class Log(Base):
    __tablename__ = "logs"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    service: Mapped[str] = mapped_column(String(100), index=True, nullable=False)
    level: Mapped[str] = mapped_column(String(20), index=True, nullable=False)  # DEBUG/INFO/WARNING/ERROR/CRITICAL
    message: Mapped[str] = mapped_column(Text, nullable=False)
    timestamp: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utc_now, index=True, nullable=False)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"), nullable=False)

    # Relationships
    user: Mapped["User"] = relationship(back_populates="logs")

class AlertRule(Base):
    __tablename__ = "alert_rules"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    service: Mapped[str] = mapped_column(String(100), index=True, nullable=False)
    threshold: Mapped[int] = mapped_column(Integer, nullable=False)
    window_minutes: Mapped[int] = mapped_column(Integer, nullable=False)
    notify_email: Mapped[str] = mapped_column(String(255), nullable=False)
    notify_webhook_url: Mapped[Optional[str]] = mapped_column(String(1024), nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utc_now, nullable=False)

class AlertHistory(Base):
    __tablename__ = "alert_history"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    service: Mapped[str] = mapped_column(String(100), index=True, nullable=False)
    error_count: Mapped[int] = mapped_column(Integer, nullable=False)
    threshold: Mapped[int] = mapped_column(Integer, nullable=False)
    triggered_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utc_now, nullable=False)
    notified_email: Mapped[str] = mapped_column(String(255), nullable=False)
